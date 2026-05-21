"""Arrival Brief endpoint (PRD Section 5.2)."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.arrival_brief import ArrivalBriefResponse
from app.services.arrival_brief_service import get_arrival_brief

router = APIRouter(prefix="/arrival-brief", tags=["arrival-brief"])


@router.get("/{stay_id}", response_model=ArrivalBriefResponse)
async def fetch_arrival_brief(stay_id: str) -> ArrivalBriefResponse:
    """Return the personalized pre-stay brief for a given reservation.

    The endpoint is intentionally unauthenticated for the demo so the brief
    can be opened from a deep-linked email (which would carry its own token
    in production). Owner enforcement can be added later via `Depends(require_guest)`.
    """
    return await get_arrival_brief(stay_id)
