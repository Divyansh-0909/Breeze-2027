# Phase 1 plan: device tiers, night-gully look, shared procedural materials

Status: draft for review (Claude Opus 5.5 builder, Antigravity Gemini 4 Hydrogen reviewer), 27 Nov 2026.

## What exists today (audited)

The gully is not a procedural Three.js scene. It is six Blender (Cycles) chunks exported as GLB with **baked RGBM
lightmaps** (`baked-assets.ts`); runtime lights add **specular only** (`fidelity.ts` zeroes direct diffuse). Reflections come
from two **Cycles HDR panorama probes** via PMREM (lane, plaza). Tone mapping is already `AgXToneMapping`, exposure
`2^0.25 = 1.19`. No fog. No post-processing (no EffectComposer). **Zero shadow-casting lights** (`castShadow=false` on every mesh).
A DPR governor (`quality-governor.tsx`) steps minimum 0.65 / low 0.8 / balanced 1.0 / high min(dpr,1.5) on measured frame time.
`?perf=overlay` shows FPS / calls / tris / tier. The crowd is ~189 Rocketbox people in ~40 BatchedMesh multi-draws.

Baseline (GTX 1650, Chrome, 1440x900, `screenshots/baseline/`): 120 fps everywhere, but draw calls
**entrance 390, plaza 170, screen 148**, zone close-ups 55–73. Breakdown at the entrance: cypher-plaza chunk 178 (it is
**not batched**; only the market chunks are), market-north 77, cypher-approach 48, cypher-gate 31, crowd ~40.
About half of all chunk materials are untextured flat colours (plaza 53 of 93, market 38–42 of ~80).

Visual baseline vs references: plaza walls crush to pure black; screen video blows out to saturated magenta;
events wall is terracotta; graffiti (COMING SOON, CONTACT US, ORGANISING COMMITTEE) is neon pink/cyan; plaster
reads flat and clean; the ground is uniform matte asphalt with no puddles.

## Pinned 4-tone palette (+1 cold accent)

| Tone | Hex | Use |
| --- | --- | --- |
| Wet charcoal concrete | `#2b2e31` | walls in shade, ground, fog family |
| Rusted iron / brown | `#6e4127` | shutters, gates, pipes, stains |
| Faded chalk-white | `#d3ccbc` | lime-wash plaster highs, stencils |
| Dull sodium amber | `#c4883e` | lamps, warm spill, window glow |
| Cold accent (tubelights only) | `#dbeaee` | fluorescent tubes |

## Files (Phase 1 only)

1. **`device-tier.ts` (new)**: one detection at start: `high | medium | low` from `pointer: coarse`, width < 700,
   `hardwareConcurrency`, `deviceMemory`, and the unmasked renderer string (SwiftShader / llvmpipe / Mali-4xx / Adreno 3xx–5xx →
   low; Intel UHD/Iris → medium; discrete or Apple M → high). `?device=` override. Exposes budgets:
   `dprCap` 1.75 / 1.5 / 1.25, `shadowCasters` 2 / 1 / 1 at 1024 / 1024 / 512, `localLights` 8 / 6 / 4,
   `textureSize` 1024 / 1024 / 512, `hazePlanes` 4 / 3 / 2, `bloom` high only (not built in Phase 1).
   `enforceShadowBudget(scene)` runs after each chunk mount: sorts shadow-casting lights by distance to camera, keeps the cap,
   clamps map size (today a no-op guard: nothing casts).
2. **`quality-governor.tsx`**: the governor's top step uses `min(devicePixelRatio, dprCap)` instead of the fixed 1.5;
   low-tier devices start at `low` (0.8) instead of `balanced`. Hysteresis unchanged.
3. **`gully-diagnostics.tsx`**: `?perf=1` alias for the overlay; overlay adds device tier, lights, shadow casters and a
   per-chunk draw breakdown (`drawBreakdown`, already added for this audit).
4. **`night-look.ts` (new)**, applied once from `CypherGatePreview.tsx`:
   - `toneMappingExposure` 1.19 → **1.05** (AgX kept).
   - `FogExp2('#0b0d10', 0.016)` (0.018 on low: shorter view); `scene.background` set to the fog colour so geometry
     fades into the same void. Fog density eased to 0 while the aerial **map** is open (the map camera is 60+ m away).
     The video screen and sponsor LED keep `fog=true` (≈ 0.84 transmission at 26 m, acceptable).
   - **Night floor**: a small constant cool irradiance (linear ≈ 0.010 of `#2b2e31`-tinted) added to every lightmapped surface's
     baked irradiance in the existing lightmap shader patch, so shaded walls bottom out at deep charcoal, never `#000`.
   - **Palette grade** in the same patch (albedo only, before lighting): cap chroma (HSV S ≤ 0.42), pull magenta/pink and
     cyan hues toward rust/chalk, and desaturate terracotta plaster toward charcoal. Not applied to the video screen, sponsor
     LED, people, or the navigation board (Phase 3 replaces the board). Graffiti keeps its shapes, loses neon.
5. **`gully-materials.ts` (new): shared procedural library**, generated once per visit on a 2D canvas (1024 high/medium,
   512 low), **three RGBA CanvasTextures in total**, each packing albedo-detail (R), roughness (G), height (B), mask (A):
   - `plaster`: peeling lime-wash: multi-octave value noise, flaking patches revealing darker render, damp streaks running
     down from the top, hairline cracks (random-walk lines).
   - `ground`: wet charcoal: aggregate grain + low-frequency puddle mask; roughness 0.06–0.12 in puddles, 0.88–0.95 dry;
     puddles darken albedo ~35%.
   - `rust`: corrugation ridges + rust bloom mask for shutters, gates, pipes, galvanised/zinc.
   Materials are classified by name once (`/render|plaster|lime|mineral concrete|house shell|building|parapet|coping/` →
   plaster; `/asphalt|road|ramp|apron|slab|ground|gutter/` → ground; `/shutter|galvan|zinc|steel|iron|gate|pipe|conduit/` →
   rust). The patch samples the class texture with **world-space biplanar mapping** (walls: x/z by normal and y; ground: xz)
   so baked lightmap UVs are untouched. Albedo is multiplied by the detail, cavity-darkened by height, roughness replaced
   (ground puddles bypass the 0.75 matte floor; walls stay ≥ 0.85), and the normal is perturbed by height derivatives
   (visible in probe/lamp specular). One extra texture fetch per fragment on classified surfaces.
6. **Draw calls (budget breach: entrance 390 → target < 120 desktop, < 80 mobile)**:
   - `static-batching.ts`: batch the cypher chunks too, with an explicit **keep** predicate so interactive meshes stay separate
     (aftermovie panels, event poster slots, accommodation artwork/overlays, contact heading, LED, lamp lenses, team mural).
   - **Flat-colour collapse**: in each chunk, opaque, untextured, non-emissive materials (not road, not sign ink, not art,
     not the accommodation house plaster) are merged into **one material per (lightmap channel, surface class, metal bucket)**:
     base colour baked into a vertex colour attribute, roughness into a `breezeRough` attribute. Then batched as above.
   - Expected: plaza chunk ~178 → ~45, market-north 77 → ~45, approach 48 → ~25, gate 31 → ~12. Crowd unchanged (~40).
     If the entrance view still exceeds 120, add view-distance culling of the far plaza interior from the lane (> 45 m).

## Checks

`?perf=1` metrics for all 7 starts on desktop (1440x900) and mobile (390x844, DPR 3, touch) via
`scripts/capture-zones.mjs`; `tests/immersive` unit tests; M MAP, V SOUND, H CONTROLS still work; no new console errors.

## Out of scope (later phases)

Cables, glow sprites, lived-in windows, props, haze, screen anti-blowout shader and theater mode (Phase 2); zone rebuilds
(Phase 3); UI drawers (Phase 4).

## Antigravity review (Gemini 4 Hydrogen High, round 0): AGREE WITH CHANGES → agreed plan

Adopted:
- Exposure **1.10** (not 1.05): the screen is `toneMapped: false`, so exposure never fixed the blow-out (Phase 2 shader does).
- Fog **FogExp2 0.011** (high/medium) / **0.013** (low); fog and background **`#050709`** (0.016 would fog ~40% of the screen
  from the gate; `#0b0d10` lifted the sky against the rooflines). Fog eases to 0 on the map.
- Night floor **0.018** (× `lightMapIntensity`, cool `vec3(0.89, 0.94, 1.0)`), added inside the decoded `lightMapIrradiance`
  expression after `breezeLightScale`, so the accommodation wall patch (which rewrites `irradiance += lightMapIrradiance;`) still applies.
- Palette grade: chroma cap **S ≤ 0.65** (keeps the pinned rust 0.645 / amber 0.684), **70%** attenuation of magenta
  (H 0.80–0.96) and cyan (H 0.45–0.58) on all graded surfaces, **60%** terracotta suppression (H 0.01–0.09) on `plaster` only.
  Luma/dot-product maths, no full HSV. Nav board (panels, borders, titles) flagged `breezeNoGrade`.
- Procedural tiles: plaster **4.0 m**, ground **3.5 m**, rust **1.5 m**; dominant-axis world projection (one fetch); corrugation only on
  shutters; puddles **0.12–0.18** wet / **0.88–0.94** dry; on road (`breezeRoad`) only the puddle mask/roughness/darkening, no extra grain
  over the Cycles aggregate; bump **0.25** high/medium, **0** low (no `dFdx` on low).
- Desktop `high` loads the 1024-wide probes (`probe.file`); others keep 512.
- Texture size **1024 / 512 / 512** (high / medium / low; coarse pointer = 512); anisotropy 4 / 4 / 2.
- `medium` tier gets a 6-lamp list.
- Draw calls: add **portal culling**: plaza batches are grouped by region (left wing, right wing, centre); wings hide while the
  camera is in the lane (z > −8, derived from the 3 m doorway geometry), verified by pixel-diffing lane frames with and without it.
  Plus cypher-chunk batching with a keep-list and the flat-colour collapse (normalised attributes, linear vertex colour).
- A material-name audit across all chunks: every classified/unclassified name listed in the Phase 1 report.
- Bloom explicitly **deferred** (no EffectComposer on any tier in Phase 1); glow sprites arrive with the Phase 2 fixtures.

Disagreed / changed:
- **Nav-board panel merge**: not done. The board is replaced by the gate composition in Phase 3 (mockup 01); merging uncommitted
  WIP geometry now would be thrown away.
- **Web Worker for texture generation**: not by default. Generation runs behind the existing loading screen while GLBs download; it
  is measured, and moves to a worker only if it exceeds 150 ms on a 4× CPU-throttled run.
- **Default "architectural → plaster" fallback**: not adopted (it would texture props and furniture). The name audit drives the regexes.
- **Crowd draws**: unchanged in Phase 1 (one multi-draw per avatar material, ~40); revisit with an avatar atlas if mobile misses < 80.

## Implementation notes (where the build departed from the agreed plan)

- **Portal culling removed.** Implemented, then pixel-diffed lane frames (culled vs not, z = −7.45 and the approach spawn): the plaza
  wing facades are visible above the compound wall, so hiding them popped buildings. A correct version needs a per-object wall-plane
  occlusion test with below/above-wall batch bands; deferred to the Phase 3 entrance rebuild (Antigravity agreed in round 1).
- **Batching rules.** Every chunk is batched. The old allowlist of "plain" userData keys excluded export bookkeeping
  (`pilotOriginalObject`, `authorizedChange`, …); it is now a blocklist of the keys the runtime reads, plus the keep-list. Art-projected and
  sign materials batch too (their shading is per material and per-fragment world boxes). Nav-board restyled copies are shared per
  original material and role.
- **Crowd on low tier** uses 8 of the 15 Rocketbox avatars (≈ 19 fewer multi-draws, 7 fewer downloads).
- **Probes** are desaturated to 35% chroma and their highlights above 1.5 compressed before PMREM (wet ground mirrored the old magenta
  screen glow as lavender, then bright sky patches as white).
- **Phones stay at DPR 1 at start** (not 0.8 as first drafted): 0.8 is visibly softer than today; the governor still steps down on
  measured frame time. Antigravity agreed in round 2.
- **Bump convention kept** (declined round-2 "fix"): `breezePerturb` matches three.js `perturbNormalArb` (normalised screen
  derivatives). Diffuse light is baked, so bump only shows in specular; wall relief comes from the albedo cavity term.

## Review rounds (Phase 1 scope only)

| Zone | Round 1 | Round 2 | Round 3 |
| --- | --- | --- | --- |
| 01 entrance gate | 7.0 | 8.0 | 8.0|
| 02 courtyard plaza | 7.0 | 7.5 | 8.5|
| 03 triptych screen | 7.5 | 8.5 | 9.0|
| 04 accommodation | 7.5 | 7.5 | 8.0|
| 05 organising mural | 7.5 | 8.5 | 8.5|
| 06 events wall | 6.5 | 8.0 | 8.0|
| 07 contact desk | 7.0 | 8.0 | 8.0|

Round 1 fixes: feathered puddles, wet darkening, puddle roughness 0.20–0.30, terracotta 0.85, softer plaster flakes, damp 0.30,
night floor 0.022, low fog 0.012, NaN guard, mirrored-transform winding, accommodation patch idempotency.
Round 2 fixes: low-tier puddle field bug (B channel is 1 − puddle), isotropic macro lookup (G at 0.23), damp 0.42 with earlier onset,
tighter flakes, wider/darker puddles (0.54–0.74, 0.36), dry ground ×0.78 and road ×0.85 value, ground/road −60% chroma.

Round 3 is the last round CLAUDE.md allows; four zones stay under 8.5, so the loop stopped here.

### Open after round 3 (zones under 8.5)

| Zone | Phase 1 gap Antigravity named | Belongs to Phase 2/3 |
| --- | --- | --- |
| 01 entrance (8.0) | lane road still slightly warm; mobile puddles repeat at the 3.5 m tile; **draw calls 182 / 141** | gate rebuild, wall-plane occlusion culling, nav board replaced |
| 04 accommodation (8.0) | foreground apron classified as plaster (cracks, no puddles); faint flaking near the lamp; trim crushes black | stencil, rate board, shutter, bulb |
| 06 events (8.0) | apron classified as plaster; green shutter leaf speckled by the rust class; trim crushes black | rusted shutter, tubelight, posters, crates |
| 07 contact (8.0) | apron classified as plaster | open booth, bulb, speakers, drawer UI |

Code points from round 3, not yet fixed: `classifySurface` tests `shutter` before `excluded` (a green shutter leaf matches both);
the plaster terracotta dimming has no saturation gate (near-neutral warm plaster loses 15% value too).
Checked and not a Phase 1 bug: the jagged streak above CONTACT US on mobile is identical with merging off (`?merge=off`): it is
z-fighting in the mobile GLB soffit.

### Measured (GTX 1650, Chrome; baseline from `next start`, round 3 from `next dev`; GPU p50 from the timer query)

| Zone | Draws before | Draws desktop / mobile | GPU ms before → desktop |
| --- | --- | --- | --- |
| 01 entrance | 390 | 182 / 141 | 4.02 → 3.70 |
| 02 plaza | 170 | 95 / 67 | 3.65 → 4.13 |
| 03 screen | 148 | 83 / 59 | 3.77 → 4.29 |
| 04 accommodation | 55 | 26 / 27 | 2.50 → 2.78 |
| 05 mural | 63 | 32 / 29 | 1.93 → 2.02 |
| 06 events | 73 | 35 / 35 | 1.99 → 2.76 |
| 07 contact | 73 | 37 / 35 | 2.35 → 2.70 |

All views vsync-capped at 120 fps; 0 shadow casters; no console errors. Merging trades culling granularity for draws: the mobile
contact view draws 228k triangles merged vs 160k unmerged. "Mobile" is a 390×844 DPR-3 low-tier emulation on the same GPU, not a phone.

## Follow-up after round 3 (user asked to fix the open gaps)

- **Paving classed as plaster**: ray-casts in the accommodation, events, contact and team views hit the "mineral concrete" /
  "building base" materials with normal y = 1. The export reuses one material for a building's base walls and the walkway slab, so
  plaster materials now also take the ground sheet, and faces with world normal y > 0.7 follow the ground path (grain, puddles, wet
  roughness, −60% chroma, ×0.78 value). Walls keep plaster.
- **Mobile puddle tiling**: the large-scale puddle lookup runs on every tier for ground fragments.
- `classifySurface` tests exclusions before the shutter class; terracotta dimming needs saturation (smoothstep(0.08, 0.2, S)).
- The speckled green leaf beside the events window is its exported texture (same in the baseline).

Antigravity follow-up check (desktop + mobile, `screenshots/phase1-gaps/`): **entrance 8.5, accommodation 9.0, events 8.5, contact 9.0**.
With plaza 8.5, screen 9.0 and mural 8.5 from round 3, every zone is at 8.5 or above. GPU time unchanged (entrance 3.70 → 3.67 ms,
events 2.76 → 2.81 ms); no console errors.

Minor items noted, not fixed: vertical step risers and kerb fronts on the same concrete material stay plaster beside their wet top
faces (a light stripe on the events and contact aprons); doorway recesses and beams crush near black (baked). Entrance draw calls
182 / 141 stay deferred to Phase 3.

## Second follow-up (user asked to fix the first three open items)

- **Step and kerb fronts**: vertical plaster within ~30 cm of the walking surface (plaza 7.2 m; lane 6.0 m rising 1:20 to the
  gate, top at z = −14, measured by ray-casts) blends into damp ground concrete. This also gives building bases a damp band.
- **Streak above CONTACT US on phones: not fixable in Phase 1 without cost.** The phone and desktop builds share one lightmap; the
  desktop GLB rendered from the exact phone camera pose shows no streak, so it comes from the simplified phone GLB distorting the soffit's
  lightmap mapping. Options: re-export the phone GLB (Phase 3 contact rebuild) or send phones the desktop plaza (+25 MB per visit).
  A first attempt (dropping the decal's down-facing triangles) removed the CONTACT US flame tips and was reverted.
- **Production build** (`next build` into `.next-perf`, `next start`, GTX 1650, `screenshots/phase1-final-prod/`):

| Zone | GPU ms baseline → Phase 1 | FPS desktop | Draws desktop / phone | Phone-size FPS |
| --- | --- | --- | --- | --- |
| 01 entrance | 4.02 → 3.68 | 120 | 182 / 141 | 110 |
| 02 plaza | 3.65 → 4.24 | 120 | 95 / 67 | 119 |
| 03 screen | 3.77 → 4.66 | 120 | 83 / 59 | 120 |
| 04 accommodation | 2.50 → 2.87 | 120 | 26 / 27 | 120 |
| 05 mural | 1.93 → 2.17 | 120 | 32 / 29 | 119 |
| 06 events | 1.99 → 2.59 | 120 | 35 / 35 | 120 |
| 07 contact | 2.35 → 2.77 | 120 | 37 / 35 | 120 |

The only console error is the baseline's existing 404 (an optional people-mask file).
