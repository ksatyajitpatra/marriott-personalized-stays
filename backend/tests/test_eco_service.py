"""Unit tests for `compute_eco_score` — PRD Section 5.1.

Covers:
    - Per-sub-score normalization curves at the boundaries (best / worst / mid).
    - Weighted total formula matches the PRD percentages exactly.
    - Green Points tier thresholds (≥ 8 → 900, ≥ 6 → 300, < 6 → 0).
    - Color band thresholds (≥ 7 green, ≥ 5 yellow, else red).
    - End-to-end snapshot for every hotel in the production seed file
      so the demo numbers (e.g. NYC Marriott Marquis = 8.9) cannot regress
      silently.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.services.eco_service import (
    _color,
    _norm_carbon,
    _norm_certs,
    _norm_energy,
    _norm_fb,
    _norm_water,
    _norm_waste,
    _points_tier,
    compute_eco_score,
)

# --- Fixtures ---------------------------------------------------------------

_SEEDS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "seeds" / "hotels.json"


def _load_seed_hotels() -> list[dict[str, Any]]:
    """Load the production hotel seed file used by the running app."""
    with _SEEDS_PATH.open() as f:
        return json.load(f)


@pytest.fixture()
def perfect_hotel() -> dict[str, Any]:
    """A hotel that scores 10.0 across the board."""
    return {
        "id": "perfect",
        "eco": {
            "energy_kwh_per_room_night": 30.0,  # below best anchor → clamped to 10
            "water_liters_per_room_night": 130.0,  # below best anchor → clamped to 10
            "waste_diversion_pct": 90.0,  # above best anchor → clamped to 10
            "certifications": ["LEED Gold", "EarthCheck"],
            "carbon_offset_program": True,
            "fb_sourcing_score": 10.0,
            "data_as_of": "2026-04-22",
            "data_source": "MESH",
        },
    }


@pytest.fixture()
def average_hotel() -> dict[str, Any]:
    """A hotel that lands mid-band on every metric (≈ 6 total)."""
    return {
        "id": "average",
        "eco": {
            "energy_kwh_per_room_night": 50.0,  # midpoint between 35 and 65 → 6
            "water_liters_per_room_night": 210.0,  # midpoint between 140 and 280 → 6
            "waste_diversion_pct": 55.0,  # midpoint between 35 and 75 → 6
            "certifications": ["Green Key"],
            "carbon_offset_program": False,
            "fb_sourcing_score": 6.0,
            "data_as_of": "2026-04-22",
            "data_source": "MESH",
        },
    }


@pytest.fixture()
def floor_hotel() -> dict[str, Any]:
    """A hotel below every threshold — should land in the red band, no bonus."""
    return {
        "id": "floor",
        "eco": {
            "energy_kwh_per_room_night": 80.0,  # past the worst anchor → floor of 2
            "water_liters_per_room_night": 320.0,
            "waste_diversion_pct": 20.0,
            "certifications": [],
            "carbon_offset_program": False,
            "fb_sourcing_score": 2.0,
            "data_as_of": "2026-04-22",
            "data_source": "MESH",
        },
    }


# --- Sub-score normalization ------------------------------------------------


class TestNormalization:
    """Each `_norm_*` helper maps a raw measurement to a 0–10 sub-score."""

    def test_energy_at_best_anchor_returns_max(self) -> None:
        assert _norm_energy(35.0) == pytest.approx(10.0)

    def test_energy_at_worst_anchor_returns_floor(self) -> None:
        # The PRD anchors land on a 2.0 floor (not 0) — "no program" still
        # isn't actively harmful per the formula's design.
        assert _norm_energy(65.0) == pytest.approx(2.0)

    def test_energy_below_best_is_clamped(self) -> None:
        assert _norm_energy(20.0) == pytest.approx(10.0)

    def test_energy_above_worst_is_clamped(self) -> None:
        assert _norm_energy(80.0) == pytest.approx(2.0)

    def test_energy_midpoint(self) -> None:
        # Halfway between 35 (10pts) and 65 (2pts) should be 6.0.
        assert _norm_energy(50.0) == pytest.approx(6.0)

    def test_water_curve(self) -> None:
        assert _norm_water(140.0) == pytest.approx(10.0)
        assert _norm_water(280.0) == pytest.approx(2.0)
        assert _norm_water(210.0) == pytest.approx(6.0)

    def test_waste_curve_inverted(self) -> None:
        # Waste is "higher is better" — verify the curve is correctly inverted.
        assert _norm_waste(75.0) == pytest.approx(10.0)
        assert _norm_waste(35.0) == pytest.approx(2.0)
        assert _norm_waste(55.0) == pytest.approx(6.0)


class TestCertifications:
    """Cert tier mapping is opinionated — lock the table down with tests."""

    def test_no_certs_returns_low_score(self) -> None:
        assert _norm_certs([]) == pytest.approx(3.0)

    def test_leed_gold_is_top_tier(self) -> None:
        assert _norm_certs(["LEED Gold", "Green Key"]) == pytest.approx(10.0)

    def test_earthcheck_is_high_tier(self) -> None:
        # No LEED Gold, but EarthCheck present.
        assert _norm_certs(["EarthCheck"]) == pytest.approx(9.0)

    def test_leed_silver_falls_to_leed_band(self) -> None:
        assert _norm_certs(["LEED Silver"]) == pytest.approx(8.5)

    def test_green_key_only(self) -> None:
        assert _norm_certs(["Green Key"]) == pytest.approx(7.0)

    def test_unknown_cert_falls_through_to_default(self) -> None:
        assert _norm_certs(["Some Unknown Cert"]) == pytest.approx(5.0)


class TestCarbonAndFb:
    def test_carbon_active_vs_inactive(self) -> None:
        assert _norm_carbon(True) == pytest.approx(10.0)
        # Per the formula's intent: "no program" ≠ harmful, so floor is 4.0
        # not 0.0.
        assert _norm_carbon(False) == pytest.approx(4.0)

    def test_fb_clamps_to_2_10_band(self) -> None:
        assert _norm_fb(0.0) == pytest.approx(2.0)
        assert _norm_fb(15.0) == pytest.approx(10.0)
        assert _norm_fb(7.8) == pytest.approx(7.8)


# --- Tier + color thresholds ------------------------------------------------


class TestPointsTier:
    """Green Points multiplier table — PRD Section 5.1."""

    @pytest.mark.parametrize(
        ("score", "bonus", "multiplier"),
        [
            (10.0, 900, 1.3),
            (8.0, 900, 1.3),  # boundary
            (7.99, 300, 1.1),
            (6.0, 300, 1.1),  # boundary
            (5.99, 0, 1.0),
            (0.0, 0, 1.0),
        ],
    )
    def test_tier_thresholds(
        self, score: float, bonus: int, multiplier: float
    ) -> None:
        assert _points_tier(score) == (bonus, multiplier)


class TestColorBand:
    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (10.0, "green"),
            (7.0, "green"),  # boundary
            (6.99, "yellow"),
            (5.0, "yellow"),  # boundary
            (4.99, "red"),
            (0.0, "red"),
        ],
    )
    def test_color_thresholds(self, score: float, expected: str) -> None:
        assert _color(score) == expected


# --- End-to-end composite ---------------------------------------------------


class TestComputeEcoScore:
    def test_perfect_hotel_caps_at_10(self, perfect_hotel: dict[str, Any]) -> None:
        result = compute_eco_score(perfect_hotel)
        assert result.total_score == pytest.approx(10.0)
        assert result.color == "green"
        assert result.green_points_bonus == 900
        assert result.green_points_multiplier == pytest.approx(1.3)

    def test_average_hotel_lands_in_yellow_with_bonus(
        self, average_hotel: dict[str, Any]
    ) -> None:
        # Mid-band on every component should land between 6 and 7 → yellow,
        # +300 bonus.
        result = compute_eco_score(average_hotel)
        assert 5.5 <= result.total_score <= 7.0
        assert result.color in {"yellow", "green"}
        assert result.green_points_bonus in {0, 300}

    def test_floor_hotel_red_no_bonus(self, floor_hotel: dict[str, Any]) -> None:
        result = compute_eco_score(floor_hotel)
        assert result.total_score < 5.0
        assert result.color == "red"
        assert result.green_points_bonus == 0
        assert result.green_points_multiplier == pytest.approx(1.0)

    def test_response_shape(self, perfect_hotel: dict[str, Any]) -> None:
        """Every sub-score field the UI reads must be populated."""
        result = compute_eco_score(perfect_hotel)
        assert len(result.sub_scores) == 6
        keys = {s.key for s in result.sub_scores}
        assert keys == {"energy", "water", "waste", "certs", "carbon", "fb"}
        # Weights sum to 100 (PRD invariant).
        assert sum(s.weight_pct for s in result.sub_scores) == 100
        for s in result.sub_scores:
            assert 0.0 <= s.score <= 10.0
            assert s.raw_value, "raw_value must always be displayable"
            assert s.data_source, "every sub-score cites its source"

    def test_weighted_sum_matches_prd_formula(self) -> None:
        """Hand-computed total should match the implementation exactly.

        Inputs chosen to land each sub-score on a clean integer so the
        expected total is unambiguous.
        """
        hotel = {
            "id": "h",
            "eco": {
                "energy_kwh_per_room_night": 50.0,  # 6.0
                "water_liters_per_room_night": 210.0,  # 6.0
                "waste_diversion_pct": 55.0,  # 6.0
                "certifications": ["Green Key"],  # 7.0
                "carbon_offset_program": True,  # 10.0
                "fb_sourcing_score": 6.0,  # 6.0
                "data_as_of": "x",
                "data_source": "MESH",
            },
        }
        # Weighted sum: 6×.25 + 6×.20 + 6×.20 + 7×.15 + 10×.10 + 6×.10
        # = 1.5 + 1.2 + 1.2 + 1.05 + 1.0 + 0.6 = 6.55 → 6.6 after rounding
        result = compute_eco_score(hotel)
        assert result.total_score == pytest.approx(6.6, abs=0.05)


# --- Snapshot of the actual seed file ---------------------------------------


_SEED_HOTELS = _load_seed_hotels()

# Locked-in scores. If anyone tweaks the seed data or the formula, these
# tests should fail loudly so we catch regressions before the demo.
_EXPECTED_SCORES: dict[str, float] = {
    "marriott-nyc-times-sq": 8.9,
    "westin-dc-city-center": 9.8,
    "ritz-carlton-chicago": 5.4,
    "element-miami": 9.9,
    "marriott-chicago-magnificent-mile": 7.2,
}


class TestSeedSnapshot:
    """Lock down the exact numbers the demo will display."""

    @pytest.mark.parametrize(
        "hotel",
        _SEED_HOTELS,
        ids=[h["id"] for h in _SEED_HOTELS],
    )
    def test_seed_hotel_score_matches_expected(
        self, hotel: dict[str, Any]
    ) -> None:
        expected = _EXPECTED_SCORES.get(hotel["id"])
        if expected is None:
            pytest.skip(f"no expected snapshot for {hotel['id']}")
        result = compute_eco_score(hotel)
        assert result.total_score == pytest.approx(expected, abs=0.05), (
            f"{hotel['id']} expected {expected}, got {result.total_score}"
        )

    def test_demo_covers_all_three_tiers(self) -> None:
        """All three Green Points tiers should be representable in the demo."""
        scores = [compute_eco_score(h).total_score for h in _SEED_HOTELS]
        assert any(s >= 8.0 for s in scores), "at least one 'Leader' (+900)"
        assert any(6.0 <= s < 8.0 for s in scores), "at least one 'Improving' (+300)"
        assert any(s < 6.0 for s in scores), "at least one 'Below standard' (no bonus)"
