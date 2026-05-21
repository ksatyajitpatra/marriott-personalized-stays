"""Eco rating schemas — see PRD Section 5.1.

Six weighted sub-scores combine into a single 0–10 score that drives
the colored ring, the Green Points multiplier, and the badge system.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EcoSubScore(BaseModel):
    """One component of the composite eco score."""

    key: str = Field(description="Stable id, e.g. 'energy', 'water'")
    label: str = Field(description="Human-readable name shown in the UI")
    score: float = Field(ge=0, le=10, description="Normalized 0–10 score")
    raw_value: str = Field(description="Original measurement, e.g. '38.2 kWh/room-night'")
    weight_pct: int = Field(ge=0, le=100, description="Contribution weight, 0–100")
    data_source: str = Field(description="Production system this would come from")


class EcoScoreResponse(BaseModel):
    """Full eco breakdown returned by `/hotels/{id}/eco-score`."""

    hotel_id: str
    total_score: float = Field(ge=0, le=10)
    color: str = Field(description="ring color: 'green' | 'yellow' | 'red'")
    green_points_bonus: int = Field(description="Bonus Bonvoy Green Points")
    green_points_multiplier: float = Field(description="Earnings multiplier (1.0 / 1.1 / 1.3)")
    sub_scores: list[EcoSubScore]
    data_as_of: str = Field(description="ISO date the upstream data is from")
    data_source: str = Field(description="Top-level source label (e.g. 'MESH')")
