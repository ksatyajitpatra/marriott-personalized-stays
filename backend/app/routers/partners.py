"""Local partner map endpoints (PRD Section 5.3)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.data.loader import get_seed
from app.models.partner import PartnerResponse
from app.services.partner_service import get_partners_near_hotel

router = APIRouter(prefix="/partners", tags=["partners"])


def _hotel_exists(hotel_id: str) -> bool:
    """Cheap existence check used to 404 early on bad hotel ids."""
    return any(h.get("id") == hotel_id for h in get_seed("hotels"))


@router.get("/nearby", response_model=list[PartnerResponse])
async def nearby_partners(
    hotel_id: str = Query(..., description="Hotel to anchor the search to"),
    pet_only: bool = Query(False, description="Filter to pet-relevant partners only"),
    bookable_only: bool = Query(
        False, description="Filter to in-app bookable pet services only"
    ),
    max_miles: float = Query(10.0, ge=0.1, le=50, description="Search radius in miles"),
    category: str | None = Query(None, description="Filter to a single category"),
) -> list[PartnerResponse]:
    """Return partners around a hotel, sorted by distance ascending."""
    if not _hotel_exists(hotel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found"
        )
    return get_partners_near_hotel(
        hotel_id,
        pet_only=pet_only,
        bookable_only=bookable_only,
        max_miles=max_miles,
        category=category,
    )
