"""Tavily web-search client used by the Live Concierge Agent.

The Tavily Search API (https://docs.tavily.com) is a single-endpoint
HTTPS service that returns LLM-friendly web results. We wrap it in a
minimal async client and provide a deterministic seed-derived fallback so
the demo runs end-to-end without an API key.

Public surface:
    - :class:`TavilyResult` — normalized result row.
    - :func:`tavily_search` — high-level async search that handles config,
      timeouts, and mock fallback. Returns a list of ``TavilyResult``
      plus a ``source`` tag (``"live"`` or ``"mock"``) describing where
      the data came from.

Privacy note (PRD § 12): we only forward ``city``, ``query``, and the
guest's ``dietary``/``interest`` tags to Tavily. No name, email, or
loyalty number is ever sent.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal

import httpx

from app.config import settings
from app.data.loader import get_seed, has_seed
from app.models.preferences import CITY_RESTAURANT_KEYS

logger = logging.getLogger(__name__)

_TAVILY_URL = "https://api.tavily.com/search"

SearchSource = Literal["live", "mock"]


@dataclass(slots=True)
class TavilyResult:
    """Normalized representation of a single search result."""

    title: str
    url: str
    snippet: str
    source_domain: str
    published_date: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TavilySearchOutcome:
    """Container holding a list of results and where they came from."""

    results: list[TavilyResult]
    source: SearchSource
    query: str


# --- Live client -----------------------------------------------------------


def _domain_of(url: str) -> str:
    """Extract a lowercase host from a URL without pulling in urllib."""
    if "://" in url:
        url = url.split("://", 1)[1]
    return url.split("/", 1)[0].lower().lstrip("www.")


async def _live_search(
    query: str,
    *,
    max_results: int,
    include_domains: list[str] | None,
) -> list[TavilyResult] | None:
    """POST to the Tavily ``/search`` endpoint; ``None`` on any failure."""
    if not settings.tavily_api_key:
        logger.info("[tavily] skip live (no TAVILY_API_KEY) query=%r", query)
        return None

    payload: dict[str, Any] = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": False,
        "include_raw_content": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains

    logger.info(
        "[tavily] POST %s query=%r max_results=%d domains=%s",
        _TAVILY_URL,
        query,
        max_results,
        include_domains or "any",
    )
    started = time.perf_counter()
    try:
        # ``verify=False`` matches the LiteLLM client — some macOS Python
        # builds reject the CloudFront / Tavily cert chain due to a
        # self-signed corporate root in the keychain.
        async with httpx.AsyncClient(
            timeout=settings.tavily_timeout_seconds, verify=False
        ) as client:
            resp = await client.post(_TAVILY_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.warning(
            "[tavily] FAIL query=%r duration=%dms err=%s",
            query,
            duration_ms,
            exc,
        )
        return None

    duration_ms = int((time.perf_counter() - started) * 1000)
    out: list[TavilyResult] = []
    for item in data.get("results", []):
        url = item.get("url") or ""
        out.append(
            TavilyResult(
                title=item.get("title") or url or "Untitled",
                url=url,
                snippet=item.get("content") or "",
                source_domain=_domain_of(url),
                published_date=item.get("published_date"),
                raw=item,
            )
        )
    logger.info(
        "[tavily] OK query=%r duration=%dms results=%d top=%s",
        query,
        duration_ms,
        len(out),
        out[0].source_domain if out else "-",
    )
    return out


# --- Mock fallback (seed-derived) -----------------------------------------


_MOCK_DOMAIN_BY_CATEGORY: dict[str, str] = {
    "events": "ticketmaster.com",
    "dining": "opentable.com",
    "pet_services": "rover.com",
    "activities": "viator.com",
    "default": "yelp.com",
}


def _mock_events(city: str, query: str, max_results: int) -> list[TavilyResult]:
    """Build mock event results from any hotel's seed ``community_events``."""
    out: list[TavilyResult] = []
    if not has_seed("hotels"):
        return out
    for hotel in get_seed("hotels"):
        if hotel.get("city", "").lower() != city.lower():
            continue
        for event in hotel.get("community_events", []):
            url = (
                f"https://www.ticketmaster.com/search?q="
                f"{event['name'].replace(' ', '+')}+{city.replace(' ', '+')}"
            )
            out.append(
                TavilyResult(
                    title=event["name"],
                    url=url,
                    snippet=(
                        f"{event.get('time', '')} at {event.get('location', '')} — "
                        f"{event.get('type', 'event')} pick (mock seed)."
                    ),
                    source_domain="ticketmaster.com",
                )
            )
    if not out:
        out.append(
            TavilyResult(
                title=f"Top events this week in {city}",
                url=f"https://www.ticketmaster.com/discover/{city.lower()}",
                snippet=(
                    f"Mock event roundup for {city}. Configure TAVILY_API_KEY "
                    "for live results."
                ),
                source_domain="ticketmaster.com",
            )
        )
    return out[:max_results]


def _mock_dining(
    city: str, dietary: list[str], max_results: int
) -> list[TavilyResult]:
    out: list[TavilyResult] = []
    key = CITY_RESTAURANT_KEYS.get(city, "")
    if has_seed("restaurants") and key:
        catalog = get_seed("restaurants").get(key, [])
        diet_set = set(dietary)
        ranked = sorted(
            catalog,
            key=lambda r: -len(diet_set & set(r.get("dietary_tags", []))),
        )
        for r in ranked[:max_results]:
            url = (
                f"https://www.opentable.com/s?term="
                f"{r['name'].replace(' ', '+')}+{city.replace(' ', '+')}"
            )
            out.append(
                TavilyResult(
                    title=r["name"],
                    url=url,
                    snippet=(
                        f"{r.get('cuisine', '')} · "
                        f"{', '.join(r.get('dietary_tags', [])) or 'no tags'} · "
                        f"{r.get('note', '')} (mock seed)"
                    ),
                    source_domain="opentable.com",
                )
            )
    if not out:
        out.append(
            TavilyResult(
                title=f"{', '.join(dietary).title() or 'Top'} dining in {city}",
                url=f"https://www.opentable.com/s?term={city.replace(' ', '+')}",
                snippet=(
                    f"Mock dining picks for {city}. "
                    "Configure TAVILY_API_KEY for live results."
                ),
                source_domain="opentable.com",
            )
        )
    return out[:max_results]


def _mock_pet_services(city: str, max_results: int) -> list[TavilyResult]:
    """Pull pet-relevant partners from any partners_* seed in the city."""
    out: list[TavilyResult] = []
    for seed in ("partners_nyc", "partners_dc", "partners_chicago"):
        if not has_seed(seed):
            continue
        for partner in get_seed(seed):
            if not partner.get("pet_relevant"):
                continue
            if city.lower() not in (partner.get("address", "")).lower():
                continue
            url = (
                f"https://www.rover.com/search?location="
                f"{city.replace(' ', '+')}&q={partner['name'].replace(' ', '+')}"
            )
            out.append(
                TavilyResult(
                    title=partner["name"],
                    url=url,
                    snippet=(
                        f"{partner.get('category', '')} · "
                        f"{partner.get('note', '')} (mock seed)"
                    ),
                    source_domain="rover.com",
                )
            )
    if not out:
        out.append(
            TavilyResult(
                title=f"Trusted dog walkers and pet services in {city}",
                url=f"https://www.rover.com/search?location={city.replace(' ', '+')}",
                snippet=(
                    f"Mock pet-services roundup for {city}. "
                    "Configure TAVILY_API_KEY for live results."
                ),
                source_domain="rover.com",
            )
        )
    return out[:max_results]


def _mock_activities(city: str, interests: list[str], max_results: int) -> list[TavilyResult]:
    out: list[TavilyResult] = []
    interest_blurb = ", ".join(interests) or "top experiences"
    out.append(
        TavilyResult(
            title=f"{interest_blurb.title()} tours in {city}",
            url=f"https://www.viator.com/{city.replace(' ', '-')}/d-",
            snippet=(
                f"Mock activity picks tied to {interest_blurb} in {city}. "
                "Configure TAVILY_API_KEY for live results."
            ),
            source_domain="viator.com",
        )
    )
    return out[:max_results]


def _mock_for_category(
    category: str,
    *,
    city: str,
    dietary: list[str],
    interests: list[str],
    max_results: int,
) -> list[TavilyResult]:
    if category == "events":
        return _mock_events(city, "", max_results)
    if category == "dining":
        return _mock_dining(city, dietary, max_results)
    if category == "pet_services":
        return _mock_pet_services(city, max_results)
    if category == "activities":
        return _mock_activities(city, interests, max_results)
    return []


# --- Public entry point ---------------------------------------------------


async def tavily_search(
    *,
    query: str,
    category: str,
    city: str,
    dietary: list[str] | None = None,
    interests: list[str] | None = None,
    include_domains: list[str] | None = None,
    max_results: int | None = None,
    force_mock: bool = False,
) -> TavilySearchOutcome:
    """Run a Tavily search with a deterministic seed-derived fallback.

    Args:
        query: The natural-language search query.
        category: One of ``events``/``dining``/``pet_services``/``activities``.
            Used purely to pick the right mock fallback.
        city: City name — used by the mock fallback to filter seeds.
        dietary: Guest dietary tags (only sent in the query string).
        interests: Guest interest tags (only used by mock activities).
        include_domains: Optional Tavily domain filter.
        max_results: Override the configured default.
        force_mock: Skip the live call entirely (used by USE_MOCK_LLM mode).

    Returns:
        A :class:`TavilySearchOutcome` with results and ``source`` ('live'/'mock').
    """
    n = max_results or settings.tavily_max_results
    dietary = dietary or []
    interests = interests or []

    if not force_mock:
        live = await _live_search(query, max_results=n, include_domains=include_domains)
        if live:
            return TavilySearchOutcome(results=live, source="live", query=query)

    logger.info(
        "[tavily] using MOCK fallback category=%s city=%s force_mock=%s key_set=%s",
        category,
        city,
        force_mock,
        bool(settings.tavily_api_key),
    )
    return TavilySearchOutcome(
        results=_mock_for_category(
            category,
            city=city,
            dietary=dietary,
            interests=interests,
            max_results=n,
        ),
        source="mock",
        query=query,
    )
