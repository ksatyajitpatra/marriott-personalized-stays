"""Affiliate click tracking + ledger endpoints (PRD § 5.2.x)."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.concierge import (
    AffiliateClickRecord,
    AffiliateClickRequest,
    AffiliateLedgerResponse,
)
from app.services.affiliate_service import get_ledger, record_click

router = APIRouter(prefix="/affiliate", tags=["affiliate"])


@router.post("/click", response_model=AffiliateClickRecord)
async def post_affiliate_click(payload: AffiliateClickRequest) -> AffiliateClickRecord:
    """Record an affiliate click into the in-memory ledger.

    The frontend fires this fire-and-forget when the guest opens a
    "Book via Marriott" deeplink. The response is the persisted record
    (so clients can confirm and roll up local UI optimistically).
    """
    return record_click(
        stay_id=payload.stay_id,
        partner=payload.partner,
        partner_domain=payload.partner_domain,
        url=payload.url,
        est_commission_usd=payload.est_commission_usd,
        bonvoy_bonus_points=payload.bonvoy_bonus_points,
    )


@router.get("/ledger/{stay_id}", response_model=AffiliateLedgerResponse)
async def get_affiliate_ledger(stay_id: str) -> AffiliateLedgerResponse:
    """Return the running click totals for a stay.

    Drives the bottom-of-brief "Marriott earned $X · You'd earn N points"
    panel that makes the commission/Bonvoy-bonus business model legible.
    """
    return get_ledger(stay_id)
