"""Live Concierge Agent — LiteLLM tool-calling loop with SSE streaming.

This module is the heart of the "Live Concierge" upgrade described in
``APP_PRD.MD`` Section 5.2.x. It exposes a single entry point,
:func:`run_concierge_agent`, which is an async generator that yields
:class:`AgentEvent` envelopes. The streaming router fans those events out
to the browser as Server-Sent Events.

Design notes:
    * Tools are plain async Python functions registered in ``_TOOLS``. Each
      one returns a ``(payload, source)`` tuple where ``source`` is
      ``"live"`` (came from a real upstream call) or ``"mock"`` (seed
      fallback).
    * In live mode we run two LiteLLM rounds:
        1. tools planning — model returns parallel ``tool_calls``
        2. composition — model gets the tool results back and produces the
           final ``ArrivalBriefResponse`` JSON
    * In mock mode (``USE_MOCK_LLM=true`` or LiteLLM unavailable) we run
      every relevant tool deterministically based on the guest's
      preferences and template-fill the brief. The trace pane still shows
      the same UI rows — judges can flip the env var to see live mode.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Awaitable, Callable

from app.data.loader import get_seed
from app.models.concierge import AgentEvent, ToolCallSummary
from app.services.affiliate_service import build_affiliate_offer
from app.services.llm_service import (
    LLMConfigError,
    LLMUnavailableError,
    litellm_chat_with_tools,
    parse_llm_json,
)
from app.services.tavily_service import TavilySearchOutcome, tavily_search

logger = logging.getLogger(__name__)


# --- Tool implementations --------------------------------------------------
#
# Each tool returns ``(payload_dict, source_tag)``. The payload is what we
# feed back to the LLM in round 2; the source tag drives the live/mock
# badges in the trace pane. Tools must be cheap, idempotent, and safe to
# run in parallel.


async def _tool_get_weather(
    *,
    city: str,
    check_in: str,
    check_out: str,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    from app.config import settings
    from app.services.weather_service import _live_forecast, _mock_forecast

    forecast = None
    source = "mock"
    if settings.openweather_api_key:
        forecast = await _live_forecast(city, check_in, check_out)
        if forecast:
            source = "live"
    if not forecast:
        forecast = _mock_forecast(city, check_in, check_out)
    payload = {
        "city": city,
        "days": [d.model_dump() for d in forecast],
    }
    return payload, source


async def _tool_search_events(
    *,
    city: str,
    check_in: str,
    check_out: str,
    interests: list[str] | None = None,
    force_mock: bool = False,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    interest_str = ", ".join(interests or []) or "any"
    query = (
        f"Things to do, concerts, and events in {city} between "
        f"{check_in} and {check_out}. Interests: {interest_str}."
    )
    out: TavilySearchOutcome = await tavily_search(
        query=query,
        category="events",
        city=city,
        interests=interests or [],
        force_mock=force_mock,
    )
    return _outcome_payload(out), out.source


async def _tool_search_dining(
    *,
    city: str,
    dietary: list[str] | None = None,
    force_mock: bool = False,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    diet_str = ", ".join(dietary or []) or "no specific"
    query = (
        f"Top-rated {diet_str} restaurants near downtown {city} with reservations."
    )
    out = await tavily_search(
        query=query,
        category="dining",
        city=city,
        dietary=dietary or [],
        force_mock=force_mock,
    )
    return _outcome_payload(out), out.source


async def _tool_search_pet_services(
    *,
    city: str,
    pet_species: str | None = None,
    force_mock: bool = False,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    species = pet_species or "dog"
    query = f"Trusted {species} walkers, sitters, and groomers in {city} with reviews."
    out = await tavily_search(
        query=query,
        category="pet_services",
        city=city,
        force_mock=force_mock,
    )
    return _outcome_payload(out), out.source


async def _tool_search_activities(
    *,
    city: str,
    interests: list[str] | None = None,
    force_mock: bool = False,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    interest_str = ", ".join(interests or []) or "popular"
    query = f"{interest_str} tours and experiences in {city}."
    out = await tavily_search(
        query=query,
        category="activities",
        city=city,
        interests=interests or [],
        force_mock=force_mock,
    )
    return _outcome_payload(out), out.source


async def _tool_get_partner_catalog(
    *,
    hotel_id: str,
    **_: Any,
) -> tuple[dict[str, Any], str]:
    """Return Marriott-partner businesses near the hotel from seed data."""
    catalog: list[dict[str, Any]] = []
    for seed in ("partners_nyc", "partners_dc", "partners_chicago"):
        try:
            for p in get_seed(seed):
                if p.get("hotel_id") == hotel_id and p.get("is_marriott_partner"):
                    catalog.append(
                        {
                            "name": p.get("name"),
                            "category": p.get("category"),
                            "note": p.get("note"),
                            "rating": p.get("rating"),
                            "address": p.get("address"),
                        }
                    )
        except KeyError:
            continue
    return {"partners": catalog}, "mock"


def _outcome_payload(outcome: TavilySearchOutcome) -> dict[str, Any]:
    """Serialize a TavilySearchOutcome into a JSON-friendly dict for the LLM."""
    return {
        "query": outcome.query,
        "source": outcome.source,
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "source_domain": r.source_domain,
            }
            for r in outcome.results
        ],
    }


_TOOLS: dict[str, Callable[..., Awaitable[tuple[dict[str, Any], str]]]] = {
    "get_weather": _tool_get_weather,
    "search_events": _tool_search_events,
    "search_dining": _tool_search_dining,
    "search_pet_services": _tool_search_pet_services,
    "search_activities": _tool_search_activities,
    "get_partner_catalog": _tool_get_partner_catalog,
}


# OpenAI-style tool descriptors fed into LiteLLM.
_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the daily forecast for the city during the stay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                    "check_out": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["city", "check_in", "check_out"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": (
                "Search the live web for events / concerts / activities "
                "happening in the city during the stay window."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "check_in": {"type": "string"},
                    "check_out": {"type": "string"},
                    "interests": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["city", "check_in", "check_out"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_dining",
            "description": (
                "Search the live web for restaurants near the hotel that "
                "match the guest's dietary preferences."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "dietary": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_pet_services",
            "description": (
                "Search the live web for trusted pet services (walkers, "
                "sitters, groomers) near the hotel. Only call when the "
                "guest is bringing a pet on this stay."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "pet_species": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_activities",
            "description": (
                "Search the live web for tours and bookable activities "
                "matching the guest's interests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "interests": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_partner_catalog",
            "description": (
                "Return Marriott-partner businesses near the hotel from "
                "the internal partner catalog. Use to ground recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {"hotel_id": {"type": "string"}},
                "required": ["hotel_id"],
            },
        },
    },
]


_AGENT_HARD_TIMEOUT_S = 12.0
_TOOL_TIMEOUT_S = 8.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Agent runner ----------------------------------------------------------


async def _run_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    force_mock: bool,
) -> tuple[str, dict[str, Any], str, int]:
    """Execute a single tool with a hard timeout.

    Returns ``(status, payload, source, duration_ms)``. ``status`` is one
    of ``ok`` / ``error`` / ``fallback``.
    """
    fn = _TOOLS.get(name)
    if fn is None:
        return "error", {"error": f"unknown tool {name!r}"}, "mock", 0

    started = time.perf_counter()
    try:
        payload, source = await asyncio.wait_for(
            fn(force_mock=force_mock, **arguments),
            timeout=_TOOL_TIMEOUT_S,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return "ok", payload, source, duration_ms
    except asyncio.TimeoutError:
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.warning("Tool %s timed out after %dms", name, duration_ms)
        return "error", {"error": "timeout"}, "mock", duration_ms
    except Exception as exc:  # noqa: BLE001 — agent must never crash on a tool
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.exception("Tool %s raised", name)
        return "error", {"error": str(exc)}, "mock", duration_ms


def _summarize_payload(name: str, payload: dict[str, Any]) -> tuple[int, str]:
    """Build a (result_count, summary) pair for a tool's payload."""
    if name == "get_weather":
        days = payload.get("days") or []
        return len(days), f"{len(days)}-day forecast"
    if name == "get_partner_catalog":
        partners = payload.get("partners") or []
        return len(partners), f"{len(partners)} Marriott partners"
    results = payload.get("results") or []
    return len(results), f"{len(results)} results"


def _plan_default_tool_calls(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    has_pet_on_stay: bool,
) -> list[dict[str, Any]]:
    """Deterministic tool plan used in mock mode (no LLM call).

    Mirrors what a well-prompted model would do given the same inputs:
    always pull weather, run dining/events when those prefs are set, and
    only run pet-services when the guest is actually bringing a pet.
    """
    prefs = guest.get("preferences", {}) or {}
    dietary: list[str] = prefs.get("dietary") or []
    interests: list[str] = prefs.get("interests") or []
    city = hotel.get("city", "")
    plan: list[dict[str, Any]] = [
        {
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "name": "get_weather",
            "arguments": {
                "city": city,
                "check_in": stay["check_in"],
                "check_out": stay["check_out"],
            },
        }
    ]
    if interests:
        plan.append(
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "name": "search_events",
                "arguments": {
                    "city": city,
                    "check_in": stay["check_in"],
                    "check_out": stay["check_out"],
                    "interests": interests,
                },
            }
        )
    if dietary:
        plan.append(
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "name": "search_dining",
                "arguments": {"city": city, "dietary": dietary},
            }
        )
    if has_pet_on_stay:
        pets = guest.get("pets") or []
        species = pets[0].get("species") if pets else "dog"
        plan.append(
            {
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "name": "search_pet_services",
                "arguments": {"city": city, "pet_species": species},
            }
        )
    return plan


def _compose_brief_from_tools(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    tool_outputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Template-fill an arrival brief from raw tool outputs (mock mode).

    The output shape matches what round 2 of the live agent returns so the
    streaming router can treat both code paths identically.
    """
    first_name = (guest.get("name") or "Guest").split()[0]
    interests = (guest.get("preferences") or {}).get("interests") or []
    dietary = (guest.get("preferences") or {}).get("dietary") or []

    weather_summary = "Forecast available below."
    weather = tool_outputs.get("get_weather", {})
    days = weather.get("days") or []
    if days:
        first = days[0]
        weather_summary = (
            f"Expect highs around {int(first.get('high_c', 0))}°C in "
            f"{hotel.get('city', '')} during your stay — {first.get('summary', '').lower()}."
        )

    events: list[dict[str, Any]] = []
    for r in (tool_outputs.get("search_events", {}).get("results") or [])[:3]:
        events.append(
            {
                "name": r.get("title", "Local event"),
                "date": stay["check_in"],
                "type": (interests[0] if interests else "local"),
                "why_youll_love_it": r.get("snippet", "")[:220],
                "source_url": r.get("url"),
            }
        )

    dining: list[dict[str, Any]] = []
    for r in (tool_outputs.get("search_dining", {}).get("results") or [])[:3]:
        dining.append(
            {
                "name": r.get("title", "Restaurant"),
                "cuisine": "local",
                "dietary_match": (
                    f"Matches your {', '.join(dietary)} preferences"
                    if dietary
                    else "Highly rated near your hotel"
                ),
                "note": r.get("snippet", "")[:220],
                "source_url": r.get("url"),
            }
        )

    return {
        "greeting": (
            f"Welcome, {first_name} — your live concierge has assembled the "
            f"latest picks for {hotel.get('name', 'your stay')}."
        ),
        "weather_summary": weather_summary,
        "packing_tips": [
            "Light layers for variable conditions",
            "Comfortable walking shoes for exploring",
            "Reusable water bottle — refill stations on property",
        ],
        "events": events,
        "dining": dining,
        "transit": (
            f"Your hotel is at {hotel.get('address', '')}. Concierge can advise on "
            "the fastest route from your arrival point."
        ),
        "property_note": (
            "Your stay includes mobile check-in and digital key — skip the front desk "
            "if you'd like."
        ),
    }


def _enrich_with_affiliates(
    brief: dict[str, Any],
    *,
    stay_id: str,
    tool_outputs: dict[str, dict[str, Any]],
) -> int:
    """Mutate ``brief`` in place to attach an AffiliateOffer to each item.

    Returns the count of items that got a non-direct affiliate link.
    """
    affiliate_count = 0

    def _url_for(item: dict[str, Any], category: str) -> str | None:
        if item.get("source_url"):
            return item["source_url"]
        # fall back to first matching tool result by name
        results = (tool_outputs.get(f"search_{category}", {}) or {}).get("results") or []
        for r in results:
            if r.get("title") == item.get("name"):
                return r.get("url")
        return results[0].get("url") if results else None

    for event in brief.get("events", []) or []:
        url = _url_for(event, "events")
        if url:
            offer = build_affiliate_offer(url, stay_id=stay_id, category="events")
            event["affiliate"] = offer.model_dump()
            event["source_url"] = url
            if offer.partner_domain != "direct":
                affiliate_count += 1
    for d in brief.get("dining", []) or []:
        url = _url_for(d, "dining")
        if url:
            offer = build_affiliate_offer(url, stay_id=stay_id, category="dining")
            d["affiliate"] = offer.model_dump()
            d["source_url"] = url
            if offer.partner_domain != "direct":
                affiliate_count += 1
    return affiliate_count


def get_tool_schemas() -> list[dict[str, Any]]:
    """Public accessor for the OpenAI tool schemas (used in tests)."""
    return list(_TOOL_SCHEMAS)


async def run_concierge_agent(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    has_pet_on_stay: bool,
    live_search_enabled: bool,
) -> AsyncIterator[AgentEvent]:
    """Stream a concierge agent run as :class:`AgentEvent` envelopes.

    The generator always emits an ``agent_started`` and an ``agent_finished``
    bookend, so the frontend can reliably toggle its loading state. Every
    ``tool_call_started`` is paired with a ``tool_call_finished`` carrying
    the same ``call_id``.
    """
    from app.config import settings

    yield AgentEvent(
        type="agent_started",
        timestamp=_now_iso(),
        payload={
            "stay_id": stay["id"],
            "hotel": hotel.get("name"),
            "live_search_enabled": live_search_enabled,
            "model": settings.litellm_model,
            "use_mock_llm": settings.use_mock_llm,
        },
    )

    deadline = time.perf_counter() + _AGENT_HARD_TIMEOUT_S
    force_mock_tools = (not live_search_enabled) or (not settings.tavily_api_key)

    # --- Round 1: planning ------------------------------------------------
    plan, plan_source = await _plan_tool_calls(
        stay=stay,
        hotel=hotel,
        guest=guest,
        has_pet_on_stay=has_pet_on_stay,
    )
    yield AgentEvent(
        type="agent_thinking",
        timestamp=_now_iso(),
        payload={
            "stage": "plan",
            "plan_source": plan_source,
            "tools_planned": [t["name"] for t in plan],
        },
    )

    # --- Execute tools in parallel --------------------------------------
    tool_outputs: dict[str, dict[str, Any]] = {}
    summaries: list[ToolCallSummary] = []
    started_events: list[AgentEvent] = []

    for call in plan:
        started_events.append(
            AgentEvent(
                type="tool_call_started",
                timestamp=_now_iso(),
                payload={
                    "call_id": call["id"],
                    "name": call["name"],
                    "arguments": call.get("arguments", {}),
                },
            )
        )
    for ev in started_events:
        yield ev

    async def _exec(call: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        status_, payload_, source_, duration_ms_ = await _run_tool(
            call["name"], call.get("arguments", {}), force_mock=force_mock_tools
        )
        return call, {
            "status": status_,
            "payload": payload_,
            "source": source_,
            "duration_ms": duration_ms_,
        }

    completed = await asyncio.gather(*(_exec(c) for c in plan), return_exceptions=False)
    for call, result in completed:
        result_count, summary_text = _summarize_payload(call["name"], result["payload"])
        tool_outputs[call["name"]] = result["payload"]
        summaries.append(
            ToolCallSummary(
                name=call["name"],
                status=result["status"],
                source=result["source"],
                duration_ms=result["duration_ms"],
                result_count=result_count,
                summary=summary_text,
            )
        )
        yield AgentEvent(
            type="tool_call_finished",
            timestamp=_now_iso(),
            payload={
                "call_id": call["id"],
                "name": call["name"],
                "status": result["status"],
                "source": result["source"],
                "duration_ms": result["duration_ms"],
                "result_count": result_count,
                "summary": summary_text,
            },
        )

    # --- Round 2: composition --------------------------------------------
    yield AgentEvent(
        type="agent_thinking",
        timestamp=_now_iso(),
        payload={"stage": "compose"},
    )

    brief: dict[str, Any] | None = None
    time_left = max(0.5, deadline - time.perf_counter())
    if not settings.use_mock_llm and time_left > 1.0:
        try:
            brief = await asyncio.wait_for(
                _compose_brief_via_llm(
                    stay=stay,
                    hotel=hotel,
                    guest=guest,
                    tool_outputs=tool_outputs,
                ),
                timeout=min(time_left, 8.0),
            )
        except (asyncio.TimeoutError, LLMConfigError, LLMUnavailableError) as exc:
            logger.warning("LLM composition fell back to template: %s", exc)
            brief = None

    if brief is None:
        brief = _compose_brief_from_tools(
            stay=stay, hotel=hotel, guest=guest, tool_outputs=tool_outputs
        )

    affiliate_count = _enrich_with_affiliates(
        brief, stay_id=stay["id"], tool_outputs=tool_outputs
    )
    live_search_used = any(s.source == "live" for s in summaries if s.name.startswith("search_"))

    yield AgentEvent(
        type="final_brief",
        timestamp=_now_iso(),
        payload={
            "brief": brief,
            "tool_calls": [s.model_dump() for s in summaries],
            "live_search_used": live_search_used,
            "affiliate_count": affiliate_count,
        },
    )
    yield AgentEvent(
        type="agent_finished",
        timestamp=_now_iso(),
        payload={
            "duration_ms": int((time.perf_counter() - (deadline - _AGENT_HARD_TIMEOUT_S)) * 1000),
            "tool_count": len(summaries),
            "affiliate_count": affiliate_count,
        },
    )


async def _plan_tool_calls(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    has_pet_on_stay: bool,
) -> tuple[list[dict[str, Any]], str]:
    """Round 1 — ask the model which tools to call, with a deterministic fallback.

    Returns ``(plan, source)`` where ``source`` is ``"litellm"`` or ``"deterministic"``.
    """
    from app.config import settings

    if settings.use_mock_llm:
        return (
            _plan_default_tool_calls(
                stay=stay, hotel=hotel, guest=guest, has_pet_on_stay=has_pet_on_stay
            ),
            "deterministic",
        )

    prefs = guest.get("preferences") or {}
    system = (
        "You are a Marriott Bonvoy concierge agent. Decide which tools to call "
        "based on the guest's preferences. Always call get_weather. Call "
        "search_dining only if dietary preferences are set. Call search_events "
        "and search_activities only if interests are set. Call search_pet_services "
        "ONLY if the guest is bringing a pet on this stay. Issue all tool calls in "
        "parallel in a single response — do not return any user-facing text yet."
    )
    user = json.dumps(
        {
            "stay": {"check_in": stay["check_in"], "check_out": stay["check_out"]},
            "hotel": {"id": hotel["id"], "city": hotel.get("city")},
            "guest_preferences": {
                "dietary": prefs.get("dietary") or [],
                "interests": prefs.get("interests") or [],
            },
            "has_pet_on_stay": has_pet_on_stay,
            "pet_species": (guest.get("pets") or [{}])[0].get("species") if guest.get("pets") else None,
        }
    )

    try:
        message = await litellm_chat_with_tools(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            tools=_TOOL_SCHEMAS,
            max_tokens=600,
        )
    except (LLMConfigError, LLMUnavailableError) as exc:
        logger.warning("Tool-planning LLM call failed, using deterministic plan: %s", exc)
        return (
            _plan_default_tool_calls(
                stay=stay, hotel=hotel, guest=guest, has_pet_on_stay=has_pet_on_stay
            ),
            "deterministic",
        )

    tool_calls = message.get("tool_calls") or []
    plan: list[dict[str, Any]] = []
    for tc in tool_calls:
        fn = tc.get("function") or {}
        name = fn.get("name")
        if name not in _TOOLS:
            continue
        try:
            args = json.loads(fn.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        plan.append({"id": tc.get("id") or f"call_{uuid.uuid4().hex[:8]}", "name": name, "arguments": args})

    if not plan:
        return (
            _plan_default_tool_calls(
                stay=stay, hotel=hotel, guest=guest, has_pet_on_stay=has_pet_on_stay
            ),
            "deterministic",
        )
    return plan, "litellm"


async def _compose_brief_via_llm(
    *,
    stay: dict[str, Any],
    hotel: dict[str, Any],
    guest: dict[str, Any],
    tool_outputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Round 2 — feed tool results back and ask for the final brief JSON."""
    from app.services.llm_service import litellm_chat

    prefs = guest.get("preferences") or {}
    system = (
        "You are a warm, knowledgeable Marriott concierge composing an arrival "
        "brief. You MUST ground every event/dining pick in the tool results "
        "provided — use the result's title verbatim. Do not invent new venues. "
        "Output strict JSON only."
    )
    user = (
        f"Guest first name: {(guest.get('name') or 'Guest').split()[0]}\n"
        f"Hotel: {hotel.get('name')} ({hotel.get('city')})\n"
        f"Stay: {stay['check_in']} to {stay['check_out']}\n"
        f"Dietary: {', '.join(prefs.get('dietary') or []) or 'none'}\n"
        f"Interests: {', '.join(prefs.get('interests') or []) or 'none'}\n\n"
        f"Tool results:\n{json.dumps(tool_outputs, indent=2)[:6000]}\n\n"
        "Return JSON with keys: greeting (1 warm sentence), weather_summary "
        "(<=40 words), packing_tips (3 strings), events (up to 3 objects with "
        "name, date YYYY-MM-DD within stay, type, why_youll_love_it <=35 words, "
        "source_url copied from the matching tool result), dining (up to 3 "
        "objects with name, cuisine, dietary_match, note <=30 words, "
        "source_url copied from the matching tool result), transit (<=60 "
        "words), property_note (<=40 words)."
    )

    raw = await litellm_chat(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=1400,
        response_format={"type": "json_object"},
    )
    return parse_llm_json(raw)
