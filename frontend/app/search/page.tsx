"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowDownAZ, Filter, Leaf, PawPrint, X } from "lucide-react";
import { hotels as hotelsApi } from "@/lib/api";
import type { HotelListItem } from "@/lib/types";
import { HotelCard } from "@/components/hotels/HotelCard";
import { cn } from "@/lib/utils";

type SortKey = "eco_desc" | "price_asc" | "price_desc" | "rating_desc";

export default function SearchPageWrapper(): React.ReactElement {
  return (
    <Suspense
      fallback={
        <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)] py-10 px-6">
          <p className="text-[var(--color-bonvoy-muted)]">Loading…</p>
        </div>
      }
    >
      <SearchPage />
    </Suspense>
  );
}

function applySort(list: HotelListItem[], key: SortKey): HotelListItem[] {
  const copy = [...list];
  switch (key) {
    case "price_asc":
      return copy.sort((a, b) => a.price_per_night - b.price_per_night);
    case "price_desc":
      return copy.sort((a, b) => b.price_per_night - a.price_per_night);
    case "rating_desc":
      return copy.sort((a, b) => b.rating - a.rating);
    case "eco_desc":
    default:
      return copy.sort((a, b) => b.eco_score - a.eco_score);
  }
}

const CITIES = ["New York", "Washington", "Chicago", "Miami"];

function SearchPage(): React.ReactElement {
  const router = useRouter();
  const params = useSearchParams();

  const initialCity = params.get("city") ?? "";
  const initialPet = params.get("pet_friendly") === "true";
  const initialMinEco = Number(params.get("min_eco") ?? "0");

  const [city, setCity] = useState(initialCity);
  const [pet, setPet] = useState(initialPet);
  const [minEco, setMinEco] = useState(initialMinEco);
  const [sort, setSort] = useState<SortKey>("eco_desc");
  const [list, setList] = useState<HotelListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtersOpen, setFiltersOpen] = useState(false);

  useEffect(() => {
    setLoading(true);
    hotelsApi
      .list({
        city: city || undefined,
        pet_friendly: pet || undefined,
        min_eco: minEco > 0 ? minEco : undefined,
      })
      .then(setList)
      .catch(() => setList([]))
      .finally(() => setLoading(false));
  }, [city, pet, minEco]);

  // Keep the URL in sync with active filters so the result is shareable.
  useEffect(() => {
    const next = new URLSearchParams();
    if (city) next.set("city", city);
    if (pet) next.set("pet_friendly", "true");
    if (minEco > 0) next.set("min_eco", String(minEco));
    const qs = next.toString();
    router.replace(qs ? `/search?${qs}` : "/search", { scroll: false });
  }, [city, pet, minEco, router]);

  const sorted = useMemo(() => applySort(list, sort), [list, sort]);

  const Filters = (
    <div className="space-y-7">
      <section>
        <h4 className="text-[12px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-3">
          Destination
        </h4>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-[13px]">
            <input
              type="radio"
              name="city"
              checked={city === ""}
              onChange={() => setCity("")}
              className="accent-[var(--color-marriott-red)]"
            />
            All cities
          </label>
          {CITIES.map((c) => (
            <label key={c} className="flex items-center gap-2 text-[13px]">
              <input
                type="radio"
                name="city"
                checked={city === c}
                onChange={() => setCity(c)}
                className="accent-[var(--color-marriott-red)]"
              />
              {c}
            </label>
          ))}
        </div>
      </section>

      <section>
        <h4 className="text-[12px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-3">
          Traveling with pets
        </h4>
        <label className="flex items-center gap-2 text-[13px]">
          <input
            type="checkbox"
            checked={pet}
            onChange={(e) => setPet(e.target.checked)}
            className="accent-[var(--color-marriott-red)]"
          />
          Show pet-friendly only
        </label>
      </section>

      <section>
        <h4 className="text-[12px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] mb-3">
          Eco rating ≥ {minEco.toFixed(1)}
        </h4>
        <input
          type="range"
          min={0}
          max={10}
          step={0.5}
          value={minEco}
          onChange={(e) => setMinEco(Number(e.target.value))}
          className="w-full accent-[var(--color-marriott-red)]"
        />
        <div className="mt-2 flex justify-between text-[11px] text-[var(--color-bonvoy-muted)]">
          <span>Any</span>
          <span>10.0</span>
        </div>
      </section>

      <button
        onClick={() => {
          setCity("");
          setPet(false);
          setMinEco(0);
        }}
        className="text-[13px] text-[var(--color-marriott-red)] hover:underline"
      >
        Reset filters
      </button>
    </div>
  );

  return (
    <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-[1280px] px-6 py-10">
        <div className="mb-6">
          <p className="text-[12px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-2">
            Hotels
          </p>
          <h1 className="heading-display text-3xl md:text-4xl text-[var(--color-bonvoy-ink)]">
            {city ? `Stays in ${city}` : "Find your stay"}
          </h1>
          <p className="text-[14px] text-[var(--color-bonvoy-muted)] mt-1">
            {loading ? "Searching…" : `${sorted.length} properties`}
            {pet && " · pet-friendly"}
            {minEco > 0 && ` · eco ${minEco.toFixed(1)}+`}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-8">
          {/* Filters — desktop sidebar */}
          <aside className="hidden lg:block bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-5 self-start sticky top-32">
            {Filters}
          </aside>

          {/* Filters — mobile drawer trigger */}
          <button
            onClick={() => setFiltersOpen(true)}
            className="lg:hidden inline-flex items-center gap-2 self-start rounded-full bg-white border border-[var(--color-bonvoy-rule)] px-4 py-2 text-[13px]"
          >
            <Filter size={14} />
            Filters
          </button>

          <div>
            <div className="flex items-center justify-between mb-4 bg-white border border-[var(--color-bonvoy-rule)] rounded-lg px-4 py-3">
              <div className="flex flex-wrap items-center gap-2 text-[12px]">
                {pet && (
                  <span className="inline-flex items-center gap-1 bg-[var(--color-bonvoy-mist)] px-2.5 py-1 rounded-full">
                    <PawPrint size={12} />
                    Pet-friendly
                    <button onClick={() => setPet(false)} aria-label="Remove">
                      <X size={12} />
                    </button>
                  </span>
                )}
                {minEco > 0 && (
                  <span className="inline-flex items-center gap-1 bg-[var(--color-bonvoy-mist)] px-2.5 py-1 rounded-full">
                    <Leaf size={12} />
                    Eco {minEco.toFixed(1)}+
                    <button onClick={() => setMinEco(0)} aria-label="Remove">
                      <X size={12} />
                    </button>
                  </span>
                )}
                {!pet && minEco === 0 && (
                  <span className="text-[var(--color-bonvoy-muted)]">
                    No filters applied
                  </span>
                )}
              </div>
              <label className="inline-flex items-center gap-2 text-[13px]">
                <ArrowDownAZ size={14} className="text-[var(--color-bonvoy-muted)]" />
                <select
                  value={sort}
                  onChange={(e) => setSort(e.target.value as SortKey)}
                  className="bg-transparent outline-none"
                >
                  <option value="eco_desc">Eco rating (high)</option>
                  <option value="rating_desc">Guest rating (high)</option>
                  <option value="price_asc">Price (low)</option>
                  <option value="price_desc">Price (high)</option>
                </select>
              </label>
            </div>

            {loading ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-[200px] bg-white border border-[var(--color-bonvoy-rule)] rounded-lg animate-pulse"
                  />
                ))}
              </div>
            ) : sorted.length === 0 ? (
              <div className="bg-white rounded-lg border border-[var(--color-bonvoy-rule)] p-10 text-center">
                <p className="text-[15px] text-[var(--color-bonvoy-ink)] mb-1">
                  No hotels match those filters.
                </p>
                <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
                  Try widening the eco rating or selecting a different city.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {sorted.map((h) => (
                  <HotelCard key={h.id} hotel={h} variant="list" />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile filters drawer */}
      {filtersOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setFiltersOpen(false)}
          />
          <div className={cn(
            "absolute right-0 top-0 h-full w-[88%] max-w-[360px] bg-white p-6 overflow-y-auto",
          )}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[18px] font-medium">Filters</h3>
              <button onClick={() => setFiltersOpen(false)} aria-label="Close">
                <X size={20} />
              </button>
            </div>
            {Filters}
            <button
              onClick={() => setFiltersOpen(false)}
              className="mt-6 w-full rounded-full bg-[var(--color-marriott-red)] text-white py-3 text-[14px] font-medium"
            >
              Show {sorted.length} results
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
