# Architecture Diagram — Alternative Versions (Slide 7)
### Same content. Different ways to land it with execs.

> Pick **one** to put on slide 7. If a single diagram still feels heavy, use **V2** as
> the main slide and tuck **V1** or **V6** into the appendix for Q&A.
>
> All diagrams render at [mermaid.live](https://mermaid.live) — paste, screenshot, drop into PPT.
>
> **Reading guide:**
> - V1 = simplest (3 lanes, 9 boxes) — fastest to grok
> - V2 = "untouched vs additive" — strongest exec narrative
> - V3 = three small diagrams, one per hero feature — visual variety
> - V4 = onion layers — for the design-y crowd
> - V5 = numbered story flow — best if you want to walk the diagram beat-by-beat
> - V6 = hub-and-spoke — emphasizes our additive layer as the center of gravity

---

## V1 — Three Clean Lanes (recommended for the slide)

**Vibe:** "Three layers, one direction of data flow. Read top-to-bottom."
**Box count:** 9. **Use when:** the room hasn't seen the project before.

```mermaid
flowchart TB
    subgraph G["GUEST  (mobile-first web app)"]
        UI["Bonvoy app shell + our additive UI<br/>(eco ring · arrival brief · partner map)"]
    end

    subgraph N["NEW — Additive Service Layer  (FastAPI)"]
        direction LR
        ECO["Eco Service"]
        BRIEF["Concierge Agent<br/>(Arrival Brief)"]
        PET["Pet & Partner Service"]
    end

    subgraph M["EXISTING Marriott Systems  (read-only in v1)"]
        direction LR
        MESH["MESH<br/>(energy / water /<br/>waste / certs)"]
        OPERA["Opera PMS<br/>(stays, pet policy)"]
        CDP["Bonvoy CDP<br/>(prefs · points · badges)"]
        TIPAI["TIP.AI LiteLLM<br/>Gateway"]
    end

    UI --> ECO
    UI --> BRIEF
    UI --> PET
    ECO --> MESH
    ECO -.points multiplier.-> CDP
    BRIEF --> CDP
    BRIEF --> TIPAI
    PET --> OPERA
    PET --> CDP

    classDef guest fill:#FFF,stroke:#222,color:#222
    classDef new fill:#A6192E,stroke:#A6192E,color:#fff
    classDef old fill:#F5F1EC,stroke:#6E6259,color:#222
    class UI guest
    class ECO,BRIEF,PET new
    class MESH,OPERA,CDP,TIPAI old
```

**One-line takeaway:** *Red is what we built. Cream is what already exists. The arrow direction tells the whole story.*

---

## V2 — "Untouched vs Additive" (strongest exec narrative)

**Vibe:** "We don't change a thing. We extend."
**Box count:** 10. **Use when:** judges/execs are sensitive to "are you proposing to rewrite Bonvoy?" — this slide answers it before they ask.

```mermaid
flowchart LR
    subgraph LEFT["EXISTING BONVOY  —  UNTOUCHED"]
        direction TB
        BOOK["Bonvoy booking flow"]
        APP["Bonvoy app shell"]
        POINTS["Points / loyalty engine"]
        PMS["Opera PMS · MARSHA · CDP · MESH"]
    end

    subgraph RIGHT["OUR ADDITIVE LAYER  —  NEW"]
        direction TB
        SURF["Additive UI surfaces<br/>(eco ring · arrival brief · partner map)"]
        SVC["Additive services<br/>(eco · concierge agent · pet)"]
        LLM["TIP.AI gateway + Tavily<br/>(grounded personalization)"]
        AFF["Affiliate ledger<br/>(commission → bonus points)"]
    end

    APP --- SURF
    BOOK --- SURF
    SVC --> PMS
    SVC --> POINTS
    SVC --> LLM
    AFF --> POINTS

    classDef untouched fill:#F5F1EC,stroke:#6E6259,color:#222
    classDef additive fill:#A6192E,stroke:#A6192E,color:#fff
    class BOOK,APP,POINTS,PMS untouched
    class SURF,SVC,LLM,AFF additive
```

**One-line takeaway:** *The left lane is Bonvoy as it is today. The right lane is everything we add. They meet at the UI shell and the points ledger — nothing else.*

---

## V3 — Feature-Centric Trio (small diagrams, one per hero)

**Vibe:** "Three independent bets. Each is a clean two-step story."
**Use when:** you want the eye to land on **one feature at a time** rather than the whole system.

> Lay these out side-by-side as three small images on slide 7 (or break onto 3 slides if you have room).

### V3a — Eco Rating

```mermaid
flowchart LR
    MESH["MESH<br/>(energy · water · waste)"] --> ECO["Eco Service<br/>weighted formula"]
    SPROUT["SPROUT<br/>(F&B sourcing)"] --> ECO
    ECO --> RING["EcoScoreRing<br/>on every hotel card"]
    ECO --> PTS["Green Points multiplier<br/>+900 / +300 / 0"]
    PTS --> CDP["Bonvoy points ledger"]
    classDef ours fill:#A6192E,stroke:#A6192E,color:#fff
    classDef ext fill:#F5F1EC,stroke:#6E6259,color:#222
    class ECO,RING,PTS ours
    class MESH,SPROUT,CDP ext
```

### V3b — Arrival Brief (agentic concierge)

```mermaid
flowchart LR
    PROF["Guest preferences<br/>(dietary · interests · pet)"] --> AGENT["Concierge Agent<br/>(6 tools, parallel,<br/>12s budget)"]
    TIPAI["TIP.AI LiteLLM"] --> AGENT
    TAV["Tavily Search<br/>(events · dining · pet · activities)"] --> AGENT
    OWM["OpenWeatherMap"] --> AGENT
    AGENT --> BRIEF["Streaming brief<br/>+ live trace"]
    BRIEF --> CHIP["Book-via-Marriott chips<br/>(+bonus Bonvoy points)"]
    classDef ours fill:#A6192E,stroke:#A6192E,color:#fff
    classDef ext fill:#F5F1EC,stroke:#6E6259,color:#222
    class AGENT,BRIEF,CHIP ours
    class PROF,TIPAI,TAV,OWM ext
```

### V3c — Pet + Local Partner Map

```mermaid
flowchart LR
    OPERA["Opera PMS<br/>(pet policy)"] --> PET["Pet & Partner Service"]
    SEEDS["Vetted partner catalog<br/>(walker · mobile grooming · vet)"] --> PET
    RADIUS["Guest radius pref<br/>(1–50 mi, default 10)"] --> PET
    PET --> MAP["Mapbox partner map"]
    PET --> BOOK["In-app booking<br/>(date · time · cancel)"]
    BOOK --> CDP["Pet service bookings<br/>on reservation"]
    classDef ours fill:#A6192E,stroke:#A6192E,color:#fff
    classDef ext fill:#F5F1EC,stroke:#6E6259,color:#222
    class PET,MAP,BOOK ours
    class OPERA,SEEDS,RADIUS,CDP ext
```

**One-line takeaway:** *Each feature is small enough to defend on its own. Together they form one additive layer.*

---

## V4 — Onion Layers (design-forward)

**Vibe:** "The guest is at the top. Each layer below is one degree further from them."
**Use when:** the room responds to structure-as-storytelling.

```mermaid
flowchart TB
    G["GUEST<br/>(mobile web)"]:::guest

    subgraph L1["LAYER 1 — UI Surfaces (additive)"]
        UI1["Eco ring"]
        UI2["Arrival brief"]
        UI3["Partner map"]
    end

    subgraph L2["LAYER 2 — Our Services (FastAPI)"]
        S1["Eco<br/>service"]
        S2["Concierge<br/>agent"]
        S3["Pet & partner<br/>service"]
        S4["Affiliate<br/>ledger"]
    end

    subgraph L3["LAYER 3 — Existing Marriott Systems (read-only)"]
        D1["MESH"]
        D2["Opera PMS"]
        D3["Bonvoy CDP /<br/>points ledger"]
        D4["TIP.AI gateway"]
        D5["SPROUT"]
    end

    subgraph L4["LAYER 4 — External APIs (privacy-bounded)"]
        E1["OpenWeatherMap"]
        E2["Tavily Search"]
        E3["Mapbox"]
    end

    G --> UI1 & UI2 & UI3
    UI1 --> S1
    UI2 --> S2
    UI3 --> S3
    S2 --> S4

    S1 --> D1 & D5
    S2 --> D3 & D4
    S3 --> D2 & D3
    S4 --> D3

    S2 --> E1 & E2
    UI3 --> E3

    classDef guest fill:#fff,stroke:#222
    classDef additive fill:#A6192E,stroke:#A6192E,color:#fff
    classDef existing fill:#F5F1EC,stroke:#6E6259
    classDef ext fill:#fff,stroke:#999,stroke-dasharray: 4 2
    class UI1,UI2,UI3,S1,S2,S3,S4 additive
    class D1,D2,D3,D4,D5 existing
    class E1,E2,E3 ext
```

**One-line takeaway:** *Four layers. We touch the top two. We read the next layer. The outermost layer is opt-in.*

---

## V5 — Numbered Story Flow (walk it like a script)

**Vibe:** "I'll walk you through what happens when a Bonvoy member uses this."
**Use when:** you'd rather narrate than explain — best for a live walkthrough.

```mermaid
flowchart LR
    G["1 · Guest opens<br/>hotel detail"] --> ECO["2 · We pull eco<br/>data from MESH"]
    ECO --> RING["3 · Eco ring + Green Points<br/>multiplier render inline"]
    RING --> BOOK["4 · Guest books<br/>(existing Bonvoy flow)"]
    BOOK --> BRIEF["5 · 48h pre-stay:<br/>guest opts in to brief"]
    BRIEF --> AGENT["6 · Concierge agent runs<br/>6 tools in parallel"]
    AGENT --> RESULT["7 · Brief streams to UI<br/>with live trace"]
    RESULT --> CTA["8 · Tracked affiliate chip<br/>→ bonus Bonvoy points"]
    CTA --> MAP["9 · In-stay: pet + partner map<br/>(radius-filtered)"]
    MAP --> PET["10 · Book pet service in-app<br/>zero front-desk involvement"]

    classDef step fill:#A6192E,stroke:#A6192E,color:#fff
    class G,ECO,RING,BOOK,BRIEF,AGENT,RESULT,CTA,MAP,PET step
```

**One-line takeaway:** *Ten steps. Steps 1–4 happen on day 0. 5–8 happen 48 hours before check-in. 9–10 happen on property. No associate is involved in any step.*

---

## V6 — Hub-and-Spoke (our layer at the center of gravity)

**Vibe:** "We sit between the guest and Marriott's systems-of-record. Everything routes through our additive layer."
**Use when:** you want to emphasize that the additive layer is the **integration surface** — minimal coupling to any single system.

```mermaid
flowchart LR
    GUEST(("Guest"))

    HUB{{"OUR ADDITIVE LAYER<br/>FastAPI services<br/>+ Concierge Agent"}}

    MESH["MESH<br/>(eco data)"]
    OPERA["Opera PMS<br/>(stays, pets)"]
    CDP["Bonvoy CDP<br/>(prefs, points)"]
    TIPAI["TIP.AI gateway"]
    TAV["Tavily search"]
    OWM["OpenWeather"]
    MAP["Mapbox"]

    GUEST <--> HUB
    HUB <--> MESH
    HUB <--> OPERA
    HUB <--> CDP
    HUB <--> TIPAI
    HUB <--> TAV
    HUB <--> OWM
    HUB <--> MAP

    classDef ours fill:#A6192E,stroke:#A6192E,color:#fff
    classDef marriott fill:#F5F1EC,stroke:#6E6259
    classDef ext fill:#fff,stroke:#999,stroke-dasharray: 4 2
    class HUB ours
    class MESH,OPERA,CDP,TIPAI marriott
    class TAV,OWM,MAP ext
```

**One-line takeaway:** *One integration surface. Read from many, write to one (points ledger).*

---

# Which one should you use?

| Audience profile | Pick |
|---|---|
| Execs who haven't seen the project before | **V1** (3 lanes) |
| Execs worried about disruption to existing Bonvoy | **V2** (untouched vs additive) |
| You want to spend more slide time per feature | **V3** (trio) |
| Design-savvy panel, time to read | **V4** (onion) |
| You'd rather narrate than explain | **V5** (numbered) |
| Architecture panel asking "how does this integrate?" | **V6** (hub-and-spoke) |

**My recommendation for an exec audience:** lead with **V2** on the slide; keep **V1** in the appendix; have **V5** ready as a fallback if a judge asks "walk me through it end-to-end."

---

# Style notes (so the diagrams stay on-brand)

- **Red `#A6192E` = something we built.** Cream `#F5F1EC` = existing Marriott. Dashed-outline white = external API.
- **One arrow direction.** Avoid bidirectional arrows except in V6 where the hub pattern depends on it.
- **Max ~10 boxes per diagram.** If you need more, split into V3-style smaller diagrams.
- **Box labels are nouns, not verbs.** ("Eco Service" not "Compute eco score").
- **Render PNG at 2x for projector clarity.** mermaid.live → Actions → Download PNG → "2x".
