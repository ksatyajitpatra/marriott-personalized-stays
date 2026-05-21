"use client";

/**
 * AffiliateChip — "Book via Marriott +N Bonvoy points" CTA.
 *
 * Surfaced next to each event/dining card. Clicking opens the partner's
 * deeplink in a new tab and fires a tracked-click POST to the backend
 * (`/affiliate/click`). The mock commission ledger drives the
 * bottom-of-brief panel that makes the business model legible.
 */

import { ExternalLink, TicketCheck } from "lucide-react";

import { affiliate as affiliateApi } from "@/lib/api";
import type { AffiliateOffer } from "@/lib/types";

export interface AffiliateChipProps {
  stayId: string;
  offer: AffiliateOffer;
  onTracked?: () => void;
}

export function AffiliateChip({
  stayId,
  offer,
  onTracked,
}: AffiliateChipProps): React.ReactElement {
  function handleClick(): void {
    // Fire-and-forget; never block the deeplink open.
    void affiliateApi
      .click({
        stay_id: stayId,
        partner: offer.partner,
        partner_domain: offer.partner_domain,
        url: offer.deeplink,
        est_commission_usd: offer.est_commission_usd,
        bonvoy_bonus_points: offer.bonvoy_bonus_points,
      })
      .then(() => onTracked?.())
      .catch(() => {
        /* swallow — tracking is best-effort */
      });
  }

  const points = offer.bonvoy_bonus_points;
  const partnerLabel =
    offer.partner === "Direct booking" ? "partner site" : offer.partner;

  return (
    <a
      href={offer.deeplink}
      target="_blank"
      rel="noopener noreferrer"
      onClick={handleClick}
      title={offer.disclosure}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md border border-[var(--color-marriott-red)] bg-[var(--color-marriott-red)] text-white text-[12px] font-medium hover:opacity-90 transition"
    >
      <TicketCheck size={13} />
      Book via Marriott
      {points > 0 ? (
        <span className="bg-white/20 rounded px-1.5 py-[1px] text-[11px]">
          +{points.toLocaleString()} pts
        </span>
      ) : null}
      <span className="text-[10px] uppercase tracking-[0.12em] opacity-80">
        {partnerLabel}
      </span>
      <ExternalLink size={11} className="opacity-80" />
    </a>
  );
}
