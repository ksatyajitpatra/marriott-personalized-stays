"use client";

import { useState } from "react";
import { Calendar, Clock, Loader2 } from "lucide-react";
import type { PetServiceBooking } from "@/lib/types";
import { formatDate, formatTime } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { MobileServiceBadge } from "./MobileServiceBadge";

const CATEGORY_LABEL: Record<string, string> = {
  vet_emergency: "Vet",
  dog_walker: "Dog walker / sitter",
  mobile_grooming: "Mobile grooming",
  pet_supply: "Pet supply",
};

interface PetServiceBookingListProps {
  bookings: PetServiceBooking[];
  reservationId?: string;
  onCancel?: (bookingId: string) => Promise<void>;
}

export function PetServiceBookingList({
  bookings,
  reservationId,
  onCancel,
}: PetServiceBookingListProps): React.ReactElement | null {
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (bookings.length === 0) return null;

  async function handleCancel(bookingId: string): Promise<void> {
    if (!onCancel) return;
    setCancellingId(bookingId);
    setError(null);
    try {
      await onCancel(bookingId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancellation failed");
    } finally {
      setCancellingId(null);
    }
  }

  return (
    <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
      <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-1">
        Pet services
      </p>
      <h3 className="text-[20px] font-medium text-[var(--color-bonvoy-ink)] mb-4">
        Booked for this stay
      </h3>
      {error && (
        <p className="text-[13px] text-[var(--color-marriott-red)] mb-3">{error}</p>
      )}
      <ul className="space-y-3">
        {bookings.map((b) => {
          const cancelled = b.status === "cancelled";
          return (
            <li
              key={b.id}
              className={cn(
                "border border-[var(--color-bonvoy-rule)] rounded-md p-4",
                cancelled && "opacity-60 bg-[var(--color-bonvoy-mist)]",
              )}
            >
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div>
                  <h4 className="text-[15px] font-medium text-[var(--color-bonvoy-ink)]">
                    {b.partner_name}
                  </h4>
                  <p className="text-[12px] text-[var(--color-bonvoy-muted)]">
                    {CATEGORY_LABEL[b.category] ?? b.category}
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {b.service_model === "mobile" && <MobileServiceBadge />}
                  <span
                    className={cn(
                      "text-[11px] uppercase tracking-[0.14em] px-2 py-0.5 rounded-full",
                      cancelled
                        ? "bg-[var(--color-bonvoy-rule)] text-[var(--color-bonvoy-muted)]"
                        : "bg-[#e8f5ee] text-[var(--color-eco-green)]",
                    )}
                  >
                    {b.status}
                  </span>
                </div>
              </div>
              <div className="flex flex-wrap gap-x-4 gap-y-1 text-[13px] text-[var(--color-bonvoy-muted)]">
                <span className="inline-flex items-center gap-1">
                  <Calendar size={13} />
                  {formatDate(b.service_date)}
                </span>
                <span className="inline-flex items-center gap-1">
                  <Clock size={13} />
                  {formatTime(b.service_time)}
                </span>
              </div>
              {b.notes && (
                <p className="mt-2 text-[13px] text-[var(--color-bonvoy-ink)]">{b.notes}</p>
              )}
              {!cancelled && onCancel && reservationId && (
                <button
                  type="button"
                  disabled={cancellingId === b.id}
                  onClick={() => void handleCancel(b.id)}
                  className="mt-3 text-[13px] text-[var(--color-marriott-red)] hover:underline disabled:opacity-50 inline-flex items-center gap-1"
                >
                  {cancellingId === b.id && <Loader2 size={12} className="animate-spin" />}
                  Cancel booking
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
