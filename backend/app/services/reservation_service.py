"""Reservation lifecycle — booking, payment, pet service add-ons.

State is held in process memory (the demo doesn't need durability).
Seed `stays.json` is materialized into the same store at startup so each
persona has trips immediately on login.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import date, datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from app.data.loader import get_seed
from app.models.reservation import (
    CreateReservationRequest,
    PetServiceBooking,
    PetServiceBookingRequest,
    ReservationResponse,
)
from app.services.guest_preference_service import get_pet_service_radius_miles
from app.services.partner_service import get_partner_by_id, get_partners_near_hotel

logger = logging.getLogger(__name__)

# In-process stores. Reset on every uvicorn restart.
_reservations: dict[str, dict[str, Any]] = {}
_pet_bookings: dict[str, list[dict[str, Any]]] = {}


# --- Helpers ---------------------------------------------------------------


def _find_hotel(hotel_id: str) -> dict[str, Any]:
    """Look up a hotel by id or 404."""
    for hotel in get_seed("hotels"):
        if hotel.get("id") == hotel_id:
            return hotel
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")


def _nights_between(check_in: str, check_out: str) -> int:
    """Compute night count, validating the date order."""
    try:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {exc}",
        ) from exc
    delta = (end - start).days
    if delta < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out must be after check-in",
        )
    return delta


def _new_confirmation_number() -> str:
    """Generate an 8-digit confirmation number."""
    # secrets keeps it cryptographically clean; format-wise still 8 digits.
    return f"{secrets.randbelow(90_000_000) + 10_000_000:08d}"


def _to_response(res: dict[str, Any]) -> ReservationResponse:
    """Project an internal reservation dict into the API response shape."""
    hotel = _find_hotel(res["hotel_id"])
    bookings = [
        PetServiceBooking(**_normalize_booking(b))
        for b in _pet_bookings.get(res["id"], [])
    ]
    return ReservationResponse(
        id=res["id"],
        guest_id=res["guest_id"],
        hotel_id=res["hotel_id"],
        hotel_name=hotel["name"],
        hotel_city=hotel["city"],
        hotel_image_url=hotel["image_url"],
        check_in=res["check_in"],
        check_out=res["check_out"],
        nights=res["nights"],
        room_type=res["room_type"],
        confirmation_number=res["confirmation_number"],
        status=res["status"],
        has_pet=res["has_pet"],
        pet_id=res.get("pet_id"),
        pet_fee_charged=res.get("pet_fee_charged"),
        total_usd=res["total_usd"],
        payment_status=res["payment_status"],
        pet_service_bookings=bookings,
    )


# --- Lifecycle hooks --------------------------------------------------------


def init_reservations_from_seeds() -> None:
    """Populate the in-memory store from `stays.json` on startup."""
    _reservations.clear()
    _pet_bookings.clear()

    hotels_by_id = {h["id"]: h for h in get_seed("hotels")}
    for stay in get_seed("stays"):
        hotel = hotels_by_id.get(stay["hotel_id"])
        if hotel is None:
            logger.warning("Skipping seeded stay %s: hotel %s missing",
                           stay.get("id"), stay.get("hotel_id"))
            continue

        nights = stay.get("nights") or _nights_between(stay["check_in"], stay["check_out"])
        total = nights * hotel["price_per_night"]
        if stay.get("pet_fee_charged"):
            total += stay["pet_fee_charged"]

        rid = stay["id"]
        # Past stays are paid+completed; upcoming stays in the demo are also
        # marked paid so the trips list shows them as confirmed.
        is_completed = stay.get("status") == "completed"
        _reservations[rid] = {
            "id": rid,
            "guest_id": stay["guest_id"],
            "hotel_id": stay["hotel_id"],
            "check_in": stay["check_in"],
            "check_out": stay["check_out"],
            "nights": nights,
            "room_type": stay["room_type"],
            "confirmation_number": stay["confirmation_number"],
            "status": stay.get("status", "upcoming"),
            "has_pet": stay.get("has_pet", False),
            "pet_id": stay.get("pet_id"),
            "pet_fee_charged": stay.get("pet_fee_charged"),
            "total_usd": float(total),
            "payment_status": "paid",
            "guests": 1,
            "is_seeded": True,
        }
        _pet_bookings[rid] = []
    logger.info("Materialized %d seeded reservations", len(_reservations))


# --- Public API used by the router ----------------------------------------


def list_for_guest(guest_id: str) -> list[ReservationResponse]:
    """Return all reservations for a given guest."""
    return [_to_response(r) for r in _reservations.values() if r["guest_id"] == guest_id]


def get_reservation(reservation_id: str, guest_id: str | None = None) -> ReservationResponse:
    """Fetch a single reservation, optionally enforcing ownership."""
    res = _reservations.get(reservation_id)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )
    if guest_id and res["guest_id"] != guest_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your reservation"
        )
    return _to_response(res)


def lookup_by_confirmation(confirmation_number: str) -> ReservationResponse:
    """Public lookup endpoint — used by guest-not-logged-in flows."""
    for res in _reservations.values():
        if res["confirmation_number"] == confirmation_number:
            return _to_response(res)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No reservation found for that confirmation number",
    )


def create_reservation(
    guest_id: str, body: CreateReservationRequest
) -> ReservationResponse:
    """Create a new reservation with optional pet add-on."""
    hotel = _find_hotel(body.hotel_id)
    if body.has_pet and not hotel.get("pet_friendly"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This hotel is not pet-friendly",
        )

    nights = _nights_between(body.check_in, body.check_out)
    total = nights * hotel["price_per_night"]
    pet_fee: int | None = None
    if body.has_pet and hotel.get("pet_fee_usd"):
        pet_fee = int(hotel["pet_fee_usd"])
        total += pet_fee

    rid = f"stay-{uuid.uuid4().hex[:8]}"
    res = {
        "id": rid,
        "guest_id": guest_id,
        "hotel_id": body.hotel_id,
        "check_in": body.check_in,
        "check_out": body.check_out,
        "nights": nights,
        "room_type": body.room_type,
        "confirmation_number": _new_confirmation_number(),
        "status": "pending_payment",
        "has_pet": body.has_pet,
        "pet_id": body.pet_id,
        "pet_fee_charged": pet_fee,
        "total_usd": float(total),
        "payment_status": "unpaid",
        "guests": body.guests,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _reservations[rid] = res
    _pet_bookings[rid] = []
    return _to_response(res)


def process_payment(reservation_id: str, guest_id: str) -> ReservationResponse:
    """Mark a reservation as paid (mock — no card processing)."""
    res = _reservations.get(reservation_id)
    if not res or res["guest_id"] != guest_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )
    if res["payment_status"] != "paid":
        res["payment_status"] = "paid"
        res["status"] = "upcoming"
    return _to_response(res)


def _validate_service_slot(res: dict[str, Any], service_date: str) -> None:
    """Ensure the appointment date falls within the stay."""
    try:
        appt = date.fromisoformat(service_date)
        check_in = date.fromisoformat(res["check_in"])
        check_out = date.fromisoformat(res["check_out"])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {exc}",
        ) from exc
    if appt < check_in or appt > check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service date must fall within your stay",
        )


def _normalize_booking(raw: dict[str, Any]) -> dict[str, Any]:
    """Fill defaults for bookings created before service_time existed."""
    return {**raw, "service_time": raw.get("service_time", "10:00")}


def book_pet_service(
    reservation_id: str,
    guest_id: str,
    body: PetServiceBookingRequest,
) -> PetServiceBooking:
    """Add a pet-service booking to an existing reservation."""
    res = _reservations.get(reservation_id)
    if not res or res["guest_id"] != guest_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )

    hotel = _find_hotel(res["hotel_id"])
    if not hotel.get("pet_friendly"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Hotel is not pet-friendly"
        )
    if not res.get("has_pet"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reservation does not include a pet",
        )

    partner = get_partner_by_id(body.partner_id)
    if not partner or partner.get("hotel_id") != res["hotel_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found near this hotel",
        )
    if not partner.get("pet_relevant"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner is not a pet service",
        )
    if not partner.get("bookable"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner is not available for in-app booking",
        )

    radius = get_pet_service_radius_miles(guest_id)
    nearby = get_partners_near_hotel(
        res["hotel_id"],
        bookable_only=True,
        max_miles=radius,
    )
    if not any(p.id == body.partner_id for p in nearby):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Partner is outside your {radius:g}-mile search radius",
        )

    _validate_service_slot(res, body.service_date)

    booking = {
        "id": f"psb-{uuid.uuid4().hex[:8]}",
        "partner_id": partner["id"],
        "partner_name": partner["name"],
        "category": partner["category"],
        "service_model": partner.get("service_model", "fixed_location"),
        "service_date": body.service_date,
        "service_time": body.service_time,
        "notes": body.notes,
        "status": "confirmed",
    }
    _pet_bookings.setdefault(reservation_id, []).append(booking)
    return PetServiceBooking(**booking)


def cancel_pet_service(
    reservation_id: str,
    guest_id: str,
    booking_id: str,
) -> PetServiceBooking:
    """Cancel a previously booked pet service."""
    res = _reservations.get(reservation_id)
    if not res or res["guest_id"] != guest_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )

    bookings = _pet_bookings.get(reservation_id, [])
    for booking in bookings:
        if booking.get("id") != booking_id:
            continue
        if booking.get("status") == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )
        booking["status"] = "cancelled"
        booking["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        return PetServiceBooking(**_normalize_booking(booking))

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Pet service booking not found"
    )


def find_seeded_reservation(stay_id: str) -> dict[str, Any] | None:
    """Return the raw stored reservation dict, if any. Used by arrival_brief_service."""
    return _reservations.get(stay_id)
