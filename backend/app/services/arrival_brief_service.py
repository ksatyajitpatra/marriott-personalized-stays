"""Arrival Brief — pre-stay personalized 1-pager (PRD Section 5.2).

Static narrative fields come from seeded persona briefs when available.
Events and dining are generated at request time via LiteLLM when the guest
has selected interests or dietary preferences; empty selections skip those
sections entirely.
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
from app.models.preferences import CITY_RESTAURANT_KEYS
from app.services.eco_service import compute_eco_score
from app.services.guest_preference_service import get_guest_record
from app.services.llm_service import (
    LLMConfigError,
    LLMUnavailableError,
    litellm_chat,
    parse_llm_json,
)
from app.services.partner_service import get_partners_near_hotel
from app.services.weather_service import get_forecast

logger = logging.getLogger(__name__)


def _find_stay(stay_id: str) -> dict[str, Any]:
    for stay in get_seed("stays"):
        if stay.get("id") == stay_id:
            return stay
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stay not found")


def _find_hotel(hotel_id: str) -> dict[str, Any]:
    for hotel in get_seed("hotels"):
        if hotel.get("id") == hotel_id:
            return hotel
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")


def _seeded_brief_for_guest(guest_id: str) -> dict[str, Any] | None:
    name = f"arrival_brief_{guest_id}"
    if has_seed(name):
        return get_seed(name)
    return None


def _eco_note(hotel: dict[str, Any]) -> str | None:
    eco = compute_eco_score(hotel)
    if eco.green_points_bonus <= 0:
        return None
    return (
        f"This hotel earned a {eco.total_score} Eco Score. "
        f"Your stay earns {3000 + eco.green_points_bonus} Bonvoy Green Points "
        f"(base 3,000 + {eco.green_points_bonus} eco bonus)."
    )


def _restaurant_catalog(hotel: dict[str, Any]) -> list[dict[str, Any]]:
    if not has_seed("restaurants"):
        return []
    key = CITY_RESTAURANT_KEYS.get(hotel.get("city", ""), "")
    if not key:
        return []
    restaurants = get_seed("restaurants").get(key, [])
    return [
        {
            "restaurant_id": r.get("id"),
            "name": r.get("name"),
            "cuisine": r.get("cuisine"),
            "dietary_tags": r.get("dietary_tags", []),
            "rating": r.get("rating"),
            "note": r.get("note"),
        }
        for r in restaurants
    ]


def _events_catalog(hotel: dict[str, Any]) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for event in hotel.get("community_events", []):
        catalog.append(
            {
                "source": "hotel",
                "name": event.get("name"),
                "time": event.get("time"),
                "location": event.get("location"),
                "type": event.get("type"),
            }
        )
    for partner in get_partners_near_hotel(hotel["id"], max_miles=5.0):
        if partner.category == "local_experience":
            catalog.append(
                {
                    "source": "partner",
                    "name": partner.name,
                    "type": "local_experience",
                    "note": partner.note,
                    "distance_miles": partner.distance_miles,
                }
            )
    return catalog


async def _llm_dining_picks(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    dietary: list[str],
) -> list[dict[str, Any]] | None:
    catalog = _restaurant_catalog(hotel)
    if not catalog:
        return None

    system = (
        "You are a Marriott Bonvoy dining concierge. Pick restaurants from the "
        "catalog that best match the guest's dietary needs. Use ONLY restaurant "
        "names from the catalog. Output strict JSON only."
    )
    user = (
        f"Guest: {guest['name']}\n"
        f"Dietary preferences: {', '.join(dietary)}\n"
        f"Hotel: {hotel['name']} in {hotel['city']}, {hotel['state']}\n"
        f"Stay: {stay['check_in']} to {stay['check_out']}\n\n"
        f"Restaurant catalog:\n{json.dumps(catalog, indent=2)}\n\n"
        "Respond as JSON with key dining (array of 3 objects): "
        "name, cuisine, dietary_match (how it fits their prefs), note (≤30 words)."
    )

    try:
        raw = await litellm_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=700,
            response_format={"type": "json_object"},
        )
        parsed = parse_llm_json(raw)
    except (LLMConfigError, LLMUnavailableError) as exc:
        logger.warning("LiteLLM dining picks failed: %s", exc)
        return None
    except json.JSONDecodeError:
        logger.warning("LiteLLM dining picks returned non-JSON")
        return None

    return [d for d in parsed.get("dining", []) if _is_dining(d)]


async def _llm_nearby_events(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    interests: list[str],
) -> list[dict[str, Any]] | None:
    catalog = _events_catalog(hotel)

    system = (
        "You are a Marriott Bonvoy local experiences concierge. Recommend events "
        "during the guest's stay that match their interests. Prefer catalog items "
        "when relevant; you may suggest realistic nearby events in the same city. "
        "Output strict JSON only."
    )
    catalog_block = (
        f"Event catalog:\n{json.dumps(catalog, indent=2)}\n\n"
        if catalog
        else ""
    )
    user = (
        f"Guest: {guest['name']}\n"
        f"Interests: {', '.join(interests)}\n"
        f"Hotel: {hotel['name']} in {hotel['city']}, {hotel['state']}\n"
        f"Stay: {stay['check_in']} to {stay['check_out']}\n\n"
        f"{catalog_block}"
        "Respond as JSON with key events (array of 3 objects): "
        "name, date (YYYY-MM-DD within stay), type (interest tag), "
        "why_youll_love_it (≤35 words, tie to their interests)."
    )

    try:
        raw = await litellm_chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=700,
            response_format={"type": "json_object"},
        )
        parsed = parse_llm_json(raw)
    except (LLMConfigError, LLMUnavailableError) as exc:
        logger.warning("LiteLLM nearby events failed: %s", exc)
        return None
    except json.JSONDecodeError:
        logger.warning("LiteLLM nearby events returned non-JSON")
        return None

    return [e for e in parsed.get("events", []) if _is_event(e)]


def _mock_dining_from_catalog(
    dietary: list[str], hotel: dict[str, Any]
) -> list[dict[str, Any]]:
    catalog = _restaurant_catalog(hotel)
    dietary_set = set(dietary)
    matched = [
        r
        for r in catalog
        if dietary_set.intersection(set(r.get("dietary_tags", [])))
        or any(d.replace("_", " ") in " ".join(r.get("dietary_tags", [])) for d in dietary)
    ]
    picks = matched[:3] if matched else catalog[:3]
    return [
        {
            "name": r["name"],
            "cuisine": r["cuisine"],
            "dietary_match": f"Matches your {', '.join(dietary)} preferences",
            "note": r.get("note", ""),
        }
        for r in picks
    ]


def _mock_events_from_catalog(
    interests: list[str], hotel: dict[str, Any], stay: dict[str, Any]
) -> list[dict[str, Any]]:
    catalog = _events_catalog(hotel)
    interest_set = set(interests)
    matched = [e for e in catalog if e.get("type") in interest_set]
    picks = matched[:3] if matched else catalog[:3]
    return [
        {
            "name": e["name"],
            "date": stay["check_in"],
            "type": e.get("type", "local"),
            "why_youll_love_it": f"A great fit for your interest in {', '.join(interests)}.",
        }
        for e in picks
    ]


def _stub_brief(
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "greeting": f"Welcome, {guest['name'].split()[0]} — we can't wait to host you at {hotel['name']}.",
        "weather_summary": f"Your forecast for {hotel['city']} is in the panel above.",
        "packing_tips": [
            "Light layers for variable conditions",
            "Comfortable walking shoes for exploring",
            "Reusable water bottle — refill stations on property",
        ],
        "transit": f"Your hotel is at {hotel['address']}. Concierge can advise on the fastest route from your arrival point.",
        "property_note": "Your stay includes mobile check-in and digital key — skip the front desk if you'd like.",
    }


async def get_arrival_brief(stay_id: str) -> ArrivalBriefResponse:
    """Return the arrival brief for a given stay."""
    stay = _find_stay(stay_id)
    hotel = _find_hotel(stay["hotel_id"])
    guest = get_guest_record(stay["guest_id"]) or {"name": "Guest", "preferences": {}}
    prefs = guest.get("preferences", {})

    dietary: list[str] = prefs.get("dietary") or []
    interests: list[str] = prefs.get("interests") or []

    seeded = _seeded_brief_for_guest(stay["guest_id"])
    if seeded and seeded.get("stay_id") == stay_id:
        body = seeded
        base_source = "seed"
    else:
        body = _stub_brief(stay, hotel, guest)
        base_source = "mock_llm"

    llm_used = False
    events: list[dict[str, Any]] = []
    dining: list[dict[str, Any]] = []

    if interests:
        llm_events = await _llm_nearby_events(
            stay=stay, hotel=hotel, guest=guest, interests=interests
        )
        if llm_events:
            events = llm_events
            llm_used = True
        else:
            events = _mock_events_from_catalog(interests, hotel, stay)

    if dietary:
        llm_dining = await _llm_dining_picks(
            stay=stay, hotel=hotel, guest=guest, dietary=dietary
        )
        if llm_dining:
            dining = llm_dining
            llm_used = True
        else:
            dining = _mock_dining_from_catalog(dietary, hotel)

    source = "litellm" if llm_used else base_source
    forecast = await get_forecast(hotel["city"], stay["check_in"], stay["check_out"])

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
        events=[BriefEvent(**e) for e in events],
        dining=[BriefDining(**d) for d in dining],
        transit=body.get("transit", ""),
        property_note=body.get("property_note", ""),
        eco_note=body.get("eco_note") or _eco_note(hotel),
    )


def _is_event(e: dict[str, Any]) -> bool:
    return all(k in e for k in ("name", "date", "type", "why_youll_love_it"))


def _is_dining(d: dict[str, Any]) -> bool:
    return all(k in d for k in ("name", "cuisine", "dietary_match", "note"))
