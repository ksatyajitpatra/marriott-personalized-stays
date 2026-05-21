"""Eco rating computation — implements PRD Section 5.1 exactly.

Composite score = sum(sub_score_i * weight_i) for six sub-scores:

    energy   25%   kWh per room-night (lower = better)
    water    20%   liters per room-night (lower = better)
    waste    20%   diversion rate % (higher = better)
    certs    15%   sustainability certifications (LEED, EarthCheck, etc.)
    carbon   10%   active carbon offset program (boolean)
    fb       10%   responsible F&B sourcing score (0–10)

Each sub-score is normalized to 0–10 before weighting. The PRD's anchor
ranges (e.g. "energy ≤ 35 kWh = perfect 10, ≥ 65 kWh = floor of 2") drive
the linear interpolation in the `_norm_*` helpers.
"""

from __future__ import annotations

from typing import Any

from app.models.eco import EcoScoreResponse, EcoSubScore

# --- Normalization curves ---------------------------------------------------

# Anchor ranges chosen from publicly reported Marriott Serve360 figures so
# real-world hotel data lands somewhere in the middle of each band.
_ENERGY_BEST_KWH = 35.0
_ENERGY_WORST_KWH = 65.0
_WATER_BEST_L = 140.0
_WATER_WORST_L = 280.0
_WASTE_BEST_PCT = 75.0
_WASTE_WORST_PCT = 35.0


def _linear(value: float, best: float, worst: float, hi: float = 10.0, lo: float = 2.0) -> float:
    """Map `value` linearly between best→hi and worst→lo, clamped.

    Works for both "lower is better" (best < worst is False) and the
    reverse (best > worst), since we just lerp using the relative position.
    """
    if best == worst:
        return hi
    # Position on the [worst, best] axis where 0 = worst, 1 = best.
    pos = (value - worst) / (best - worst)
    pos = max(0.0, min(1.0, pos))
    return round(lo + pos * (hi - lo), 1)


def _norm_energy(kwh: float) -> float:
    """Lower kWh/room-night → higher score."""
    return _linear(kwh, _ENERGY_BEST_KWH, _ENERGY_WORST_KWH)


def _norm_water(liters: float) -> float:
    """Lower liters/room-night → higher score."""
    return _linear(liters, _WATER_BEST_L, _WATER_WORST_L)


def _norm_waste(pct: float) -> float:
    """Higher diversion % → higher score."""
    return _linear(pct, _WASTE_BEST_PCT, _WASTE_WORST_PCT)


def _norm_certs(certs: list[str]) -> float:
    """Score sustainability certifications by tier.

    The PRD lets us be opinionated here — LEED Gold + EarthCheck is
    treated as the gold standard.
    """
    if not certs:
        return 3.0
    text = " ".join(certs)
    if "LEED Gold" in text:
        return 10.0
    if "EarthCheck" in text:
        return 9.0
    if "LEED" in text:
        return 8.5
    if "Green Key" in text:
        return 7.0
    return 5.0


def _norm_carbon(active: bool) -> float:
    """Boolean offset program → 10 vs 4 (not 0, since "no program" still ≠ harmful)."""
    return 10.0 if active else 4.0


def _norm_fb(score_0_10: float) -> float:
    """Pass-through F&B sourcing score, clamped to the 2–10 band."""
    return round(max(2.0, min(10.0, float(score_0_10))), 1)


# --- Points multiplier (PRD Section 5.1) ------------------------------------


def _points_tier(total: float) -> tuple[int, float]:
    """Return (bonus_points, multiplier) for a given composite score."""
    if total >= 8:
        return 900, 1.3
    if total >= 6:
        return 300, 1.1
    return 0, 1.0


def _color(total: float) -> str:
    """Ring color band for the UI."""
    if total >= 7:
        return "green"
    if total >= 5:
        return "yellow"
    return "red"


# --- Main entry point -------------------------------------------------------


def compute_eco_score(hotel: dict[str, Any]) -> EcoScoreResponse:
    """Compute the full eco breakdown for a hotel.

    Args:
        hotel: Raw hotel seed dict containing the `eco` sub-object with
            energy, water, waste, certifications, carbon offset flag, and
            F&B sourcing score.

    Returns:
        Fully populated `EcoScoreResponse` ready to send to the client.

    Example:
        >>> hotel = {"id": "h1", "eco": {
        ...     "energy_kwh_per_room_night": 38.2,
        ...     "water_liters_per_room_night": 162,
        ...     "waste_diversion_pct": 72,
        ...     "certifications": ["LEED Silver", "Green Key"],
        ...     "carbon_offset_program": True,
        ...     "fb_sourcing_score": 7.8,
        ...     "data_as_of": "2026-04-22",
        ...     "data_source": "MESH",
        ... }}
        >>> compute_eco_score(hotel).total_score > 0
        True
    """
    eco = hotel["eco"]

    # Compute each normalized sub-score.
    energy = _norm_energy(float(eco["energy_kwh_per_room_night"]))
    water = _norm_water(float(eco["water_liters_per_room_night"]))
    waste = _norm_waste(float(eco["waste_diversion_pct"]))
    certs = _norm_certs(list(eco.get("certifications", [])))
    carbon = _norm_carbon(bool(eco.get("carbon_offset_program")))
    fb = _norm_fb(float(eco.get("fb_sourcing_score", 5.0)))

    # Components: (key, label, score, raw_value_for_display, weight_pct)
    components: list[tuple[str, str, float, str, int]] = [
        ("energy", "Energy Intensity", energy,
         f"{eco['energy_kwh_per_room_night']} kWh/room-night", 25),
        ("water", "Water Usage", water,
         f"{eco['water_liters_per_room_night']} L/room-night", 20),
        ("waste", "Waste Diversion", waste,
         f"{eco['waste_diversion_pct']}%", 20),
        ("certs", "Certifications", certs,
         ", ".join(eco.get("certifications", [])) or "None", 15),
        ("carbon", "Carbon Offset Program", carbon,
         "Active" if eco.get("carbon_offset_program") else "None", 10),
        ("fb", "Responsible F&B Sourcing", fb,
         f"{eco.get('fb_sourcing_score', 0)}/10", 10),
    ]

    total = round(sum(score * (weight / 100) for _, _, score, _, weight in components), 1)
    bonus, multiplier = _points_tier(total)
    source = eco.get("data_source", "MESH")

    return EcoScoreResponse(
        hotel_id=hotel["id"],
        total_score=total,
        color=_color(total),
        green_points_bonus=bonus,
        green_points_multiplier=multiplier,
        sub_scores=[
            EcoSubScore(
                key=key,
                label=label,
                score=score,
                raw_value=raw,
                weight_pct=weight,
                data_source=source,
            )
            for key, label, score, raw, weight in components
        ],
        data_as_of=eco.get("data_as_of", ""),
        data_source=source,
    )
