"""In-memory guest preference overrides (demo — merges over seed JSON)."""

from __future__ import annotations

from typing import Any

from app.data.loader import get_seed

DEFAULT_PET_SERVICE_RADIUS_MILES = 10.0
MIN_PET_SERVICE_RADIUS_MILES = 1.0
MAX_PET_SERVICE_RADIUS_MILES = 50.0

# guest_id -> partial preferences dict
_overrides: dict[str, dict[str, Any]] = {}


def _clamp_radius(miles: float) -> float:
    return max(MIN_PET_SERVICE_RADIUS_MILES, min(MAX_PET_SERVICE_RADIUS_MILES, miles))


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


def update_preferences(guest_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Merge preference updates for a persona and return the new preferences dict."""
    guest = get_guest_record(guest_id)
    if guest is None:
        raise KeyError(guest_id)

    current = _overrides.setdefault(guest_id, {})
    if "pet_service_radius_miles" in updates:
        current["pet_service_radius_miles"] = _clamp_radius(
            float(updates["pet_service_radius_miles"])
        )
    return get_guest_record(guest_id)["preferences"]  # type: ignore[index]
