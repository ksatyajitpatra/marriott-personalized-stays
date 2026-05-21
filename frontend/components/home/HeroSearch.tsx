"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { CalendarDays, MapPin, Search, Users } from "lucide-react";

const POPULAR_DESTS = ["New York", "Washington", "Chicago", "Miami"];

/**
 * "Where can we take you?" search card. We don't run real availability —
 * the search routes to /search?city=… which calls the backend. Date and
 * guest fields are visual fidelity only.
 */
export function HeroSearch(): React.ReactElement {
  const router = useRouter();
  const today = new Date();
  const inDefault = today.toISOString().slice(0, 10);
  const out = new Date(today.getTime() + 2 * 86400000).toISOString().slice(0, 10);

  const [city, setCity] = useState("");
  const [checkIn, setCheckIn] = useState(inDefault);
  const [checkOut, setCheckOut] = useState(out);
  const [guests, setGuests] = useState(2);
  const [petFriendly, setPetFriendly] = useState(false);

  function submit(e: React.FormEvent): void {
    e.preventDefault();
    const params = new URLSearchParams();
    if (city) params.set("city", city);
    if (petFriendly) params.set("pet_friendly", "true");
    router.push(`/search?${params.toString()}`);
  }

  return (
    <form
      onSubmit={submit}
      className="bg-white rounded-lg shadow-2xl border border-[var(--color-bonvoy-rule)] p-5 md:p-6"
    >
      <h2 className="text-[20px] font-medium text-[var(--color-bonvoy-ink)] mb-5">
        Where can we take you?
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-[1.5fr_1fr_1fr_0.8fr] gap-3">
        <label className="block">
          <span className="block text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-1">
            Destination
          </span>
          <div className="flex items-center gap-2 border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2.5 focus-within:border-[var(--color-bonvoy-ink)]">
            <MapPin size={16} className="text-[var(--color-bonvoy-muted)]" />
            <input
              list="popular-dests"
              type="text"
              placeholder="City, hotel, address"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="flex-1 bg-transparent outline-none text-[14px]"
            />
            <datalist id="popular-dests">
              {POPULAR_DESTS.map((d) => (
                <option key={d} value={d} />
              ))}
            </datalist>
          </div>
        </label>

        <label className="block">
          <span className="block text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-1">
            Check-in
          </span>
          <div className="flex items-center gap-2 border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2.5">
            <CalendarDays size={16} className="text-[var(--color-bonvoy-muted)]" />
            <input
              type="date"
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
              className="flex-1 bg-transparent outline-none text-[14px]"
            />
          </div>
        </label>

        <label className="block">
          <span className="block text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-1">
            Check-out
          </span>
          <div className="flex items-center gap-2 border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2.5">
            <CalendarDays size={16} className="text-[var(--color-bonvoy-muted)]" />
            <input
              type="date"
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
              className="flex-1 bg-transparent outline-none text-[14px]"
            />
          </div>
        </label>

        <label className="block">
          <span className="block text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-1">
            Guests
          </span>
          <div className="flex items-center gap-2 border border-[var(--color-bonvoy-rule)] rounded-md px-3 py-2.5">
            <Users size={16} className="text-[var(--color-bonvoy-muted)]" />
            <select
              value={guests}
              onChange={(e) => setGuests(Number(e.target.value))}
              className="flex-1 bg-transparent outline-none text-[14px]"
            >
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <option key={n} value={n}>
                  {n} {n === 1 ? "Guest" : "Guests"}
                </option>
              ))}
            </select>
          </div>
        </label>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mt-4">
        <label className="inline-flex items-center gap-2 text-[13px] text-[var(--color-bonvoy-ink)]">
          <input
            type="checkbox"
            checked={petFriendly}
            onChange={(e) => setPetFriendly(e.target.checked)}
            className="h-4 w-4 accent-[var(--color-marriott-red)]"
          />
          Traveling with a pet
        </label>
        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-full bg-[var(--color-marriott-red)] hover:bg-[var(--color-marriott-red-dark)] text-white px-7 py-3 text-[14px] font-medium transition-colors"
        >
          <Search size={16} />
          Find Hotels
        </button>
      </div>
    </form>
  );
}
