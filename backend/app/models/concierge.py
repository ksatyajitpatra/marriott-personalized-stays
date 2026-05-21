"""Pydantic models for the Live Concierge Agent (PRD Section 5.2.x).

These models describe the wire format used by the agent's streaming SSE
endpoint and the affiliate / commission ledger. They live in their own
module so the routers, services, and tests can share them without
introducing circular imports.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# --- Affiliate / commission ------------------------------------------------


class AffiliateOffer(BaseModel):
    """A "Book via Marriott" deeplink wrapped around a 3rd-party result.

    Each tool result that we surface in the brief is decorated with one of
    these. The ``deeplink`` is a tracked URL the guest can click; the
    ``est_commission_usd`` and ``bonvoy_bonus_points`` fields drive the
    ledger panel that makes the business model legible to judges.
    """

    partner: str = Field(
        ...,
        description="Display name, e.g. 'OpenTable', 'Viator', 'Rover', 'direct'.",
    )
    partner_domain: str = Field(
        ...,
        description="Lower-cased domain we matched against the rate table.",
    )
    deeplink: str = Field(..., description="Tracked URL with utm_* parameters.")
    est_commission_usd: float = Field(
        ..., description="Static rate-table estimate, USD."
    )
    bonvoy_bonus_points: int = Field(
        ..., description="Bonus Bonvoy points returned to the guest if booked."
    )
    disclosure: str = Field(
        default=(
            "Marriott earns an affiliate commission if you book; "
            "50% flows back to you as Bonvoy bonus points."
        )
    )


# --- Agent tool calls / events --------------------------------------------


ToolStatus = Literal["started", "ok", "error", "fallback"]


class ToolCall(BaseModel):
    """A single planned tool invocation (request side)."""

    id: str = Field(..., description="Stable id for matching with ToolResult.")
    name: str = Field(..., description="Tool name, e.g. 'search_dining'.")
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """A finished tool invocation (response side)."""

    id: str
    name: str
    status: ToolStatus
    duration_ms: int
    source: Literal["live", "mock"] = Field(
        ...,
        description="Whether the data came from a live API call or seed fallback.",
    )
    result_count: int = 0
    summary: str = Field(default="", description="Human-readable one-liner.")
    error: str | None = None


class ToolCallSummary(BaseModel):
    """Compact tool-call record returned by the non-streaming endpoint.

    The streaming endpoint emits richer ``AgentEvent``s; this is the
    flattened version we attach to ``ArrivalBriefResponse`` so clients that
    don't subscribe to the SSE feed can still see what happened.
    """

    name: str
    status: ToolStatus
    source: Literal["live", "mock"]
    duration_ms: int
    result_count: int
    summary: str = ""


# --- Streamed agent events -------------------------------------------------


class AgentEvent(BaseModel):
    """Envelope for everything the agent emits over SSE.

    The frontend trace pane reads ``type`` to decide how to render the row.
    ``payload`` is intentionally loose so we can evolve event shapes without
    breaking the wire contract.
    """

    type: Literal[
        "agent_started",
        "tool_call_started",
        "tool_call_finished",
        "agent_thinking",
        "final_brief",
        "agent_finished",
        "agent_error",
    ]
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp.")
    payload: dict[str, Any] = Field(default_factory=dict)


# --- Click ledger ----------------------------------------------------------


class AffiliateClickRequest(BaseModel):
    """Body for ``POST /affiliate/click``."""

    stay_id: str
    partner: str
    partner_domain: str
    url: str
    est_commission_usd: float = 0.0
    bonvoy_bonus_points: int = 0


class AffiliateClickRecord(BaseModel):
    """Persisted (in-memory) click event."""

    stay_id: str
    partner: str
    partner_domain: str
    url: str
    est_commission_usd: float
    bonvoy_bonus_points: int
    clicked_at: str


class AffiliateLedgerResponse(BaseModel):
    """Aggregated totals for a stay — drives the bottom-of-brief summary."""

    stay_id: str
    click_count: int
    projected_commission_usd: float
    projected_bonus_points: int
    clicks: list[AffiliateClickRecord] = Field(default_factory=list)
