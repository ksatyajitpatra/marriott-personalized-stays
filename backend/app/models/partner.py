"""Local partner map schemas — see PRD Section 5.3."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ServiceModel = Literal["fixed_location", "mobile"]

# In-app bookable pet services — vets and pet supply are discovery-only on the map.
BOOKABLE_PET_CATEGORIES: frozenset[str] = frozenset(
    {
        "dog_walker",
        "mobile_grooming",
    }
)

NON_BOOKABLE_PET_CATEGORIES: frozenset[str] = frozenset(
    {
        "vet_emergency",
        "vet",
        "pet_supply",
        "dog_park",
    }
)


class PartnerResponse(BaseModel):
    """A single pin on the local partner map."""

    id: str
    hotel_id: str
    name: str
    category: str = Field(
        description=(
            "One of: vet_emergency, dog_walker, dog_park, pet_supply, mobile_grooming, "
            "vegan_restaurant, restaurant, bike_rental, refill_station, "
            "ev_charging, local_experience"
        )
    )
    service_model: ServiceModel = "fixed_location"
    bookable: bool = False
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
    service_area_miles: float | None = None
    mobile_service_note: str | None = None


def resolve_partner_fields(raw: dict) -> dict:
    """Apply PRD defaults for bookable/service_model when omitted from seed JSON."""
    category = raw.get("category", "")
    service_model = raw.get("service_model")
    if service_model not in ("fixed_location", "mobile"):
        service_model = "mobile" if category == "mobile_grooming" else "fixed_location"

    bookable = raw.get("bookable")
    if category in NON_BOOKABLE_PET_CATEGORIES or category.startswith("vet"):
        bookable = False
    elif category in BOOKABLE_PET_CATEGORIES:
        bookable = True if bookable is None else bool(bookable)
    else:
        bookable = False

    return {
        **raw,
        "service_model": service_model,
        "bookable": bool(bookable),
    }
