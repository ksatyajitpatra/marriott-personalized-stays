"""In-memory guest preference overrides (demo — merges over seed JSON)."""

from __future__ import annotations

from typing import Any

from app.data.loader import get_seed
from app.models.preferences import (
    DIETARY_OPTIONS,
    INTEREST_OPTIONS,
    PET_SERVICE_CATEGORY_OPTIONS,
)

DEFAULT_PET_SERVICE_RADIUS_MILES = 10.0
MIN_PET_SERVICE_RADIUS_MILES = 1.0
MAX_PET_SERVICE_RADIUS_MILES = 50.0

# guest_id -> partial preferences dict
_overrides: dict[str, dict[str, Any]] = {}


def _clamp_radius(miles: float) -> float:
    return max(MIN_PET_SERVICE_RADIUS_MILES, min(MAX_PET_SERVICE_RADIUS_MILES, miles))


def _filter_allowed(values: list[str] | None, allowed: tuple[str, ...]) -> list[str]:
    if not values:
        return []
    allowed_set = set(allowed)
    return [v for v in values if v in allowed_set]


def get_guest_record(guest_id: str) -> dict[str, Any] | None:
    """Return the full guest seed dict merged with runtime overrides."""
    for guest in get_seed("guests"):
        if guest.get("id") == guest_id:
            merged = {**guest, "preferences": {**guest.get("preferences", {})}}
            if guest_id in _overrides:
                merged["preferences"] = {
                    **merged["preferences"],
                    **_overrides[guest_id],
                }
            return merged
    return None


def get_pet_service_radius_miles(guest_id: str) -> float:
    """Return the guest's pet service search radius (default 10 mi)."""
    guest = get_guest_record(guest_id)
    if guest is None:
        return DEFAULT_PET_SERVICE_RADIUS_MILES
    raw = guest.get("preferences", {}).get(
        "pet_service_radius_miles", DEFAULT_PET_SERVICE_RADIUS_MILES
    )
    try:
        return _clamp_radius(float(raw))
    except (TypeError, ValueError):
        return DEFAULT_PET_SERVICE_RADIUS_MILES


def get_pet_service_categories(guest_id: str) -> list[str]:
    """Return selected bookable pet service types, or [] if none chosen."""
    guest = get_guest_record(guest_id)
    if guest is None:
        return []
    raw = guest.get("preferences", {}).get("pet_service_categories", [])
    if not isinstance(raw, list):
        return []
    return _filter_allowed(raw, PET_SERVICE_CATEGORY_OPTIONS)


def update_preferences(guest_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Merge preference updates for a persona and return the new preferences dict."""
    guest = get_guest_record(guest_id)
    if guest is None:
        raise KeyError(guest_id)

    current = _overrides.setdefault(guest_id, {})
    if "pet_service_radius_miles" in updates and updates["pet_service_radius_miles"] is not None:
        current["pet_service_radius_miles"] = _clamp_radius(
            float(updates["pet_service_radius_miles"])
        )
    if "dietary" in updates and updates["dietary"] is not None:
        current["dietary"] = _filter_allowed(updates["dietary"], DIETARY_OPTIONS)
    if "interests" in updates and updates["interests"] is not None:
        current["interests"] = _filter_allowed(updates["interests"], INTEREST_OPTIONS)
    if "pet_service_categories" in updates and updates["pet_service_categories"] is not None:
        current["pet_service_categories"] = _filter_allowed(
            updates["pet_service_categories"], PET_SERVICE_CATEGORY_OPTIONS
        )
    return get_guest_record(guest_id)["preferences"]  # type: ignore[index]
