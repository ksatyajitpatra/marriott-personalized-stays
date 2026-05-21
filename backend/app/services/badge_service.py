"""Bonvoy badge engine — derives the full badge shelf from completed
stays + reservations + each property's eco score.

Design principles:
    * Single source of truth: the data (stays.json + hotels.json +
      partner bookings). Never read a static `badges` field from the
      guest seed.
    * Tiered badges show ONE tile that advances. Frontend renders the
      current tier label + progress to next tier.
    * Categories: sustainability, loyalty, explorer, lifestyle.
    * 12 badges total — enough variety, not overwhelming.

Each badge follows one of two patterns:

    Counter badge   — accumulates a metric (stays, cities) and unlocks
                      tiers at thresholds. Current tier = highest passed.
    Single-shot     — one-tier "did the thing" badge (e.g. first stay).

Both produce the same `BadgeItem` shape so the UI can render them
uniformly with a progress bar (locked / in-progress / max).
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from app.data.loader import get_seed
from app.models.badge import (
    BadgeCategorySection,
    BadgeItem,
    BadgeShelfResponse,
    BadgeShelfStats,
)
from app.services.eco_service import compute_eco_score

logger = logging.getLogger(__name__)

_GREEN_STAY_THRESHOLD = 8.0


# --- Domain helpers ---------------------------------------------------------


def _hotel_index() -> dict[str, dict[str, Any]]:
    """hotel_id → hotel dict."""
    return {h["id"]: h for h in get_seed("hotels")}


def _all_reservations_for_guest(guest_id: str) -> list[dict[str, Any]]:
    """All reservations for the guest, including upcoming ones.

    We pull from the in-memory reservation store so newly created
    bookings during the demo also count. Falls back to the static seed
    if the reservation service hasn't been initialized.
    """
    try:
        from app.services import reservation_service

        return [
            r
            for r in reservation_service._reservations.values()
            if r["guest_id"] == guest_id
        ]
    except (ImportError, AttributeError):
        return [s for s in get_seed("stays") if s.get("guest_id") == guest_id]


def _completed_reservations_for_guest(
    guest_id: str,
) -> list[dict[str, Any]]:
    """Just completed stays — most badges only count completed stays."""
    return [
        r
        for r in _all_reservations_for_guest(guest_id)
        if r.get("status") == "completed"
    ]


def _pet_service_bookings_count(guest_id: str) -> int:
    """Total non-cancelled pet service bookings the guest has made."""
    try:
        from app.services import reservation_service

        count = 0
        for rid, bookings in reservation_service._pet_bookings.items():
            res = reservation_service._reservations.get(rid)
            if not res or res["guest_id"] != guest_id:
                continue
            count += sum(
                1 for b in bookings if b.get("status") != "cancelled"
            )
        return count
    except (ImportError, AttributeError):
        return 0


# --- Badge builder primitives -----------------------------------------------


def _build_tiered_badge(
    *,
    badge_id: str,
    label: str,
    category: str,
    description: str,
    image_id: str,
    progress: int,
    tiers: list[tuple[int, str]],
    metric_noun: str,
) -> BadgeItem:
    """Build a counter-style badge (Frequent Stayer, Eco Warrior, etc.).

    Args:
        badge_id: Stable id.
        label: Display name.
        category: One of the 4 categories.
        description: One-line story for the tile.
        image_id: Asset id (e.g. 'frequent-stayer').
        progress: Current count of the metric.
        tiers: Ordered list of (threshold, tier_label) tuples.
        metric_noun: What we're counting ('stays', 'cities', etc.) for the hint.
    """
    current_tier = 0
    current_tier_label: str | None = None
    for i, (threshold, tlabel) in enumerate(tiers, start=1):
        if progress >= threshold:
            current_tier = i
            current_tier_label = tlabel

    earned = current_tier >= 1
    next_threshold: int | None = None
    next_label: str | None = None
    if current_tier < len(tiers):
        next_threshold, next_label = tiers[current_tier]

    if next_threshold is not None:
        remaining = next_threshold - progress
        if earned:
            hint = f"{remaining} more {metric_noun} to {next_label}"
        else:
            hint = f"{remaining} {metric_noun} to unlock {next_label}"
    else:
        hint = "Maxed out — top tier earned"

    return BadgeItem(
        id=badge_id,
        label=label,
        category=category,  # type: ignore[arg-type]
        description=description,
        image_id=image_id,
        earned=earned,
        current_tier=current_tier,
        max_tier=len(tiers),
        current_tier_label=current_tier_label,
        progress_value=progress,
        next_tier_threshold=next_threshold,
        next_tier_label=next_label,
        hint=hint,
    )


def _build_single_badge(
    *,
    badge_id: str,
    label: str,
    category: str,
    description: str,
    image_id: str,
    earned: bool,
    earned_hint: str,
    locked_hint: str,
) -> BadgeItem:
    """Build a one-shot badge ('did the thing once' style)."""
    return BadgeItem(
        id=badge_id,
        label=label,
        category=category,  # type: ignore[arg-type]
        description=description,
        image_id=image_id,
        earned=earned,
        current_tier=1 if earned else 0,
        max_tier=1,
        current_tier_label="Earned" if earned else None,
        progress_value=1 if earned else 0,
        next_tier_threshold=None if earned else 1,
        next_tier_label=None if earned else "Earned",
        hint=earned_hint if earned else locked_hint,
    )


# --- Per-category badge factories -------------------------------------------


def _sustainability_badges(
    *, eco_leader_stays: int, brand_unlocks: dict[str, dict[str, Any]]
) -> list[BadgeItem]:
    """Eco play — three badges."""
    badges: list[BadgeItem] = [
        _build_single_badge(
            badge_id="green_stay",
            label="Green Stay",
            category="sustainability",
            description="Booked an eco-leader hotel (rated 8.0+)",
            image_id="green-stay",
            earned=eco_leader_stays >= 1,
            earned_hint=f"{eco_leader_stays} eco-leader "
            f"{'stay' if eco_leader_stays == 1 else 'stays'} on file",
            locked_hint="Stay at a hotel rated 8.0+ to unlock",
        ),
        _build_tiered_badge(
            badge_id="eco_warrior",
            label="Eco Warrior",
            category="sustainability",
            description="Repeated commitment to eco-leader properties",
            image_id="eco-warrior",
            progress=eco_leader_stays,
            tiers=[(3, "Bronze"), (10, "Silver"), (25, "Gold")],
            metric_noun="eco-leader stays",
        ),
    ]

    # Brand Eco Native — single badge, earned at the FIRST eco-leader brand stay.
    # We surface the highest-eco brand the guest has unlocked at.
    if brand_unlocks:
        # Pick the unlock with the highest eco_score for the tile copy.
        top = max(brand_unlocks.values(), key=lambda u: u["eco_score"])
        badges.append(
            _build_single_badge(
                badge_id="brand_eco_native",
                label="Brand Eco Native",
                category="sustainability",
                description=f"Unlocked at {top['hotel_name']} (eco {top['eco_score']:.1f}/10)",
                image_id="brand-eco-native",
                earned=True,
                earned_hint=f"{len(brand_unlocks)} eco-leader "
                f"{'brand' if len(brand_unlocks) == 1 else 'brands'} unlocked",
                locked_hint="",
            )
        )
    else:
        badges.append(
            _build_single_badge(
                badge_id="brand_eco_native",
                label="Brand Eco Native",
                category="sustainability",
                description="Eco-leader stay at a sustainability-forward brand",
                image_id="brand-eco-native",
                earned=False,
                earned_hint="",
                locked_hint="Stay at Westin, Element, or Ritz-Carlton with eco 8.0+",
            )
        )

    return badges


def _loyalty_badges(
    *, completed_stays: int, brand_counts: Counter[str]
) -> list[BadgeItem]:
    """Loyalty / repeat-stayer badges — three badges."""
    top_brand_count = max(brand_counts.values(), default=0)
    top_brand = (
        max(brand_counts, key=lambda b: brand_counts[b])
        if brand_counts
        else None
    )

    return [
        _build_single_badge(
            badge_id="welcome_aboard",
            label="Welcome Aboard",
            category="loyalty",
            description="First completed Bonvoy stay",
            image_id="welcome-aboard",
            earned=completed_stays >= 1,
            earned_hint="Your Bonvoy journey has begun",
            locked_hint="Complete your first stay to unlock",
        ),
        _build_tiered_badge(
            badge_id="frequent_stayer",
            label="Frequent Stayer",
            category="loyalty",
            description="Total completed stays across the portfolio",
            image_id="frequent-stayer",
            progress=completed_stays,
            tiers=[
                (5, "Bronze"),
                (10, "Silver"),
                (25, "Gold"),
                (50, "Platinum"),
                (100, "Ambassador"),
            ],
            metric_noun="stays",
        ),
        _build_single_badge(
            badge_id="brand_loyalist",
            label="Brand Loyalist",
            category="loyalty",
            description=(
                f"5+ stays at {top_brand}" if top_brand and top_brand_count >= 5
                else "5 stays at the same Marriott brand"
            ),
            image_id="brand-loyalist",
            earned=top_brand_count >= 5,
            earned_hint=f"You're a {top_brand} regular" if top_brand else "Brand loyalty unlocked",
            locked_hint=(
                f"{5 - top_brand_count} more stays at {top_brand} to unlock"
                if top_brand and top_brand_count > 0
                else "Stay 5 times at the same brand to unlock"
            ),
        ),
    ]


def _explorer_badges(
    *,
    cities_visited: int,
    brands_visited: int,
    properties_visited: int,
    total_demo_properties: int,
) -> list[BadgeItem]:
    """Explorer / variety badges — three badges."""
    return [
        _build_tiered_badge(
            badge_id="globetrotter",
            label="Globetrotter",
            category="explorer",
            description="Different cities visited",
            image_id="globetrotter",
            progress=cities_visited,
            tiers=[(3, "Bronze"), (5, "Silver"), (10, "Gold")],
            metric_noun="cities",
        ),
        _build_tiered_badge(
            badge_id="brand_sampler",
            label="Brand Sampler",
            category="explorer",
            description="Different Marriott brands experienced",
            image_id="brand-sampler",
            progress=brands_visited,
            tiers=[(3, "Bronze"), (5, "Silver")],
            metric_noun="brands",
        ),
        _build_single_badge(
            badge_id="property_pioneer",
            label="Property Pioneer",
            category="explorer",
            description=f"Stayed at all {total_demo_properties} featured properties",
            image_id="property-pioneer",
            earned=properties_visited >= total_demo_properties and total_demo_properties > 0,
            earned_hint="Hall of Fame — every featured property",
            locked_hint=(
                f"{total_demo_properties - properties_visited} more "
                f"{'property' if total_demo_properties - properties_visited == 1 else 'properties'} "
                f"to complete the set"
            ),
        ),
    ]


def _lifestyle_badges(
    *,
    pet_stay_count: int,
    arrival_briefs_seen: int,
    pet_service_bookings: int,
) -> list[BadgeItem]:
    """Lifestyle / preference-driven badges — three badges."""
    return [
        _build_single_badge(
            badge_id="pet_parent",
            label="Pet Parent",
            category="lifestyle",
            description="Booked a Bonvoy stay with a pet",
            image_id="pet-parent",
            earned=pet_stay_count >= 1,
            earned_hint=f"{pet_stay_count} pet-inclusive "
            f"{'stay' if pet_stay_count == 1 else 'stays'} on file",
            locked_hint="Add a pet to a reservation to unlock",
        ),
        _build_single_badge(
            badge_id="concierge_of_one",
            label="Concierge of One",
            category="lifestyle",
            description="Personalized arrival brief delivered",
            image_id="concierge-of-one",
            earned=arrival_briefs_seen >= 1,
            earned_hint="Personalized briefings active for your trips",
            locked_hint="Enable arrival briefs in your profile to unlock",
        ),
        _build_tiered_badge(
            badge_id="local_explorer",
            label="Local Explorer",
            category="lifestyle",
            description="Pet & local services booked from the partner map",
            image_id="local-explorer",
            progress=pet_service_bookings,
            tiers=[(1, "Bronze"), (3, "Silver"), (5, "Gold")],
            metric_noun="local bookings",
        ),
    ]


# --- Public API -------------------------------------------------------------


def compute_badge_shelf(guest_id: str) -> BadgeShelfResponse:
    """Compute the full multi-category badge shelf for a guest.

    Args:
        guest_id: Persona id (alex / jordan / sam in the demo).

    Returns:
        Full shelf with grouped sections, top-line stats, and qualifying
        stays for the eco "how was this earned?" breakdown.

    Example:
        >>> shelf = compute_badge_shelf("alex")
        >>> shelf.stats.total_earned >= 0
        True
    """
    hotels = _hotel_index()
    completed = _completed_reservations_for_guest(guest_id)
    all_reservations = _all_reservations_for_guest(guest_id)

    # --- Counters we'll feed into each badge factory ------------------------

    eco_leader_stays = 0
    qualifying_stays_summary: list[dict[str, Any]] = []
    brand_unlocks: dict[str, dict[str, Any]] = {}

    cities_visited: set[str] = set()
    brands_visited: set[str] = set()
    properties_visited: set[str] = set()
    brand_counts: Counter[str] = Counter()

    for stay in completed:
        hotel = hotels.get(stay["hotel_id"])
        if hotel is None:
            logger.warning("Stay %s references unknown hotel %s", stay.get("id"), stay.get("hotel_id"))
            continue

        cities_visited.add(hotel["city"])
        properties_visited.add(hotel["id"])
        brand = hotel.get("brand", "Unknown")
        brands_visited.add(brand)
        brand_counts[brand] += 1

        eco = compute_eco_score(hotel)
        if eco.total_score >= _GREEN_STAY_THRESHOLD:
            eco_leader_stays += 1
            qualifying_stays_summary.append(
                {
                    "stay_id": stay.get("id"),
                    "hotel_id": hotel["id"],
                    "hotel_name": hotel["name"],
                    "check_in": stay.get("check_in"),
                    "eco_score": eco.total_score,
                }
            )
            # Track which sustainability-forward brands have been unlocked.
            brand_lower = brand.strip().lower()
            if brand_lower in {"westin", "element", "the ritz-carlton"} and brand_lower not in brand_unlocks:
                brand_unlocks[brand_lower] = {
                    "hotel_name": hotel["name"],
                    "eco_score": eco.total_score,
                }

    # Lifestyle metrics — count across ALL reservations (not just completed),
    # since e.g. an upcoming pet stay should still earn the Pet Parent badge.
    pet_stay_count = sum(1 for r in all_reservations if r.get("has_pet"))
    arrival_briefs_seen = sum(
        1 for r in all_reservations if r.get("status") in {"upcoming", "in_stay", "completed"}
    )  # Every active stay can render a brief — proxy for "the feature is live for them".
    pet_service_bookings = _pet_service_bookings_count(guest_id)

    total_demo_properties = len(hotels)

    # --- Build each section --------------------------------------------------

    sections = [
        BadgeCategorySection(
            id="sustainability",
            label="Sustainability",
            description="Earned by choosing eco-leader properties",
            badges=_sustainability_badges(
                eco_leader_stays=eco_leader_stays,
                brand_unlocks=brand_unlocks,
            ),
        ),
        BadgeCategorySection(
            id="loyalty",
            label="Loyalty",
            description="Earned by coming back",
            badges=_loyalty_badges(
                completed_stays=len(completed),
                brand_counts=brand_counts,
            ),
        ),
        BadgeCategorySection(
            id="explorer",
            label="Explorer",
            description="Earned by trying new places",
            badges=_explorer_badges(
                cities_visited=len(cities_visited),
                brands_visited=len(brands_visited),
                properties_visited=len(properties_visited),
                total_demo_properties=total_demo_properties,
            ),
        ),
        BadgeCategorySection(
            id="lifestyle",
            label="Lifestyle",
            description="Earned by personalizing your stay",
            badges=_lifestyle_badges(
                pet_stay_count=pet_stay_count,
                arrival_briefs_seen=arrival_briefs_seen,
                pet_service_bookings=pet_service_bookings,
            ),
        ),
    ]

    total_earned = sum(1 for s in sections for b in s.badges if b.earned)
    total_available = sum(len(s.badges) for s in sections)

    return BadgeShelfResponse(
        guest_id=guest_id,
        stats=BadgeShelfStats(
            total_earned=total_earned,
            total_available=total_available,
            completed_stays=len(completed),
            cities_visited=len(cities_visited),
            brands_visited=len(brands_visited),
            eco_leader_stays=eco_leader_stays,
        ),
        sections=sections,
        qualifying_stays=qualifying_stays_summary,
    )
