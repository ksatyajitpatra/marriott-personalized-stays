"""Unit tests for `compute_badge_shelf` — full Bonvoy badge engine.

The service derives badges across 4 categories (sustainability,
loyalty, explorer, lifestyle) from the guest's reservations + each
hotel's computed eco score. We verify the rules against the demo seed
data so badge regressions cannot ship silently.

Run from the repo root:
    cd backend && .venv/bin/pytest tests/test_badge_service.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.data.loader import load_seeds
from app.services import reservation_service
from app.services.badge_service import compute_badge_shelf
from app.models.badge import BadgeItem


# --- Test setup -------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def _load_demo_seeds() -> None:
    """Load production seed files + materialize reservations once per module."""
    seeds_path = Path(__file__).resolve().parent.parent.parent / "data" / "seeds"
    load_seeds(seeds_path)
    reservation_service.init_reservations_from_seeds()


def _badge_by_id(shelf, badge_id: str) -> BadgeItem:
    """Find a single badge across all sections, raising if missing."""
    for section in shelf.sections:
        for badge in section.badges:
            if badge.id == badge_id:
                return badge
    raise AssertionError(f"Badge {badge_id} not found in shelf")


def _earned_ids(shelf) -> set[str]:
    return {
        b.id for s in shelf.sections for b in s.badges if b.earned
    }


# --- Shape & invariants -----------------------------------------------------


class TestShelfShape:
    """Structural invariants: every shelf has 4 sections × 3 badges = 12."""

    @pytest.mark.parametrize("guest_id", ["alex", "jordan", "sam"])
    def test_shelf_has_four_categories_and_twelve_badges(self, guest_id: str) -> None:
        shelf = compute_badge_shelf(guest_id)
        assert len(shelf.sections) == 4
        ids = [s.id for s in shelf.sections]
        assert ids == ["sustainability", "loyalty", "explorer", "lifestyle"]
        assert sum(len(s.badges) for s in shelf.sections) == 12
        assert shelf.stats.total_available == 12

    @pytest.mark.parametrize("guest_id", ["alex", "jordan", "sam"])
    def test_total_earned_matches_section_counts(self, guest_id: str) -> None:
        shelf = compute_badge_shelf(guest_id)
        observed = sum(1 for s in shelf.sections for b in s.badges if b.earned)
        assert shelf.stats.total_earned == observed

    @pytest.mark.parametrize("guest_id", ["alex", "jordan", "sam"])
    def test_every_badge_has_image_id_and_hint(self, guest_id: str) -> None:
        shelf = compute_badge_shelf(guest_id)
        for section in shelf.sections:
            for badge in section.badges:
                assert badge.image_id, f"{badge.id} missing image_id"
                assert badge.hint, f"{badge.id} missing hint"
                assert 0 <= badge.current_tier <= badge.max_tier
                assert badge.max_tier >= 1


# --- Alex: prolific badged user (5 completed stays, 3 eco-leaders) ----------


class TestAlex:
    """Alex is the 'showcase' persona — earns badges across every category."""

    def test_alex_completed_stay_stats_match_seed(self) -> None:
        shelf = compute_badge_shelf("alex")
        assert shelf.stats.completed_stays == 5
        assert shelf.stats.cities_visited == 4  # NYC, DC, Miami, Chicago
        # 4 distinct brands across his stays:
        # Westin (DC), Element (Miami), Marriott Hotels (NYC + Chicago),
        # The Ritz-Carlton (Chicago).
        assert shelf.stats.brands_visited == 4
        assert shelf.stats.eco_leader_stays == 3

    def test_alex_earns_first_tier_badges(self) -> None:
        shelf = compute_badge_shelf("alex")
        earned = _earned_ids(shelf)
        # Sustainability: Green Stay + Brand Eco Native
        assert "green_stay" in earned
        assert "brand_eco_native" in earned
        # Loyalty: Welcome Aboard + Frequent Stayer (5 stays = Bronze)
        assert "welcome_aboard" in earned
        assert "frequent_stayer" in earned
        # Explorer: all three at Bronze+
        assert "globetrotter" in earned
        assert "brand_sampler" in earned
        assert "property_pioneer" in earned
        # Lifestyle: Concierge of One (he has active stays)
        assert "concierge_of_one" in earned

    def test_alex_eco_warrior_unlocks_at_three_eco_stays(self) -> None:
        eco_warrior = _badge_by_id(compute_badge_shelf("alex"), "eco_warrior")
        # 3 eco-leader stays meets PRD's Bronze threshold (3).
        assert eco_warrior.earned is True
        assert eco_warrior.current_tier == 1
        assert eco_warrior.current_tier_label == "Bronze"
        assert eco_warrior.next_tier_label == "Silver"

    def test_alex_frequent_stayer_at_bronze(self) -> None:
        fs = _badge_by_id(compute_badge_shelf("alex"), "frequent_stayer")
        assert fs.current_tier == 1
        assert fs.current_tier_label == "Bronze"
        assert fs.progress_value == 5
        assert fs.next_tier_threshold == 10  # next tier is Silver @ 10

    def test_alex_property_pioneer_when_all_properties_visited(self) -> None:
        pp = _badge_by_id(compute_badge_shelf("alex"), "property_pioneer")
        # Demo has 5 hotels and Alex has stayed at all 5.
        assert pp.earned is True
        assert pp.hint.startswith("Hall of Fame")

    def test_alex_qualifying_stays_eco_threshold(self) -> None:
        shelf = compute_badge_shelf("alex")
        for stay in shelf.qualifying_stays:
            assert stay["eco_score"] >= 8.0
            assert stay["hotel_name"]
            assert "stay_id" in stay
            assert "check_in" in stay


# --- Jordan: pet-stay lifestyle persona -------------------------------------


class TestJordan:
    """Jordan demonstrates the lifestyle category — pet booking, brief."""

    def test_jordan_earns_pet_parent_and_concierge(self) -> None:
        earned = _earned_ids(compute_badge_shelf("jordan"))
        assert "pet_parent" in earned
        assert "concierge_of_one" in earned

    def test_jordan_does_not_earn_eco_warrior_yet(self) -> None:
        ew = _badge_by_id(compute_badge_shelf("jordan"), "eco_warrior")
        # 1 eco-leader stay < 3 needed for Bronze.
        assert ew.earned is False
        assert ew.next_tier_threshold == 3
        assert "eco-leader stays" in ew.hint

    def test_jordan_globetrotter_locked_with_progress_hint(self) -> None:
        g = _badge_by_id(compute_badge_shelf("jordan"), "globetrotter")
        assert g.earned is False
        assert g.progress_value == 1
        assert "cities to unlock" in g.hint


# --- Sam: brand-new member, mostly locked shelf -----------------------------


class TestSam:
    """Sam shows the 'new user' state — locked tiles with progress hints."""

    def test_sam_has_zero_completed_stays(self) -> None:
        shelf = compute_badge_shelf("sam")
        assert shelf.stats.completed_stays == 0
        assert shelf.stats.eco_leader_stays == 0

    def test_sam_welcome_aboard_locked_with_hint(self) -> None:
        wa = _badge_by_id(compute_badge_shelf("sam"), "welcome_aboard")
        assert wa.earned is False
        assert wa.hint == "Complete your first stay to unlock"

    def test_sam_no_pet_parent_badge(self) -> None:
        pp = _badge_by_id(compute_badge_shelf("sam"), "pet_parent")
        assert pp.earned is False

    def test_sam_can_still_earn_concierge_of_one_via_upcoming_stay(self) -> None:
        # Sam has an upcoming stay in the seed, which is enough to flip
        # Concierge of One on as a "the feature is live for you" moment.
        c = _badge_by_id(compute_badge_shelf("sam"), "concierge_of_one")
        assert c.earned is True


# --- Tier math --------------------------------------------------------------


class TestTierProgression:
    """Verify the counter-tier helper picks the right rung."""

    def test_below_first_threshold_is_locked(self) -> None:
        gt = _badge_by_id(compute_badge_shelf("sam"), "globetrotter")
        assert gt.current_tier == 0
        assert gt.earned is False

    def test_at_threshold_unlocks_tier(self) -> None:
        # Alex visited exactly 4 cities → Globetrotter Bronze (tier 1) earned,
        # Silver (5 cities) is next.
        gt = _badge_by_id(compute_badge_shelf("alex"), "globetrotter")
        assert gt.current_tier == 1
        assert gt.next_tier_threshold == 5
        assert gt.next_tier_label == "Silver"

    def test_max_tier_has_no_next_threshold(self) -> None:
        # Synthetic: pick a single-shot badge that's earned.
        wa = _badge_by_id(compute_badge_shelf("alex"), "welcome_aboard")
        assert wa.current_tier == wa.max_tier == 1
        assert wa.next_tier_threshold is None
