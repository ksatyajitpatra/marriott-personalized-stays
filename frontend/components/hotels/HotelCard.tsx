import Link from "next/link";
import { PawPrint, Star } from "lucide-react";
import type { HotelListItem } from "@/lib/types";
import { formatUsd, cityHeroImage } from "@/lib/utils";
import { EcoScoreRing } from "@/components/eco/EcoScoreRing";

interface HotelCardProps {
  hotel: HotelListItem;
  variant?: "rail" | "list";
}

/**
 * Marriott.com-style property card. The rail variant is denser (used on
 * the homepage carousel); the list variant is wide (used on /search).
 */
export function HotelCard({
  hotel,
  variant = "rail",
}: HotelCardProps): React.ReactElement {
  if (variant === "list") {
    return (
      <Link
        href={`/hotels/${hotel.id}`}
        className="group grid grid-cols-1 md:grid-cols-[280px_1fr_220px] gap-6 bg-white border border-[var(--color-bonvoy-rule)] rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
      >
        <div
          className="aspect-[4/3] md:aspect-auto md:h-full bg-cover bg-center"
          style={{ backgroundImage: `url(${hotel.image_url}), url(${cityHeroImage(hotel.city)})` }}
          aria-hidden
        />
        <div className="px-1 md:px-2 py-5 min-w-0">
          <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)] mb-1">
            {hotel.brand}
          </p>
          <h3 className="text-[20px] font-medium text-[var(--color-bonvoy-ink)] mb-1 group-hover:text-[var(--color-marriott-red)] transition-colors">
            {hotel.name}
          </h3>
          <p className="text-[13px] text-[var(--color-bonvoy-muted)] mb-3">
            {hotel.address}
          </p>
          <p className="text-[14px] text-[var(--color-bonvoy-ink)] line-clamp-2 mb-3">
            {hotel.tagline}
          </p>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[13px]">
            <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-ink)]">
              <Star size={14} className="fill-[var(--color-bonvoy-ink)]" />
              {hotel.rating.toFixed(1)}
            </span>
            {hotel.pet_friendly && (
              <span className="inline-flex items-center gap-1 text-[var(--color-bonvoy-muted)]">
                <PawPrint size={14} />
                Pet-friendly
              </span>
            )}
            <EcoScoreRing
              score={hotel.eco_score}
              color={hotel.eco_color}
              size={36}
              label="Eco"
            />
          </div>
        </div>
        <div className="px-5 py-5 md:border-l border-[var(--color-bonvoy-rule)] flex flex-col items-end justify-between gap-3 bg-[var(--color-bonvoy-mist)] md:bg-transparent">
          <div className="text-right">
            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)]">
              From
            </p>
            <p className="text-[26px] font-medium text-[var(--color-bonvoy-ink)] leading-tight">
              {formatUsd(hotel.price_per_night)}
              <span className="text-[12px] font-normal text-[var(--color-bonvoy-muted)]">
                {" "}
                /night
              </span>
            </p>
          </div>
          <span className="inline-flex items-center justify-center w-full md:w-auto rounded-full bg-[var(--color-marriott-red)] text-white px-5 py-2 text-[13px] font-medium group-hover:bg-[var(--color-marriott-red-dark)] transition-colors">
            View Hotel
          </span>
        </div>
      </Link>
    );
  }

  return (
    <Link
      href={`/hotels/${hotel.id}`}
      className="group block bg-white rounded-lg overflow-hidden border border-[var(--color-bonvoy-rule)] hover:shadow-md transition-shadow"
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center group-hover:scale-[1.03] transition-transform duration-500"
          style={{ backgroundImage: `url(${hotel.image_url}), url(${cityHeroImage(hotel.city)})` }}
          aria-hidden
        />
        <div className="absolute top-3 right-3 bg-white rounded-full p-1 shadow-sm">
          <EcoScoreRing
            score={hotel.eco_score}
            color={hotel.eco_color}
            size={42}
          />
        </div>
        {hotel.pet_friendly && (
          <span className="absolute bottom-3 left-3 inline-flex items-center gap-1 bg-white/95 text-[11px] uppercase tracking-[0.14em] text-[var(--color-bonvoy-ink)] px-2.5 py-1 rounded-full">
            <PawPrint size={12} />
            Pet-friendly
          </span>
        )}
      </div>
      <div className="p-4">
        <p className="text-[10px] uppercase tracking-[0.18em] text-[var(--color-bonvoy-muted)] mb-1">
          {hotel.brand}
        </p>
        <h3 className="text-[16px] font-medium text-[var(--color-bonvoy-ink)] mb-1 leading-snug">
          {hotel.name}
        </h3>
        <p className="text-[12px] text-[var(--color-bonvoy-muted)] mb-3">
          {hotel.city}, {hotel.state}
        </p>
        <div className="flex items-baseline justify-between">
          <span className="inline-flex items-center gap-1 text-[12px] text-[var(--color-bonvoy-ink)]">
            <Star size={12} className="fill-[var(--color-bonvoy-ink)]" />
            {hotel.rating.toFixed(1)}
          </span>
          <span className="text-[14px] font-medium text-[var(--color-bonvoy-ink)]">
            {formatUsd(hotel.price_per_night)}
            <span className="text-[11px] font-normal text-[var(--color-bonvoy-muted)]">
              {" "}
              /night
            </span>
          </span>
        </div>
      </div>
    </Link>
  );
}
