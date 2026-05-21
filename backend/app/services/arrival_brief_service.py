"""Arrival Brief — pre-stay personalized 1-pager (PRD Section 5.2).

Strategy:
  1. Each demo persona has a hand-curated brief in `arrival_brief_{guest}.json`
     that we serve directly — fast, deterministic, perfect for the demo.
  2. Live weather (OpenWeatherMap) is overlaid onto the brief when available.
  3. If the requested stay has no seeded brief, we fall back to an LLM-
     generated one (or a simple stub if the LLM is disabled).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from app.data.loader import get_seed, has_seed
from app.models.arrival_brief import (
    ArrivalBriefResponse,
    BriefDining,
    BriefEvent,
)
from app.services.eco_service import compute_eco_score
from app.services.llm_service import (
    LLMConfigError,
    LLMUnavailableError,
    litellm_chat,
    parse_llm_json,
)
from app.services.weather_service import get_forecast

logger = logging.getLogger(__name__)


# --- Helpers ---------------------------------------------------------------


def _find_stay(stay_id: str) -> dict[str, Any]:
    """Look up a stay by id from the seed file, or 404."""
    for stay in get_seed("stays"):
        if stay.get("id") == stay_id:
            return stay
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stay not found")


def _find_hotel(hotel_id: str) -> dict[str, Any]:
    """Look up a hotel by id from the seed file."""
    for hotel in get_seed("hotels"):
        if hotel.get("id") == hotel_id:
            return hotel
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")


def _seeded_brief_for_guest(guest_id: str) -> dict[str, Any] | None:
    """Return the per-persona seeded brief if one exists."""
    name = f"arrival_brief_{guest_id}"
    if has_seed(name):
        return get_seed(name)
    return None


def _eco_note(hotel: dict[str, Any]) -> str | None:
    """Produce a 1-line eco callout if the hotel scored well."""
    eco = compute_eco_score(hotel)
    if eco.green_points_bonus <= 0:
        return None
    return (
        f"This hotel earned a {eco.total_score} Eco Score. "
        f"Your stay earns {3000 + eco.green_points_bonus} Bonvoy Green Points "
        f"(base 3,000 + {eco.green_points_bonus} eco bonus)."
    )


# --- LLM fallback ----------------------------------------------------------


async def _llm_generate_brief(
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
) -> dict[str, Any] | None:
    """Generate a brief via LiteLLM. Returns None if unavailable."""
    prefs = guest.get("preferences", {})
    system = (
        "You are a knowledgeable Marriott concierge. Generate a warm, "
        "concise pre-stay arrival brief. Output strict JSON only."
    )
    user = (
        f"Stay: {stay['check_in']} to {stay['check_out']} at {hotel['name']} "
        f"in {hotel['city']}, {hotel['state']}.\n"
        f"Guest: {guest['name']}, dietary: {prefs.get('dietary', [])}, "
        f"interests: {prefs.get('interests', [])}, "
        f"accessibility: {prefs.get('accessibility', [])}.\n\n"
        "Respond as JSON with keys: greeting (1 sentence), "
        "weather_summary (1 sentence), packing_tips (3 short strings), "
        "events (3 objects: name/date/type/why_youll_love_it), "
        "dining (3 objects: name/cuisine/dietary_match/note), "
        "transit (1-2 sentences), property_note (1-2 sentences)."
    )
    try:
        raw = await litellm_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=900,
            response_format={"type": "json_object"},
        )
    except LLMConfigError:
        return None
    except LLMUnavailableError as exc:
        logger.warning("LiteLLM brief failed: %s", exc)
        return None

    try:
        return parse_llm_json(raw)
    except json.JSONDecodeError:
        return None


def _stub_brief(
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
) -> dict[str, Any]:
    """Last-resort deterministic brief when no seed and no LLM."""
    return {
        "greeting": f"Welcome, {guest['name'].split()[0]} — we can't wait to host you at {hotel['name']}.",
        "weather_summary": f"Your forecast for {hotel['city']} is in the panel above.",
        "packing_tips": [
            "Light layers for variable conditions",
            "Comfortable walking shoes for exploring",
            "Reusable water bottle — refill stations on property",
        ],
        "events": [],
        "dining": [],
        "transit": f"Your hotel is at {hotel['address']}. Concierge can advise on the fastest route from your arrival point.",
        "property_note": "Your stay includes mobile check-in and digital key — skip the front desk if you'd like.",
    }


# --- Public entry point ----------------------------------------------------


async def get_arrival_brief(stay_id: str) -> ArrivalBriefResponse:
    """Return the arrival brief for a given stay.

    Args:
        stay_id: The stay/reservation id (e.g. 'stay-alex-001').

    Returns:
        Fully populated `ArrivalBriefResponse` with weather, dining, etc.

    Raises:
        HTTPException: 404 if the stay isn't found.
    """
    stay = _find_stay(stay_id)
    hotel = _find_hotel(stay["hotel_id"])

    # Resolve the matching guest record (for personalization).
    guest = next(
        (g for g in get_seed("guests") if g["id"] == stay["guest_id"]),
        {"name": "Guest", "preferences": {}},
    )

    # Prefer the seeded brief if the guest+stay match, else LLM, else stub.
    seeded = _seeded_brief_for_guest(stay["guest_id"])
    source: str
    body: dict[str, Any]
    if seeded and seeded.get("stay_id") == stay_id:
        body = seeded
        source = "seed"
    else:
        llm = await _llm_generate_brief(stay, hotel, guest)
        if llm is not None:
            body = llm
            source = "litellm"
        else:
            body = _stub_brief(stay, hotel, guest)
            source = "mock_llm"

    # Always overlay live weather (with mock fallback).
    forecast = await get_forecast(hotel["city"], stay["check_in"], stay["check_out"])

    # Merge: seeded data wins for narrative fields; we add structured weather.
    return ArrivalBriefResponse(
        stay_id=stay_id,
        guest_id=stay["guest_id"],
        hotel=hotel["name"],
        city=f"{hotel['city']}, {hotel['state']}",
        check_in=stay["check_in"],
        check_out=stay["check_out"],
        generated_at=body.get("generated_at") or datetime.now(timezone.utc).isoformat(),
        generated_by=source,
        greeting=body.get("greeting", _stub_brief(stay, hotel, guest)["greeting"]),
        weather_summary=body.get("weather_summary", "Forecast available below."),
        weather_forecast=forecast,
        packing_tips=list(body.get("packing_tips", [])),
        events=[BriefEvent(**e) for e in body.get("events", []) if _is_event(e)],
        dining=[BriefDining(**d) for d in body.get("dining", []) if _is_dining(d)],
        transit=body.get("transit", ""),
        property_note=body.get("property_note", ""),
        eco_note=body.get("eco_note") or _eco_note(hotel),
    )


def _is_event(e: dict[str, Any]) -> bool:
    """Validate a raw event dict has the keys our model needs."""
    return all(k in e for k in ("name", "date", "type", "why_youll_love_it"))


def _is_dining(d: dict[str, Any]) -> bool:
    """Validate a raw dining dict has the keys our model needs."""
    return all(k in d for k in ("name", "cuisine", "dietary_match", "note"))
