"""Hotel search, detail, and eco-score endpoints (PRD Section 5.1)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.data.loader import get_seed
from app.models.eco import EcoScoreResponse
from app.models.hotel import HotelDetail, HotelListItem
from app.services.eco_service import compute_eco_score
from app.services.hotel_content_service import hotel_to_detail, hotel_to_list_item

router = APIRouter(prefix="/hotels", tags=["hotels"])


def _find_hotel(hotel_id: str) -> dict[str, Any]:
    """Look up a hotel by id or 404."""
    for hotel in get_seed("hotels"):
        if hotel.get("id") == hotel_id:
            return hotel
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")


@router.get("", response_model=list[HotelListItem])
async def list_hotels(
    city: str | None = Query(None, description="Case-insensitive substring match"),
    pet_friendly: bool | None = Query(None),
    min_eco: float | None = Query(None, ge=0, le=10, description="Minimum eco score 0-10"),
) -> list[HotelListItem]:
    """Search hotels with optional filters; sort by eco score desc, then price."""
    hotels: list[dict[str, Any]] = get_seed("hotels")
    items: list[HotelListItem] = []

    for hotel in hotels:
        if city and city.lower() not in hotel["city"].lower():
            continue
        if pet_friendly is not None and hotel.get("pet_friendly") != pet_friendly:
            continue

        item = await hotel_to_list_item(hotel)
        if min_eco is not None and item.eco_score < min_eco:
            continue
        items.append(item)

    return sorted(items, key=lambda h: (-h.eco_score, h.price_per_night))


@router.get("/{hotel_id}", response_model=HotelDetail)
async def get_hotel(hotel_id: str) -> HotelDetail:
    """Full detail page payload for a single hotel."""
    return await hotel_to_detail(_find_hotel(hotel_id))


@router.get("/{hotel_id}/eco-score", response_model=EcoScoreResponse)
async def get_eco_score(hotel_id: str) -> EcoScoreResponse:
    """Full eco breakdown — used by the EcoSubScoreBreakdown accordion."""
    return compute_eco_score(_find_hotel(hotel_id))
