# Realism rescue (interrupt between Phase 3 rounds 2 and 3)

Status: research done, plan under review (Claude Opus 5.5 builder, Antigravity reviewer), 27 Nov 2026. Branch
`work-in-progress-2027` (worktree `Breeze-2027-wip`). Phase 3 is paused after its round 2 fixes (`PHASE3-ZONES-PLAN.md`).

User request: the Phase 2 / 3 captures read too flat, over-lit and procedural next to `references/` and the three.js night pieces by
@teddyaisi ("Last Train · 01:17 AM") and @javpixel_art ("The Abduction"). Rescue lighting contrast and material realism before
Phase 3 resumes, inside the budgets: shadow-casting lights 2 desktop / 1 phone, draw calls < 120 / < 80.

## 1. What the creators shared (Firecrawl, X provider; posts and the authors' replies, 27 Nov)

- **@teddyaisi, "Last Train · 01:17 AM"** (2126184852148138338): 45 s J-horror MiniDV short, "pure code with three.js (no Blender,
  no UE5)", 2K 60 fps. In replies: zero external models (all geometry is code); **raymarched volumetric fog**, **internal
  supersampling** and **SMAA**, rendered offline frame by frame into FFmpeg (≈ 44 min on an M5 Mac for 2,700 frames: an offline
  render, not a real-time budget); "almost all custom post-processing shaders": **subtle colour bleed, vertical light streaks like an
  old CCD camcorder, low-light grain, tiny tape glitches"; **laggy auto-exposure driven on the renderer's exposure curve** when moving
  into the dark; handheld sway with telephoto damping. Process: 23 rounds; each round 9 timestamps captured, **blind visual critiques
  by two models**, feedback turned into the next prompt.
  The second post (2126185557814645186) could not be fetched (X / provider errors on three tries).
- **@javpixel_art, "The Abduction"** (2125403467942654008): fully 3D three.js piece. In replies: **WebGPU** ("WebGPU and a lot of
  iterations"); the scene is built with "a lot of elements to highlight reflections, lighting and textures" (wet, reflective
  receivers); method: screenshot the scene, have an image model paint an enhanced version, then work toward that target. His
  account's recent post list could not be fetched (provider error).

What this means for us (real-time, phones included, baked Blender lightmaps): the look comes from (a) few strong, local light
sources over very dark surroundings, (b) wet / reflective receivers that show the lights twice, (c) a camera-like finishing pass
(grain, slight bleed, exposure that adapts), and (d) air you can see light in. Their raymarched fog and supersampling were offline;
we take the cheap equivalents.

## 2. Reference skills read (MengTo/Skills; read as text from GitHub, not installed)

`npx skills add` was not run: it executes third-party code and installs instructions into the agent's own configuration. The two
skills were read instead:
- **light-a-threejs-workspace**: build surfaces at real scale (sills and openings with thickness, rounded silhouette edges that catch
  light); a key, a broad fill and a practical; linear lighting, tone-map once at output; change exposure, emissive and key/fill ratio
  together; shafts through visible air by marching only in front of the depth buffer, with step-size-independent accumulation and
  jittered samples; verify at 2× for shimmer.
- **optimize-threejs-games**: measure a repeatable view first (device, viewport, quality, pose, draws, triangles, textures); find the
  limiting side (CPU vs GPU) before cutting; low-risk fixes first; degrade decorative effects before readability; re-measure the same
  view after every change.

## 3. Where our flatness comes from (code facts)

- There is no `AmbientLight` / `HemisphereLight` in the gully runtime. Diffuse light is the Blender bake: RGBM lightmaps decoded ×
  `lightMapIntensity` (π), plus a night floor `vec3(0.89, 0.94, 1.0) * 0.022` (night-look.ts), AgX at exposure 1.10. The HDR probes
  give reflections only (`specularOnlyEnvironment`), at `scene.environmentIntensity = probe.intensity`.
- So the "ambient wash" is the bake's own fill (sky + bounce) and its compressed range, not a light we can turn down. The levers are
  the lightmap decode (a contrast curve / fill reduction), the night floor, exposure, probe intensity, and local runtime light.
- Runtime lights on lightmapped surfaces add specular only (fidelity.ts zeroes their direct diffuse to avoid double counting); our
  shader light pools (light-pools.ts) add diffuse. Shadow casters today: 0.

## 4. Agreed plan (Gemini 4 Hydrogen XHigh; Neon is not available on this account) and what was built (rescue round 1)

Reviewer verdict on the five requested fixes: (1) ambient wash: ADAPT (no runtime ambient exists; crush the bake, cone-shaped
shader pools instead of shadowed spots; 0 shadow casters kept because shadow passes re-render the scene and break the draw budget);
(2) AO: ADAPT, shader-only; (3) crisp PBR, 0.06 / 0.94 roughness, max anisotropy: DO (+ a manifest-gated 1K loader); (4) posters,
events sliver, accommodation stencil / rate board / spill: DO; (5) bevels: ADAPT (our own fixtures only; baked GLB topology stays),
halos / haze: DO.

Built in round 1 (all 0 extra draws, 0 shadow casters):
- **Bake contrast** (`baked-assets.ts`): lightmap fill crushed, `lm *= 0.32 + 0.78 * smoothstep(0.01, 0.28, luma)` (the reviewer's
  0.14 / 0.36 version blacked out the plaza in a calibration capture), walls above 10.5 m fade to 50% by 17.5 m; night floor
  0.022 → 0.0045 (`night-look.ts`).
- **Cone pools** (`light-pools.ts`): pools take an optional cone (world axis, angle, penumbra 0.65), smoothstep on the cone cosine;
  the entrance streetlamp, events tube and sliver, accommodation tube and bulb are cones.
- **Surfaces** (`gully-materials.ts`, `device-tier.ts`): wet puddles roughness 0.055–0.11 (0.10–0.14 on phones) against dry
  0.88–0.94; wall-to-floor contact occlusion over the bottom 0.45 m (0.28 at the seam); anisotropy 16 / 8 / 4; bump 0.42 / 0.38 /
  0.16 (phones had none).
- **Posters** (`event-wall-art.ts`, `zone-dressing.ts`, `public/posters/`): no more drawn silhouettes. Events posters and the
  gate / plaza flyers are photo battle posters: the event's own image, otherwise one of 12 Unsplash placeholder photos
  (`public/posters/CREDITS.md`), cover-fitted, photocopy curve, title band, date strip, then weathered and torn.
- **Events**: amber sliver at 2.5× (#ff9d3b) with a low cone grazing the floor (r 2.4, ×1.35); tube cone r 6.5 ×0.95 with a
  1.55 × 0.42 halo; EVENTS heading chalk #e4dccb.
- **Accommodation**: tube cone pool r 3.4 ×0.85 with halo; open: tungsten #ffb45c cone pouring out of the hatch (r 3.8 ×2.1);
  two-tone STAY (chalk) // ACCOMMODATION (rust #8c522c); rate board on a chamfered steel plate with 8 rivets, brighter chalk.
- **Halos**: dual-lobe glow sprites (core + 22% wide lobe).
- Not yet: the camera finishing pass (half-float target, halation, grain, vignette, auto-exposure; +1–2 draws), haze cones per
  fixture, the 1K WebP PBR loader, analytic normal slopes. Kept for round 2 if the scores call for them.

## 5. Rescue round 1 review (Hydrogen XHigh) and the fixes

Scores before → after (lighting contrast / material realism): entrance 5.5→7.5 / 6.0→7.0; events 5.5→6.5 / 5.5→7.0; accommodation
6.0→7.5 / 6.0→7.5; plaza 7.0→**5.5** / 7.5→8.0 (regression: buildings lost in the dark).
Fixed for round 2: crush floor 0.32→0.48, upper fade 0.5→0.72, night floor 0.0045→0.011; crowd ambient floor 0.012π; the lane's
streetlamp and screen-spill pools were active in the plaza (z > −24) and took the screen spill's slot: now z > −15; the events tube
and accommodation tube cones pointed away from their walls (now (−0.25, −0.97, 0) and 0.1·f − y); halo rim (wide lobe without a
fade) and sprite offset 0.15 → 0.02; posters on aged newsprint bands, brighter photocopy; galvanised grey steel (#7a7d80) with
patchy rust (mask 0.55–0.84, metalness ≥ 0.35 on bare metal); deeper plaster peel (0.84→0.62); booth backs are steel plates (not
speaker tolex); entrance: misaligned outline and the flyers over GULLY VERSE removed, right-wall flyers 0.48; a plaza flyer that
clipped the accommodation corner removed; flyer tape remnants cleared.
Added: the **camera finishing pass** (`components/immersive/finishing.ts`, +1 draw): the scene renders linear into a half-float
target (MSAA 4 on desktop, none on phones), then one full-screen triangle: halation (8 / 4 taps on two rings, highlights > 1.0 bleed
warm), 1.5 px edge chroma, AgX once, shadow grain ±1.8%, vignette 14%. Shaders are compiled for the target at the readiness gate
(no first-frame stall). Preview A/B: `?finish=off`. Not done: auto-exposure (a luminance read-back per frame; left out on cost).

## 6. Research: @garrettkjohnson (Firecrawl / X provider, 27 Nov)

Garrett Johnson (three.js contributor; formerly NASA JPL, Woven by Toyota). Recent posts: **three-gpu-pathtracer** is retiring
its WebGL path tracer (v0.0.28 stays) for a WebGPU one; emissive meshes become real lights (light tree sampling) in the next
release; he shares renders made with it (offline, not real time). Retweets: Marco Fugaro's **three-advanced-techniques**
(https://three-advanced-techniques.com): production TSL / WebGPU nodes: XeGTAO ambient occlusion at reduced resolution with
temporal accumulation, an 8-pass Bloom (Unreal look), screen-space reflections by Newton's method on the depth buffer, TAA
upscaling, sliced PMREM regeneration, SH irradiance probe columns, CPU ray-traced precomputed AO / radiosity against a BVH,
a GPU tier detector; Karim Beyrouti's rainforest (path tracer, WebGPU).
His GitHub (https://github.com/gkjohnson): three-mesh-bvh (fast ray casts and spatial queries), three-gpu-pathtracer,
three-bvh-csg, threejs-sandbox (effects experiments), three-edge-projection, js-framerate-optimizer, webgl-gpu-power-estimation,
batched-material-properties-demo (BatchedMesh with per-instance material properties in one draw).

What applies to us (WebGL2, baked Blender lightmaps, phones):
- **Use now**: the finishing-pass approach (bloom/halation look at low pass counts); our shader-side contact AO stands in for
  XeGTAO (which needs a depth/normal G-buffer and WebGPU TSL); three-mesh-bvh would speed up the dressing's ray-cast placement
  (dozens of casts at load) if load time matters.
- **Use offline**: three-gpu-pathtracer or the precomputed AO / radiosity idea could bake per-vertex AO for the runtime-added props
  and fixtures (which have no bake), rendered once and shipped; the Blender bake already covers the static gully.
- **Later, with a WebGPU move**: XeGTAO, SSR on the wet floor (puddles would mirror the lamps and screen properly instead of only
  the probe), TAAU (render below native resolution on phones). All three are TSL nodes and need `WebGPURenderer`; that migration is
  a project of its own.
- batched-material-properties-demo: per-instance material properties in one BatchedMesh draw: a route to merge the crowd's
  per-avatar material draws (41 in the plaza) later.

## 7. Rescue round 2 review and measured calibration

Round 2 scores (lighting / material): entrance 8.0 / 7.5; events 7.0–7.5 / 7.5–8.0; accommodation 7.5 / 8.0; plaza 8.0 / 8.0.
Fixed for round 3: both warm slivers were hidden behind the shutters' bottom bars (moved clear); trim box widened under the events
tube; finishing pass: halation threshold 1.0 → 0.72 (lenses, windows and the LED now bloom) on three staggered rings (no star
flares), grain frozen under reduced motion, phones get 2× MSAA in the target, the canvas no longer allocates its own MSAA behind it,
the pass compiles with the scene, the compile binding is in try/finally; diagnostics sample both renders of a frame or neither;
open hatch: register 0.25, header 0.52, chalk face sits on the plate; GULLY VERSE dark rust ink; damp runs 0.42 → 0.58, wetter
lane, phone puddle roughness 0.18 (no glitter), a rotated second lookup breaks the 4 m plaster repeat, apron 0.78 → 0.60;
right-wing sodium moved into the plaza view (z −29); crowd ambient 0.018; accommodation approach 0.6 m further back.

**Measured calibration** (method from a shared "AAA look" workflow: pick matched sample areas in reference frames and in the
render, measure lightness / chroma / hue, least-squares fit the parameters, render, measure, repeat). `scripts/measure-look.py`
with `scripts/look-samples.json` (22 matched areas over the four views: lit and shadowed walls, floors, doorways, sky; rectangles
checked by drawing them on both images; mean colour taken in linear light, compared in OKLab).
- A single global grade could not close the gap (fit RMSE 0.170 → 0.141 only, with a degenerate contrast of 0.19): the error was
  local and of opposite sign by zone. Per-zone luminance gains measured against the mockups: lane ×0.21, events ×0.37,
  accommodation ×0.82, plaza ×4.2.
- Applied as zone multipliers on the baked light (`zone-light.json`, read by the lightmap decode in `baked-assets.ts`), moved
  halfway per iteration. Where the gain would not move (lane, events) the light came from our own pools, so the entrance
  streetlamp 2.8 → 1.3 and the events tube 0.95 → 0.5 (measurement-led).
- Iterations: RMSE 0.170 (rescue r2) → 0.155 (i1) → 0.154 (i2) → **0.142 (i3)** → 0.146 (i4, plaza clamped at 4.0: overshoot).
  Kept the values that produced i3: lane 0.25, events 0.415, accommodation 0.827, plaza 3.197. The rest of the gap is composition
  (lit graffiti, different framings), not light level.

## 8. Result after round 3 (final review round; Hydrogen XHigh)

| View | Lighting contrast: before → r1 → r2 → r3 | Material realism: before → r1 → r2 → r3 |
| --- | --- | --- |
| Entrance gate | 5.5 → 7.5 → 8.0 → **8.0** | 6.0 → 7.0 → 7.5 → **7.5** |
| Events wall (0 / 4 events) | 5.5 → 6.5 → 7.0–7.5 → **7.0** | 5.5 → 7.0 → 7.5–8.0 → **7.5** |
| Accommodation (closed / open) | 6.0 → 7.5 → 7.5 → **7.5** | 6.0 → 7.5 → 8.0 → **8.0** |
| Courtyard plaza | 7.0 → 5.5 → 8.0 → **8.5** | 7.5 → 8.0 → 8.0 → **8.0** |

Perf (GTX 1650, Chrome, `?perf=1`): draws desktop / phone: entrance 127 / 102, plaza 103 / 74, accommodation 38 / 35, events 35–36 / 34
(+1 each for the finishing pass); shadow casters 0; GPU p50 3.4–3.8 ms (entrance, events, accommodation), ~5 ms plaza; 115–120 fps.
Measured error against the mockups (OKLab, 22 areas): 0.170 → 0.146.

Stopped after round 3 as the review loop requires; still under 8.5 (reviewer's top gaps):
- **Zone-gain seams** (my calibration): the zone multipliers switch with hard box edges, so steps of 3.9–7.7× show above the
  events / accommodation fascias and on floors at the box edges, and the plaza (×3.2) seen through the gate is brighter than the
  lane walls (×0.25). Fix: blend the boxes over ~1.5 m and cap the step between neighbours; include the accommodation wall patch.
- **Unlit decals**: stencils, chalk boards, rate board, flyers are `MeshBasicMaterial` (fixed brightness): they ignore the pools,
  so "STAY //" washes out under the tube and nothing on them catches the lamps. Fix: lit decal material (pools + runtime lights).
- **Events**: tube 0.5 and gain 0.415 flattened the wall; the 0-event sliver is a pinpoint at floor level; 4 events have no spill.
- **Accommodation open**: bulb outside the grille lights the wall, not the interior.
- **Entrance**: flat untextured nav board panels; entrance draw calls (127 / 102) over 120 / 80 (plaza batches are merged before
  lane culling, so 41 / 34 plaza draws remain from the lane).
- **Phones**: foreground asphalt glitter / grain speckle.
- Fixed after the review: the diagnostics GPU-timer queue could stop draining once full (now drained every frame).

## 9. Follow-up after "fix the gaps" (user request; reviewed by Antigravity through the MCP, Hydrogen High)

Fixed: soft log-space zone blending (no seams; the accommodation patch uses the same curve via `breezeLit`), decals lit by the
lamp pools (`patchUnlit`), full-width sliver in every closed state, events tube 0.75, hatch bulb inside the grille, phone bump 0.08
and grain 0.022, the GPU-timer queue drains every frame. Measured error vs mockups 0.153 (the brighter tube trades a little match
for contrast).

| View | Lighting r3 → follow-up | Material r3 → follow-up |
| --- | --- | --- |
| Entrance gate | 8.0 → 8.0 | 7.5 → 7.5 |
| Events wall | 7.0 → **7.5** | 7.5 → 7.5 |
| Accommodation | 7.5 → **8.0** | 8.0 → 8.0 |
| Courtyard plaza | 8.5 → 8.5 | 8.0 → 8.0 |

Still under 8.5 (reviewer): the shutter sliver still reads as a centre spark (the gap under the shutter is too thin to show a
lit interior); plaster still reads smooth (no peeling-paint relief); flat nav board panels; phone asphalt speckle; a streak through
"ACCOMMODATION" in the closed state; entrance draws 127 / 102. These are material and geometry detail (a texture or modelling
pass), not more light tuning.
Note: the agy CLI started refusing file reads in headless plan mode ("read_file" auto-denied) on this run; the MCP worked.

## 10. Detail pass: navigation board, events, accommodation (user request after walking the scene)

- **Navigation board** (`sign-wear.ts`, applied in `fidelity.ts` to the board's paint and lettering materials): weathered painted metal
  in world space: fine chips to grey metal, thin rust runs, light grime, patchy sun-fade, shinier bare metal; lettering worn. A
  first, stronger version read as camouflage and was toned down.
- **Events**: the shutter stops 12 cm short of the floor, with the lit interior just behind it (the window frame stands 0.16 m proud,
  so the first placement hid behind its sill); stronger peeling plaster everywhere (more peel, darker render beneath, a shadow
  line under each lifted edge, deeper height step); weathered crates (faded, scuffed, dirt from the bottom).
- **Accommodation**: hand-chalked rate board (handwriting face, tilted rows, chalk eroded on its own layer, a rubbed-out smudge);
  shelf with ledgers and pinned notices inside the open hatch; no chalk drips across the rust ACCOMMODATION line (they were the
  "streak").
- Perf: draw calls unchanged; GPU p50 desktop 3.6–4.0 ms (plaza 6.4 ms: the second plaster lookup over large walls), phone 1.6–2.5 ms.
  Measured error vs mockups 0.144.
- Review (Antigravity MCP, Hydrogen High): entrance 8.0 / **8.0** (board itself ~8.5); events 0 events 7.5 / 7.5, 4 events
  **8.0 / 8.0**; accommodation closed **8.0** / 7.5, open **8.0 / 8.0**; plaza 8.5 / 8.0. Remaining: GULLY VERSE reads as a faint stencil
  (mockup: bold outlined graffiti); plaster peel still flat up close; puddles / conduits / piping on the accommodation wall; plaza
  asphalt stipple; phone textures soft (512 on the low tier).
