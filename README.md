# Marriott Bonvoy Enhanced Experience
### CodeFest 4.0 | Team: Dhruv Varshney & Satyajit Patra

A mobile-first web app that adds personalized, sustainability-aware, and local-discovery features to the Marriott Bonvoy experience.

## Three Hero Features

| Feature | What It Does |
|---|---|
| 🌿 **Eco Rating** | Per-property sustainability score (0–10) with Green Points multiplier and badges |
| 📋 **Arrival Brief** | LLM-generated personalized pre-stay briefing (weather, events, dining, transit) |
| 🐾 **Pet + Local Partner Map** | Pet booking integration + interactive Mapbox map of nearby services |

## Quick Start

```bash
./scripts/quickstart.sh
```

Then:
- Add `NEXT_PUBLIC_MAPBOX_TOKEN` to `frontend/.env.local` (free at [mapbox.com](https://account.mapbox.com/))
- Add `OPENWEATHER_API_KEY` to `backend/.env` (free at [openweathermap.org](https://openweathermap.org/api))

## Dev Commands

```bash
# Frontend (Next.js 14 — http://localhost:3000)
cd frontend && npm run dev

# Backend (FastAPI — http://localhost:8000)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Both via Docker
docker-compose up
```

## Project Structure

```
marriott-personalized-stays/
├── APP_PRD.md                 # Full product spec — READ THIS FIRST
├── docker-compose.yml
├── frontend/                  # Next.js 14 app
│   ├── app/                   # App Router pages
│   ├── components/
│   │   ├── eco/               # EcoScoreRing, EcoSubScoreBreakdown
│   │   ├── brief/             # ArrivalBriefCard, WeatherWidget
│   │   ├── map/               # LocalPartnerMap, PartnerCard
│   │   └── profile/           # BadgeShelf, PreferencesSection
│   ├── store/                 # Zustand (persona, preferences)
│   └── types/                 # Shared TypeScript types
├── backend/                   # FastAPI app
│   └── app/
│       ├── routers/           # hotels, guests, brief, partners
│       ├── models/            # Pydantic schemas
│       └── services/          # eco_service, brief_service, llm_service
├── data/
│   └── seeds/                 # Mock JSON data for all features
└── .cursor/
    ├── rules/                 # Cursor AI context rules
    └── hooks.json             # Auto-updates PRD tracker on file edits
```

## Demo Personas

Switch between personas at `/profile` or via the persona switcher in the nav.

| Persona | Tier | Preferences | Pet |
|---|---|---|---|
| Alex Rivera | Gold | Vegetarian, eco-conscious | None |
| Jordan Kim | Platinum | Halal | Mochi (Shiba Inu) |
| Sam Patel | Silver | Vegan, accessibility needs | None |

## Full PRD

See [`APP_PRD.md`](./APP_PRD.md) for complete feature specs, data schemas, KPI alignment, and build plan.
