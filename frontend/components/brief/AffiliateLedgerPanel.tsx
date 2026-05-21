"use client";

/**
 * AffiliateLedgerPanel — bottom-of-brief summary panel that surfaces
 * the running commission + projected bonus points totals for a stay.
 *
 * This is the explicit "judges see the revenue model" moment described
 * in the PRD upgrade. We poll the backend ledger every few seconds while
 * the panel is mounted (the user clicks affiliate chips during the demo).
 */

import { useEffect, useState } from "react";
import { Coins, TrendingUp } from "lucide-react";

import { affiliate as affiliateApi } from "@/lib/api";
import type { AffiliateLedgerResponse } from "@/lib/types";

export interface AffiliateLedgerPanelProps {
  stayId: string;
  /** When provided, the panel re-fetches the ledger whenever this counter changes. */
  refreshKey?: number;
}

export function AffiliateLedgerPanel({
  stayId,
  refreshKey = 0,
}: AffiliateLedgerPanelProps): React.ReactElement | null {
  const [ledger, setLedger] = useState<AffiliateLedgerResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    affiliateApi
      .ledger(stayId)
      .then((l) => {
        if (!cancelled) setLedger(l);
      })
      .catch(() => {
        /* swallow — non-critical UI */
      });
    return () => {
      cancelled = true;
    };
  }, [stayId, refreshKey]);

  if (!ledger || ledger.click_count === 0) return null;

  return (
    <section className="bg-[var(--color-bonvoy-mist)] border border-[var(--color-bonvoy-rule)] rounded-lg p-5 md:p-6 mb-6">
      <div className="flex items-center gap-2 text-[var(--color-marriott-red)] mb-2">
        <TrendingUp size={14} />
        <span className="text-[11px] uppercase tracking-[0.2em]">
          How this brief earns its keep
        </span>
      </div>
      <p className="text-[14px] text-[var(--color-bonvoy-ink)] leading-relaxed mb-3">
        You&rsquo;ve clicked through{" "}
        <strong>{ledger.click_count}</strong> partner link
        {ledger.click_count === 1 ? "" : "s"} on this brief. If you book,
        Marriott earns ~{" "}
        <strong>${ledger.projected_commission_usd.toFixed(2)}</strong> in
        affiliate commission — half of that flows back to you as Bonvoy
        bonus points.
      </p>
      <div className="grid grid-cols-2 gap-3 mt-4">
        <Stat
          icon={<TrendingUp size={14} />}
          label="Projected commission"
          value={`$${ledger.projected_commission_usd.toFixed(2)}`}
          tone="ink"
        />
        <Stat
          icon={<Coins size={14} />}
          label="Bonus points if booked"
          value={`+${ledger.projected_bonus_points.toLocaleString()}`}
          tone="green"
        />
      </div>
      <p className="text-[11px] text-[var(--color-bonvoy-muted)] mt-3 leading-snug">
        Static rate-table estimate based on each partner&rsquo;s public affiliate program.
        Not a live booking quote. Marriott reinvests 50% of every commission as
        Bonvoy bonus points to keep loyalty tied to the direct channel.
      </p>
    </section>
  );
}

function Stat({
  icon,
  label,
  value,
  tone,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  tone: "ink" | "green";
}): React.ReactElement {
  const valueClass =
    tone === "green"
      ? "text-[var(--color-eco-green)]"
      : "text-[var(--color-bonvoy-ink)]";
  return (
    <div className="bg-white border border-[var(--color-bonvoy-rule)] rounded-md p-3">
      <div className="flex items-center gap-1.5 text-[var(--color-bonvoy-muted)] text-[11px] uppercase tracking-[0.16em] mb-1">
        {icon}
        {label}
      </div>
      <p className={`text-[20px] font-medium ${valueClass}`}>{value}</p>
    </div>
  );
}
