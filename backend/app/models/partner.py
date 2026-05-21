"""Local partner map schemas — see PRD Section 5.3."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PartnerResponse(BaseModel):
    """A single pin on the local partner map."""

    id: str
    hotel_id: str
    name: str
    category: str = Field(
        description=(
            "One of: vet_emergency, dog_walker, dog_park, pet_supply, "
            "vegan_restaurant, restaurant, bike_rental, refill_station, "
            "ev_charging, local_experience"
        )
    )
    lat: float
    lng: float
    address: str
    phone: str | None = None
    hours: str | None = None
    rating: float
    is_marriott_partner: bool
    pet_relevant: bool
    distance_km: float
    distance_miles: float
    note: str | None = None
    dietary_tags: list[str] = Field(default_factory=list)
