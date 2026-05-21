import Link from "next/link";
import { ChevronRight, Leaf, MapPin, PawPrint } from "lucide-react";
import { hotels } from "@/lib/api";
import { HeroSearch } from "@/components/home/HeroSearch";
import { HotelCard } from "@/components/hotels/HotelCard";

export const dynamic = "force-dynamic";

const HERO_IMG =
  "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=2400&q=80";

const RAIL_BACKGROUNDS: Array<{ city: string; img: string }> = [
  {
    city: "New York",
    img: "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=900&q=80",
  },
  {
    city: "Washington",
    img: "https://images.unsplash.com/photo-1617469767053-d3b523a0b982?auto=format&fit=crop&w=900&q=80",
  },
  {
    city: "Chicago",
    img: "https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=900&q=80",
  },
  {
    city: "Miami",
    img: "https://images.unsplash.com/photo-1535498730771-e735b998cd64?auto=format&fit=crop&w=900&q=80",
  },
];

export default async function HomePage(): Promise<React.ReactElement> {
  const list = await hotels.list().catch(() => []);
  const top = list.slice(0, 4);

  return (
    <div>
      {/* HERO */}
      <section className="relative">
        <div
          className="relative h-[560px] md:h-[640px] bg-cover bg-center"
          style={{ backgroundImage: `url(${HERO_IMG})` }}
          aria-hidden
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/30 via-black/15 to-transparent" />
        </div>

        <div className="mx-auto max-w-[1280px] px-6 -mt-[420px] md:-mt-[480px] relative z-10">
          <div className="max-w-2xl text-white pb-6">
            <p className="text-[11px] uppercase tracking-[0.24em] text-white/85 mb-3">
              Marriott Bonvoy
            </p>
            <h1 className="heading-display text-4xl md:text-6xl mb-4 drop-shadow-sm">
              Endless experiences,
              <br />
              one membership.
            </h1>
            <p className="text-[15px] text-white/90 max-w-xl leading-relaxed">
              From flagship city stays to all-inclusive resorts, every Bonvoy
              booking now comes with a personalized eco rating, an arrival
              brief, and a pet-friendly travel map.
            </p>
          </div>

          <div className="max-w-[1100px]">
            <HeroSearch />
          </div>
        </div>
      </section>

      {/* PERSONALIZED FEATURE BANNER */}
      <section className="mx-auto max-w-[1280px] px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: <Leaf size={22} />,
              title: "Eco Rating on every property",
              copy: "A 0–10 sustainability score with energy, water, waste, and certification breakdowns. Earn bonus Green Points on greener stays.",
              cta: "Browse top-rated eco stays",
              href: "/search?min_eco=8",
            },
            {
              icon: <MapPin size={22} />,
              title: "Your Arrival Brief",
              copy: "A curated 1-pager 48 hours before check-in: weather, events, dining picks aligned with your preferences, and transit options.",
              cta: "See a sample brief",
              href: "/trips",
            },
            {
              icon: <PawPrint size={22} />,
              title: "Travel together",
              copy: "Pet-friendly stays plus an interactive map of vets, dog parks, and pet supply stops near your hotel — reserved with your room.",
              cta: "Find pet-friendly hotels",
              href: "/search?pet_friendly=true",
            },
          ].map((b) => (
            <Link
              key={b.title}
              href={b.href}
              className="group block border-t-2 border-[var(--color-marriott-red)] pt-6"
            >
              <div className="text-[var(--color-marriott-red)] mb-4">{b.icon}</div>
              <h3 className="text-[20px] font-medium text-[var(--color-bonvoy-ink)] mb-2 leading-snug">
                {b.title}
              </h3>
              <p className="text-[14px] text-[var(--color-bonvoy-muted)] mb-4 leading-relaxed">
                {b.copy}
              </p>
              <span className="inline-flex items-center gap-1 text-[13px] font-medium text-[var(--color-marriott-red)] group-hover:gap-2 transition-all">
                {b.cta}
                <ChevronRight size={14} />
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* TOP DESTINATIONS */}
      <section className="mx-auto max-w-[1280px] px-6 pb-16">
        <div className="flex items-end justify-between mb-6">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-2">
              Top destinations
            </p>
            <h2 className="heading-display text-3xl md:text-4xl text-[var(--color-bonvoy-ink)]">
              Where Bonvoy members are going.
            </h2>
          </div>
          <Link
            href="/search"
            className="hidden sm:inline-flex items-center gap-1 text-[13px] font-medium text-[var(--color-marriott-red)] hover:gap-2 transition-all"
          >
            View all hotels
            <ChevronRight size={14} />
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {RAIL_BACKGROUNDS.map((d) => (
            <Link
              key={d.city}
              href={`/search?city=${encodeURIComponent(d.city)}`}
              className="group relative aspect-[3/4] rounded-lg overflow-hidden"
            >
              <div
                className="absolute inset-0 bg-cover bg-center group-hover:scale-105 transition-transform duration-500"
                style={{ backgroundImage: `url(${d.img})` }}
                aria-hidden
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />
              <div className="absolute inset-x-4 bottom-4 text-white">
                <h3 className="text-[20px] font-medium">{d.city}</h3>
                <p className="text-[12px] text-white/80 inline-flex items-center gap-1">
                  Explore stays <ChevronRight size={12} />
                </p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* FEATURED HOTELS */}
      <section className="bg-[var(--color-bonvoy-mist)]">
        <div className="mx-auto max-w-[1280px] px-6 py-16">
          <div className="flex items-end justify-between mb-6">
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-2">
                Featured stays
              </p>
              <h2 className="heading-display text-3xl md:text-4xl text-[var(--color-bonvoy-ink)]">
                Highly-rated, eco-leading hotels.
              </h2>
              <p className="text-[14px] text-[var(--color-bonvoy-muted)] mt-2 max-w-xl">
                Our top properties by Eco Rating. Every score is computed from
                MESH-style energy, water, waste, certification, and F&amp;B
                sourcing data.
              </p>
            </div>
            <Link
              href="/search"
              className="hidden sm:inline-flex items-center gap-1 text-[13px] font-medium text-[var(--color-marriott-red)] hover:gap-2 transition-all"
            >
              Browse all
              <ChevronRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {top.map((h) => (
              <HotelCard key={h.id} hotel={h} />
            ))}
          </div>
        </div>
      </section>

      {/* DEMO BANNER */}
      <section className="bg-[var(--color-marriott-red)] text-white">
        <div className="mx-auto max-w-[1280px] px-6 py-12 grid grid-cols-1 md:grid-cols-[1fr_auto] items-center gap-6">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-white/80 mb-2">
              Codefest demo
            </p>
            <h3 className="heading-display text-2xl md:text-3xl">
              Switch personas to see the experience adapt.
            </h3>
            <p className="text-[14px] text-white/85 mt-2 max-w-2xl">
              Three Bonvoy guests are pre-loaded — Alex (eco-minded), Jordan
              (traveling with a dog), and Sam (vegan, accessibility needs).
              Their preferences drive every screen.
            </p>
          </div>
          <Link
            href="/sign-in"
            className="justify-self-start md:justify-self-end inline-flex items-center gap-2 rounded-full bg-white text-[var(--color-marriott-red)] px-6 py-3 text-[14px] font-medium hover:bg-white/90 transition-colors"
          >
            Try a persona
            <ChevronRight size={14} />
          </Link>
        </div>
      </section>
    </div>
  );
}
