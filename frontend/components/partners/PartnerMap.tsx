"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import { PawPrint, Phone, Star } from "lucide-react";
import type { HotelDetail, PartnerResponse } from "@/lib/types";
import { partners as partnersApi } from "@/lib/api";
import { cn } from "@/lib/utils";

const TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

const CATEGORY_LABEL: Record<string, string> = {
  vet_emergency: "Vet · 24h",
  dog_walker: "Dog walker",
  dog_park: "Dog park",
  pet_supply: "Pet supply",
  vegan_restaurant: "Vegan dining",
  restaurant: "Restaurant",
  bike_rental: "Bike rental",
  refill_station: "Water refill",
  ev_charging: "EV charging",
  local_experience: "Local experience",
};

const CATEGORY_COLOR: Record<string, string> = {
  vet_emergency: "#A6192E",
  dog_walker: "#1f8a4c",
  dog_park: "#1f8a4c",
  pet_supply: "#7a4f1d",
  vegan_restaurant: "#1f8a4c",
  restaurant: "#1a1a1a",
  bike_rental: "#0f6cbf",
  refill_station: "#0f6cbf",
  ev_charging: "#0f6cbf",
  local_experience: "#7a3a8e",
};

type Filter = "all" | "pet" | "dining" | "experiences";

const FILTER_CATEGORIES: Record<Filter, string[]> = {
  all: [],
  pet: ["vet_emergency", "dog_walker", "dog_park", "pet_supply"],
  dining: ["vegan_restaurant", "restaurant"],
  experiences: ["bike_rental", "refill_station", "ev_charging", "local_experience"],
};

interface PartnerMapProps {
  hotel: HotelDetail;
}

export function PartnerMap({ hotel }: PartnerMapProps): React.ReactElement {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  const [list, setList] = useState<PartnerResponse[]>([]);
  const [filter, setFilter] = useState<Filter>(hotel.pet_friendly ? "pet" : "all");
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    partnersApi
      .nearby({ hotel_id: hotel.id, max_miles: 5 })
      .then(setList)
      .catch(() => setList([]))
      .finally(() => setLoading(false));
  }, [hotel.id]);

  // Init map only once
  useEffect(() => {
    if (!TOKEN || !containerRef.current || mapRef.current) return;
    mapboxgl.accessToken = TOKEN;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [hotel.lng, hotel.lat],
      zoom: 13.5,
      attributionControl: false,
    });
    map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right");
    mapRef.current = map;

    // Hotel marker (Marriott red, larger)
    const hotelEl = document.createElement("div");
    hotelEl.style.cssText =
      "width:24px;height:24px;border-radius:50%;background:#A6192E;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,.25);";
    new mapboxgl.Marker({ element: hotelEl })
      .setLngLat([hotel.lng, hotel.lat])
      .setPopup(
        new mapboxgl.Popup({ offset: 16 }).setHTML(
          `<div style="font:500 13px system-ui;padding:2px 4px"><span style="color:#A6192E">★ ${hotel.name}</span></div>`,
        ),
      )
      .addTo(map);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [hotel.lat, hotel.lng, hotel.name]);

  // Re-render partner markers whenever list/filter changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const visible = visibleList(list, filter);
    visible.forEach((p) => {
      const el = document.createElement("button");
      el.style.cssText = `width:14px;height:14px;border-radius:50%;background:${
        CATEGORY_COLOR[p.category] ?? "#1a1a1a"
      };border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,.2);cursor:pointer`;
      el.setAttribute("aria-label", p.name);
      el.onclick = () => setActive(p.id);
      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([p.lng, p.lat])
        .addTo(map);
      markersRef.current.push(marker);
    });
  }, [list, filter]);

  const visible = visibleList(list, filter);
  const activePartner = visible.find((p) => p.id === active) ?? null;

  return (
    <div className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg overflow-hidden">
      <div className="p-5 border-b border-[var(--color-bonvoy-rule)]">
        <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-marriott-red)] mb-1">
          Around the property
        </p>
        <h3 className="text-[20px] font-medium text-[var(--color-bonvoy-ink)] mb-3">
          Pet + Local Partner Map
        </h3>
        <div className="flex flex-wrap gap-2">
          {(["all", "pet", "dining", "experiences"] as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-full px-3 py-1 text-[12px] border",
                filter === f
                  ? "bg-[var(--color-bonvoy-ink)] text-white border-[var(--color-bonvoy-ink)]"
                  : "bg-white text-[var(--color-bonvoy-ink)] border-[var(--color-bonvoy-rule)] hover:border-[var(--color-bonvoy-ink)]",
              )}
            >
              {f === "all"
                ? `All (${list.length})`
                : f === "pet"
                  ? "Pet"
                  : f === "dining"
                    ? "Dining"
                    : "Experiences"}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_320px]">
        <div className="relative">
          {TOKEN ? (
            <div ref={containerRef} className="h-[420px] md:h-[520px] w-full" />
          ) : (
            <NoTokenFallback hotel={hotel} list={visible} />
          )}
          {activePartner && (
            <div className="absolute left-4 bottom-4 right-4 md:right-auto md:max-w-sm bg-white rounded-lg shadow-xl border border-[var(--color-bonvoy-rule)] p-4 text-[13px]">
              <div className="flex items-start justify-between gap-3 mb-1">
                <div>
                  <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)]">
                    {CATEGORY_LABEL[activePartner.category] ?? activePartner.category}
                  </p>
                  <h4 className="font-medium text-[var(--color-bonvoy-ink)] text-[15px]">
                    {activePartner.name}
                  </h4>
                </div>
                <button
                  onClick={() => setActive(null)}
                  className="text-[var(--color-bonvoy-muted)] hover:text-[var(--color-bonvoy-ink)]"
                  aria-label="Close"
                >
                  ×
                </button>
              </div>
              <p className="text-[12px] text-[var(--color-bonvoy-muted)] mb-2">
                {activePartner.address}
              </p>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
                <span className="inline-flex items-center gap-1">
                  <Star size={12} />
                  {activePartner.rating.toFixed(1)}
                </span>
                <span>{activePartner.distance_miles.toFixed(1)} mi</span>
                {activePartner.phone && (
                  <a
                    href={`tel:${activePartner.phone}`}
                    className="inline-flex items-center gap-1 text-[var(--color-marriott-red)]"
                  >
                    <Phone size={12} />
                    {activePartner.phone}
                  </a>
                )}
              </div>
              {activePartner.note && (
                <p className="mt-2 text-[12px] text-[var(--color-bonvoy-muted)]">
                  {activePartner.note}
                </p>
              )}
            </div>
          )}
        </div>

        <aside className="border-l border-[var(--color-bonvoy-rule)] max-h-[520px] overflow-y-auto">
          {loading ? (
            <div className="p-5 text-[13px] text-[var(--color-bonvoy-muted)]">
              Finding partners…
            </div>
          ) : visible.length === 0 ? (
            <div className="p-5 text-[13px] text-[var(--color-bonvoy-muted)]">
              No partners match this filter within 5 miles.
            </div>
          ) : (
            <ul>
              {visible.map((p) => (
                <li key={p.id} className="border-b border-[var(--color-bonvoy-rule)] last:border-b-0">
                  <button
                    onClick={() => {
                      setActive(p.id);
                      mapRef.current?.flyTo({
                        center: [p.lng, p.lat],
                        zoom: 14.5,
                      });
                    }}
                    className={cn(
                      "w-full text-left px-4 py-3 hover:bg-[var(--color-bonvoy-mist)] transition-colors",
                      active === p.id && "bg-[var(--color-bonvoy-mist)]",
                    )}
                  >
                    <div className="flex items-start justify-between gap-2 mb-0.5">
                      <span
                        className="inline-block h-2 w-2 rounded-full mt-1.5 flex-shrink-0"
                        style={{ background: CATEGORY_COLOR[p.category] ?? "#1a1a1a" }}
                        aria-hidden
                      />
                      <span className="flex-1 min-w-0">
                        <span className="block text-[13px] font-medium text-[var(--color-bonvoy-ink)] truncate">
                          {p.name}
                        </span>
                        <span className="block text-[11px] text-[var(--color-bonvoy-muted)]">
                          {CATEGORY_LABEL[p.category] ?? p.category} · {p.distance_miles.toFixed(1)} mi
                        </span>
                      </span>
                      {p.pet_relevant && (
                        <PawPrint size={12} className="text-[var(--color-bonvoy-muted)]" />
                      )}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>

      {!TOKEN && (
        <p className="px-5 py-3 text-[12px] text-[var(--color-bonvoy-muted)] border-t border-[var(--color-bonvoy-rule)] bg-[var(--color-bonvoy-mist)]">
          Set <code className="font-mono">NEXT_PUBLIC_MAPBOX_TOKEN</code> in
          <code className="font-mono"> frontend/.env.local</code> to enable the
          interactive map.
        </p>
      )}
    </div>
  );
}

function visibleList(list: PartnerResponse[], filter: Filter): PartnerResponse[] {
  if (filter === "all") return list;
  const allowed = new Set(FILTER_CATEGORIES[filter]);
  return list.filter((p) => allowed.has(p.category));
}

function NoTokenFallback({
  hotel,
  list,
}: {
  hotel: HotelDetail;
  list: PartnerResponse[];
}): React.ReactElement {
  return (
    <div className="h-[420px] md:h-[520px] bg-[var(--color-bonvoy-mist)] flex flex-col items-center justify-center p-6 text-center">
      <p className="text-[12px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)] mb-2">
        Map preview unavailable
      </p>
      <p className="text-[14px] text-[var(--color-bonvoy-ink)] mb-3">
        Add a Mapbox token to see {list.length} partners around {hotel.name}.
      </p>
    </div>
  );
}
