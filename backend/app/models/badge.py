"""Badge shelf schemas.

Badges are derived from a guest's completed stays + reservations. Each
badge belongs to a `category` (sustainability / loyalty / explorer /
lifestyle) and may have multiple `tiers` (e.g. Frequent Stayer 5 → 100).
The UI shows ONE tile per badge that visually advances, with a progress
bar to the next tier.

See `app/services/badge_service.py` for the rules.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

BadgeCategory = Literal["sustainability", "loyalty", "explorer", "lifestyle"]


class BadgeTierStep(BaseModel):
    """One rung on a multi-tier badge ladder (e.g. 5 / 10 / 25 stays)."""

    threshold: int = Field(ge=0, description="Numeric threshold to reach this tier")
    label: str = Field(description="Display label for this tier (e.g. 'Bronze', '10 Stays')")


class BadgeItem(BaseModel):
    """One badge on the guest's shelf — earned, in-progress, or locked.

    For tiered badges, `current_tier` reflects the highest tier earned
    so far (0 if not earned), and `progress` carries the metric we're
    counting toward the next tier.
    """

    id: str = Field(description="Stable id, e.g. 'frequent_stayer'")
    label: str = Field(description="Display name (e.g. 'Frequent Stayer')")
    category: BadgeCategory
    description: str = Field(description="One-line story shown on the tile")
    image_id: str = Field(
        description="Stable image asset id; frontend resolves to /badges/{image_id}.png",
    )
    earned: bool = Field(description="True once the lowest tier is reached")
    current_tier: int = Field(
        ge=0,
        description="Highest tier reached (0 = not earned, 1+ = earned). Single-tier badges max at 1.",
    )
    max_tier: int = Field(ge=1, description="Total tiers available on this badge")
    current_tier_label: str | None = Field(
        default=None, description="Display label for the current tier (e.g. 'Silver')"
    )
    progress_value: int = Field(
        ge=0, description="Current count of the metric this badge tracks"
    )
    next_tier_threshold: int | None = Field(
        default=None,
        description="Threshold to reach the next tier; None if at max",
    )
    next_tier_label: str | None = Field(
        default=None, description="Display label of the next unlock"
    )
    hint: str = Field(
        description="Short hint for the user — what to do next (e.g. '2 more stays to Silver')",
    )


class BadgeCategorySection(BaseModel):
    """A grouped section of badges on the shelf."""

    id: BadgeCategory
    label: str = Field(description="Section heading shown above the badges")
    description: str = Field(description="One-line section subtitle")
    badges: list[BadgeItem]


class BadgeShelfStats(BaseModel):
    """Top-line counters shown above the shelf."""

    total_earned: int = Field(ge=0, description="Number of badges with earned=True")
    total_available: int = Field(ge=0, description="Total badges in the system")
    completed_stays: int = Field(ge=0)
    cities_visited: int = Field(ge=0)
    brands_visited: int = Field(ge=0)
    eco_leader_stays: int = Field(ge=0, description="Stays at hotels rated >= 8")


class BadgeShelfResponse(BaseModel):
    """Full badge shelf payload for the profile page."""

    guest_id: str
    stats: BadgeShelfStats
    sections: list[BadgeCategorySection]
    qualifying_stays: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Eco-leader stays used for the 'how was this earned?' breakdown",
    )
