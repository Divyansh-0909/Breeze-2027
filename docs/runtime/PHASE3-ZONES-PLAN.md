# Phase 3 plan: zone-by-zone overhauls and data-driven states

Status: draft for review (Claude Opus 5.5 builder, Antigravity Gemini 4 Hydrogen reviewer), 27 Nov 2026. Branch
`work-in-progress-2027` (worktree `Breeze-2027-wip`). Earlier phases: `PHASE1-NIGHT-GULLY-PLAN.md`, `PHASE2-COURTYARD-SCREEN-PLAN.md`.
Mockups: `references/01-entrance-gate.webp`, `04-accommodation.png`, `05-organising-mural.webp`, `06-events-wall.webp`,
`07-contact-desk.png`. Baseline captures: `screenshots/phase3-baseline/`.

User decisions (27 Nov): the navigation board over the gate is **restyled** as a weathered, hand-painted gully sign (kept for
wayfinding); accommodation shows the mockup tiers **DORM PASS / SHARED ROOM / 3-DAY STAY with prices "TBA"** from one config file,
**closed by default**.

## Architecture (applies to every zone)

- **No new draw families.** Zone parts join the Phase 2 merged meshes: steel (rust surface), props (lit atlas), emissive atlas
  (lenses, glows, interiors), decals (stencils, flyers, chalk boards), glow sprites. States (shutter open/closed, poster count) are
  decided once per visit, so everything stays static and merged. The only new draw is a **poster atlas** (all event posters composed
  into one canvas texture). Expected: plaza view ~+1 draw (104 / 75), zone views +2–4.
- **Light pools become a registry**: any number of pool specs (lamps per zone); each frame the N nearest to the camera (score =
  distance − radius) are bound, with a 0.4 s fade in/out so swaps never pop. N stays 4 / 4 / 3 (no shader change).
- Atlases grow to fit new art (stencil words, chalk boards, rate board, key board, mesh grille), still sized by tier (1024 / 512).
- Every zone state can be forced in the preview for testing: `?events=0|1|4|9`, `?stay=open|closed` (preview path only; live pages
  use the catalog and the config).

## 1. Entrance gate (mockup 01; `cypher-gate` + `cypher-approach` chunks)

- **Compound wall, lane side**: muted chalk/charcoal `GULLY VERSE` (large) and `BREEZE '27` stencils on the left wall; torn hip-hop /
  battle flyers plus stencilled arrows pointing into the gate on the right wall. Placed by ray-cast against the gate chunk (doorway
  x ±1.5, wall face z ≈ −15). Decal draw.
- **Crooked sodium streetlamp** over the gate: bent pole on the left pier, arm leaning over the doorway, caged sodium head
  (steel + emissive), a tight amber pool on the gate bars and the concrete in front (lane-side pool, radius 7, ×2.2) and a cool
  screen-spill pool spilling out through the doorway (radius 6, cool-neutral, ×0.5).
- **Gate leaf**: the existing steel-rod leaf keeps its rust surface; check it reads half-open (rotate about its hinge if not).
- **Navigation board restyle** (`nav-board.ts`): blue header → faded rust-brown painted sheet (`#6e4127` family), green panels →
  dull charcoal-teal paint; lettering chalk (`#d3ccbc`) instead of glowing white; no emissive ("retroreflective") glow; rust bloom and
  chipped edges via the rust surface; arrows kept. Sponsor LED kept.
- **Entrance draw calls** (182 / 141 vs 120 / 80, deferred from Phase 1): see "Open question" below.

## 2. Events wall (mockup 06; data-driven)

- Hide the baked poster slots and their frames; damp charcoal plaster stays (Phase 1 grade); existing `EVENTS` lettering tinted to
  faded chalk/rust; **rusted corrugated roll-down shutter** in the centre window (steel, shutter surface: ridges + rust); overhead cool
  tube (existing practical) gets a glow sprite and a cool pool; weathered crates by the doorways (props).
- **Poster coherence pass**: each event image is drawn once into the poster atlas cell: 30% desaturation, multiplied concrete grime,
  torn-paper alpha edge, slight curl shading. The crisp original URL stays for the dialog.
- **State by `events.length`** (all current events, not the page):
  - `0`: no posters; shutter closed with a thin warm tungsten sliver under its bottom edge (emissive strip + small warm pool);
    `LINEUP DROPPING SOON` stencil on the plaster. The dialog's "Event listings are temporarily unavailable" is replaced by a
    "Lineup dropping soon" line.
  - `1`: one hero poster ×1.4 left of the shutter, lit; `MORE DROPPING SOON` stencil right; clicking it opens that event directly.
  - `2–6`: posters on fixed anchors both sides of the shutter, z-rotation −3° … +3°, z-offsets 0.002 m apart.
  - `7+`: the newest 6 on the wall, shutter cracked open 0.35 m with warm interior glow; clicking the shutter or `BROWSE EVENTS`
    opens the full events list (today's dialog; Phase 4 turns it into the drawer).

## 3. Organising committee mural (mockup 05)

- Mural material (team carousel, `artKind: mural-composition`): desaturate ~35% toward dusty rust / ochre / chalk; blend the plaster
  sheet (albedo detail, grime, cracks, bump) into the paint at ~88% so the wall relief shows through.
- Replace the harsh white flood with one **dim warm caged work lamp** above the mural (fixture + sodium pool, radius 6), and on the
  mural only, remap its baked flood light toward warm and fade it toward the edges (radial falloff) so the edges sink into shadow.

## 4. Accommodation (mockup 04; `isAccommodationOpen`)

- `lib/accommodation.ts`: `{ isAccommodationOpen: false, tiers: [{ name: "DORM PASS", price: "TBA" }, { name: "SHARED ROOM", price: "TBA" },
  { name: "3-DAY STAY", price: "TBA" }] }`; `?stay=open|closed` overrides in the preview.
- **Closed**: the COMING SOON graffiti is hidden; muted chalk `STAY // ACCOMMODATION` stencil on the wall; rusted shutter pulled down
  over the right window with a faint warm sliver and `CHECK-IN OPENS SOON` stencilled on it.
- **Open**: shutter rolled up (a rolled drum at the head); behind it a dim check-in counter (props), a low-watt hanging tungsten bulb
  (emissive + small warm pool), a key-hook board and a worn register book (atlas); a riveted dark-metal **chalk rate board** on the
  wall listing the tiers (one bold pass if only one tier).

## 5. Contact booth (mockup 07)

- The bright "message surface" inside the window is hidden; the window becomes a dim open booth: hanging warm bulb (emissive +
  pool), rusted metal mesh grille at the back (alpha-tested decal), two old speaker boxes inside (props), torn flyers along the counter
  base (decals), the `CONTACT US` graffiti desaturated further toward chalk / rust, and a weathered chalk quick-contact board on the
  left wall. The form stays as today until Phase 4 moves it into the side drawer.
- Known: the phone-GLB lightmap streak on the soffit above CONTACT US needs a phone-GLB re-export (Blender pipeline), out of runtime scope.

## Checks

Zone captures (desktop + phone) into `screenshots/phase3-r<n>/`, state captures for events 0 / 1 / 4 / 9 and stay open / closed, the
theater/keys script, draw calls per zone, no console errors; up to 3 Antigravity rounds to 8.5+ per zone.

## Open question for the reviewer: the entrance draw budget

The entrance view (lane, looking at the gate) is 182 desktop / 141 phone: lane chunks ~70, plaza chunk ~45 (seen through the gate
and above the wall), crowd ~41 multi-draws (15 avatars × 2–3 materials), plus nav board and dressing. Options considered:
(a) spatially split plaza batches into below/above-wall bands and cull the below-wall band from the lane: saves ~20 at the entrance
but adds ~15 in the plaza view (103 → ~118 desktop, 74 → ~89 phone: breaks the phone plaza budget);
(b) hide the crowd's avatars that are entirely behind the wall from the lane: does not reduce multi-draws (one per material);
(c) a lane-only "crowd glimpse" (only the avatars visible through the gate, 6 avatars): crowd 41 → ~15 at the entrance;
(d) merge the lane chunks' remaining per-material draws further with a texture atlas of their small textured props (offline).
Proposal: (c) now (runtime only), (d) recorded as a pipeline follow-up; accept the entrance as the one view over budget otherwise.

## Surveyed geometry (27 Nov, merged-off scene)

- Gate: compound wall lane face z −14.19, x ±8.3, height 7.2–9.85 (coping to 10.03); doorway between jambs x ±1.08; the steel-rod
  leaf already stands open toward the lane (x −0.97…−0.86, z −14.86…−13.15). The **navigation board stands 4 m in front of the gate**
  (z −11, uprights x ±3.2, panels y 9.2–14.95), so from the approach spawn anything mounted above the doorway is hidden: the crooked
  streetlamp stands on the **left wall beside the board** (pole at x −4.4 against the wall, arm leaning in to x ≈ −3.5, head y ≈ 11.9),
  and its amber pool falls on the left wall, the gate bars and the lane floor.
- Events wall: plane x −15.85; baked poster slots 0–7 at z −27.93…−29.72 (left pair) and −32.38…−34.17 (right pair), rows
  y 7.38–8.38 and 8.50–9.50, plus their retainer frames; centre window between them (z ≈ −30…−32.1); `EVENTS` heading z −28.3…−29.3,
  y 9.55–9.75; tube practical at (−14.75, 10.1, −31.1).
- Accommodation: graffiti around (−16.9, 9.0, −17.5) on a wall facing (0.947, 0, 0.321); the right window is ray-cast along the wall.
- Contact: message surface x 15.86…17.38, z −20.81…−16.55, y 8.2…9.21 (angled facade; booth interior placed in the contact frame of
  `cypher-contact.ts`).
- Mural: plane x 15.13, z −35.32…−27.57, y 7.30…11.08.

Drafted by Hydrogen and reviewed: `event-wall-art.ts` (fixture events for `?events=N`, poster coherence pass).

## Plan review (27 Nov, Gemini 4 Hydrogen High via the agy CLI): AGREE WITH CHANGES

Adopted:
- **Entrance budget**: option (c) crowd glimpse (6 doorway avatars at the lane, crowd ~41 → ~15 draws) **plus lane-mode culling**: while
  the camera is in the lane (z > −13.5), hide the plaza dressing that cannot be seen through the gate (props, prop shadows, wall decals)
  and the cypher-plaza batches that sit wholly below the coping (y < 9.85) outside the doorway sight cone (x ∉ [−2.5, 2.5]). No
  re-batching, so the plaza view keeps its 104 / 75. Phase 3 target for the entrance: **≤ 140 desktop / ≤ 105 phone** (true baseline
  190 / 148, not 182 / 141); (d) offline atlasing stays a pipeline follow-up.
- **Pool registry**: score = distance − radius with a −5 m bias for pools within 10 m (so a wide pool cannot crowd out the small
  practical next to the viewer), 1.5 m hysteresis before swapping, 0.35 s fade-in; on phones the plaza keeps its 3 core pools when
  z < −20 (the zone pools only take a slot at their own zone).
- **Entrance**: streetlamp pole x −4.2, head (−2.6, 11.1, −13.6), pool r 7.5 ×2.0; screen spill (0, 8.8, −16.5) r 6.5 ×0.45; sponsor
  LED dimmed ×0.30; stencils/flyers kept in x ∈ [±1.35, ±4.1] (clear of the jambs and the wall ends); the 3 avatars standing in front
  of the right-wall flyers are hidden; the restyled nav board keeps emissiveIntensity 0.08 so the paint does not go black at night.
- **Events**: hide the green shutter leaf beside the window; 6 paste-ups 0.78 × 1.05 m, hero 1.10 × 1.48 m, −3°…+3°, 0.002 m z-steps;
  tube pool r 7 ×1.1; closed sliver r 2.8 ×0.55; 7+ crack 0.35 m, interior pool r 3.5 ×0.9; one event: clicking the hero poster opens
  that event; 7+: clicking the shutter opens the full list; `?events` fixtures also fill in when the catalog is unavailable in the
  preview; the wall pages with `eventsPerPage` 8 stay in the dialog.
- **Mural**: the mural background is near-black, so a plain plaster blend stays black: luma < 0.12 is first remapped to the graded
  plaster, then the 88% plaster detail blend; baked light × vec3(1.15, 0.85, 0.55) with a radial falloff 1.0 → 0.18; both the
  `original` and `alternate` mural materials are patched; lamp (14.75, 11.45, −31.45) r 6 ×1.6.
- **Accommodation**: widen `accommodationView` 3.65 → 4.6 m aimed at z ≈ −16.7 so the phone crop holds the window; the hidden
  COMING SOON leaves a bright baked patch, so the STAY stencil (w 2.2, y 8.95) sits over it on a grime decal; open bulb r 3.2 ×1.2.
- **Contact**: hiding the message surface exposes an empty hole, so an interior box 0.85 m deep (props, dark plaster) is added
  behind it; bulb r 3.5 ×1.3; chalk board 1.45 × 1.05 at y ≈ 8.6; `CONTACT US` desaturated to S ≤ 0.30.

Declined: none of the numbers; the reviewer's suggestion to split plaza batches (a) stays declined for the phone plaza budget, which
it also flagged.
