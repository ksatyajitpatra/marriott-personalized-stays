"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Calendar,
  ChevronRight,
  CreditCard,
  Luggage,
  PawPrint,
  Sparkles,
} from "lucide-react";
import { reservations as resApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import type { ReservationResponse } from "@/lib/types";
import { formatDate, formatUsd, cn } from "@/lib/utils";

const STATUS_LABEL: Record<ReservationResponse["status"], string> = {
  pending_payment: "Pending payment",
  upcoming: "Upcoming",
  in_stay: "In stay",
  completed: "Completed",
};

const STATUS_BADGE: Record<ReservationResponse["status"], string> = {
  pending_payment: "bg-amber-100 text-amber-900",
  upcoming: "bg-emerald-100 text-emerald-900",
  in_stay: "bg-blue-100 text-blue-900",
  completed: "bg-neutral-200 text-neutral-700",
};

export default function TripsPage(): React.ReactElement {
  const router = useRouter();
  const guest = useAuthStore((s) => s.guest);
  const hydrated = useAuthStore((s) => s.hydrated);
  const [list, setList] = useState<ReservationResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!hydrated) return;
    if (!guest) {
      router.replace("/sign-in?next=/trips");
      return;
    }
    resApi
      .list()
      .then(setList)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load trips."));
  }, [guest, hydrated, router]);

  if (!hydrated || !guest) {
    return <div className="min-h-[calc(100vh-4rem)] bg-[var(--color-bonvoy-mist)]" />;
  }

  const upcoming = (list ?? []).filter((r) => r.status !== "completed");
  const past = (list ?? []).filter((r) => r.status === "completed");

  return (
    <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-[1100px] px-6 py-10">
        <p className="text-[12px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-2">
          Marriott Bonvoy
        </p>
        <h1 className="heading-display text-3xl md:text-4xl text-[var(--color-bonvoy-ink)] mb-2">
          {guest.name.split(" ")[0]}&rsquo;s trips
        </h1>
        <p className="text-[14px] text-[var(--color-bonvoy-muted)] mb-8">
          {guest.tier} member · {guest.points.toLocaleString()} points
        </p>

        {error && (
          <div className="mb-6 rounded-lg border border-[var(--color-marriott-red)]/30 bg-white px-4 py-3 text-sm text-[var(--color-marriott-red-dark)]">
            {error}
          </div>
        )}

        {list === null ? (
          <div className="grid gap-4">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-[180px] bg-white rounded-lg border border-[var(--color-bonvoy-rule)] animate-pulse"
              />
            ))}
          </div>
        ) : (
          <>
            <Section title="Upcoming" empty="No upcoming trips. Time to plan one.">
              {upcoming.map((r) => (
                <TripCard key={r.id} r={r} highlight />
              ))}
            </Section>
            {past.length > 0 && (
              <Section title="Past stays">
                {past.map((r) => (
                  <TripCard key={r.id} r={r} />
                ))}
              </Section>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function Section({
  title,
  empty,
  children,
}: {
  title: string;
  empty?: string;
  children: React.ReactNode;
}): React.ReactElement {
  const isEmpty = Array.isArray(children) && children.length === 0;
  return (
    <section className="mb-10">
      <h2 className="text-[18px] font-medium text-[var(--color-bonvoy-ink)] mb-4">
        {title}
      </h2>
      {isEmpty && empty ? (
        <p className="text-[14px] text-[var(--color-bonvoy-muted)] bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
          {empty}
        </p>
      ) : (
        <div className="grid gap-4">{children}</div>
      )}
    </section>
  );
}

function TripCard({
  r,
  highlight = false,
}: {
  r: ReservationResponse;
  highlight?: boolean;
}): React.ReactElement {
  return (
    <Link
      href={`/trips/${r.id}`}
      className="grid grid-cols-1 md:grid-cols-[220px_1fr_auto] gap-4 bg-white border border-[var(--color-bonvoy-rule)] rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
    >
      <div
        className="aspect-[4/3] md:aspect-auto md:h-full bg-cover bg-center"
        style={{ backgroundImage: `url(${r.hotel_image_url})` }}
        aria-hidden
      />
      <div className="px-2 md:px-4 py-5 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span
            className={cn(
              "text-[10px] uppercase tracking-[0.18em] px-2 py-0.5 rounded-full",
              STATUS_BADGE[r.status],
            )}
          >
            {STATUS_LABEL[r.status]}
          </span>
          <span className="text-[11px] text-[var(--color-bonvoy-muted)] font-mono">
            CONF · {r.confirmation_number}
          </span>
        </div>
        <h3 className="text-[18px] font-medium text-[var(--color-bonvoy-ink)]">
          {r.hotel_name}
        </h3>
        <p className="text-[13px] text-[var(--color-bonvoy-muted)] mb-3">
          {r.hotel_city}
        </p>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-[13px] text-[var(--color-bonvoy-ink)]">
          <span className="inline-flex items-center gap-1">
            <Calendar size={14} className="text-[var(--color-bonvoy-muted)]" />
            {formatDate(r.check_in)} – {formatDate(r.check_out)}
          </span>
          <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-muted)]">
            <Luggage size={14} />
            {r.nights} {r.nights === 1 ? "night" : "nights"} · {r.room_type}
          </span>
          {r.has_pet && (
            <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-muted)]">
              <PawPrint size={14} />
              Traveling with pet
            </span>
          )}
        </div>
      </div>
      <div className="px-5 py-5 md:border-l border-[var(--color-bonvoy-rule)] flex flex-col items-end justify-between gap-3">
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)]">
            Total
          </p>
          <p className="text-[20px] font-medium text-[var(--color-bonvoy-ink)]">
            {formatUsd(r.total_usd)}
          </p>
          <p className="inline-flex items-center gap-1 text-[12px] text-[var(--color-bonvoy-muted)]">
            <CreditCard size={12} />
            {r.payment_status === "paid" ? "Paid" : "Unpaid"}
          </p>
        </div>
        <span
          className={cn(
            "inline-flex items-center gap-1 text-[13px] font-medium",
            highlight
              ? "text-[var(--color-marriott-red)]"
              : "text-[var(--color-bonvoy-ink)]",
          )}
        >
          {highlight && <Sparkles size={14} />}
          View Arrival Brief
          <ChevronRight size={14} />
        </span>
      </div>
    </Link>
  );
}
