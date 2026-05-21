"""Hotel domain schemas — list, detail, and LLM-generated content."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HotelContent(BaseModel):
    """LLM-generated marketing copy for a hotel.

    Cached per-hotel at startup (see `hotel_content_service`).
    """

    tagline: str
    highlights: list[str]
    editorial: str
    room_types: list[str]
    generated_by: str = Field(default="mock_llm", description="'mock_llm' or 'litellm'")


class HotelListItem(BaseModel):
    """Compact hotel card for search results."""

    id: str
    name: str
    brand: str
    city: str
    state: str
    address: str
    lat: float
    lng: float
    image_url: str
    price_per_night: int
    rating: float
    pet_friendly: bool
    eco_score: float
    eco_color: str
    tagline: str


class HotelDetail(BaseModel):
    """Full hotel detail page payload."""

    id: str
    name: str
    brand: str
    city: str
    state: str
    country: str
    address: str
    lat: float
    lng: float
    image_url: str
    price_per_night: int
    rating: float
    pet_friendly: bool
    pet_max_weight_kg: float | None = None
    pet_fee_usd: int | None = None
    pet_note: str | None = None
    eco_score: float
    eco_color: str
    community_events: list[dict[str, Any]] = Field(default_factory=list)
    content: HotelContent
