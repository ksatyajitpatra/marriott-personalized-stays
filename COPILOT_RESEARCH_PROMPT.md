# Deep Research Prompt: Reimagining Marriott Bonvoy for Gen Z (Without Breaking Boomers or Burning Out Associates)

> Paste this entire document into the internal Marriott Copilot's deep-research mode. Ask it to cite internal docs (PMS specs, ESG reports, loyalty program docs, associate workflow SOPs, accessibility guidelines, prior hackathon submissions, etc.) wherever possible.

---

## 1. Context for the Researcher

We are a small team participating in Marriott's internal CodeFest 4.0. Most teams will build AI agents for **code analysis / developer productivity**. We are deliberately going the other direction: a **customer + associate-facing product play** that proposes additive features to the existing Bonvoy app.

### Core Thesis
Marriott's current Bonvoy app over-indexes on Boomers and Millennials. **Gen Z (born ~1997–2012) is the next decade's traveler, but they are under-acquired and under-retained.** We want to evolve Bonvoy to win Gen Z *without* alienating existing loyal cohorts and *without* increasing operational load on hotel associates (front desk, housekeeping, F&B, concierge). In many cases, our features should *reduce* associate load.

### Hard Constraints / Non-Negotiables
1. **Additive, not replacement.** Existing Bonvoy flows must remain untouched for current users.
2. **Associate Effort Delta must be neutral or negative** for every feature. If a feature increases front-desk workload, it must be auto-routed, AI-mediated, or self-service.
3. **Privacy by default.** Gen Z is the most privacy-paranoid generation; per-feature consent toggles, on-device inference where feasible, and a hard "delete everything" path are required.
4. **Data realism.** Where we mock data for the demo, we must articulate *exactly* which existing Marriott system (Opera PMS, MARSHA, GRC, EMPOWER, ESG/Serve360 reports, loyalty data, IoT/BMS, supplier APIs) would supply it in production.
5. **Demo scope.** A single-weekend buildable web/mobile prototype that *visually* communicates the vision; backend can be heavily mocked but architecturally honest.

### Prior Art We Are Building On
A previous internal hackathon project called **"Chariot"** (treat the name as irrelevant — patterns matter):
- Microservices on AWS (Cognito, S3, API Gateway), RBAC, Dockerized
- LLM-powered guest chatbot with RAG over hotel-uploaded docs (manuals, policies, etiquette)
- Multilingual chat (e.g., French response to English query)
- Per-trip context (past / current / upcoming)
- Self-service work-order requests (toiletries etc.) auto-routed to housekeeping queue
- Associate-side dashboard with insights (loyalty distribution, engagement scores, NLP-derived operational insights)
- Manager doc upload → tunes the AI's tone and policy adherence per property
- Eco-rating slider in user prefs (0–10) — but not data-grounded
- Accessibility: dyslexia font, language translation
- Strict "delete account" / data-wipe flow

Treat Chariot as **proven architectural scaffolding**. Don't redesign it; extend it.

---

## 2. The Feature Wishlist We Want You to Pressure-Test

For **each** feature below, please research and return:

- **(a) The actual Gen Z need / behavior research** backing this (cite Marriott internal customer research first; fall back to public sources like Skift, Phocuswright, Deloitte travel reports, Hilton/Hyatt competitive moves).
- **(b) Existing Marriott capabilities** we can plug into (system, API, dataset, team, internal product). Cite internal docs.
- **(c) Data sources** — real production sources + acceptable demo mock strategy.
- **(d) Associate Effort Delta** — does it add or remove associate work? Quantify if possible.
- **(e) Privacy/regulatory considerations** (GDPR, CCPA, ADA, accessibility laws by region, pet regulations, food allergen disclosure laws).
- **(f) Failure modes / weaknesses** in our current concept and how to mitigate.
- **(g) Competitive parity check** — do Hilton Honors, World of Hyatt, IHG One, Airbnb, Booking.com Genius already have this? What's our differentiation?

### Feature List

1. **Eco Rating (data-grounded, not slider-based)**
   Per-property score broken into sub-scores: energy intensity (kWh/occupied room-night), water (L/ORN), waste diversion %, F&B local/sustainable sourcing %, linen-reuse rate, renewable energy %, carbon offset transparency. Surfaced at search/booking time. Tied to a **Bonvoy Green Points multiplier** so eco-conscious bookings earn bonus points. Investigate: Marriott Serve360 data, BMS feeds, EcoVadis-style supplier scoring, GHG Protocol Scope 1/2/3 mapping to room-night.

2. **Pre-Check-In "Arrival Brief"** (LLM-generated, sent 48h prior)
   1-page personalized brief: weather forecast, packing tips, local events during stay matched to guest preferences, restaurant recs filtered by dietary needs, accessibility notes for the property, transit options from arrival airport, parking, pet-info if applicable, sunrise/sunset times, local etiquette. Investigate: Marriott's existing pre-arrival email infra, weather APIs, events APIs (Ticketmaster, Eventbrite, Bandsintown), dietary tag data on Marriott F&B partners.

3. **Silent / Async-First Service Layer**
   Every interaction (mobile key, late checkout, room swap, complaints, special requests, F&B order, housekeeping opt-out) is doable in-app with zero phone calls or front-desk lines. Human is the *escalation*, not the default. Investigate: current mobile key coverage, current digital check-in coverage gaps, complaint-routing SOPs, escalation thresholds.

4. **Accessibility Suite ("Quiet Mode" + more)**
   - Sensory-friendly room flags (unscented amenities, blackout curtains, low-noise floor, away from elevator/ice machine)
   - High-contrast + screen-reader-first navigation
   - ASL video concierge on demand (third-party API: Convo, Sorenson)
   - Cognitive load mode (simplified UI, dyslexia font, reduced motion)
   - Hearing-impaired room kit pre-flagged on booking (visual doorbell, vibrating alarm)
   Investigate: Marriott's existing accessible-room inventory tagging, ADA compliance audit findings, neurodivergent traveler research.

5. **Vegan / Dietary Intelligence**
   Per-property vegan/vegetarian/halal/kosher/gluten-free/allergen index with confidence score. In-room dining filtered by diet. Nearby vetted partner restaurants (HappyCow-style integration). Pre-stocked mini-fridge option. Investigate: F&B vendor data, allergen tracking SOPs, current dietary tagging gaps.

6. **Pet-Friendliness Graph**
   Beyond a binary "pets allowed" flag: nearby vets (24/7 emergency), dog walkers, sitters, dog parks, pet-welcome restaurants and bars, pet supply stores, pet weight/breed restrictions per property, pet fee transparency, in-room pet bed/bowl on request. Marketplace model with partner revenue share. Investigate: existing pet policy data quality, opportunities with Rover/Wag/local vet networks.

7. **Local Partner Marketplace**
   Curated, Marriott-vetted local experiences: bike rentals, vegan restaurants, accessibility-friendly tours, sustainable activities, refill stations, indie coffee, local makers. Revenue share with partners. Differs from concierge-recommended in that it's **transactable in-app** with Bonvoy points eligible. Investigate: existing Marriott Bonvoy Moments, local partnership programs, GDS partner integrations.

8. **Community Events & Guest Matching**
   - Property-level: what's happening at the hotel (run club 7am, coworking lounge hours, rooftop yoga, sustainability tour)
   - City-level: what's happening nearby during the stay window
   - Optional opt-in **guest matching**: same property + similar loyalty tier or interests → suggested meetups (privacy-controlled, anonymized handles, opt-out default). Targets Gen Z's "third place" / community values.
   Investigate: legal/safety implications of guest-to-guest matching, existing Marriott event data.

9. **Pre-Stay & Live-Stay Conversational Concierge**
   Chariot-style RAG chatbot, but with three modes: **pre-arrival** (Arrival Brief + planning), **on-property** (real-time requests, FAQ, work orders), **post-stay** (lost & found, follow-up bookings, feedback). Multilingual. Voice-first option. Investigate: current chatbot/IVR coverage, language coverage, RAG data sources per property.

10. **Bonvoy Green Points & Gen Z Reward Reskin**
    Re-theme some loyalty mechanics for Gen Z: experiences > status, social proof (privacy-respecting), micro-rewards for sustainable choices (linen reuse, declined housekeeping, public transit to airport, refilling water bottle at station), gamified streaks. Investigate: current Bonvoy points economics, behavioral economics studies on micro-rewards, regulatory limits on loyalty currency.

---

## 3. Specific Research Tasks We Need You to Do

Please return findings organized in these sections:

### A. Gen Z Travel Behavior — Internal Marriott Data First
- What does Marriott's own customer research / segmentation say about Gen Z?
- Booking funnel drop-off rates by age cohort.
- App engagement metrics by cohort.
- Loyalty program participation rate by cohort.
- Top complaints / NPS detractors among Gen Z guests.
- Revenue per available room (RevPAR) impact projections if Gen Z share grows.

### B. Competitive Landscape
- Gen Z-targeted features at: Hilton Honors, World of Hyatt, IHG One Rewards, Accor ALL, Airbnb, Booking.com, Selina, citizenM, Yotel.
- Where are *they* winning Gen Z that we're losing?

### C. Associate Workflow Research
- Pull current SOPs for: front-desk check-in, special requests handling, complaint escalation, housekeeping work orders, F&B in-room dining, concierge recommendations.
- Identify the **top 5 highest-volume associate tasks** that could be automated/self-served without quality loss.
- Identify any features in our wishlist that risk *increasing* associate load and propose mitigations.
- Cite internal Marriott training materials, EMPOWER data, GXP data.

### D. Data Plumbing — For Each Feature, Answer:
- Which Marriott system owns the source-of-truth data?
- Which team owns that system? (Approximate org / VP-level if possible.)
- Is there an existing internal API? Schema?
- What's the freshness SLA?
- If data doesn't exist, what's the cheapest way to start collecting?
- For the **Eco Rating** specifically: produce a data-flow diagram suggestion from BMS/utility/supplier sources → ETL → score → app surface.

### E. Sustainability — Real Numbers
- Marriott's published Serve360 commitments and current progress.
- What metrics are *already* tracked per-property vs. portfolio-wide vs. not at all?
- What would it take to surface real per-property eco data in the app?
- Greenwashing risk and how to mitigate (third-party verification, methodology transparency).

### F. Accessibility — Compliance + Inclusion
- Marriott's current accessibility commitments and ADA/WCAG compliance status.
- Inventory tagging gaps for sensory-friendly / neurodivergent-friendly rooms.
- ASL concierge feasibility and existing hospitality precedents.
- Legal landscape (ADA Title III, EU Accessibility Act 2025, local regs).

### G. Privacy & Trust Architecture
- Current Bonvoy data-handling posture (cite privacy policy, internal data classification).
- What guest-matching / community features are legally viable in EU vs US vs APAC?
- On-device inference candidates (where can we avoid sending data to servers?).
- "Delete everything" implementation realism — what's actually deletable today vs. retained for compliance?

### H. Unique Angles We Might Be Missing
Brainstorm 10+ additional Gen Z-relevant feature ideas we haven't listed, scored on:
- Impact (1–10)
- Build effort for a hackathon demo (1–10)
- Associate Effort Delta (-5 to +5; negative is good)
- Strategic fit with Marriott's stated priorities

### I. Weaknesses in Our Current Concept
Be brutal. Where will judges poke holes? What's naive, what's been done before, what's operationally impossible, what's a privacy minefield, what won't scale?

### J. Demo Architecture Recommendation
Given a 1–2 day build window, recommend:
- Frontend stack (React Native / Next.js / Expo / Flutter — with reasoning)
- Backend stack (FastAPI + Postgres + Redis? Mock-only? Serverless?)
- LLM/RAG stack (which internal Marriott LLM gateway? Which embeddings? Which vector DB?)
- Auth (mock Cognito? bypass?)
- Which 3 features to **fully build** vs. **storyboard/mock** for max judge impact.
- A concrete **demo script** (90–120 seconds, beat-by-beat) that maximizes "wow."

### K. Pitch Narrative
Draft a 60-second elevator pitch and a 5-minute demo script that:
- Opens with the Gen Z problem statement (with one killer stat).
- Frames the dual constraint (don't break Boomers, don't burden associates).
- Walks 3 hero features.
- Closes with the data-plumbing and rollout story (so judges know it's not just a demo).

---

## 4. Output Format We Want From You

For each section above, return:
1. **Findings** (bulleted, with internal-doc citations where possible: doc name, owner team, link).
2. **Recommendations** (what we should *do*, prioritized).
3. **Open questions** (what you couldn't resolve and we should investigate manually).
4. **Confidence level** per claim (High / Medium / Low).

At the very end, produce:
- A **prioritized feature shortlist** (top 5 to build for the demo) with justification.
- A **risk register** (top 10 risks, likelihood × impact, mitigation).
- A **one-page exec summary** suitable for showing a Marriott VP.

---

## 5. Tone & Posture

- Be skeptical. Push back on our assumptions.
- Prefer internal Marriott sources over public ones; cite both when relevant.
- Quantify wherever possible. "Gen Z prefers X" is weak; "Gen Z prefers X by 34% vs. Millennials per [Skift 2025 report]" is strong.
- Surface inconvenient truths. If a feature is a bad idea, say so.
- We're not married to any feature on the list — kill any that don't survive scrutiny.

---

## 6. What Success Looks Like for This Research

We come out of your response with:
1. A ruthlessly prioritized list of 3–5 features we'll actually build.
2. Confidence the Eco Rating, Arrival Brief, Accessibility Suite, and Concierge are *grounded in real Marriott data plumbing*, not vaporware.
3. A defensible answer to every "but what about the associates?" and "but what about Boomers?" question.
4. A pitch narrative that lands with non-technical Marriott execs.
5. Identification of at least 2 ideas we hadn't thought of that are clearly winners.

Go deep. Take your time. Cite sources.
