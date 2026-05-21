"""Arrival Brief schemas — see PRD Section 5.2.

The brief is an LLM-generated 1-pager surfaced 48 hours before check-in.
For demo speed we ship hand-curated briefs in `/data/seeds/arrival_brief_*.json`
and only call the LLM when explicitly enabled.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.concierge import AffiliateOffer, ToolCallSummary


class BriefEvent(BaseModel):
    name: str
    date: str
    type: str
    why_youll_love_it: str
    affiliate: AffiliateOffer | None = None
    source_url: str | None = None


class BriefDining(BaseModel):
    name: str
    cuisine: str
    dietary_match: str
    note: str
    affiliate: AffiliateOffer | None = None
    source_url: str | None = None


class WeatherDay(BaseModel):
    """Optional structured weather day used by the WeatherWidget."""

    date: str
    high_c: float
    low_c: float
    summary: str
    icon: str = Field(default="sun", description="One of: sun, cloud, rain, snow, partly")


class ArrivalBriefResponse(BaseModel):
    stay_id: str
    guest_id: str
    hotel: str
    city: str
    check_in: str
    check_out: str
    generated_at: str
    generated_by: str = Field(default="seed", description="'seed' | 'mock_llm' | 'litellm'")

    greeting: str
    weather_summary: str
    weather_forecast: list[WeatherDay] = Field(default_factory=list)
    packing_tips: list[str]
    events: list[BriefEvent]
    dining: list[BriefDining]
    transit: str
    property_note: str
    eco_note: str | None = None
    live_search_used: bool = Field(
        default=False,
        description="True when the agent's Tavily-backed tools returned live data.",
    )
    tool_calls: list[ToolCallSummary] = Field(
        default_factory=list,
        description="Compact record of each tool invocation made during generation.",
    )
