"use client";

import { useState } from "react";
import { ChevronDown, Leaf, Sparkles } from "lucide-react";
import type { EcoScoreResponse } from "@/lib/types";
import { EcoScoreRing } from "./EcoScoreRing";
import { cn } from "@/lib/utils";

interface EcoScoreDetailProps {
  data: EcoScoreResponse;
}

const ECO_LABEL: Record<EcoScoreResponse["color"], string> = {
  green: "Leader",
  yellow: "Improving",
  red: "Below standard",
};

/**
 * Full eco-score breakdown panel — circular ring + Green Points line
 * + an accordion of the 6 sub-scores (PRD 5.1).
 */
export function EcoScoreDetail({ data }: EcoScoreDetailProps): React.ReactElement {
  const [open, setOpen] = useState<string | null>(data.sub_scores[0]?.key ?? null);

  return (
    <section className="bg-white rounded-lg border border-[var(--color-bonvoy-rule)] overflow-hidden">
      <div className="p-6 grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-center bg-[var(--color-bonvoy-mist)]">
        <EcoScoreRing
          score={data.total_score}
          color={data.color}
          size={92}
        />
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Leaf size={14} className="text-[var(--color-eco-green)]" />
            <span className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)]">
              Eco Rating · {ECO_LABEL[data.color]}
            </span>
          </div>
          <h3 className="text-2xl font-medium text-[var(--color-bonvoy-ink)] mb-1">
            {data.total_score.toFixed(1)} / 10 sustainability score
          </h3>
          <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
            Source: {data.data_source} · as of {data.data_as_of}
          </p>
          {data.green_points_bonus > 0 && (
            <div className="mt-3 inline-flex items-center gap-2 rounded-full bg-white border border-[var(--color-eco-green)]/30 px-3 py-1.5 text-[12px] text-[var(--color-eco-green)]">
              <Sparkles size={14} />
              Earn {data.green_points_bonus.toLocaleString()} bonus Green Points
              · {data.green_points_multiplier.toFixed(1)}× base earning
            </div>
          )}
        </div>
      </div>

      <ul>
        {data.sub_scores.map((s, i) => {
          const expanded = open === s.key;
          return (
            <li
              key={s.key}
              className={cn(
                "border-t border-[var(--color-bonvoy-rule)]",
                i === 0 && "border-t-0",
              )}
            >
              <button
                onClick={() => setOpen(expanded ? null : s.key)}
                className="w-full text-left px-6 py-4 flex items-center gap-4 hover:bg-[var(--color-bonvoy-mist)]/50 transition-colors"
              >
                <span className="text-[24px] font-medium text-[var(--color-bonvoy-ink)] tabular-nums w-14">
                  {s.score.toFixed(1)}
                </span>
                <span className="flex-1">
                  <span className="block text-[15px] font-medium text-[var(--color-bonvoy-ink)]">
                    {s.label}
                  </span>
                  <span className="block text-[12px] text-[var(--color-bonvoy-muted)]">
                    {s.raw_value} · weighted {s.weight_pct}%
                  </span>
                </span>
                <ChevronDown
                  size={18}
                  className={cn(
                    "text-[var(--color-bonvoy-muted)] transition-transform",
                    expanded && "rotate-180",
                  )}
                />
              </button>
              {expanded && (
                <div className="px-6 pb-5 -mt-1 grid grid-cols-1 sm:grid-cols-[auto_1fr] gap-x-5 gap-y-2 text-[13px] text-[var(--color-bonvoy-muted)]">
                  <div className="relative h-2 sm:col-span-2 bg-[var(--color-bonvoy-mist)] rounded overflow-hidden mb-1">
                    <div
                      className="absolute inset-y-0 left-0 rounded"
                      style={{
                        width: `${(s.score / 10) * 100}%`,
                        background: `var(--color-eco-${data.color})`,
                      }}
                    />
                  </div>
                  <span className="uppercase tracking-[0.14em] text-[11px] sm:col-span-2">
                    Source · {s.data_source}
                  </span>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
