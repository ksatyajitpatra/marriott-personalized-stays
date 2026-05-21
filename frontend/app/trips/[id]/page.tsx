"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  ChevronLeft,
  Cloud,
  CloudRain,
  CloudSnow,
  Leaf,
  Luggage,
  MapPin,
  PartyPopper,
  Sparkles,
  Sun,
  Train,
  UtensilsCrossed,
} from "lucide-react";
import {
  ApiError,
  arrivalBrief,
  hotels as hotelsApi,
  reservations as resApi,
} from "@/lib/api";
import type {
  ArrivalBriefResponse,
  HotelDetail,
  ReservationResponse,
  WeatherDay,
} from "@/lib/types";
import { formatDate, formatShortDate, cityHeroImage } from "@/lib/utils";
import { useAuthStore } from "@/lib/auth-store";
import { useProfileStore } from "@/lib/profile-store";
import { PetServiceBookingList } from "@/components/pet/PetServiceBookingList";
import { PartnerMap } from "@/components/partners/PartnerMap";

const ICONS: Record<WeatherDay["icon"], React.ReactNode> = {
  sun: <Sun size={20} />,
  partly: <Cloud size={20} />,
  cloud: <Cloud size={20} />,
  rain: <CloudRain size={20} />,
  snow: <CloudSnow size={20} />,
};

export default function TripDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}): React.ReactElement {
  const router = useRouter();
  const guest = useAuthStore((s) => s.guest);
  const hydrated = useAuthStore((s) => s.hydrated);
  const radiusMiles = useProfileStore((s) => s.radiusMiles);
  const loadProfile = useProfileStore((s) => s.loadProfile);
  const setRadiusMiles = useProfileStore((s) => s.setRadiusMiles);

  const [id, setId] = useState<string | null>(null);
  const [reservation, setReservation] = useState<ReservationResponse | null>(null);
  const [hotel, setHotel] = useState<HotelDetail | null>(null);
  const [brief, setBrief] = useState<ArrivalBriefResponse | null>(null);
  const [error, setError] = useState<"unauthorized" | "notfound" | "other" | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void params.then((p) => setId(p.id));
  }, [params]);

  useEffect(() => {
    if (!hydrated || !id) return;
    if (!guest) {
      router.replace(`/sign-in?next=/trips/${id}`);
      return;
    }
    void loadProfile();
  }, [guest, hydrated, id, loadProfile, router]);

  async function reloadTrip(tripId: string): Promise<void> {
    const r = await resApi.get(tripId);
    setReservation(r);
  }

  useEffect(() => {
    if (!hydrated || !id) return;
    if (!guest) return;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const r = await resApi.get(id);
        setReservation(r);
        const h = await hotelsApi.get(r.hotel_id).catch(() => null);
        setHotel(h);
        const b = await arrivalBrief.get(id).catch(() => null);
        setBrief(b);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          setError("unauthorized");
        } else if (err instanceof ApiError && err.status === 404) {
          setError("notfound");
        } else {
          setError("other");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [guest, hydrated, id, router]);

  if (!hydrated || loading) {
    return (
      <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)] py-10 px-6">
        <div className="mx-auto max-w-[1100px]">
          <div className="h-64 bg-white rounded-lg border border-[var(--color-bonvoy-rule)] animate-pulse mb-6" />
          <div className="h-40 bg-white rounded-lg border border-[var(--color-bonvoy-rule)] animate-pulse" />
        </div>
      </div>
    );
  }

  if (error === "notfound" || !reservation) {
    return (
      <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)] py-16 px-6 text-center">
        <h1 className="heading-display text-3xl mb-2">Trip not found</h1>
        <p className="text-[var(--color-bonvoy-muted)] mb-6">
          This reservation isn&rsquo;t in your account.
        </p>
        <Link
          href="/trips"
          className="inline-flex items-center gap-1 text-[var(--color-marriott-red)]"
        >
          <ChevronLeft size={14} /> Back to trips
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-[1100px] px-6 py-10">
        <Link
          href="/trips"
          className="inline-flex items-center gap-1 text-[13px] text-[var(--color-bonvoy-muted)] hover:text-[var(--color-marriott-red)] mb-5"
        >
          <ChevronLeft size={14} />
          All trips
        </Link>

        <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg overflow-hidden mb-8">
          <div
            className="h-48 md:h-64 bg-cover bg-center"
            style={{ backgroundImage: `url(${reservation.hotel_image_url}), url(${cityHeroImage(reservation.hotel_city)})` }}
            aria-hidden
          />
          <div className="p-6 grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4 md:items-end">
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-1">
                Confirmation · {reservation.confirmation_number}
              </p>
              <h1 className="heading-display text-3xl md:text-4xl text-[var(--color-bonvoy-ink)]">
                {reservation.hotel_name}
              </h1>
              <p className="text-[14px] text-[var(--color-bonvoy-muted)] mt-1">
                {reservation.hotel_city}
              </p>
            </div>
            <div className="md:text-right text-[14px] text-[var(--color-bonvoy-ink)]">
              <p className="inline-flex items-center gap-2">
                <Calendar size={14} className="text-[var(--color-bonvoy-muted)]" />
                {formatDate(reservation.check_in)} – {formatDate(reservation.check_out)}
              </p>
              <p className="inline-flex items-center gap-2 mt-1 text-[13px] text-[var(--color-bonvoy-muted)]">
                <Luggage size={14} />
                {reservation.nights} nights · {reservation.room_type}
              </p>
            </div>
          </div>
        </section>

        {!brief ? (
          <div className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-8 text-center">
            <p className="text-[15px] text-[var(--color-bonvoy-ink)] mb-2">
              Your Arrival Brief will appear here.
            </p>
            <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
              Briefs are generated 48 hours before check-in. Check back soon.
            </p>
          </div>
        ) : (
          <>
            <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={14} className="text-[var(--color-marriott-red)]" />
                <span className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-bonvoy-muted)]">
                  Your Arrival Brief
                </span>
              </div>
              <p className="text-[18px] md:text-[20px] text-[var(--color-bonvoy-ink)] leading-relaxed mb-4">
                {brief.greeting}
              </p>
              <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
                Generated{" "}
                {brief.generated_by === "litellm"
                  ? "by TIP.AI"
                  : brief.generated_by === "mock_llm"
                    ? "by mock LLM"
                    : "from a curated brief"}{" "}
                · {new Date(brief.generated_at).toLocaleString()}
              </p>
            </section>

            <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
              <Heading icon={<Sun size={16} />} eyebrow="Forecast">
                Weather while you&rsquo;re here
              </Heading>
              <p className="text-[14px] text-[var(--color-bonvoy-ink)] mb-5">
                {brief.weather_summary}
              </p>
              {brief.weather_forecast.length > 0 && (
                <ul className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {brief.weather_forecast.map((d) => (
                    <li
                      key={d.date}
                      className="border border-[var(--color-bonvoy-rule)] rounded-md p-3 text-center"
                    >
                      <p className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)]">
                        {formatShortDate(d.date)}
                      </p>
                      <div className="my-2 inline-flex text-[var(--color-marriott-red)]">
                        {ICONS[d.icon]}
                      </div>
                      <p className="text-[14px] font-medium text-[var(--color-bonvoy-ink)]">
                        {d.high_c.toFixed(0)}° / {d.low_c.toFixed(0)}°C
                      </p>
                      <p className="text-[11px] text-[var(--color-bonvoy-muted)] truncate">
                        {d.summary}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {brief.packing_tips.length > 0 && (
              <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
                <Heading icon={<Luggage size={16} />} eyebrow="Pack smart">
                  What to bring
                </Heading>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-[14px] text-[var(--color-bonvoy-ink)]">
                  {brief.packing_tips.map((t) => (
                    <li key={t} className="flex gap-2">
                      <span className="text-[var(--color-marriott-red)]">·</span>
                      {t}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {brief.events.length > 0 && (
              <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
                <Heading icon={<PartyPopper size={16} />} eyebrow="Happening nearby">
                  Curated for your interests
                </Heading>
                <ul className="space-y-4">
                  {brief.events.map((e, i) => (
                    <li
                      key={i}
                      className="grid grid-cols-1 sm:grid-cols-[120px_1fr] gap-2 sm:gap-5 py-3 border-b border-[var(--color-bonvoy-rule)] last:border-b-0"
                    >
                      <div className="text-[12px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)]">
                        {formatShortDate(e.date)}
                        <br />
                        <span className="text-[10px] text-[var(--color-bonvoy-muted)]">
                          {e.type}
                        </span>
                      </div>
                      <div>
                        <h4 className="text-[16px] font-medium text-[var(--color-bonvoy-ink)] mb-1">
                          {e.name}
                        </h4>
                        <p className="text-[13px] text-[var(--color-bonvoy-muted)] leading-relaxed">
                          {e.why_youll_love_it}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {brief.dining.length > 0 && (
              <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6 md:p-8 mb-6">
                <Heading icon={<UtensilsCrossed size={16} />} eyebrow="Dining picks">
                  Aligned with your preferences
                </Heading>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {brief.dining.map((d, i) => (
                    <li
                      key={i}
                      className="border border-[var(--color-bonvoy-rule)] rounded-md p-4"
                    >
                      <div className="flex items-center justify-between gap-3 mb-1">
                        <h4 className="text-[15px] font-medium text-[var(--color-bonvoy-ink)]">
                          {d.name}
                        </h4>
                        <span className="text-[11px] uppercase tracking-[0.16em] text-[var(--color-bonvoy-muted)] flex-shrink-0">
                          {d.cuisine}
                        </span>
                      </div>
                      <p className="text-[12px] text-[var(--color-eco-green)] mb-1">
                        {d.dietary_match}
                      </p>
                      <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
                        {d.note}
                      </p>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
                <Heading icon={<Train size={16} />} eyebrow="Getting around">
                  Transit
                </Heading>
                <p className="text-[14px] text-[var(--color-bonvoy-ink)] leading-relaxed">
                  {brief.transit}
                </p>
              </section>
              <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
                <Heading icon={<MapPin size={16} />} eyebrow="On property">
                  Property note
                </Heading>
                <p className="text-[14px] text-[var(--color-bonvoy-ink)] leading-relaxed">
                  {brief.property_note}
                </p>
              </section>
            </div>

            {brief.eco_note && (
              <section className="bg-[var(--color-bonvoy-ink)] text-white rounded-lg p-6 md:p-8 flex gap-4">
                <Leaf
                  size={20}
                  className="text-[var(--color-eco-green)] flex-shrink-0 mt-0.5"
                />
                <div>
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/60 mb-1">
                    Sustainability note
                  </p>
                  <p className="text-[14px] leading-relaxed text-white/90">
                    {brief.eco_note}
                  </p>
                </div>
              </section>
            )}
          </>
        )}

        <PetServiceBookingList
          bookings={reservation.pet_service_bookings}
          reservationId={reservation.id}
          onCancel={async (bookingId) => {
            await resApi.cancelPetService(reservation.id, bookingId);
            await reloadTrip(reservation.id);
          }}
        />

        {reservation.has_pet && hotel && (
          <section className="mb-8">
            <PartnerMap
              hotel={hotel}
              reservationId={reservation.id}
              hasPetStay={reservation.has_pet}
              radiusMiles={radiusMiles}
              stayCheckIn={reservation.check_in}
              stayCheckOut={reservation.check_out}
              onRadiusChange={(m) => void setRadiusMiles(m)}
              onServiceBooked={() => void reloadTrip(reservation.id)}
              defaultServiceDate={reservation.check_in}
            />
          </section>
        )}
      </div>
    </div>
  );
}

function Heading({
  icon,
  eyebrow,
  children,
}: {
  icon: React.ReactNode;
  eyebrow: string;
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 text-[var(--color-marriott-red)] mb-1.5">
        {icon}
        <span className="text-[11px] uppercase tracking-[0.2em]">{eyebrow}</span>
      </div>
      <h3 className="text-[20px] md:text-[22px] font-medium text-[var(--color-bonvoy-ink)]">
        {children}
      </h3>
    </div>
  );
}
