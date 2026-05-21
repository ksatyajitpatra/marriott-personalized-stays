"""Reservation schemas — booking flow and pet service add-ons."""

from __future__ import annotations

from pydantic import BaseModel, Field


TIME_PATTERN = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"


class CreateReservationRequest(BaseModel):
    """Booking payload from `POST /reservations`."""

    hotel_id: str
    check_in: str = Field(description="ISO date YYYY-MM-DD")
    check_out: str = Field(description="ISO date YYYY-MM-DD")
    room_type: str
    guests: int = Field(default=1, ge=1, le=6)
    has_pet: bool = False
    pet_id: str | None = None


class PaymentRequest(BaseModel):
    """Mock payment payload — values are not stored or validated.

    Fields exist only so the frontend can post a realistic-looking form.
    """

    card_number: str = Field(min_length=4)
    expiry: str
    cvv: str = Field(min_length=3, max_length=4)
    cardholder_name: str


class LookupRequest(BaseModel):
    """Lookup-by-confirmation payload (used by guest lookup flow)."""

    confirmation_number: str


class PetServiceBookingRequest(BaseModel):
    """Booking a pet service against a stay."""

    partner_id: str
    service_date: str = Field(description="ISO date YYYY-MM-DD")
    service_time: str = Field(
        description="Local appointment time HH:MM (24-hour)",
        pattern=TIME_PATTERN,
    )
    notes: str = ""


class PetServiceBooking(BaseModel):
    """A booked pet service tied to a reservation."""

    id: str
    partner_id: str
    partner_name: str
    category: str
    service_model: str = "fixed_location"
    service_date: str
    service_time: str = Field(default="10:00", pattern=TIME_PATTERN)
    notes: str
    status: str = Field(description="confirmed | cancelled")


class ReservationResponse(BaseModel):
    """Full reservation projection returned to the frontend."""

    id: str
    guest_id: str
    hotel_id: str
    hotel_name: str
    hotel_city: str
    hotel_image_url: str
    check_in: str
    check_out: str
    nights: int
    room_type: str
    confirmation_number: str
    status: str = Field(description="pending_payment | upcoming | in_stay | completed")
    has_pet: bool
    pet_id: str | None = None
    pet_fee_charged: int | None = None
    total_usd: float
    payment_status: str = Field(description="unpaid | paid")
    pet_service_bookings: list[PetServiceBooking] = Field(default_factory=list)
