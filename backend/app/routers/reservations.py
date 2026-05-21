"""Reservation booking flow + pet service add-ons."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import require_guest
from app.models.auth import GuestSummary
from app.models.pet_service import PetServiceRecommendationsResponse
from app.models.reservation import (
    CreateReservationRequest,
    LookupRequest,
    PaymentRequest,
    PetServiceBooking,
    PetServiceBookingRequest,
    ReservationResponse,
)
from app.services import pet_service_recommendation_service, reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
async def my_trips(
    guest: GuestSummary = Depends(require_guest),
) -> list[ReservationResponse]:
    """Return all reservations for the logged-in persona."""
    return reservation_service.list_for_guest(guest.id)


@router.post("/lookup", response_model=ReservationResponse)
async def lookup_trip(body: LookupRequest) -> ReservationResponse:
    """Public lookup by confirmation number — no auth required."""
    return reservation_service.lookup_by_confirmation(body.confirmation_number)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_trip(
    reservation_id: str,
    guest: GuestSummary = Depends(require_guest),
) -> ReservationResponse:
    """Fetch a single reservation owned by the logged-in persona."""
    return reservation_service.get_reservation(reservation_id, guest.id)


@router.post("", response_model=ReservationResponse)
async def create_trip(
    body: CreateReservationRequest,
    guest: GuestSummary = Depends(require_guest),
) -> ReservationResponse:
    """Book a new reservation for the logged-in persona."""
    return reservation_service.create_reservation(guest.id, body)


@router.post("/{reservation_id}/payment", response_model=ReservationResponse)
async def pay_trip(
    reservation_id: str,
    _: PaymentRequest,
    guest: GuestSummary = Depends(require_guest),
) -> ReservationResponse:
    """Mark a reservation paid (mock — payload is validated but not stored)."""
    return reservation_service.process_payment(reservation_id, guest.id)


@router.get(
    "/{reservation_id}/pet-services/recommendations",
    response_model=PetServiceRecommendationsResponse,
)
async def pet_service_recommendations(
    reservation_id: str,
    guest: GuestSummary = Depends(require_guest),
) -> PetServiceRecommendationsResponse:
    """Realtime LiteLLM-ranked pet service picks for a pet-inclusive stay."""
    return await pet_service_recommendation_service.get_pet_service_recommendations(
        reservation_id, guest.id
    )


@router.post("/{reservation_id}/pet-services", response_model=PetServiceBooking)
async def book_pet_service(
    reservation_id: str,
    body: PetServiceBookingRequest,
    guest: GuestSummary = Depends(require_guest),
) -> PetServiceBooking:
    """Add a pet service booking to a reservation."""
    return reservation_service.book_pet_service(reservation_id, guest.id, body)


@router.delete(
    "/{reservation_id}/pet-services/{booking_id}",
    response_model=PetServiceBooking,
)
async def cancel_pet_service(
    reservation_id: str,
    booking_id: str,
    guest: GuestSummary = Depends(require_guest),
) -> PetServiceBooking:
    """Cancel a pet service booking on a reservation."""
    return reservation_service.cancel_pet_service(
        reservation_id, guest.id, booking_id
    )
