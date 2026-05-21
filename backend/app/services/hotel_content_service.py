"""Per-hotel marketing copy — LLM-generated with a deterministic fallback.

Cached at startup so the demo is instant and uses zero LLM tokens by default.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.data.loader import get_seed
from app.models.hotel import HotelContent, HotelDetail, HotelListItem
from app.services.eco_service import compute_eco_score
from app.services.llm_service import (
    LLMConfigError,
    LLMUnavailableError,
    litellm_chat,
    parse_llm_json,
)

logger = logging.getLogger(__name__)

# In-process cache: hotel_id -> serialized HotelContent dict.
_content_cache: dict[str, dict[str, Any]] = {}


def _mock_hotel_content(hotel: dict[str, Any]) -> dict[str, Any]:
    """Deterministic fallback so the app boots even without LLM access."""
    city = hotel["city"]
    brand = hotel["brand"]
    pet_phrase = " Pet-friendly with thoughtful amenities." if hotel.get("pet_friendly") else ""
    eco_phrase = (
        " Sustainability-forward property with transparent eco credentials."
        if hotel.get("eco")
        else ""
    )

    room_types = ["Deluxe King", "Deluxe Double Queen", "Executive Suite"]
    if hotel.get("pet_friendly"):
        room_types.append("Pet-Friendly King")

    return {
        "tagline": f"{brand} hospitality in the heart of {city}.{pet_phrase}",
        "highlights": [
            f"Prime {city} location steps from local landmarks",
            f"Member-favorite {brand} rooms with Bonvoy benefits",
            "Mobile check-in and digital key ready"
            + (" · Eco-rated stay" if eco_phrase else ""),
        ],
        "editorial": (
            f"Welcome to {hotel['name']}. Whether you're here for business or "
            f"exploration, enjoy curated Marriott service, thoughtful design, "
            f"and neighborhood discovery tools built into your stay."
            f"{eco_phrase}{pet_phrase} Book direct to earn Bonvoy points."
        ),
        "room_types": room_types,
        "generated_by": "mock_llm",
    }


async def _llm_hotel_content(hotel: dict[str, Any]) -> dict[str, Any] | None:
    """Try to generate content via LiteLLM; return None on any failure."""
    system = (
        "You are a Marriott Bonvoy concierge writer. Produce concise, warm "
        "marketing copy in strict JSON. Never invent facts beyond the input."
    )
    user = (
        "Write hotel marketing copy as JSON with keys: tagline (≤120 chars), "
        "highlights (array of 3 short bullets), editorial (≤80 words), "
        "room_types (array of 3-4 strings).\n\n"
        f"Hotel: {hotel['name']} ({hotel['brand']}) in {hotel['city']}, "
        f"{hotel['state']}. Pet-friendly: {hotel.get('pet_friendly')}. "
        f"Eco notes: {hotel.get('eco', {}).get('notes', 'n/a')}."
    )
    try:
        raw = await litellm_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=400,
            response_format={"type": "json_object"},
        )
    except LLMConfigError:
        return None
    except LLMUnavailableError as exc:
        logger.warning("LiteLLM call failed for %s: %s", hotel["id"], exc)
        return None

    try:
        parsed = parse_llm_json(raw)
    except json.JSONDecodeError:
        logger.warning("LiteLLM returned non-JSON for %s; falling back", hotel["id"])
        return None

    return {
        "tagline": str(parsed.get("tagline", ""))[:240] or _mock_hotel_content(hotel)["tagline"],
        "highlights": [str(x) for x in parsed.get("highlights", [])][:4]
        or _mock_hotel_content(hotel)["highlights"],
        "editorial": str(parsed.get("editorial", "")) or _mock_hotel_content(hotel)["editorial"],
        "room_types": [str(x) for x in parsed.get("room_types", [])][:6]
        or _mock_hotel_content(hotel)["room_types"],
        "generated_by": "litellm",
    }


async def _generate_hotel_content(hotel: dict[str, Any]) -> dict[str, Any]:
    """Return content via LLM if possible, else the mock."""
    live = await _llm_hotel_content(hotel)
    return live if live is not None else _mock_hotel_content(hotel)


async def warm_hotel_content_cache() -> None:
    """Pre-generate content for every hotel at startup."""
    hotels: list[dict[str, Any]] = get_seed("hotels")
    for hotel in hotels:
        if hotel["id"] in _content_cache:
            continue
        _content_cache[hotel["id"]] = await _generate_hotel_content(hotel)
    logger.info("Hotel content cache warmed (%d entries)", len(_content_cache))


async def _get_content(hotel_id: str, hotel: dict[str, Any]) -> HotelContent:
    """Return the cached content for a hotel, generating on miss."""
    if hotel_id not in _content_cache:
        _content_cache[hotel_id] = await _generate_hotel_content(hotel)
    return HotelContent(**_content_cache[hotel_id])


# --- Projections used by the hotels router ---------------------------------


async def hotel_to_list_item(hotel: dict[str, Any]) -> HotelListItem:
    """Project a raw hotel dict into the search-results card shape."""
    eco = compute_eco_score(hotel)
    content = await _get_content(hotel["id"], hotel)
    return HotelListItem(
        id=hotel["id"],
        name=hotel["name"],
        brand=hotel["brand"],
        city=hotel["city"],
        state=hotel["state"],
        address=hotel["address"],
        lat=hotel["lat"],
        lng=hotel["lng"],
        image_url=hotel["image_url"],
        price_per_night=hotel["price_per_night"],
        rating=hotel["rating"],
        pet_friendly=hotel["pet_friendly"],
        eco_score=eco.total_score,
        eco_color=eco.color,
        tagline=content.tagline,
    )


async def hotel_to_detail(hotel: dict[str, Any]) -> HotelDetail:
    """Project a raw hotel dict into the full detail-page shape."""
    eco = compute_eco_score(hotel)
    content = await _get_content(hotel["id"], hotel)
    return HotelDetail(
        id=hotel["id"],
        name=hotel["name"],
        brand=hotel["brand"],
        city=hotel["city"],
        state=hotel["state"],
        country=hotel["country"],
        address=hotel["address"],
        lat=hotel["lat"],
        lng=hotel["lng"],
        image_url=hotel["image_url"],
        price_per_night=hotel["price_per_night"],
        rating=hotel["rating"],
        pet_friendly=hotel["pet_friendly"],
        pet_max_weight_kg=hotel.get("pet_max_weight_kg"),
        pet_fee_usd=hotel.get("pet_fee_usd"),
        pet_note=hotel.get("pet_note"),
        eco_score=eco.total_score,
        eco_color=eco.color,
        community_events=hotel.get("community_events", []),
        content=content,
    )
