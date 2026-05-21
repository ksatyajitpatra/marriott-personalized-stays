"""Affiliate / commission framing for the Live Concierge Agent.

This is a deliberately small, in-memory service that wraps each Tavily
result with a "Book via Marriott" deeplink and tracks click-throughs
against a per-stay ledger. None of this is real revenue plumbing — it
exists to make the business model **legible** during the demo (the wow
moment for judges) without involving live OAuth into OpenTable, Viator,
Rover, etc.

Public surface:
    - :func:`build_affiliate_offer` — decorate any URL with a tracked deeplink
      and a static rate-table commission/points pair.
    - :func:`record_click` / :func:`get_ledger` — in-memory click ledger.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock
from urllib.parse import urlencode, urlparse, urlunparse

from app.models.concierge import (
    AffiliateClickRecord,
    AffiliateLedgerResponse,
    AffiliateOffer,
)

logger = logging.getLogger(__name__)


# --- Static partner / commission table ------------------------------------
#
# Rates are sourced from each partner's published affiliate program where
# available, otherwise a conservative industry default. This is a static
# table — not a live partner integration.
_PARTNER_TABLE: dict[str, tuple[str, float]] = {
    "opentable.com": ("OpenTable", 0.08),
    "resy.com": ("Resy", 0.06),
    "yelp.com": ("Yelp Reservations", 0.05),
    "viator.com": ("Viator", 0.08),
    "getyourguide.com": ("GetYourGuide", 0.08),
    "ticketmaster.com": ("Ticketmaster", 0.05),
    "rover.com": ("Rover", 0.15),
    "wag.com": ("Wag!", 0.12),
    "expedia.com": ("Expedia", 0.04),
    "booking.com": ("Booking.com", 0.04),
}

# Average ticket sizes per category — used to convert a commission rate
# into a dollar estimate without needing the partner's actual price.
_AVG_TICKET_USD: dict[str, float] = {
    "events": 65.0,
    "dining": 80.0,
    "pet_services": 45.0,
    "activities": 95.0,
    "default": 50.0,
}

# 50% of the affiliate commission flows back to the guest as bonus points,
# at the standard Bonvoy redemption value of $0.01 / point. The other 50%
# stays with Marriott — this is the storytelling number on the ledger.
_BONUS_POINTS_PER_USD = 50


def _detect_partner(url: str) -> tuple[str, str]:
    """Return ``(partner_display_name, partner_domain)`` for the URL.

    Falls back to ``("Direct booking", "<domain>")`` when the domain is
    not in the known table.
    """
    domain = urlparse(url).netloc.lower().lstrip("www.")
    if not domain:
        domain = "direct"
    if domain in _PARTNER_TABLE:
        return _PARTNER_TABLE[domain][0], domain
    # try suffix match (e.g. www.opentable.com → opentable.com)
    for known in _PARTNER_TABLE:
        if domain.endswith(known):
            return _PARTNER_TABLE[known][0], known
    return ("Direct booking", domain)


def _decorate_deeplink(url: str, *, stay_id: str, campaign: str) -> str:
    """Append Marriott affiliate UTM params to a URL idempotently."""
    if not url:
        return url
    parts = urlparse(url)
    extra = {
        "utm_source": "marriott_bonvoy",
        "utm_medium": "arrival_brief",
        "utm_campaign": campaign,
        "stay_id": stay_id,
    }
    sep = "&" if parts.query else ""
    new_query = f"{parts.query}{sep}{urlencode(extra)}"
    return urlunparse(parts._replace(query=new_query))


def build_affiliate_offer(
    url: str,
    *,
    stay_id: str,
    category: str,
) -> AffiliateOffer:
    """Build an :class:`AffiliateOffer` for a given third-party URL.

    Args:
        url: The original third-party URL (e.g. an OpenTable listing).
        stay_id: Stay id used to tag the deeplink so we can attribute clicks.
        category: Category key (`events` / `dining` / `pet_services` /
            `activities`) used to look up the average ticket size.

    Returns:
        A populated ``AffiliateOffer``. Always returns a value — unknown
        partners fall back to a "Direct booking" label with a 0% rate.
    """
    partner, domain = _detect_partner(url)
    rate = _PARTNER_TABLE.get(domain, ("Direct booking", 0.0))[1]
    avg_ticket = _AVG_TICKET_USD.get(category, _AVG_TICKET_USD["default"])
    commission = round(avg_ticket * rate, 2)
    bonus_points = int(commission * _BONUS_POINTS_PER_USD)
    return AffiliateOffer(
        partner=partner,
        partner_domain=domain,
        deeplink=_decorate_deeplink(url, stay_id=stay_id, campaign=category),
        est_commission_usd=commission,
        bonvoy_bonus_points=bonus_points,
    )


# --- In-memory click ledger ------------------------------------------------


_ledger: dict[str, list[AffiliateClickRecord]] = {}
_ledger_lock = Lock()


def record_click(
    *,
    stay_id: str,
    partner: str,
    partner_domain: str,
    url: str,
    est_commission_usd: float,
    bonvoy_bonus_points: int,
) -> AffiliateClickRecord:
    """Append a click event to the per-stay ledger and return it.

    Thread-safe via a small ``threading.Lock`` — FastAPI's worker model
    plus our async handlers means concurrent clicks for a stay are
    plausible during the demo.
    """
    record = AffiliateClickRecord(
        stay_id=stay_id,
        partner=partner,
        partner_domain=partner_domain,
        url=url,
        est_commission_usd=est_commission_usd,
        bonvoy_bonus_points=bonvoy_bonus_points,
        clicked_at=datetime.now(timezone.utc).isoformat(),
    )
    with _ledger_lock:
        _ledger.setdefault(stay_id, []).append(record)
    logger.info(
        "Affiliate click recorded stay=%s partner=%s commission=%.2f",
        stay_id,
        partner,
        est_commission_usd,
    )
    return record


def get_ledger(stay_id: str) -> AffiliateLedgerResponse:
    """Return the running click totals for a stay."""
    with _ledger_lock:
        clicks = list(_ledger.get(stay_id, []))
    total_commission = round(sum(c.est_commission_usd for c in clicks), 2)
    total_points = sum(c.bonvoy_bonus_points for c in clicks)
    return AffiliateLedgerResponse(
        stay_id=stay_id,
        click_count=len(clicks),
        projected_commission_usd=total_commission,
        projected_bonus_points=total_points,
        clicks=clicks,
    )


def reset_ledger() -> None:
    """Clear the in-memory ledger — used by tests."""
    with _ledger_lock:
        _ledger.clear()
