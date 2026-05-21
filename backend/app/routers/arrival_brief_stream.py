"""SSE endpoint for the Live Concierge Agent.

Exposes ``GET /arrival-brief/{stay_id}/stream`` which streams
:class:`AgentEvent` envelopes as ``text/event-stream``. The original
non-streaming ``GET /arrival-brief/{stay_id}`` endpoint is untouched —
this router is purely additive.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.config import settings
from app.models.concierge import AgentEvent
from app.services.arrival_brief_service import (
    _find_hotel,  # noqa: F401 — reused private helpers
    _find_stay,
)
from app.services.concierge_agent import run_concierge_agent
from app.services.guest_preference_service import get_guest_record
from app.services.reservation_service import get_reservation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/arrival-brief", tags=["arrival-brief"])


def _format_sse(event: AgentEvent) -> str:
    """Render an AgentEvent as a single SSE message frame."""
    body = json.dumps(event.model_dump(), ensure_ascii=False)
    # The ``event:`` field lets clients filter by type; we still ship the
    # full envelope in ``data:`` for clients that just want JSON.
    return f"event: {event.type}\ndata: {body}\n\n"


@router.get("/{stay_id}/stream")
async def stream_arrival_brief(
    stay_id: str,
    live_search: bool = Query(
        default=False,
        description=(
            "Opt-in flag for live web search. Falls back to "
            "live_search_enabled_default when omitted."
        ),
    ),
) -> StreamingResponse:
    """Stream the live concierge agent's tool-call trace + final brief.

    Args:
        stay_id: The stay to generate a brief for.
        live_search: If True, the agent's web-search tools attempt the live
            Tavily call. If False (or missing TAVILY_API_KEY), all tools
            return seed-derived mock data — the trace pane shows ``mock``
            badges so judges can see the difference.

    Returns:
        A ``StreamingResponse`` of ``text/event-stream`` carrying
        :class:`AgentEvent` JSON payloads.
    """
    stay = _find_stay(stay_id)
    hotel = _find_hotel(stay["hotel_id"])
    guest = get_guest_record(stay["guest_id"])
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
        )

    # Reservation existence is best-effort — pet-on-stay info enriches the
    # plan but a missing reservation should never block the demo.
    has_pet_on_stay = False
    try:
        reservation = get_reservation(stay_id)
        if reservation:
            has_pet_on_stay = bool(getattr(reservation, "has_pet", False))
    except Exception:  # noqa: BLE001
        logger.debug("No reservation for stay %s — assuming no pet", stay_id)

    effective_live_search = live_search or settings.live_search_enabled_default

    logger.info(
        "[agent] stream START stay=%s hotel=%s live_search=%s tavily_key=%s use_mock_llm=%s",
        stay_id,
        hotel.get("name"),
        effective_live_search,
        bool(settings.tavily_api_key),
        settings.use_mock_llm,
    )

    async def event_source() -> AsyncIterator[str]:
        try:
            async for event in run_concierge_agent(
                stay=stay,
                hotel=hotel,
                guest=guest,
                has_pet_on_stay=has_pet_on_stay,
                live_search_enabled=effective_live_search,
            ):
                logger.info(
                    "[agent] event=%s payload_keys=%s",
                    event.type,
                    list(event.payload.keys()),
                )
                yield _format_sse(event)
        except Exception as exc:  # noqa: BLE001 — never crash the SSE
            logger.exception("Concierge agent crashed for stay %s", stay_id)
            err = AgentEvent(
                type="agent_error",
                timestamp="",
                payload={"error": str(exc)},
            )
            yield _format_sse(err)
        finally:
            logger.info("[agent] stream END stay=%s", stay_id)

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
