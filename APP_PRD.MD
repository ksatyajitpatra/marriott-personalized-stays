# Marriott Bonvoy Enhanced Experience
## Product Requirements Document (PRD)
### CodeFest 4.0 | Team: Dhruv Varshney & Satyajit Patra | May 2026

---

## 1. Problem Statement

Marriott Bonvoy's enrollment is growing across all generations, yet **personalization, sustainability transparency, and local discovery remain largely absent** from the booking and in-stay experience. Guests — regardless of age — increasingly expect experiences tailored to their preferences, values, and travel style, not just points and room upgrades.

**Key data backing this:**
- Gen Z was 12% of Bonvoy enrollment in 2024 (up from 1% in 2017) but only 1.6% of revenue — they enroll and vanish
- 83% of modern travelers prioritize **personalized experiences** over points
- 60% expect AI-based personalized recommendations
- Airbnb captures 38% of the younger traveler market vs. Marriott's 23%
- 65% of US travelers find booking travel overwhelming

**The gap:** Marriott has no guest-facing eco scores, no local partner discovery, no pre-arrival personalized briefing — all things that increase intent-to-book and direct channel loyalty.

---

## 2. Solution Overview

This app is an additive layer to the existing Bonvoy experience — a web app (mobile-first) that demonstrates three hero features plus supporting enhancements. It does NOT replace any existing Bonvoy flow. Everything is opt-in.

**Design Principles:**
- **Additive, never replacement** — existing flows stay untouched
- **Associate Effort Delta ≤ 0** — no feature increases front-desk or associate workload
- **Privacy by default** — per-feature consent toggles; data minimization
- **All generations** — designed for everyone, not positioned as "Gen Z only"
- **Data-grounded** — every mock data point cites the real Marriott source it would come from in production

---
`
## 3. Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS + shadcn/ui components
- **Maps:** Mapbox GL JS (interactive map for local partners)
- **State:** Zustand (lightweight, no Redux overhead)
- **Icons:** Lucide React
- **Charts:** Recharts (for eco score breakdown)

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** SQLite (local dev) → PostgreSQL (prod)
- **LLM:** TIP.AI LiteLLM gateway (Claude/GPT-4) or mock for demo
- **Weather API:** OpenWeatherMap (free tier, current + 5-day forecast)
- **Events API:** Ticketmaster Discovery API (free tier) or mock
- **Geocoding:** Mapbox Geocoding API
- **Auth:** Mock auth — 3 hardcoded guest personas (no Cognito overhead)

### Infrastructure
- **Cloud:** AWS sandbox (mi-lz-codefest-2026-sandbox27)
- **Container:** Docker + docker-compose
- **CI:** GitHub Actions (optional)

### Data Strategy
- All data is mocked but architecturally honest — each mock dataset cites the real Marriott source
- Mock data loaded at app startup from JSON seed files in `/data/seeds/`

---

## 4. Guest Personas (Mock Auth)

| Persona | Name | Loyalty Tier | Preferences | Used For |
|---|---|---|---|---|
| **Alex** | Alex Rivera | Bonvoy Gold | Vegetarian, eco-conscious, no pets | Arrival Brief demo |
| **Jordan** | Jordan Kim | Bonvoy Platinum | Halal, travels with dog | Pet + Local Partner demo |
| **Sam** | Sam Patel | Bonvoy Silver | Vegan, cyclist, accessibility needs | Eco Rating + Map demo |

---

## 5. Feature Specifications

---

### 5.1 🌿 Eco Rating — MVP Feature #1

**Status:** Build fully

**What it is:**
A transparent, data-grounded sustainability score (0–10) shown on every hotel's search result and detail page. Broken into sub-scores so it's defensible, not greenwashing. Linked to a Bonvoy Green Points multiplier and an Eco Badge system.

**Why it matters:**
- Marriott already tracks this data via MESH (monthly reporting) and Serve360 goals
- No competitor surfaces per-property eco data to guests at booking time
- Creates a behavioral nudge: pick greener hotels, earn more points
- Directly aligned with Serve360 2026–2030 goals

**Score Components (weighted):**

| Sub-Score | Weight | Data Source (Production) | Mock Strategy |
|---|---|---|---|
| Energy Intensity (kWh/room-night) | 25% | MESH system (monthly, 22nd of month) | Seeded per hotel |
| Water Usage (L/room-night) | 20% | MESH system | Seeded per hotel |
| Waste Diversion Rate | 20% | MESH system | Seeded per hotel |
| Sustainability Certifications | 15% | MESH Scorecard (LEED, Green Key, etc.) | Boolean flags per hotel |
| Carbon Offset Program | 10% | CAP Database / Net Zero Cloud | Boolean flag |
| Responsible F&B Sourcing | 10% | SPROUT (quarterly) | Seeded score |

**Scoring Formula:**
```
eco_score = Σ(sub_score_i × weight_i) × 10
```
Displayed as: `8.4 / 10` with a colored ring (green ≥ 7, yellow 5–7, red < 5)

**Bonvoy Green Points Multiplier:**
- Score ≥ 8: **3000 base + 900 bonus points** (×1.3 multiplier)
- Score 6–7.9: 3000 base + 300 bonus points (×1.1 multiplier)
- Score < 6: 3000 base, no multiplier

**Eco Badge System:**
- Stay at a hotel with score ≥ 8 → earn **"Green Stay" badge**
- Stay at 3 such hotels → **"Eco Warrior" badge**
- Badges appear on guest profile and encourage direct booking
- Brand-specific: Westin, Ritz-Carlton, Element stay at ≥ 8 → brand badge unlocked

**UI Components:**
- `EcoScoreRing` — circular progress ring with score in center (hotel card + detail page)
- `EcoSubScoreBreakdown` — expandable accordion with all 6 sub-scores
- `EcoPointsCallout` — "Book this hotel, earn +900 Green Points"
- `EcoBadgeDisplay` — badge shelf on user profile page
- `DataSourceNote` — small footnote: "Based on MESH energy/water/waste data, last updated [date]"

**Data Note:** 1-month data lag is acceptable and honest. The demo uses seeded data with realistic ranges based on publicly available Marriott Serve360 reports.

---

### 5.2 📋 Pre-Check-In Arrival Brief — MVP Feature #2

**Status:** Build fully

**What it is:**
An LLM-generated, personalized 1-page briefing sent (or viewable in-app) 48 hours before check-in. Pulls from live weather, local events, and the guest's saved preferences to produce a fully tailored brief.

**Why it matters:**
- Zero associate involvement — fully automated
- Directly addresses travel anxiety (65% of travelers find booking overwhelming)
- Creates a memorable, sticky touchpoint between booking and arrival
- Differentiates from every competitor — none do this at this quality

**Brief Contents:**

| Section | Data Source (Production) | Mock/Live for Demo |
|---|---|---|
| Weather forecast for stay dates | OpenWeatherMap API | **LIVE** (free tier) |
| Packing tips (weather-derived) | LLM inference | LLM or mock |
| Local events during stay | Ticketmaster API / LLM search | Mock JSON or live |
| Restaurant recs filtered by dietary pref | Opera PMS F&B data + partner DB | Mock JSON seeded per city |
| Transit from arrival airport | Google Maps / Citymapper API | Mock static data |
| Property accessibility notes | Opera PMS / GXP guest notes | Mock per hotel |
| Sunrise/sunset times | Astronomy API (free) | **LIVE** |
| Pet-friendly tips (if dog profile) | Property pet policy data | Mock per hotel |

**Personalization Engine:**
- Reads from `guest.preferences` (set in user profile)
- Dietary filter: vegetarian / vegan / halal / kosher / gluten-free
- Interest tags: culture, outdoor, food, nightlife, sports, sustainability
- Accessibility: mobility, hearing, vision, sensory sensitivity
- Pet: dog name, breed, weight

**Consent Toggle:**
- In user profile settings: "Arrival Brief" toggle (enabled by default, can disable)
- Data used: stay dates, property location, saved preferences
- No location tracking, no browsing history

**LLM Prompt Strategy:**
```
System: You are a knowledgeable Marriott concierge. Generate a warm, 
concise arrival brief for a guest staying at {hotel_name} in {city}.

Context:
- Stay: {check_in} to {check_out} ({nights} nights)
- Weather: {weather_data}
- Guest preferences: {dietary}, {interests}, {accessibility}
- Local events: {events_json}
- Restaurant options: {restaurants_json}

Output a structured JSON with sections: weather_summary, packing_tips, 
events (top 3), dining (top 3 matching diet), transit, property_notes.
Keep each section under 60 words.
```

**UI Components:**
- `ArrivalBriefCard` — beautiful card in "My Stays" view, 48h before check-in
- `BriefSection` — reusable section with icon, heading, content
- `DietaryBadge` — small pill showing dietary filter applied
- `WeatherWidget` — 3-day mini forecast strip
- `ConsentToggleRow` — in profile settings

---

### 5.3 🐾 Pet + Local Partner Graph — MVP Feature #3

**Status:** Build fully

**What it is:**
A combined feature: (a) guests can add a pet profile when booking, (b) a local partner map at each property shows nearby vetted services. This replaces a static "pet friendly: yes" flag with a rich, transactable experience.

**Why it matters:**
- Pet travel is a $10B+ market; 70% of pet owners say pet-friendliness influences hotel choice
- No major hotel chain has a live local partner map at this granularity
- Generates a small revenue share model (Marriott takes cut from partner referrals)
- Extremely visual — great for a demo

**Pet Profile (in booking flow):**
- Pet name, species, breed, weight
- Stored in `guest.pets[]` in profile
- At booking: "This property is pet-friendly. Add your pet?"
- Pet fee shown transparently at booking time (not at check-in surprise)

**Local Partner Map:**

Categories shown on interactive Mapbox map:
- 🐾 Vets (24/7 emergency flagged)
- 🦮 Dog walkers & sitters (Rover/Wag API or mock)
- 🌿 Dog parks & green spaces
- 🍽️ Pet-welcome restaurants
- 🛒 Pet supply stores
- 🚲 Bike rentals (for all guests)
- 🥗 Vegan / plant-based restaurants
- ⚡ EV charging stations
- 💧 Refill stations (sustainability play)
- 🎭 Local experiences & tours

**Map UX:**
- Default view: hotel at center, 2km radius
- Filter chips at top: toggle categories on/off
- Tap a pin → partner card: name, distance, hours, rating, "Get Directions" / "Reserve"
- "Reserve" opens in-app booking or deep-links to partner
- Partners shown with "Marriott Partner" badge if verified

**Data Sources:**
- Mock: JSON seed files in `/data/seeds/partners_{city}.json`
- Production path: Google Places API + curated Marriott partner agreements
- Pet policy per property: mock in `/data/seeds/hotels.json`, production source = Opera PMS

**UI Components:**
- `LocalPartnerMap` — full Mapbox interactive map
- `PartnerCategoryFilter` — horizontal scrolling chip filters
- `PartnerCard` — bottom sheet on pin tap
- `PetProfileForm` — in booking flow and user profile
- `PetFriendlyBadge` — on hotel search card when pet profile active

---

## 6. Supporting Features (Partial / Storyboard)

### 6.1 User Profile & Preferences Hub

**Build level:** Fully build (it's the backbone of personalization)

- Dietary preferences (multi-select: vegetarian, vegan, halal, kosher, gluten-free, nut allergy)
- Travel interests (multi-select: culture, food, outdoor, nightlife, sustainability, wellness)
- Accessibility needs (multi-select: mobility, hearing, vision, sensory)
- Pet profiles (add/remove pets)
- Consent toggles:
  - Arrival Brief (on/off)
  - Local partner recommendations (on/off)
  - Eco-aware booking nudges (on/off)
  - Preference learning from past stays (on/off — future feature)
- Language preference
- Bonvoy tier display + points balance (mocked)
- Badge shelf (eco badges earned)

### 6.2 Accessibility Quick Mode

**Build level:** CSS + toggle only (no backend)

- High-contrast mode
- Dyslexia-friendly font (OpenDyslexic)
- Reduced motion
- Larger touch targets
- Stored in `localStorage`, no server needed

### 6.3 Community Events (Hotel + City)

**Build level:** Mock JSON only for demo; future LLM integration

- Hotel-level events: run club, coworking hours, rooftop yoga (hardcoded in hotel seed data)
- City events: mock top 5 events per demo city
- Shown in the Arrival Brief and in a "What's On" tab in the hotel detail page
- **Future:** Real-time LLM search via TIP.AI or Perplexity-style live retrieval

### 6.4 Interactive Local Partner Map (Nice-to-Have Enhancement)

**Build level:** Full Mapbox integration — visual impact is high, worth the effort

This map appears in three places:
1. Hotel detail page → "Explore the Neighborhood" section
2. Arrival Brief → "Getting Around" section (static mini-map)
3. In-stay screen → full map with live filtering

The map makes the entire app feel premium and differentiates it visually from any other hotel demo.

---

## 7. Application Screens & Navigation

```
App Shell (mobile-first, 390px base)
│
├── /                          → Home / Search
│   ├── SearchBar              → city, dates, guests, pet toggle
│   ├── FeaturedHotels         → with EcoScoreRing overlay
│   └── PersonalizedSection    → "For You" based on profile
│
├── /search                    → Search Results
│   ├── HotelCard[]            → name, price, EcoScoreRing, pet badge
│   ├── EcoFilterChip          → filter by eco score ≥ 7 / ≥ 8
│   └── PetFriendlyFilter      → toggle when pet profile active
│
├── /hotel/:id                 → Hotel Detail
│   ├── HeroImage
│   ├── EcoScoreSection        → ring + full sub-score breakdown
│   ├── EcoPointsCallout       → bonus points callout
│   ├── AmenitiesList
│   ├── LocalPartnerMap        → interactive Mapbox map
│   ├── CommunityEvents        → "What's On" tab
│   └── BookNowCTA
│
├── /stays                     → My Stays
│   ├── UpcomingStay           → with ArrivalBriefCard (48h before)
│   ├── CurrentStay            → quick actions
│   └── PastStays              → badge earned display
│
├── /arrival-brief/:stay_id    → Full Arrival Brief View
│   ├── WeatherWidget
│   ├── PackingTips
│   ├── EventsList
│   ├── DiningRecommendations
│   ├── TransitInfo
│   └── PropertyNotes
│
├── /profile                   → Guest Profile
│   ├── LoyaltyTierCard        → tier, points, badges
│   ├── BadgeShelf             → eco badges earned
│   ├── PreferencesSection     → dietary, interests, accessibility
│   ├── PetProfiles            → manage pets
│   ├── ConsentToggles         → privacy settings
│   └── AccessibilitySettings  → display modes
│
└── /booking/:hotel_id         → Booking Flow
    ├── RoomSelection
    ├── PetAddStep             → (if pet profile exists)
    ├── EcoPointsPreview       → "You'll earn +900 Green Points"
    └── Confirmation
```

---

## 8. Mock Data Architecture

### Seed Files (loaded at startup)

```
/data/seeds/
├── hotels.json              # 8-10 Marriott properties with all eco data
├── partners_nyc.json        # Local partners around NYC demo hotel
├── partners_dc.json         # Local partners around DC demo hotel  
├── partners_chicago.json    # Local partners around Chicago demo hotel
├── events.json              # Community/city events per property
├── restaurants.json         # F&B options with dietary tags per city
├── guests.json              # 3 persona profiles (Alex, Jordan, Sam)
└── stays.json               # Pre-loaded upcoming stays for each persona
```

### Hotel Eco Data Schema (hotels.json)
```json
{
  "id": "marriott-nyc-times-sq",
  "name": "New York Marriott Marquis",
  "brand": "Marriott Hotels",
  "city": "New York",
  "lat": 40.7590,
  "lng": -73.9845,
  "pet_friendly": true,
  "pet_max_weight_kg": 23,
  "pet_fee_usd": 75,
  "eco": {
    "energy_kwh_per_room_night": 42.3,
    "water_liters_per_room_night": 185,
    "waste_diversion_pct": 68,
    "certifications": ["LEED Silver", "Green Key"],
    "carbon_offset_program": true,
    "fb_sourcing_score": 7.2,
    "data_as_of": "2026-04-22",
    "data_source": "MESH (Marriott Environmental Sustainability Hub)"
  }
}
```

---

## 9. Build Plan

### Day 1 (Today / Tonight)
- [ ] Scaffold Next.js 14 + FastAPI project structure
- [ ] Set up Tailwind CSS + shadcn/ui
- [ ] Set up Mapbox account + API key
- [ ] Create mock data seed files (hotels, partners, guests, stays)
- [ ] Build core layout: nav, shell, mobile viewport
- [ ] Build hotel search + results page with EcoScoreRing
- [ ] Build hotel detail page skeleton

### Day 2 (Tomorrow)
- [ ] Complete Eco Rating: sub-score breakdown, points callout, badge assignment
- [ ] Build Local Partner Map (Mapbox, category filters, partner cards)
- [ ] Build Arrival Brief: profile prefs → LLM/mock → rendered card
- [ ] Build User Profile page (preferences, consent toggles, badges)
- [ ] Wire up pet profile to booking flow

### Day 3 (Polish + Presentation)
- [ ] Accessibility mode toggle (CSS only)
- [ ] Community events section on hotel detail
- [ ] Demo script walkthrough — fix any rough edges
- [ ] Record backup demo video
- [ ] Build presentation slides

---

## 10. KPI Alignment (CodeFest 4.0 Judging Criteria)

| Marriott Enterprise KPI | How This App Addresses It |
|---|---|
| **Bonvoy Occupancy & Enrollments** | Eco Rating + badges increase intent to book directly; pet + local graph increases loyalty |
| **Intent to Recommend** | Personalized Arrival Brief is the single highest-impact satisfaction driver |
| **Digital Direct Share** | All features drive interaction through the app, not OTAs |
| **Leadership Index** | Associate Effort Delta ≤ 0 for all features — no new front-desk burden |

---

## 11. Associate Impact Summary

**Our commitment: no feature in this product increases workload on Marriott associates.**

| Feature | Associate Effort Delta | How |
|---|---|---|
| Eco Rating | **0** | Fully automated from MESH data; no associate input needed |
| Arrival Brief | **−2** | Reduces concierge calls for weather/event/transit questions |
| Local Partner Map | **−1** | Reduces "what's nearby?" front desk questions |
| Pet Booking | **0** | Pet fee + policy shown at booking; no surprise check-in conversation |
| User Preferences | **0** | Stored digitally; reduces manual preference note-taking |

---

## 12. Privacy Architecture

| Feature | Data Used | Consent Model | Storage |
|---|---|---|---|
| Arrival Brief | Stay dates, location, saved prefs | Toggle in profile (on by default) | Server-side, per-stay |
| Eco Rating | None (public hotel data) | N/A | Cached on server |
| Local Partner Map | Hotel location | No consent needed (not personal) | No PII stored |
| Pet Profile | Pet name, breed, weight | Explicit add in profile | Guest profile |
| Preference Learning | Past stay data | Opt-in toggle (off by default) | Encrypted profile |

Marriott already has a "delete all data" flow (per Bonvoy Privacy Policy). We inherit this — no new implementation needed.

---

## 13. Competitive Positioning

| Feature | Hilton | Hyatt | Airbnb | **This App** |
|---|---|---|---|---|
| Per-property eco score | ❌ | ❌ | ❌ | ✅ Sub-scores + points multiplier |
| Pre-arrival AI brief | ❌ | ❌ | ❌ | ✅ LLM-generated, diet-aware |
| Local partner map | ❌ | ❌ | Partial | ✅ Interactive + reservable |
| Pet marketplace | ❌ | ❌ | ❌ | ✅ Vets, walkers, parks |
| Gamified eco badges | ❌ | Partial | ✅ | ✅ Property + brand-specific |

---

## 14. Open Questions (To Investigate If Time)

1. TIP.AI token budget — test demo LLM call consumption early
2. Mapbox free tier limits — 50K map loads/month (more than enough for demo)
3. Can we use Ticketmaster Discovery API free tier for live events in Arrival Brief?
4. Preference auto-learning from past stays — future enhancement, mention in pitch

---

## 15. Implementation Status Tracker

> This section is auto-updated as features are built. Check off items as they are completed.

### Core Infrastructure
- [ ] Next.js 14 project initialized
- [ ] FastAPI backend initialized
- [ ] Docker + docker-compose setup
- [ ] Seed data files created
- [ ] Mapbox integration working

### Feature: Eco Rating
- [ ] EcoScoreRing component
- [ ] EcoSubScoreBreakdown component
- [ ] EcoPointsCallout component
- [ ] EcoBadgeDisplay component
- [ ] Hotels loaded from seed data with eco scores
- [ ] Filter by eco score on search results

### Feature: Arrival Brief
- [ ] Weather API integration (OpenWeatherMap)
- [ ] LLM prompt + mock fallback
- [ ] ArrivalBriefCard component
- [ ] BriefSection components (weather, events, dining, transit)
- [ ] Consent toggle in profile
- [ ] Dietary preference filter applied

### Feature: Pet + Local Partner Map
- [ ] Mapbox map component
- [ ] Partner seed data (NYC, DC, Chicago)
- [ ] Category filter chips
- [ ] PartnerCard bottom sheet
- [ ] PetProfileForm in booking + profile
- [ ] Pet filter on hotel search

### Supporting
- [ ] User Profile page (preferences, consent, badges)
- [ ] Accessibility mode toggle
- [ ] Community events section
- [ ] Booking flow skeleton
- [ ] 3 demo personas loadable
