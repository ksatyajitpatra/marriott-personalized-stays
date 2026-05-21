"""Pet service recommendation schemas — LiteLLM-curated picks for a stay."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PetServiceRecommendationItem(BaseModel):
    """A single recommended bookable pet service for this reservation."""

    partner_id: str
    partner_name: str
    category: str
    service_model: str
    distance_miles: float
    rating: float
    bookable: bool = True
    mobile_service_note: str | None = None
    rationale: str
    suggested_time: str | None = Field(
        default=None,
        description="Human-friendly time window, e.g. '10:00 AM day after arrival'",
    )
    priority: int = Field(ge=1, description="1 = top recommendation")


class PetServiceRecommendationsResponse(BaseModel):
    """LLM-ranked pet services for a pet-inclusive reservation."""

    reservation_id: str
    generated_at: str
    generated_by: str = Field(description="'mock_llm' | 'litellm'")
    radius_miles: float
    summary: str
    recommendations: list[PetServiceRecommendationItem] = Field(default_factory=list)
