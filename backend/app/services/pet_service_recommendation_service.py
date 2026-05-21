"""Realtime pet service recommendations via LiteLLM (PRD Section 5.3).

On each request we pass the guest's stay context plus the bookable partner
catalog from seed data and ask the LLM to rank services with rationale.
Falls back to a deterministic mock when USE_MOCK_LLM=true or the call fails.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status

from app.data.loader import get_seed
from app.models.partner import PartnerResponse
from app.models.pet_service import (
    PetServiceRecommendationItem,
    PetServiceRecommendationsResponse,
)
from app.services.guest_preference_service import (
    get_guest_record,
    get_pet_service_categories,
    get_pet_service_radius_miles,
)
from app.services.llm_service import (
    LLMConfigError,
    LLMUnavailableError,
    litellm_chat,
    parse_llm_json,
)
from app.services.partner_service import get_partners_near_hotel
from app.services.reservation_service import get_reservation

logger = logging.getLogger(__name__)

_CATEGORY_LABEL = {
    "dog_walker": "dog walker / sitter",
    "mobile_grooming": "mobile grooming",
}


def _find_hotel(hotel_id: str) -> dict[str, Any]:
    for hotel in get_seed("hotels"):
        if hotel.get("id") == hotel_id:
            return hotel
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")


def _pet_for_stay(guest: dict[str, Any], pet_id: str | None) -> dict[str, Any] | None:
    pets: list[dict[str, Any]] = guest.get("pets") or []
    if pet_id:
        for pet in pets:
            if pet.get("id") == pet_id:
                return pet
    return pets[0] if pets else None


def _partner_catalog(partners: list[PartnerResponse]) -> list[dict[str, Any]]:
    """Compact partner list for the LLM prompt."""
    return [
        {
            "partner_id": p.id,
            "name": p.name,
            "category": p.category,
            "service_model": p.service_model,
            "distance_miles": p.distance_miles,
            "rating": p.rating,
            "hours": p.hours,
            "note": p.note,
            "mobile_service_note": p.mobile_service_note,
        }
        for p in partners
    ]


def _item_from_partner(
    partner: PartnerResponse,
    *,
    rationale: str,
    suggested_time: str | None,
    priority: int,
) -> PetServiceRecommendationItem:
    return PetServiceRecommendationItem(
        partner_id=partner.id,
        partner_name=partner.name,
        category=partner.category,
        service_model=partner.service_model,
        distance_miles=partner.distance_miles,
        rating=partner.rating,
        bookable=partner.bookable,
        mobile_service_note=partner.mobile_service_note,
        rationale=rationale,
        suggested_time=suggested_time,
        priority=priority,
    )


def _mock_recommendations(
    *,
    reservation_id: str,
    radius_miles: float,
    partners: list[PartnerResponse],
    pet: dict[str, Any] | None,
    stay_check_in: str,
    preferred_categories: list[str],
) -> PetServiceRecommendationsResponse:
    """Deterministic ranking when LiteLLM is disabled or unavailable."""
    pet_name = pet.get("name", "your pet") if pet else "your pet"
    pool = partners
    if preferred_categories:
        preferred = [p for p in partners if p.category in preferred_categories]
        if preferred:
            pool = preferred
    sorted_partners = sorted(pool, key=lambda p: (-p.rating, p.distance_miles))[:4]

    items: list[PetServiceRecommendationItem] = []
    for idx, partner in enumerate(sorted_partners, start=1):
        label = _CATEGORY_LABEL.get(partner.category, partner.category.replace("_", " "))
        mobile = " — comes to the hotel" if partner.service_model == "mobile" else ""
        rationale = (
            f"Highly rated {label} only {partner.distance_miles:.1f} mi from your hotel{mobile}. "
            f"A strong pick for {pet_name} during your stay."
        )
        suggested = f"Morning on {stay_check_in}" if idx == 1 else "Mid-stay afternoon"
        items.append(
            _item_from_partner(
                partner,
                rationale=rationale,
                suggested_time=suggested,
                priority=idx,
            )
        )

    summary = (
        f"We found {len(partners)} bookable pet services within {radius_miles:g} miles. "
        f"Top picks for {pet_name} are ranked below — book in one tap."
    )
    return PetServiceRecommendationsResponse(
        reservation_id=reservation_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        generated_by="mock_llm",
        radius_miles=radius_miles,
        summary=summary,
        recommendations=items,
    )


async def _llm_recommendations(
    *,
    reservation_id: str,
    radius_miles: float,
    partners: list[PartnerResponse],
    guest: dict[str, Any],
    pet: dict[str, Any] | None,
    hotel: dict[str, Any],
    stay_check_in: str,
    stay_check_out: str,
    preferred_categories: list[str],
) -> PetServiceRecommendationsResponse | None:
    """Call LiteLLM to rank partners. Returns None on failure."""
    catalog = _partner_catalog(partners)
    by_id = {p.id: p for p in partners}
    pet_desc = (
        f"{pet['name']} ({pet['breed']}, {pet['weight_kg']} kg)"
        if pet
        else "guest traveling with a pet"
    )

    system = (
        "You are a Marriott Bonvoy pet-travel concierge. Rank bookable pet services "
        "for a hotel stay. Use ONLY partner_id values from the provided catalog. "
        "Output strict JSON only."
    )
    prefs_block = ""
    if preferred_categories:
        labels = [
            _CATEGORY_LABEL.get(c, c.replace("_", " ")) for c in preferred_categories
        ]
        prefs_block = (
            f"Guest preferred service types (prioritize these): {', '.join(labels)}\n"
        )

    user = (
        f"Guest: {guest['name']}\n"
        f"Pet: {pet_desc}\n"
        f"Hotel: {hotel['name']} in {hotel['city']}, {hotel['state']}\n"
        f"Stay: {stay_check_in} to {stay_check_out}\n"
        f"Search radius: {radius_miles} miles from hotel\n"
        f"{prefs_block}\n"
        f"Bookable partners catalog:\n{json.dumps(catalog, indent=2)}\n\n"
        "Respond as JSON with keys:\n"
        "- summary (1-2 warm sentences introducing the picks)\n"
        "- recommendations (array of 3-4 objects, each with: partner_id, rationale "
        "(≤40 words, mention the pet by name if known), suggested_time (short phrase "
        "like '10:00 AM day after check-in'), priority (1 = best))"
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
        logger.warning("LiteLLM pet services failed: %s", exc)
        return None

    try:
        parsed = parse_llm_json(raw)
    except json.JSONDecodeError:
        logger.warning("LiteLLM pet services returned non-JSON")
        return None

    items: list[PetServiceRecommendationItem] = []
    for entry in parsed.get("recommendations", [])[:5]:
        pid = str(entry.get("partner_id", ""))
        partner = by_id.get(pid)
        if partner is None:
            continue
        items.append(
            _item_from_partner(
                partner,
                rationale=str(entry.get("rationale", ""))[:280]
                or f"Recommended for your stay near {hotel['city']}.",
                suggested_time=entry.get("suggested_time"),
                priority=int(entry.get("priority", len(items) + 1)),
            )
        )

    if not items:
        return None

    items.sort(key=lambda x: x.priority)
    return PetServiceRecommendationsResponse(
        reservation_id=reservation_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        generated_by="litellm",
        radius_miles=radius_miles,
        summary=str(parsed.get("summary", ""))[:500]
        or f"Personalized pet service picks within {radius_miles:g} miles of your hotel.",
        recommendations=items,
    )


async def get_pet_service_recommendations(
    reservation_id: str,
    guest_id: str,
) -> PetServiceRecommendationsResponse:
    """Return realtime LLM-ranked pet services for a pet-inclusive reservation."""
    reservation = get_reservation(reservation_id, guest_id)

    if not reservation.has_pet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reservation does not include a pet",
        )

    guest = get_guest_record(guest_id)
    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
        )

    hotel = _find_hotel(reservation.hotel_id)
    if not hotel.get("pet_friendly"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hotel is not pet-friendly",
        )

    radius = get_pet_service_radius_miles(guest_id)
    preferred_categories = get_pet_service_categories(guest_id)
    partners = get_partners_near_hotel(
        reservation.hotel_id,
        pet_only=True,
        bookable_only=True,
        max_miles=radius,
    )

    pet = _pet_for_stay(guest, reservation.pet_id)

    if not partners:
        pet_name = pet.get("name", "your pet") if pet else "your pet"
        return PetServiceRecommendationsResponse(
            reservation_id=reservation_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            generated_by="mock_llm",
            radius_miles=radius,
            summary=(
                f"No bookable pet services were found within {radius:g} miles for {pet_name}. "
                "Try widening your search radius in Profile."
            ),
            recommendations=[],
        )

    live = await _llm_recommendations(
        reservation_id=reservation_id,
        radius_miles=radius,
        partners=partners,
        guest=guest,
        pet=pet,
        hotel=hotel,
        stay_check_in=reservation.check_in,
        stay_check_out=reservation.check_out,
        preferred_categories=preferred_categories,
    )
    if live is not None:
        return live

    return _mock_recommendations(
        reservation_id=reservation_id,
        radius_miles=radius,
        partners=partners,
        pet=pet,
        stay_check_in=reservation.check_in,
        preferred_categories=preferred_categories,
    )
