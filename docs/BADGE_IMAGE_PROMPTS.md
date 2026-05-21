# Badge Image Prompts — Marriott Bonvoy Enhanced Experience

Drop generated PNGs (square, transparent or dark background) into
`frontend/public/badges/` using the `image_id` listed below as the
filename, e.g. `green-stay.png`, `frequent-stayer.png`.

The frontend `BadgeShelf` will load `/badges/{image_id}.png` automatically
and fall through to a Lucide icon if the asset is missing — so you can
ship badges incrementally.

## Style Direction (use as a system / "global style" prompt)

> **Refined Marriott luxury — gold-leaf metallic icons on a deep
> ink-black background, minimal flat-modern design. Square 1:1 ratio.
> Single hero icon, centered, occupying ~60% of the canvas. Thin elegant
> line-work with subtle metallic gradient. No text, no logos, no people.
> Premium, editorial, hospitality-grade. Color palette: warm gold
> (#C9A961), brushed bronze, deep ink black (#0F1419), off-white accent.
> The badge should feel like an embossed seal you'd find on a leather
> luxury hotel passport.**

Paste that style block at the **top** of every Copilot prompt below for
consistency, then append the per-badge prompt.

---

## Sustainability category (3 badges)

### `green-stay.png`
> A single elegant gold leaf, slightly curled, centered on a deep
> ink-black square. The leaf has subtle veining picked out in brighter
> gold. A faint circular embossed border surrounds it like a luxury
> hotel seal. Clean, minimal, no text.

### `eco-warrior.png`
> A heraldic shield in brushed gold, viewed straight-on, embossed
> with a stylized leaf motif at its center. The shield has a subtle
> bronze patina at the edges. Centered on deep ink-black background.
> Reads as "guardian of sustainability." No text, no banners.

### `brand-eco-native.png`
> A delicate gold sprig with three small leaves, rendered in a clean
> botanical illustration style, centered on a deep ink-black square.
> The leaves have a hand-engraved, fine-line look — like an etching on
> the front of a luxury brand's stationery. No text.

---

## Loyalty category (3 badges)

### `welcome-aboard.png`
> A single stylized five-point star in polished gold, centered on a
> deep ink-black square, surrounded by a thin embossed circular
> border. The star has subtle radial gleam lines suggesting
> "first light." Hospitality-luxe, like the front of a personalized
> welcome card. No text.

### `frequent-stayer.png`
> Three concentric gold rings, perfectly nested, centered on a deep
> ink-black square. Each ring slightly thicker than the last,
> suggesting growing loyalty. Subtle metallic gradient on the rings.
> An embossed circular border surrounds the design. Minimal, premium.
> No text.

### `brand-loyalist.png`
> An ornate gold laurel wreath with two curving branches forming an
> open circle, centered on a deep ink-black square. Thin, elegant
> line-work. The wreath has a subtle bronze sheen at the tips of each
> leaf. Reads as "ceremonial recognition." No text inside the wreath.

---

## Explorer category (3 badges)

### `globetrotter.png`
> A simple line-art globe in gold, viewed at a slight 3/4 angle,
> showing a few thin meridian and equator lines. A single small gold
> star sits to the upper-right of the globe, like a destination
> marker. Centered on a deep ink-black square. Minimal, editorial.
> No text, no continent shapes — just the wireframe globe.

### `brand-sampler.png`
> Five small gold diamond shapes arranged in a horizontal row,
> centered on a deep ink-black square. Each diamond is slightly
> different in size, creating a subtle wave pattern. Each diamond
> has a faint metallic gradient. A thin embossed border surrounds the
> composition. Reads as "variety, curated." No text.

### `property-pioneer.png`
> A gold trophy or chalice, viewed straight-on, with two delicate
> handles curving outward. Centered on a deep ink-black square. The
> trophy has a subtle engraved laurel detail on its bowl. Premium,
> hospitality awards aesthetic. No text, no banners.

---

## Lifestyle category (3 badges)

### `pet-parent.png`
> A single elegant gold paw print, centered on a deep ink-black
> square. The paw has a subtle metallic gradient and a thin embossed
> circular border around it. Clean, minimal, modern — not cartoonish.
> Feels like a luxury pet hotel's emblem. No text.

### `concierge-of-one.png`
> A gold key with an ornate baroque handle, lying horizontally,
> centered on a deep ink-black square. The key has subtle bronze
> aging at the bow. Reads as "concierge service" — like the kind of
> oversized brass key you'd see at a five-star property. Embossed
> circular border. No text.

### `local-explorer.png`
> A gold compass rose, four cardinal points only, with a slim
> elongated needle. Centered on a deep ink-black square. The compass
> is rendered as flat line-art with subtle metallic gradient — not
> photorealistic. Thin embossed border. Editorial, minimal. No text,
> no degree markings.

---

## How to use these in Copilot / image generators

1. Open Copilot (or DALL·E 3, Midjourney, Stable Diffusion XL — any of them work).
2. Paste the **Style Direction** block first.
3. Append the per-badge prompt (e.g. the `green-stay` block).
4. Generate at 1024×1024.
5. Save as `frontend/public/badges/{image_id}.png` using the heading
   names above (e.g. `green-stay.png`).
6. Reload the profile page — `BadgeShelf` swaps in the PNG automatically.

### Tips
- If a prompt feels too "ornate," append: *"reduce ornamentation, simplify line-work."*
- If results have text artifacts: append *"absolutely no text, no letters, no numbers, no logos."*
- For consistency across all 12, **generate them in one session** — most models hold style memory across a conversation.
- For Copilot specifically, pin the Style Direction as a "system message" if available; otherwise paste it before every per-badge prompt.

## File checklist

```
frontend/public/badges/
├── green-stay.png
├── eco-warrior.png
├── brand-eco-native.png
├── welcome-aboard.png
├── frequent-stayer.png
├── brand-loyalist.png
├── globetrotter.png
├── brand-sampler.png
├── property-pioneer.png
├── pet-parent.png
├── concierge-of-one.png
└── local-explorer.png
```

12 PNGs, square 1024×1024, ~80–200 KB each after compression.
