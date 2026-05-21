"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ChevronRight, Leaf, MapPin, PawPrint } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import type { GuestSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

const PERSONA_BLURBS: Record<string, { tagline: string; details: string }> = {
  alex: {
    tagline: "Gold member · vegetarian · sustainability-minded",
    details:
      "Sees eco ratings front-and-center, gets sustainability-themed arrival briefs and Green Stay nudges.",
  },
  jordan: {
    tagline: "Platinum member · halal · traveling with Mochi (Shiba Inu)",
    details:
      "Pet + Local Partner Map shows vets, dog parks, and pet supply stops near the hotel.",
  },
  sam: {
    tagline: "Silver member · vegan · accessibility needs",
    details:
      "Accessibility-aware arrival brief with vegan dining picks and step-free transit notes.",
  },
};

export default function SignInPageWrapper(): React.ReactElement {
  return (
    <Suspense fallback={<div className="min-h-[calc(100vh-4rem)] bg-[var(--color-bonvoy-mist)]" />}>
      <SignInPage />
    </Suspense>
  );
}

function SignInPage(): React.ReactElement {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") ?? "/";
  const signIn = useAuthStore((s) => s.signIn);
  const [guests, setGuests] = useState<GuestSummary[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.guests
      .list()
      .then(setGuests)
      .catch(() => setError("Could not reach the demo backend on :8000."));
  }, []);

  async function pick(guestId: string): Promise<void> {
    setLoadingId(guestId);
    setError(null);
    try {
      await signIn(guestId);
      router.push(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed.");
    } finally {
      setLoadingId(null);
    }
  }

  return (
    <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-[1100px] px-6 py-14">
        <div className="mb-10 max-w-2xl">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-3">
            Marriott Bonvoy · Demo
          </p>
          <h1 className="heading-display text-4xl md:text-5xl mb-4">
            Sign in or join.
          </h1>
          <p className="text-[var(--color-bonvoy-muted)] text-[15px] leading-relaxed">
            This Codefest demo ships with three Bonvoy personas. Pick one to
            see how Eco Rating, the Arrival Brief, and the Pet + Local Partner
            Map adapt to that traveler. Real authentication is mocked — no
            password required.
          </p>
        </div>

        {error && (
          <div className="mb-8 rounded-lg border border-[var(--color-marriott-red)]/30 bg-white px-4 py-3 text-sm text-[var(--color-marriott-red-dark)]">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {guests.map((g) => {
            const blurb = PERSONA_BLURBS[g.id];
            const loading = loadingId === g.id;
            return (
              <button
                key={g.id}
                onClick={() => pick(g.id)}
                disabled={loading}
                className={cn(
                  "group bg-white text-left rounded-xl border border-[var(--color-bonvoy-rule)] p-6 transition-all",
                  "hover:border-[var(--color-marriott-red)] hover:shadow-lg hover:-translate-y-0.5",
                  loading && "opacity-60 cursor-wait",
                )}
              >
                <div className="flex items-center justify-between mb-4">
                  <div
                    className="h-12 w-12 rounded-full flex items-center justify-center text-white font-medium text-lg"
                    style={{ background: g.tier_color }}
                    aria-hidden
                  >
                    {g.name
                      .split(" ")
                      .map((p) => p[0])
                      .slice(0, 2)
                      .join("")}
                  </div>
                  <span className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)]">
                    {g.tier}
                  </span>
                </div>

                <h3 className="text-xl font-medium text-[var(--color-bonvoy-ink)] mb-1">
                  {g.name}
                </h3>
                <p className="text-[13px] text-[var(--color-bonvoy-muted)] mb-4">
                  {blurb?.tagline}
                </p>

                <div className="border-t border-[var(--color-bonvoy-rule)] pt-4 mb-4">
                  <p className="text-[12px] text-[var(--color-bonvoy-muted)]">
                    Bonvoy ID
                  </p>
                  <p className="text-[13px] font-mono">{g.bonvoy_id}</p>
                </div>

                <p className="text-[12px] text-[var(--color-bonvoy-muted)] leading-relaxed mb-5">
                  {blurb?.details}
                </p>

                <div className="flex items-center justify-between">
                  <span className="text-[14px] font-medium text-[var(--color-bonvoy-ink)]">
                    {g.points.toLocaleString()} pts
                  </span>
                  <span className="inline-flex items-center gap-1 text-[13px] font-medium text-[var(--color-marriott-red)] group-hover:gap-2 transition-all">
                    {loading ? "Signing in…" : "Continue as " + g.name.split(" ")[0]}
                    <ChevronRight size={16} />
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Feature explainer rail (Marriott-style three-up) */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-[13px]">
          {[
            {
              icon: <Leaf size={20} />,
              title: "Eco Rating",
              copy:
                "0–10 sustainability score on every property card and detail page, with Green Points multipliers from MESH-style data.",
            },
            {
              icon: <MapPin size={20} />,
              title: "Arrival Brief",
              copy:
                "A personalized 1-pager 48 hours before check-in — weather, events, dining, transit, and on-property notes.",
            },
            {
              icon: <PawPrint size={20} />,
              title: "Pet + Local Partner Map",
              copy:
                "Vets, dog parks, supply stores, and curated local experiences pinned around the hotel on an interactive map.",
            },
          ].map((f) => (
            <div key={f.title} className="border-t border-[var(--color-bonvoy-rule)] pt-5">
              <div className="text-[var(--color-marriott-red)] mb-3">{f.icon}</div>
              <h4 className="font-medium text-[var(--color-bonvoy-ink)] mb-1.5">
                {f.title}
              </h4>
              <p className="text-[var(--color-bonvoy-muted)] leading-relaxed">
                {f.copy}
              </p>
            </div>
          ))}
        </div>

        <p className="mt-12 text-[12px] text-[var(--color-bonvoy-muted)]">
          Already booked?{" "}
          <Link href="/trips" className="underline hover:text-[var(--color-marriott-red)]">
            Find your reservation
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
