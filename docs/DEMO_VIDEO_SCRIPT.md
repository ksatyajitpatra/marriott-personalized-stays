# Bonvoy+ Curated — Demo Video Script

> **Target length:** 3:30 (± 10 sec)
> **Use case:** Backup demo video that lives inside the 8-minute live CodeFest slot.
> Also doubles as the script for the live demo if the recording fails.

---

## Why 3:30

For a CodeFest demo that lives **inside** the 8-minute live slot, **3:30 is the sweet spot**.

- **Longer than 4:00** → eats into your hypothesis / architecture / Q&A beats.
- **Shorter than 3:00** → can't show all three hero features convincingly.
- **3:30** → all three features land, leaves ~4:30 for slides + Q&A.

---

## Recording rules baked into this script

1. **One persona switch only** (Sam → Jordan). Two switches eat 30 seconds and confuse viewers.
2. **No mouse hesitation.** Every action is pre-rehearsed and narrated *as you do it*, not before or after.
3. **Voice-over recorded separately** and laid over screen capture — much easier than nailing both live. If recording live, add ~15 sec of buffer.
4. **"Privacy boundary"** and **"Associate Effort Delta ≤ 0"** are name-dropped twice — those are the two phrases senior leadership will remember.
5. **"For every generation"** appears in the cold open and the close — directly answers the "don't frame this as Gen Z only" PRD constraint.

---

## Script

> **Format:** `[ON-SCREEN action]` in brackets, narration in plain text.
> Words in **bold** are emphasis beats — slow down or stress them.
> Times are cumulative.

---

### Cold open — 0:00 → 0:15  (15 sec)

**[ON-SCREEN: app `/sign-in` page, three persona cards visible]**

> "Marriott already collects sustainability data, dietary preferences, pet policies, and partner relationships across 8,000-plus properties. **None of it surfaces where it converts** — at booking, before arrival, or in-stay. Bonvoy+ is the layer that fixes that. Three features. Zero new associate workload. Let me show you."

---

### Beat 1 — Eco transparency at booking — 0:15 → 1:00  (45 sec)

**[Click Sam — "Bonvoy Silver, vegan, cyclist." Land on home.]**

> "I'm signed in as Sam — a Bonvoy Silver member who's vegan and travels with a bike. I'm searching New York."

**[Type "New York" → Search. Results page loads with EcoScoreRing on every card.]**

> "Every result card now shows a per-property **Eco Score**, zero to ten. **No major hotel chain does this today at the booking funnel.**"

**[Drag the eco filter slider to 7. Toggle the pet-friendly chip.]**

> "I can filter by eco score, by pet-friendliness — surfaces Marriott already collects but never exposed."

**[Click into the New York Marriott Marquis hotel page. Scroll to the eco breakdown.]**

> "Open a property and you see the **six sub-scores** — energy, water, waste, certifications, carbon offset, F&B sourcing — each cited to its source system. **MESH, last updated April 22nd.** Guests can audit the math. This is **defensible, not greenwashing.**"

**[Highlight the "+900 Green Points" callout.]**

> "And properties scoring eight or above earn the guest a **900-point Green Points multiplier.** That's a behavioral nudge, not a checkbox — it gives Marriott a direct-channel reason to book inside our app instead of an OTA."

---

### Beat 2 — Agentic Arrival Brief — 1:00 → 2:15  (75 sec — **the hero beat**)

**[Persona switcher → Jordan. "Bonvoy Platinum, halal, traveling with dog Cooper."]**

> "Now I'm Jordan — Platinum tier, halal diet, traveling with a dog named Cooper to Chicago next weekend."

**[Click My Trips → upcoming Chicago stay. Click "Build my brief."]**

> "I tap **Build my brief.** What you're watching is **not a chatbot** — it's an agent."

**[Agent Trace Pane streams live. Six tool rows light up in parallel with `live` / `mock` badges and timing.]**

> "Six tools fire in **parallel** — weather, events, halal dining, pet services, activities, and our partner catalog. Each row shows whether it hit a **live** API or a deterministic **mock fallback**, plus latency. **Twelve-second hard timeout, every tool. Demo-safe under load.**"

**[Brief composes below the trace pane. Halal dining picks render. Pet services render. Weather + packing tips render.]**

> "Two LLM rounds — one to plan tool calls, one to compose. The composer can **only** rank what tools returned. **It cannot invent a partner or an event.** That's how we kill hallucinations."

**[Hover an "Book via Marriott +250 pts" affiliate chip on a dining card. Scroll to the affiliate ledger panel at the bottom.]**

> "Every recommendation is a tracked deeplink. OpenTable, Viator, Rover, Ticketmaster — all real public affiliate programs, eight to fifteen percent. **Half of every commission flows back to the guest as Bonvoy bonus points.** This is a new **Non-RevPAR Affiliation Fees** revenue stream that doesn't depend on a single new contract Marriott doesn't already have access to."

**[Pause one beat on the privacy line.]**

> "And — important — Tavily and the LLM only ever see **city, dates, dietary tags, interests, and the query.** **No name. No loyalty number. No pet name.** The privacy boundary is enforced in code."

---

### Beat 3 — Pet + Local Partner Map — 2:15 → 3:00  (45 sec)

**[Scroll the Chicago trip page to the Partner Map. Filter to Pet. Drag the radius slider from 10 mi → 5 mi.]**

> "Same trip, scroll down — interactive Mapbox of local partners. Vets, mobile groomers, dog parks, walkers. Filter by pet, drag the radius — **ten miles by default, guest-configurable.**"

**[Tap a "Comes to you" mobile-grooming pin → Paws & Polish. Tap Book.]**

> "Mobile providers get a **'Comes to you'** badge — they meet the guest at the hotel. **Zero coordination overhead for the front desk.** I tap Book —"

**[Booking sheet appears. Pick a date and time. Confirm.]**

> "— pick a date, a time, confirm. Pet booking is now on the reservation. **Pet-friendly travel is a four-point-six billion dollar market with no integrated app experience.** We just shipped one."

---

### Close — 3:00 → 3:30  (30 sec — the money close)

**[Cut to a clean view of the Trips page or the home screen with Bonvoy+ branding.]**

> "Three features, one privacy boundary, **twelve thousand seven hundred lines of code.**"

> "Every feature ladders to a named Bonvoy KPI — **Digital Direct Share, Intent to Recommend, Non-RevPAR Affiliation Fees, RevPAR.**"

> "And the line we will not cross — **Associate Effort Delta less than or equal to zero, on every feature.** No new SOPs, no new training, no new staffing."

> "Marriott already has the data and the partners. **We just made them visible, personal, and bookable** — for **every** generation."

**[Fade to the Bonvoy+ logo / title slide.]**

---

## Beat-by-beat timing summary

| Beat | Start | End | Duration | Purpose |
|---|---|---|---|---|
| Cold open | 0:00 | 0:15 | 15s | Hook + thesis |
| Eco transparency | 0:15 | 1:00 | 45s | Sustainability + direct-channel lever |
| Agentic Arrival Brief | 1:00 | 2:15 | 75s | **Hero feature** — agent, privacy, affiliate revenue |
| Pet + Local Partner Map | 2:15 | 3:00 | 45s | Pet TAM + accessibility + ops efficiency |
| Close | 3:00 | 3:30 | 30s | KPI ladder + Associate Effort Delta + tagline |
| **Total** | | | **3:30** | |

---

## Recording checklist

- [ ] **Mobile viewport, 390 px width.** Use Chrome DevTools device toolbar — looks like a real Bonvoy app and matches Slide 11 screenshots.
- [ ] **Hide bookmarks bar and any IDE chrome** before recording.
- [ ] **Pre-warm the brief** — trigger Build-my-brief once before recording so cold-start latency doesn't hurt the trace pane drama. (Or accept the cold start — it actually makes the trace pane *more* impressive because tools light up sequentially.)
- [ ] **Pin the camera focus** — lock the recording region to the browser only (QuickTime → "Record selection", or Loom area-select).
- [ ] **Record narration second pass** — screen-record the flow silently first, then voice-over with this script in front of you. Way easier than hitting timing live.
- [ ] **Two takes minimum.** The second is always tighter.
- [ ] **Final length check:** if you're over 3:45, cut the radius-slider line in Beat 3 first, then the "behavioral nudge" line in Beat 1.

---

## Stylistic guardrails

| Avoid | Use instead |
|---|---|
| "Gamification" | "Behavioral nudge" or "Green Points multiplier" |
| "Gen Z" / "for the new generation" | "For every generation" / "the conscious-traveler cohort" |
| "We can charge more for these hotels" | "Premium positioning for sustainability-leader properties" |
| "Chatbot" | "Agent with parallel tool-calling" |
| "AI features" | "Agentic, grounded recommendations" |

---

## Variants (optional, if you want backups)

- **90-second cut** — drop Beat 1 (eco) and the close; lead straight with the brief, end on Pet Map. Good if the live demo runs long and you need a tight backup.
- **45-second teaser loop** — Beat 2 only, no narration, captioned bullets. Good for autoplay on Slide 6.

Ask if you want either of these written out.
