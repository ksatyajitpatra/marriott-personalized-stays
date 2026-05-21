"use client";

import { useEffect, useState } from "react";
import {
  Award,
  Compass,
  Footprints,
  Globe2,
  Heart,
  Leaf,
  Lock,
  type LucideIcon,
  PawPrint,
  PlaneTakeoff,
  Repeat,
  ShieldCheck,
  Sparkles,
  Star,
  Trophy,
} from "lucide-react";
import { auth } from "@/lib/api";
import type {
  BadgeCategory,
  BadgeCategorySection,
  BadgeItem,
  BadgeShelfResponse,
} from "@/lib/types";
import { cn } from "@/lib/utils";

/**
 * Bonvoy badge shelf — 4 categories × 3 badges = 12 total.
 *
 * Each tile shows a single badge. Tiered badges (Frequent Stayer,
 * Eco Warrior, Globetrotter, etc.) advance in place — current tier
 * label + progress bar to next tier — Sephora/Chipotle-style.
 *
 * The data is fully derived on the backend from completed stays +
 * reservations. See `app/services/badge_service.py`.
 */
export function BadgeShelf(): React.ReactElement {
  const [shelf, setShelf] = useState<BadgeShelfResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    auth
      .badges()
      .then((data) => {
        if (!cancelled) setShelf(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          // Surface a clearer message if the API is unreachable so the
          // user doesn't see a bare "Not Found".
          const fallback =
            err instanceof Error && err.message
              ? `Couldn't load badges (${err.message}). Is the backend running?`
              : "Couldn't load badges right now.";
          setError(fallback);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
        <div className="h-32 bg-[var(--color-bonvoy-mist)] rounded-md animate-pulse" />
      </section>
    );
  }

  if (error || !shelf) {
    return (
      <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
        <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
          {error ?? "Badges unavailable right now."}
        </p>
      </section>
    );
  }

  return (
    <div className="space-y-6">
      <ShelfHeader stats={shelf.stats} />
      {shelf.sections.map((section) => (
        <CategorySection key={section.id} section={section} />
      ))}
      {shelf.qualifying_stays.length > 0 && (
        <EarnedHistory stays={shelf.qualifying_stays} />
      )}
    </div>
  );
}

// --- Header summary ---------------------------------------------------------

function ShelfHeader({
  stats,
}: {
  stats: BadgeShelfResponse["stats"];
}): React.ReactElement {
  return (
    <section className="bg-[var(--color-bonvoy-ink)] text-white rounded-lg p-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-white/70 mb-1">
            Bonvoy badges
          </p>
          <h2 className="heading-display text-2xl mb-1">
            {stats.total_earned}{" "}
            <span className="text-white/60 text-[18px]">
              of {stats.total_available} earned
            </span>
          </h2>
          <p className="text-[13px] text-white/75">
            Earned automatically as you book, stay, and explore.
          </p>
        </div>
        <ul className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-2 text-[12px]">
          <Stat label="Stays" value={stats.completed_stays} />
          <Stat label="Cities" value={stats.cities_visited} />
          <Stat label="Brands" value={stats.brands_visited} />
          <Stat label="Eco-leader stays" value={stats.eco_leader_stays} />
        </ul>
      </div>
    </section>
  );
}

function Stat({
  label,
  value,
}: {
  label: string;
  value: number;
}): React.ReactElement {
  return (
    <li>
      <p className="text-[20px] font-medium tabular-nums leading-tight">
        {value}
      </p>
      <p className="text-[10px] uppercase tracking-[0.16em] text-white/60">
        {label}
      </p>
    </li>
  );
}

// --- Category section -------------------------------------------------------

const CATEGORY_ICONS: Record<BadgeCategory, LucideIcon> = {
  sustainability: Leaf,
  loyalty: Repeat,
  explorer: Compass,
  lifestyle: Heart,
};

function CategorySection({
  section,
}: {
  section: BadgeCategorySection;
}): React.ReactElement {
  const Icon = CATEGORY_ICONS[section.id];
  return (
    <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
      <header className="flex items-center gap-3 mb-4">
        <span className="w-8 h-8 rounded-full bg-[var(--color-bonvoy-mist)] inline-flex items-center justify-center">
          <Icon size={15} className="text-[var(--color-bonvoy-ink)]" />
        </span>
        <div>
          <h3 className="text-[16px] font-medium text-[var(--color-bonvoy-ink)]">
            {section.label}
          </h3>
          <p className="text-[12px] text-[var(--color-bonvoy-muted)]">
            {section.description}
          </p>
        </div>
      </header>
      <ul className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {section.badges.map((badge) => (
          <BadgeTile key={badge.id} badge={badge} />
        ))}
      </ul>
    </section>
  );
}

// --- Single badge tile ------------------------------------------------------

/**
 * Per-badge fallback icon, used until the AI-generated PNGs are dropped
 * into `public/badges/{image_id}.png`. The image element tries the PNG
 * first and falls through to the lucide icon if the asset 404s.
 */
const BADGE_ICONS: Record<string, LucideIcon> = {
  "green-stay": Leaf,
  "eco-warrior": ShieldCheck,
  "brand-eco-native": Sparkles,
  "welcome-aboard": Star,
  "frequent-stayer": Repeat,
  "brand-loyalist": Award,
  globetrotter: Globe2,
  "brand-sampler": PlaneTakeoff,
  "property-pioneer": Trophy,
  "pet-parent": PawPrint,
  "concierge-of-one": Footprints,
  "local-explorer": Compass,
};

function BadgeTile({ badge }: { badge: BadgeItem }): React.ReactElement {
  const FallbackIcon = BADGE_ICONS[badge.image_id] ?? Award;
  const [imgFailed, setImgFailed] = useState(false);
  const showImage = !imgFailed;
  const progress = computeProgressFraction(badge);

  return (
    <li
      className={cn(
        "relative border rounded-lg p-4 transition-all",
        badge.earned
          ? "border-[var(--color-bonvoy-rule)] bg-white"
          : "border-dashed border-[var(--color-bonvoy-rule)] bg-[var(--color-bonvoy-mist)]/30",
      )}
      title={badge.hint}
    >
      <div className="flex items-start gap-3">
        {/* Icon / image */}
        <div
          className={cn(
            "shrink-0 w-12 h-12 rounded-lg inline-flex items-center justify-center overflow-hidden",
            badge.earned
              ? "bg-[var(--color-bonvoy-ink)]"
              : "bg-[var(--color-bonvoy-mist)]",
          )}
        >
          {showImage ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={`/badges/${badge.image_id}.png`}
              alt=""
              className={cn(
                "w-full h-full object-cover",
                !badge.earned && "opacity-40 grayscale",
              )}
              onError={() => setImgFailed(true)}
            />
          ) : badge.earned ? (
            <FallbackIcon size={22} className="text-white" />
          ) : (
            <Lock size={18} className="text-[var(--color-bonvoy-muted)]" />
          )}
        </div>

        {/* Copy */}
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-2">
            <p
              className={cn(
                "text-[13px] font-medium leading-tight",
                badge.earned
                  ? "text-[var(--color-bonvoy-ink)]"
                  : "text-[var(--color-bonvoy-muted)]",
              )}
            >
              {badge.label}
            </p>
            {badge.current_tier_label && badge.max_tier > 1 && (
              <span className="text-[10px] uppercase tracking-[0.14em] text-[var(--color-marriott-red)] font-medium shrink-0">
                {badge.current_tier_label}
              </span>
            )}
          </div>
          <p className="text-[11px] text-[var(--color-bonvoy-muted)] mt-1 leading-snug line-clamp-2">
            {badge.description}
          </p>
        </div>
      </div>

      {/* Progress bar — only for tiered badges in progress */}
      {badge.max_tier > 1 && badge.next_tier_threshold !== null && (
        <div className="mt-3">
          <div className="h-1.5 bg-[var(--color-bonvoy-mist)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--color-marriott-red)] rounded-full transition-all"
              style={{ width: `${Math.round(progress * 100)}%` }}
            />
          </div>
          <p className="mt-1.5 text-[10px] uppercase tracking-[0.14em] text-[var(--color-bonvoy-muted)]">
            {badge.hint}
          </p>
        </div>
      )}

      {/* Single-shot badge hint */}
      {badge.max_tier === 1 && (
        <p className="mt-3 text-[11px] text-[var(--color-bonvoy-muted)] leading-snug">
          {badge.hint}
        </p>
      )}

      {/* "Maxed out" ribbon for top-tier earned */}
      {badge.max_tier > 1 &&
        badge.current_tier === badge.max_tier &&
        badge.earned && (
          <span className="absolute top-3 right-3 text-[9px] uppercase tracking-[0.16em] text-[var(--color-marriott-red)] font-medium">
            Maxed
          </span>
        )}
    </li>
  );
}

/**
 * Compute the 0–1 progress fraction inside the *current* tier toward the
 * next one. For the locked state (current_tier === 0) we lerp from 0 to
 * the first threshold.
 */
function computeProgressFraction(badge: BadgeItem): number {
  if (badge.next_tier_threshold === null) {
    // Maxed out.
    return 1;
  }
  const lower = badge.current_tier > 0
    ? thresholdAt(badge, badge.current_tier - 1)
    : 0;
  const upper = badge.next_tier_threshold;
  if (upper <= lower) return 1;
  const frac = (badge.progress_value - lower) / (upper - lower);
  return Math.max(0, Math.min(1, frac));
}

/**
 * For a tiered badge, the threshold for tier i is unfortunately not on
 * the response — we only get the *current* and *next* threshold. So we
 * approximate the lower bound by counting back from progress_value:
 * it's whichever is smaller — the user's current value, or the previous
 * tier's threshold (which we don't have, so we settle for 0).
 *
 * Result: if the bar is "current tier earned" we just show the fill
 * relative to the next threshold from zero, which is good enough visually.
 */
function thresholdAt(badge: BadgeItem, _index: number): number {
  // Without the full ladder we settle for showing fill from 0 to next.
  // This still produces an intuitive "almost there" bar when between
  // tiers, since progress_value > previous threshold by definition.
  return 0;
}

// --- Eco "how was this earned?" section -------------------------------------

function EarnedHistory({
  stays,
}: {
  stays: BadgeShelfResponse["qualifying_stays"];
}): React.ReactElement {
  return (
    <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
      <details className="group">
        <summary className="cursor-pointer list-none flex items-center justify-between text-[12px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)]">
          <span>Eco-leader stays on file ({stays.length})</span>
          <span className="text-[11px] text-[var(--color-marriott-red)] group-open:hidden">
            Show
          </span>
          <span className="text-[11px] text-[var(--color-marriott-red)] hidden group-open:inline">
            Hide
          </span>
        </summary>
        <ul className="mt-4 space-y-2">
          {stays.map((stay) => (
            <li
              key={stay.stay_id}
              className="flex items-center justify-between text-[13px]"
            >
              <span className="text-[var(--color-bonvoy-ink)]">
                {stay.hotel_name}
              </span>
              <span className="text-[var(--color-bonvoy-muted)]">
                {stay.check_in} · eco {stay.eco_score.toFixed(1)}/10
              </span>
            </li>
          ))}
        </ul>
      </details>
    </section>
  );
}
