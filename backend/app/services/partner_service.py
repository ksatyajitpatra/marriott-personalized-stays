"""Local partner map data — flat queries over the per-city seed files."""

from __future__ import annotations

from typing import Any

from app.data.loader import get_seed, has_seed
from app.models.partner import PartnerResponse

KM_PER_MILE = 1.60934

# Seed file names per supported city (PRD Section 8).
_PARTNER_SEEDS: tuple[str, ...] = (
    "partners_nyc",
    "partners_dc",
    "partners_chicago",
)


def _all_partners() -> list[dict[str, Any]]:
    """Concatenate all per-city partner seed files into a single list."""
    out: list[dict[str, Any]] = []
    for name in _PARTNER_SEEDS:
        if has_seed(name):
            out.extend(get_seed(name))
    return out


def get_partner_by_id(partner_id: str) -> dict[str, Any] | None:
    """Return the raw seed dict for a partner, or None."""
    for p in _all_partners():
        if p.get("id") == partner_id:
            return p
    return None


def get_partners_near_hotel(
    hotel_id: str,
    *,
    pet_only: bool = False,
    max_miles: float = 10.0,
    category: str | None = None,
) -> list[PartnerResponse]:
    """Return partners around a hotel, sorted by distance ascending.

    Args:
        hotel_id: Hotel to anchor the search to.
        pet_only: If True, only return pet-relevant partners.
        max_miles: Max radius (miles).
        category: Optional category filter (e.g. 'vet_emergency').

    Returns:
        List of `PartnerResponse`, nearest first.
    """
    max_km = max_miles * KM_PER_MILE
    results: list[PartnerResponse] = []

    for p in _all_partners():
        if p.get("hotel_id") != hotel_id:
            continue
        if pet_only and not p.get("pet_relevant"):
            continue
        if category and p.get("category") != category:
            continue
        dist_km = float(p.get("distance_km", 99))
        if dist_km > max_km:
            continue

        results.append(
            PartnerResponse(
                id=p["id"],
                hotel_id=p["hotel_id"],
                name=p["name"],
                category=p["category"],
                lat=p["lat"],
                lng=p["lng"],
                address=p["address"],
                phone=p.get("phone"),
                hours=p.get("hours"),
                rating=p["rating"],
                is_marriott_partner=p.get("is_marriott_partner", False),
                pet_relevant=p.get("pet_relevant", False),
                distance_km=round(dist_km, 1),
                distance_miles=round(dist_km / KM_PER_MILE, 1),
                note=p.get("note"),
                dietary_tags=list(p.get("dietary_tags", [])),
            )
        )

    return sorted(results, key=lambda x: x.distance_km)
