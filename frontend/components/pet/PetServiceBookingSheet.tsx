"use client";

import { useState } from "react";
import { X } from "lucide-react";
import type { PartnerResponse } from "@/lib/types";
import { MobileServiceBadge } from "./MobileServiceBadge";

interface PetServiceBookingSheetProps {
  partner: PartnerResponse;
  defaultDate: string;
  minDate?: string;
  maxDate?: string;
  onClose: () => void;
  onConfirm: (payload: {
    service_date: string;
    service_time: string;
    notes: string;
  }) => Promise<void>;
}

export function PetServiceBookingSheet({
  partner,
  defaultDate,
  minDate,
  maxDate,
  onClose,
  onConfirm,
}: PetServiceBookingSheetProps): React.ReactElement {
  const [serviceDate, setServiceDate] = useState(defaultDate);
  const [serviceTime, setServiceTime] = useState("10:00");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await onConfirm({ service_date: serviceDate, service_time: serviceTime, notes });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Booking failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} aria-hidden />
      <form
        onSubmit={(e) => void handleSubmit(e)}
        className="relative w-full sm:max-w-md bg-white rounded-t-xl sm:rounded-xl shadow-xl border border-[var(--color-bonvoy-rule)] p-6"
      >
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-1">
              Book pet service
            </p>
            <h3 className="text-[18px] font-medium text-[var(--color-bonvoy-ink)]">
              {partner.name}
            </h3>
            {partner.service_model === "mobile" && (
              <MobileServiceBadge className="mt-2" />
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-[var(--color-bonvoy-muted)] hover:text-[var(--color-bonvoy-ink)]"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        {partner.mobile_service_note && (
          <p className="text-[13px] text-[var(--color-bonvoy-muted)] mb-4 bg-[var(--color-bonvoy-mist)] rounded-md p-3">
            {partner.mobile_service_note}
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <label className="block">
            <span className="text-[12px] uppercase tracking-[0.14em] text-[var(--color-bonvoy-muted)]">
              Service date
            </span>
            <input
              type="date"
              required
              min={minDate}
              max={maxDate}
              value={serviceDate}
              onChange={(e) => setServiceDate(e.target.value)}
              className="mt-1 w-full border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2 text-[14px]"
            />
          </label>
          <label className="block">
            <span className="text-[12px] uppercase tracking-[0.14em] text-[var(--color-bonvoy-muted)]">
              Service time
            </span>
            <input
              type="time"
              required
              value={serviceTime}
              onChange={(e) => setServiceTime(e.target.value)}
              className="mt-1 w-full border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2 text-[14px]"
            />
          </label>
        </div>

        <label className="block mb-4">
          <span className="text-[12px] uppercase tracking-[0.14em] text-[var(--color-bonvoy-muted)]">
            Notes (optional)
          </span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Pet name, special instructions…"
            className="mt-1 w-full border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2 text-[14px] resize-none"
          />
        </label>

        {error && (
          <p className="text-[13px] text-[var(--color-marriott-red)] mb-3">{error}</p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-full bg-[var(--color-marriott-red)] hover:bg-[var(--color-marriott-red-dark)] disabled:opacity-60 text-white py-3 text-[14px] font-medium"
        >
          {submitting ? "Booking…" : "Confirm booking"}
        </button>
      </form>
    </div>
  );
}
