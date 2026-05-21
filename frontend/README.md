# Marriott Bonvoy Enhanced Experience — Frontend

A Next.js 16 (App Router) frontend that mimics marriott.com&rsquo;s look while
showcasing three additive features: **Eco Rating**, **Arrival Brief**, and
**Pet + Local Partner Map**. See the root `APP_PRD.MD` for the product spec.

## Quick start

1. Make sure the backend is running (`cd ../backend && uvicorn app.main:app --reload`).
2. Copy environment template and add a Mapbox token:
   ```bash
   cp .env.example .env.local
   # then edit .env.local and paste your pk.* Mapbox token
   ```
3. Install + run:
   ```bash
   npm install
   npm run dev
   ```
4. Open <http://localhost:3000>.

## Routes

| Path | What it shows | Backend used |
|---|---|---|
| `/` | Marriott-style hero, search card, featured eco stays | `GET /hotels` |
| `/sign-in` | Persona switcher (Alex / Jordan / Sam) | `GET /guests`, `POST /auth/login` |
| `/search` | Filterable hotel results (city, pet, eco rating) | `GET /hotels?city=&pet_friendly=&min_eco=` |
| `/hotels/[id]` | Detail page with EcoScore breakdown + Mapbox partner map | `GET /hotels/{id}`, `GET /hotels/{id}/eco-score`, `GET /partners/nearby` |
| `/trips` | "My Trips" list (auth required) | `GET /reservations` |
| `/trips/[id]` | Arrival Brief view | `GET /reservations/{id}`, `GET /arrival-brief/{id}` |

## Stack

- **Next.js 16** App Router + **React 19** + **TypeScript**
- **Tailwind CSS v4** (inline `@theme` tokens — no `tailwind.config.ts`)
- **Zustand** for the auth/persona store
- **Mapbox GL JS** for the partner map
- **lucide-react** icons

## Project layout

```
frontend/
├── app/
│   ├── layout.tsx            # global chrome (header + footer)
│   ├── page.tsx              # /  homepage
│   ├── sign-in/page.tsx      # /sign-in
│   ├── search/page.tsx       # /search
│   ├── hotels/[id]/page.tsx  # /hotels/[id]   (server-rendered)
│   ├── trips/page.tsx        # /trips         (client, auth-gated)
│   └── trips/[id]/page.tsx   # /trips/[id]    (client, auth-gated)
├── components/
│   ├── chrome/               # MarriottHeader, MarriottFooter
│   ├── home/                 # HeroSearch
│   ├── hotels/               # HotelCard
│   ├── eco/                  # EcoScoreRing, EcoScoreDetail
│   ├── partners/             # PartnerMap
│   └── auth/                 # AuthBootstrapper (hydrates session on load)
└── lib/
    ├── api.ts                # typed FastAPI client (cookies forwarded server-side)
    ├── types.ts              # mirrors backend Pydantic models
    ├── auth-store.ts         # Zustand store
    └── utils.ts              # cn(), formatUsd, formatDate, ...
```

## Design notes

- The brand red is `#A6192E` (Marriott Primary). All buttons, accents, and
  active nav rules use it.
- The chrome (header + footer) mirrors marriott.com&rsquo;s structure: thin black
  utility bar, white nav bar, dark multi-column footer.
- `/sign-in`, `/trips`, and `/trips/[id]` are client-rendered because they
  require the session cookie (set on the FastAPI domain). `/`, `/search`, and
  `/hotels/[id]` are server-rendered and forward incoming cookies for SSR.

## Personas

Three demo guests are loaded from `data/seeds/guests.json`:

| Persona | Tier | Theme |
|---|---|---|
| Alex Rivera | Gold | Vegetarian, sustainability-minded |
| Jordan Kim | Platinum | Halal, traveling with Mochi (Shiba Inu) |
| Sam Patel | Silver | Vegan, accessibility needs |

The Arrival Brief, dining picks, and partner-map filters all change based on
which persona is signed in.
