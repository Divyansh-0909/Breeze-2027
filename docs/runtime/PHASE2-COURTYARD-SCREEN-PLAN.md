# Phase 2 plan: courtyard visual glue, grounded props, triptych screen

Status: draft for review (Claude Opus 5.5 builder, Antigravity Gemini 4 Hydrogen reviewer), 27 Nov 2026.
References: `references/02-courtyard-plaza.webp`, `references/03-triptych-screen.webp`. Phase 1 record:
`docs/runtime/PHASE1-NIGHT-GULLY-PLAN.md` (palette, tiers, budgets).

## Constraints from the existing scene

- Lighting is **baked** (RGBM lightmaps). Runtime lights add **specular only** on lightmapped surfaces (`fidelity.ts` zeroes their
  direct diffuse so the bake is not counted twice). A new `PointLight` therefore would not light a wall. New fixtures need their own
  diffuse term: see **light pools** below.
- Draw calls today (production, desktop / phone): plaza view **95 / 67**, screen view **83 / 59**, budgets < 120 / < 80. Phase 2 has
  ~13 desktop and ~11 phone draws of headroom in the plaza view.
- Shadow casters: 0 today (budget 2 desktop / 1 phone). Phase 2 adds none (pools are unshadowed; contact shadows are decals).
- Surveyed layout (ray-casts, merged-off scene): plaza floor y = 7.2; facades left x ≈ −16.4, right x ≈ 15.5–16.3, back z ≈ −50.8,
  gate wall z = −15; floors at y ≈ 10.4 / 13.6 / 16.8, roofs ≈ 21; glazed panes at y 11.13–12.42, 14.13–15.42, 17.13–18.42 on the back
  (z −50.8 … −51.75) and right (x 15.8 / 16.27) facades. Screen panels: centre (0, 11.59, −45.72), 14.56 × 5.98 m overall, rear casing
  x −7.34 … 7.34, y 8.54 … 14.64; screen supports x ±3.1 … 7.0 at z −46; rear parapet z −47.8.
- The "floating table" is the **DJ table + turntable** at (−9.3, 8.2, −22.8) (meshes `DJ table leg`, `DJ tabletop at cypher edge`,
  `Turntable platter`).

## Files

1. **`light-pools.ts` (new): diffuse light pools for new fixtures.** One shared uniform block (`vec4 pos+radius[N]`, `vec3 colour[N]`)
   injected into the lightmapped material patch (`fidelity.ts`) and the people patch: `irradiance += colour · max(N·L,0) ·
   (1 − (d/r)²)²` (smooth window, distance 8–12 m as in the playbook), plus a small matching specular. N = budget.localLights − the
   existing specular pool, capped at **4 desktop / 3 phone**. No three.js lights are added, no shadow maps, no recompiles (fixed N).
2. **`courtyard-dressing.ts` (new)**, mounted with the plaza chunk:
   - **Overhead cables**: ~28 sagging catenaries between facade anchors at y 10.6–19 across the courtyard, plus a bundle above the
     gate (z −14…−16) and hanging feeds from the screen truss to the PA stacks. `TubeGeometry` (radialSegments 4, tubularSegments 12,
     radius 0.010–0.022 m, sag 4–9% of span), all merged into **one BufferGeometry, one draw**; dark rubber MeshStandardMaterial
     (roughness 0.55, catches lamp highlights).
   - **Balcony work lamps (3)**: two sodium-amber caged work lamps (left wing y ≈ 13.9, back facade y ≈ 17.1) and one dim cool-white
     tube (right wing y ≈ 10.9). Housings + cages merged with the truss steel (**shared draw**), emissive lenses (**one draw**), additive
     glow sprites (**one InstancedMesh draw**), each feeding a light pool (sodium `#c4883e`, tube `#dbeaee`, radius 9–11 m).
   - **Lived-in windows**: 6 warm interior planes 1.5 cm in front of measured glazed panes (back and right facades, floors 1–3), one
     canvas atlas (warm tungsten gradient, curtain silhouettes, vertical bars and a grid variant), **one draw**, emissive 0.35–0.6 so they
     stay low-intensity.
   - **Grounded props** (replace the DJ table: hidden, kept out of batching): two stacks of matte-black PA boxes, a rusted oil drum,
     three stacked plastic crates near the accommodation corner (around (−9, 7.2, −24)), plus PA stacks at both screen sides (screen
     section). One procedural canvas atlas (speaker grille, crate plastic, drum rust/paint) on one MeshStandardMaterial: **one draw**;
     a soft contact-shadow blob decal under each prop: **one draw** (skipped on phones if the budget is tight).
   - **Wall weathering**: muted charcoal/chalk `GULLY VERSE` and `BREEZE '27` stencils and 5–7 torn monochrome battle flyers on the
     blank inner courtyard wall (left wing ground floor between z −36 and −46, confirmed by a capture before placing). One canvas atlas,
     decal quads with polygon offset, palette-graded, **one draw**. Stencils multiply into the wall (dark paint); flyers are paper.
3. **Triptych screen** (`cypher-aftermovie.ts`, new `screen-rig.ts`):
   - **Anti-blowout LED material** replacing the panels' `MeshBasicMaterial`: video × 0.8, soft-knee highlight compression
     (`c / (1 + 0.35·c)` rescaled), a 4 cm LED pixel grid and faint scanlines that fade out (fwidth) before they alias, slight black
     lift (LED panels are never pure black). Same video texture, same UV crops, same `V SOUND ON` sync.
   - **Rusted pipe truss**: two towers (x ±7.9) and a top box beam (y ≈ 15.2) of 48 mm pipes with diagonal lacing, merged
     (**shared steel draw** with the lamp housings), rust via the Phase 1 rust sheet (UV-mapped).
   - **Power cables** from the top beam down both sides into **PA stacks** (2 × 3 boxes, x ±8.6, z −45): cables merge into the cable
     draw, boxes into the prop draw.
   - **Dust haze**: 3 (high/medium) / 2 (low) soft billboard planes between screen and crowd, procedural noise (256 px canvas),
     alpha 0.05–0.09, slow drift, depthWrite off, fogged: **one InstancedMesh draw**. Their tint follows the screen's average colour
     (sampled from a 1×1 mip of the video each 0.5 s) at low strength, so haze glows like spill.
   - **Theater mode**: the existing "Watch Aftermovie" action (E / click on the panels) opens a minimal dark overlay: the film itself
     (the same `<video>` element, moved into the overlay while open) at up to 92 vw × 16:9, sound toggle, `Esc` / backdrop / button returns
     to walking (camera and focus restored). Surface `rgba(14,14,15,0.88)` + `blur(12px)` per the Phase 4 tokens, opaque fallback without
     backdrop-filter.
4. **Light pool for the screen**: one cool-neutral pool in front of the screen (radius 12 m) whose colour follows the same 1×1 video
   sample at 0.25 strength, so the crowd and ground pick up screen spill without a shadowed light.
5. **Budgets / tiers**: everything new respects `device-tier.ts` (haze planes 4/3/2, pools 4/4/3, glow sprites on all tiers since they are
   one draw). `?perf=1` overlay unchanged.

Expected draws in the plaza view: cables 1, steel 1, lenses 1, glow 1, windows 1, props 1, prop shadows 1, wall decals 1, haze 1, LED
material 0 (replaces the existing panel material) → **+9 → ~104 desktop / ~76 phone**.

## Checks

Captures of the plaza (02) and screen (03) views, desktop and phone, `screenshots/phase2-r<n>/`; `?perf=1` draws and GPU time; theater
mode open/close with Esc and the M / V / H keys; no new console errors; then up to 3 Antigravity rounds to 8.5+.

## Out of scope

Entrance gate rebuild, events/accommodation/contact/mural zone work (Phase 3); UI drawers and tokens beyond the theater overlay (Phase 4).

## Antigravity plan review (Gemini 4 Hydrogen High): AGREE WITH CHANGES → agreed plan

Adopted:
- **Light pools**: fixed count **4 / 4 / 3** (high / medium / low), not derived from `localLights` (that formula left 0 on laptops and
  phones). Positions transformed to **view space** on the CPU each frame and evaluated against three's `geometryPosition` /
  `geometryNormal`, so they also light the BatchedMesh crowd with no extra varyings. Falloff clamped `max(0, 1 − d²/r²)²`; diffuse
  scaled by π (Lambert's 1/π); specular through three's `RE_Direct` (its diffuse part is discarded on lightmapped surfaces).
- **Placement per mockup 02**: sodium caged lamp on the right wing floor 3 (y ≈ 17.1), cool tubes on the right wing floor 2 (y ≈ 13.9)
  and the back facade floor 2 (y ≈ 14.5). Warm windows include **2–3 on the left wing** (6–8 total).
- **Screen colour** sampled from the video through an 8×8 canvas every 0.5 s (no GPU read-back), eased per frame.
- **Cables**: cross-courtyard anchors y **16.5–20.5 m** (clear of the truss), sag **5–7%**, **3–4 bundles** of 4–6 wires plus 4–6 gate wires,
  radius **0.016–0.026 m**, tubularSegments 16–20 for spans > 15 m; screen power feeds radius **0.030–0.045 m**.
- **Windows and lamp lenses share one MeshBasicMaterial atlas** (toneMapped, fogged; window core ≈ `#ffe0ad` at 0.55–0.70): one draw.
- **Haze** 4 / 3 / 2 planes, alpha 0.06–0.09 (0.08–0.11 on low), full elliptical edge fade, bottoms above y 7.25.
- **LED screen**: **tone-mapped (AgX)**, linear video × 0.75 with a soft shoulder, black lift 0.015, 4 cm grid from panel-local
  position (not UVs), fwidth fade `smoothstep(0.22, 0.48, …)`, fogged.
- **Truss** centred at z −45.7, 0.45 m deep, chords r 0.025, lacing r 0.016, radialSegments 4; rust via the Phase 1 surface shader
  (not the packed sheet as a plain map).
- **Wall decals**: stencils painted into the same alpha atlas as the flyers (normal blending), one material, one draw.
- **Theater mode**: the `<video>` lives in one persistent wrapper (never re-parented; Safari pauses re-parented video); 720p stays on
  the low tier; no backdrop blur on the low tier (opaque `rgba(14,14,15,0.96)`).
- Prop contact shadows skipped on the low tier. Props sit on the DJ table footprint (−9.3, 7.2, −22.8).

Expected plaza-view draws: ~102 desktop / ~73 phone.

## Status (27 Nov 2026): implemented, not yet reviewed

Built per the agreed plan: `light-pools.ts`, `dressing-textures.ts`, `courtyard-dressing.ts` (cables, truss and lamp housings, windows
and lenses, glow, props, contact shadows, wall decals, haze), the LED material in `cypher-aftermovie.ts`, theater mode in
`CypherAftermovieControls.tsx` + `journey.css`, the DJ table pruned before merging, pools on the crowd. Placement fixes after detail
captures: sodium lamp lowered onto the mural building (y 16.55), back-window quads moved in front of the double-sided glass, glow
sprites softened, BREEZE '27 under GULLY VERSE, flyers off the windows, props at 2.2× probe intensity.
Round-1 captures: `screenshots/phase2-r1/` (7 zones desktop + phone, 6 detail views). Next: Antigravity round 1, theater-mode
check (open / Esc / backdrop click), M / V / H keys.

## Review round 1 (Gemini 4 Hydrogen High)

Scores: **02 courtyard plaza 6.0**, **03 triptych screen 7.5**. No budget breaches in Phase 2 views (plaza 103 / 74, screen 91 / 65).
Theater mode and keys (`scripts/check-theater-keys.mjs`, drafted by Hydrogen, reviewed and lightly corrected): open with E, close
with Esc and with a backdrop click, V / H / M, no console errors: all PASS.

Adopted for round 2: lamps moved onto the visible right-wing balcony building (sodium y 16.9, cool tube y 13.7, both z ≈ −24.5…−25)
and the back tube clear of the screen (x −11.5, y 13.9); tube glow stretched (1.25 × 0.28, colour 0.10); haze planes kept between the
screen and the viewing spot (z −44.4 … −38.8), alpha 0.15 / 0.18 (low), noise exponent 1.15; props get the night floor and lighter
atlas colours; screen pool radius 14, intensity 0.32 + 0.35 × luma; truss steel `#6a4e3a`; LED black lift 0.004; two power drops in
each gap between the centre and side panels; gate wires wall to wall (±5.2); cross-courtyard anchors snapped to the facades by
ray-cast; two more left-wing windows (ray-cast anchored); GULLY VERSE in chalk between the two windows (z −45.8, 2.6 m wide, measured
from a capture), flyers off the glass and dimmer (0.11–0.14); decal ray-casts skip glazing; no per-frame colour allocations.

Declined:
- **"Theater mode re-parents the video"**: the film element was always detached (the LED wall has played it detached since before
  Phase 2); it joins the theater frame only while open, with play() after each move. The theater check passes; keeping it attached
  and invisible risks Chrome pausing a hidden muted video.
- **"restart(true) never returns to 720p"**: unchanged behaviour from before Phase 2 (Watch plays the full film); the low tier now
  keeps 720p.
- **GULLY VERSE at z −17.8**: that is the accommodation recess (COMING SOON); the stencil moved to the measured plain wall instead.

## Review round 2

Scores: **02 courtyard plaza 7.0**, **03 triptych screen 8.5**. Antigravity agreed with all three declined round-1 points.
Theater and keys: all PASS; no console errors; draws unchanged.

Adopted for round 3: right-wing lamps at the soffits of their floors (round 1 put both pools a floor low: sodium housing y 19.1,
pool (14.5, 18.4, −25.8), r 11.5, ×1.75; cool tube y 16.0, pool y 15.3, r 10, ×1.15) with their service wires; back tube pool y 13.6,
×0.75; gate wires ending at the alley walls (x ±3.6: those walls are in another chunk, so the plaza ray-cast cannot snap them); the two
window quads that had landed on balcony doors removed, a 1.44 m centre-bay window on the left wing floors 2 and 3, the window behind
the truss moved to the clear pane at x 12.02; speaker atlas lifted (cabinet `#3a3c40`, grille `#4a4c52`, drivers `#7a7c84`), prop
roughness 0.65; screen pool moved to (0, 11, −43.4), radius 15.5, 0.28 + 0.28 × luma (a wide wash, not a hotspot); haze alpha 0.20 /
0.22, film tint 0.48.

## Review round 3 (final round): stopped per CLAUDE.md

| View | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- |
| 02 courtyard plaza | 6.0 | 7.0 | **7.5** |
| 03 triptych screen | 7.5 | 8.5 | **9.0** |

The screen passes. The plaza stays under 8.5 after the third round, so the loop stopped and the gaps were reported. Antigravity
confirmed the LED highlights stay controlled on saturated frames; theater mode, keys, budgets (plaza 103 / 74, screen 91 / 65) and
0 errors all pass.

Remaining plaza gaps (Phase 2 work, not yet done):
- The right-wing cool tube at the floor-2 soffit (y 16.0, 0.10 m off the wall) is now hidden behind the floor-3 balcony fascia from street
  level (a round-3 regression); it needs to come forward of the fascia line. The sodium lamp sits tight to the fascia edge.
- The cypher-corner PA stack and crates still read near-black: no pool reaches them (all four are allocated) and the night floor alone
  is not enough.
- The left-wing warm windows sit in deep recesses that the forecourt camera sees at grazing angles.
- Antigravity reported the back-left window (−10.0, 14.78, −50.95) as gone in round 3: that entry is unchanged since round 1 and the
  window is visible in the round-3 plaza frame, so this one is a misread.
Phase 3 items it named: the full-wall foreground GULLY VERSE and STAY / EVENTS lighting of the mockup's framing, and the existing dark
triangular balcony fascia shapes on the right wing.
Antigravity (Hydrogen) also drafted `scripts/check-theater-keys.mjs` (reviewed and lightly corrected before use).

## Follow-ups after round 3 (user asked to fix the plaza gaps)

1. Right-wing lamps: a geometry probe showed the overhangs reach only ~0.9 m from the wall (to x 15.1–15.4); lamps are now placed at
   mount by an upward ray cast from just inside the edge (x 15.3) and hang 0.22 m under it (cool tube under the floor-2 overhang at
   z −24, sodium under the eave at z −25.6), with hangers and service wires along the overhang; pools widened (13 / 12).
2. Props: night floor plus an ambient fill (0.06) through `patchProp`; per-prop tone (vertex colour) keeps the screen-side PA stacks
   at 0.7 so the fill meant for the unlit corner does not grey them.
3. Windows: a warm spill halo (0.14) in front of each lit window (same additive draw) so the recessed windows read from the forecourt;
   one more left-wing window at z −38.5 (accepted only when the ray reaches the facade); the z −41.5 attempt landed half on plaster
   and was removed.

Follow-up checks (Hydrogen High): plaza 7.5 → **8.0** → **8.5**; screen **9.0** throughout. Both Phase 2 views now pass.

Model check (user request): `agy models` (CLI 1.5.18) lists no Gemini 4 Neon on this account, and `--model gemini-4-neon-high` is
rejected ("not recognized as a known model"), the entitlement-sync issue. The strongest available model, Gemini 4 Hydrogen XHigh, ran
the last check; through the MCP it exceeded the server's 5-minute limit, so it ran through the `agy` CLI in read-only plan mode
(`--mode plan --sandbox --print-timeout 15m`).

## Final check (Gemini 4 Hydrogen XHigh, via the agy CLI in read-only plan mode)

XHigh first pass (after the Hydrogen High follow-ups): plaza 8.0, screen 9.0. Its fixes were applied: lenses moved to the housing faces
(the sodium lens was 3.9 cm inside its box, the tube lens coplanar), sodium hung lower (0.35 m, x 15.15, ×2.6), softer window halos
(0.08, 0.2 m out), corner PA stack facing the plaza, stencils dimmed (0.2 / 0.18), wire bundle 3 raised to y 19.6, gap drops bowed,
top beam meeting the outer tower chords, glow and haze InstancedMeshes disposed, film sampled only inside the plaza, theater frame
height-capped on phones. Declined: the "gamma lift" on the additive glow (every three.js material converts colour space before
blending; the glow matches the rest of the scene).

**Final XHigh scores: 02 courtyard plaza 8.5, 03 triptych screen 9.2.** Captures `screenshots/phase2-final/`; draws plaza 103 / 74,
screen 91 / 65; theater and keys PASS; 0 console errors.

Remaining nits (not done): sideways bow for near-vertical wires (the wire sag is vertical only, so the gap drops stay straight);
sodium pool warmth on the right-wing bay; the floor-1 left window at z −24.8 grazes its pier; glow-sprite near-plane flip when the
camera is within 0.15 m of a lamp (cannot happen at walking height); first film sample waits 0.5 s.
