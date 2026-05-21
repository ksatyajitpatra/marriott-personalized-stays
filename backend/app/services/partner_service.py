"""Local partner map data — flat queries over the per-city seed files."""

from __future__ import annotations

from typing import Any

from app.data.loader import get_seed, has_seed
from app.models.partner import PartnerResponse, resolve_partner_fields

KM_PER_MILE = 1.60934

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
    """Return the raw seed dict for a partner with resolved defaults, or None."""
    for p in _all_partners():
        if p.get("id") == partner_id:
            return resolve_partner_fields(p)
    return None


def _within_radius(partner: dict[str, Any], max_miles: float) -> bool:
    dist_miles = float(partner.get("distance_km", 99)) / KM_PER_MILE
    if dist_miles > max_miles:
        return False
    if partner.get("service_model") == "mobile":
        area = partner.get("service_area_miles")
        if area is not None and float(area) < dist_miles:
            return False
    return True


def _to_response(partner: dict[str, Any]) -> PartnerResponse:
    resolved = resolve_partner_fields(partner)
    dist_km = float(resolved.get("distance_km", 0))
    return PartnerResponse(
        id=resolved["id"],
        hotel_id=resolved["hotel_id"],
        name=resolved["name"],
        category=resolved["category"],
        service_model=resolved["service_model"],
        bookable=resolved["bookable"],
        lat=resolved["lat"],
        lng=resolved["lng"],
        address=resolved["address"],
        phone=resolved.get("phone"),
        hours=resolved.get("hours"),
        rating=resolved["rating"],
        is_marriott_partner=resolved.get("is_marriott_partner", False),
        pet_relevant=resolved.get("pet_relevant", False),
        distance_km=round(dist_km, 1),
        distance_miles=round(dist_km / KM_PER_MILE, 1),
        note=resolved.get("note"),
        dietary_tags=list(resolved.get("dietary_tags", [])),
        service_area_miles=resolved.get("service_area_miles"),
        mobile_service_note=resolved.get("mobile_service_note"),
    )


def get_partners_near_hotel(
    hotel_id: str,
    *,
    pet_only: bool = False,
    bookable_only: bool = False,
    max_miles: float = 10.0,
    category: str | None = None,
) -> list[PartnerResponse]:
    """Return partners around a hotel, sorted by distance ascending."""
    results: list[PartnerResponse] = []

    for raw in _all_partners():
        p = resolve_partner_fields(raw)
        if p.get("hotel_id") != hotel_id:
            continue
        if pet_only and not p.get("pet_relevant"):
            continue
        if bookable_only and not p.get("bookable"):
            continue
        if category and p.get("category") != category:
            continue
        if not _within_radius(p, max_miles):
            continue
        results.append(_to_response(p))

    return sorted(results, key=lambda x: x.distance_km)
