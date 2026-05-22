# Bonvoy Curated — Personalized, Sustainable, Pet-Inclusive Stays

### CodeFest 4.0 | Team: Dhruv Varshney & Satyajit Patra | May 2026

An additive, mobile-first web app that layers three hero features onto Marriott Bonvoy — built entirely on data Marriott already owns. Existing Bonvoy flows stay untouched; every feature is opt-in, privacy-aware, and adds **zero associate workload**.

---

## Why this wins

1. **First-mover on per-property eco transparency.** No major chain shows a guest-facing sustainability score at booking. We do — grounded in MESH energy/water/waste data Marriott already collects.
2. **Personalization beats points for the next decade of demand.** 61% of guests will pay more for personalized stays; only 23% receive it today. We close that gap inside Bonvoy.
3. **Behavioral loyalty, not transactional.** A Green Points multiplier and an Eco Badge shelf turn sustainable choices into a repeatable habit, not a one-time toggle.
4. **Pet-inclusive travel is a $4.6B → $7.34B market with no incumbent app experience.** We make pet services bookable inside Bonvoy with one tap — including mobile providers that come to the hotel.
5. **Live agentic AI, not a static brief.** A streaming concierge agent calls real web-search tools in parallel (Tavily + OpenWeatherMap), grounds every recommendation in fresh results, and exposes its full tool-call trace to the guest.
6. **Associate Effort Delta ≤ 0.** Every feature is server-side, MESH-fed, and self-serve. No front-desk training, no new SOPs, no extra workload.

---

## Three Hero Features

| Feature | What it does | Production data path |
|---|---|---|
| **Eco Rating** | Per-property sustainability score (0–10) with sub-score breakdown, Green Points multiplier (×1.0 / ×1.1 / ×1.3), and an Eco Badge shelf ("Green Stay", "Eco Warrior") | MESH (energy/water/waste, monthly), Serve360 certifications, CAP Database, SPROUT |
| **Live Concierge — Arrival Brief** | Streaming agent (SSE) generates a personalized pre-stay brief 48h before check-in. Parallel tool calls for weather, events, dining, pet services, activities; live trace pane visible to the guest; every pick wraps a tracked **"Book via Marriott"** affiliate chip with bonus Bonvoy points | LiteLLM (TIP.AI) + Tavily Search + OpenWeatherMap; falls back to seed data when keys are absent |
| **Pet + Local Partner Map** | Interactive Mapbox map of vetted local services around the property; in-app booking for `dog_walker` and `mobile_grooming` partners (including providers that come to the hotel); guest-configurable search radius (1–50 mi, default 10) | Google Places + curated Marriott partner agreements (mocked in `data/seeds/partners_*.json`) |

### Supporting features

- **Preference Hub** at `/profile` — multi-select chips for dietary, interests, and pet-service categories; radius slider; debounced PATCH; drives every personalized section in the app.
- **Empty-preference rule** — if a preference dimension is empty, that section is **hidden** (never generic filler).
- **Three demo personas** with hardcoded auth (no Cognito overhead).
- **Affiliate ledger** — in-memory click-through tracker that surfaces projected commission and guest bonus points at the bottom of each brief.

---

## Hard Constraints (never violated)

- **Additive only** — existing Bonvoy flows stay untouched.
- **Associate Effort Delta ≤ 0** — no feature increases hotel-worker workload.
- **Privacy by default** — per-feature consent toggles; the only data ever sent off-platform to Tavily is `{city, dates, dietary tags, interest tags, query}` — no name, email, loyalty number, pet name, or confirmation number.
- **All data is mocked but architecturally honest** — every mock cites the real Marriott source it would come from in production (MESH, Opera PMS, GXP, CAP, SPROUT, etc.).
- **All generations** — designed for the *conscious-traveler cohort* (cuts across generations), not framed as Gen Z only.

---

## Tech Stack

**Frontend** — Next.js 14 (App Router), Tailwind CSS, shadcn/ui, Mapbox GL JS, Zustand, Lucide, Recharts.
**Backend** — FastAPI (Python 3.11), Pydantic v2, `httpx`, Server-Sent Events for the agent stream.
**LLM** — TIP.AI LiteLLM gateway (`us.anthropic.claude-sonnet-4-6` default); deterministic mock fallback (`USE_MOCK_LLM=true`).
**Live web search** — Tavily Search API (mocked when `TAVILY_API_KEY` is empty).
**Weather** — OpenWeatherMap free tier (mocked on 401 / missing key).
**Infra** — Docker + docker-compose; AWS sandbox (`mi-lz-codefest-2026-sandbox27`).

Approx codebase size at submission: **~15,750 LOC** across frontend + backend.

---

## Quick Start

```bash
./scripts/quickstart.sh
```

Then add the two free-tier keys you need for live mode:

- `NEXT_PUBLIC_MAPBOX_TOKEN` → `frontend/.env.local` (free at [mapbox.com](https://account.mapbox.com/))
- `OPENWEATHER_API_KEY` → `backend/.env` (free at [openweathermap.org](https://openweathermap.org/api))

Optional, for the live agent:

- `TAVILY_API_KEY` → `backend/.env` (free tier at [tavily.com](https://tavily.com))
- `LITELLM_BASE_URL` + `LITELLM_API_KEY` → `backend/.env` (or set `USE_MOCK_LLM=true`)

The app is **demo-safe with no keys** — every external dependency falls back to seed-derived data and the agent trace marks each tool as `mock` instead of `live`.

---

## Dev Commands

```bash
# Frontend (Next.js 14 — http://localhost:3000)
cd frontend && npm run dev

# Backend (FastAPI — http://localhost:8000, OpenAPI at /docs)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Both, containerized
docker-compose up
```

---

## Demo Flow (8-minute pitch)

1. **Open `/` as Alex (Gold)** — show home + featured hotels with `EcoScoreRing` overlay.
2. **`/search` → eco filter ≥ 7** — show Green Points multiplier callout on each card.
3. **Hotel detail** — open the eco sub-score breakdown; show the Marriott data-source footnote (MESH, last updated date).
4. **Switch persona to Jordan (Platinum, has dog Mochi)** — `/trips/[id]` for an upcoming pet stay.
5. **"Build my brief"** — watch the agent trace pane stream parallel tool calls (`get_weather`, `search_events`, `search_dining`, `search_pet_services`); brief assembles section-by-section.
6. **Affiliate chips + ledger panel** — click a "Book via Marriott +320 pts" chip; ledger updates live.
7. **Pet + Local Partner Map** — toggle the radius slider, tap a mobile-grooming pin, book a date+time inside the stay window.
8. **`/profile`** — flip a dietary chip → trip-detail dining section refetches and re-personalizes.

---

## Demo Personas

Hardcoded mock auth — switch from the nav or `/profile`.

| Persona | Tier | Preferences | Pet | Best for |
|---|---|---|---|---|
| **Alex Rivera** | Bonvoy Gold | Vegetarian, eco-conscious | — | Eco Rating + Arrival Brief |
| **Jordan Kim** | Bonvoy Platinum | Halal | Mochi (Shiba Inu) | Pet booking + Local Partner Map |
| **Sam Patel** | Bonvoy Silver | Vegan, accessibility needs | — | Preference-driven personalization |

---

## Project Structure

```
marriott-personalized-stays/
├── APP_PRD.MD                        # Full product spec — read this first
├── docker-compose.yml
├── scripts/quickstart.sh
│
├── frontend/                         # Next.js 14 app
│   ├── app/                          # App Router (/, /search, /hotels/[id], /trips/[id], /profile, /sign-in)
│   ├── components/
│   │   ├── eco/                      # EcoScoreRing, EcoScoreDetail, BadgeShelf
│   │   ├── brief/                    # BriefBuildPane, AgentTracePane, AffiliateChip, AffiliateLedgerPanel
│   │   ├── pet/                      # PetServiceBookingSheet, PetServiceBookingList,
│   │   │                             #   PetServiceRadiusControl, MobileServiceBadge
│   │   ├── partners/, hotels/, home/, profile/, chrome/, auth/
│   ├── lib/                          # api.ts, agent-stream.ts (typed SSE client)
│   └── store/                        # Zustand (persona, profile, preferences)
│
├── backend/                          # FastAPI app
│   └── app/
│       ├── main.py
│       ├── routers/                  # auth, guests, hotels, partners, reservations,
│       │                             #   arrival_brief, arrival_brief_stream, affiliate, health
│       ├── services/                 # eco, badge, weather, llm, concierge_agent (streaming),
│       │                             #   tavily, affiliate, partner, hotel_content,
│       │                             #   guest_preference, pet_service_recommendation,
│       │                             #   reservation, arrival_brief
│       └── models/                   # Pydantic schemas
│
├── data/seeds/                       # All mock data
│   ├── hotels.json                   # 8–10 properties with full eco sub-scores
│   ├── partners_{nyc,dc,chicago}.json
│   ├── restaurants.json, events.json
│   ├── guests.json, stays.json
│   └── arrival_brief_{alex,jordan,sam}.json
│
├── docs/                             # Architecture diagrams, KPI sheet, presentation deck
└── .cursor/                          # AI rules + auto-update hooks for the PRD tracker
```

---

## Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/auth/profile` | Current persona + preferences |
| `PATCH` | `/auth/profile/preferences` | Update dietary / interests / pet-service prefs + radius |
| `GET` | `/hotels`, `/hotels/{id}` | Hotel list/detail with computed eco score |
| `GET` | `/partners/nearby?hotel_id=…&max_miles=…` | Local partner map (radius-filtered) |
| `GET` | `/arrival-brief/{stay_id}` | Composed brief (cached) |
| `GET` | `/arrival-brief/{stay_id}/stream?live_search=true` | **SSE** stream of `AgentEvent` envelopes (tool calls, partials, final brief) |
| `GET` | `/reservations/{id}/pet-services/recommendations` | Live LiteLLM ranking of bookable pet partners |
| `POST` | `/reservations/{id}/pet-services` | Book a pet service (date + time, eligibility-gated) |
| `DELETE` | `/reservations/{id}/pet-services/{booking_id}` | Cancel booking (no associate involvement) |
| `POST` | `/affiliate/click` | Record tracked click |
| `GET` | `/affiliate/ledger/{stay_id}` | Running totals for the brief's commission panel |

OpenAPI docs: `http://localhost:8000/docs`.

---

## Privacy & Data Boundary

- **Mock auth, no PII** — the three personas live in `data/seeds/guests.json`.
- **Outbound to Tavily** — only `{city, dates, dietary tags, interest tags, query}`. Never name, email, loyalty number, pet name, or confirmation number.
- **Outbound to LiteLLM** — only the prompt template + redacted preference tags + city/dates.
- **`live_search_enabled`** sub-toggle defaults to **off**; with it off (or no `TAVILY_API_KEY`), every tool returns seed-derived data and the trace pane shows `mock` badges.
- **Per-feature consent toggles** in `/profile` (Arrival Brief, local partner recs, eco-aware nudges).

---

## Resources & Citations

The market and behavior claims used in the deck and on Slide 4 of the pitch are grounded in the following public sources:

**Sustainability & conscious travel**
1. Booking.com — *Sustainable Travel Report 2023.* 76% want to travel more sustainably; 43% will pay extra for sustainable certification. [news.booking.com](https://news.booking.com/bookingcoms-2023-sustainable-travel-report-reveals-trends/)
2. Expedia Group — *Sustainable Travel Study 2024.* 90% of travelers seek sustainable options; 70% are overwhelmed by where to start. [newsroom.expediagroup.com](https://newsroom.expediagroup.com/news-releases)

**Personalization**
3. McKinsey — *The value of getting personalization right—or wrong—is multiplying.* 71% expect personalization; 76% are frustrated when they don't get it. [mckinsey.com](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right-or-wrong-is-multiplying)
4. Salesforce — *State of the Connected Customer (6th edition).* 73% expect companies to understand their unique needs. [salesforce.com](https://www.salesforce.com/resources/research-reports/state-of-the-connected-customer/)

**AI in travel**
5. Oliver Wyman — *How Generative AI is Transforming Business Travel (2024).* 41% of US travelers used GenAI for trip planning; 78% open to AI-assisted booking. [oliverwyman.com](https://www.oliverwyman.com/our-expertise/insights/2024/feb/how-generative-ai-is-transforming-business-travel.html)
6. Phocuswright — *AI in Travel research updates (2024).* [phocuswright.com](https://www.phocuswright.com/Travel-Research/Research-Updates/2024)

**Pet travel market**
7. Mordor Intelligence — *Pet-Friendly Hotels Market Report.* $4.6B (2024) → $7.34B (2029), ~9.79% CAGR. [mordorintelligence.com](https://www.mordorintelligence.com/industry-reports/pet-friendly-hotels-market)
8. American Pet Products Association — *National Pet Owners Survey 2024.* 66% of US households own a pet; 78% travel with them. [americanpetproducts.org](https://www.americanpetproducts.org/research-insights/industry-trends-and-stats)

**Marriott context**
9. Marriott International — *Q4 / FY2024 earnings release.* Bonvoy reached 228M members at year-end 2024. [news.marriott.com](https://news.marriott.com/news/2025/02/11/marriott-international-reports-fourth-quarter-and-full-year-2024-results)
10. Marriott Annual Report. [marriott.gcs-web.com](https://marriott.gcs-web.com/financial-information/annual-reports)

**Generational + competitive context**
11. Deloitte — *2024 Travel Industry Outlook.* Younger cohorts over-index on values-aligned travel. [deloitte.com](https://www2.deloitte.com/us/en/insights/industry/travel-hospitality-leisure/summer-travel.html)
12. Hilton — *2025 Trends Report.* Useful comp: Hilton talks personalization but has not launched per-property sustainability scoring — reinforces our first-mover claim. [stories.hilton.com](https://stories.hilton.com/trendsreport)

---

## Path to Production (from the deck)

| Milestone | Duration | Headcount | Notes |
|---|---|---|---|
| MESH read-only feed → Eco Rating service | 4 weeks | 2 BE + 1 data eng | Pilot 50 properties |
| Concierge agent hardening + Tavily/Ticketmaster contracts | 6 weeks | 2 BE + 1 PM | Add OpenTable / Viator / Rover affiliate agreements |
| Pet partner agreements (Rover/Wag) + booking SLAs | 8 weeks | 1 BD + 1 BE | Start in NYC / DC / Chicago / Miami |
| Bonvoy app integration (additive screens, feature flags) | 6 weeks | 2 FE + 1 mobile | Behind LaunchDarkly |
| Pilot launch (4 cities, 50 properties) | 4 weeks | full team | Measure ADR uplift, direct-booking rate, NPS |

Total budget envelope: **$250K** through pilot.

---

## Full PRD

See [`APP_PRD.MD`](./APP_PRD.MD) for complete feature specs, data schemas, scoring formulas, KPI alignment, and the implementation tracker.
