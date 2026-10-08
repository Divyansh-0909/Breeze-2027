# Gullyverse — Stage 1 spatial acceptance

Stage 1 establishes one navigable quarry and preserves the original Aftermovie stage. Geometry, camera framing and stage distance are ready for user review, **not visually approved**. Stage 2 has not started. Detailed rock/material production, graffiti, finished stalls/population, Team/Contact interactions, cinematic map and boundary menu remain in their assigned later stages.

## Reference authority and availability

The supplied pack was found at `breeze-2027-visual-reference-pack/design/references`
and copied intact to the requested canonical `design/references` location.
All 39 files are available: README plus 38 images. No critical reference is missing.
Read the [reference README](../design/references/README.md); visually inspected
all entrance, tunnel, quarry, scaffold and Aftermovie references, all eight
original screenshots, all seven current screenshots, and all three stall/crowd
photographs. Reference images remain outside public runtime assets. No photographed
artwork, foreign branding or people were copied into the environment.

The original screenshots preserve stage playback, Team content and Contact fields.
The current screenshots are the before layout. The new quarry references control
scale and morphology; the scaffold reference controls foreground/distant-stage
placement. Its night exposure is superseded by warm readable daylight.

## One world and destination registry

[blockout.layout.json](../public/models/gullyverse/blockout.layout.json) is the
authoritative metre-based layout. [world.ts](../components/immersive/world.ts)
derives footprint collisions, camera orientations, movie focus and reentry.
Environment geometry, directional arrows, runtime navigation, authoring cameras
and the retained map's basic geography all read these coordinates.

+X is right, +Y is up, forward from the entrance is −Z. Normal eye height is
1.72 m; collision capsule radius is 0.38 m. Default vertical FOV is 58° with
a 52° minimum horizontal FOV for portrait framing; near/far planes are 0.1/700 m.

| Element | Geometry origin / position (x, y, z), m | Interaction / camera anchor, m |
| --- | --- | --- |
| Rocky entrance | (0, 0, 0) | Landing (0, 1.72, 24) |
| Straight tunnel | z = 0 to −42 | Exit reveal (0, 1.72, −32); walking hub (0, 1.72, −51) |
| Navigation scaffold | (5, 0, −74) | Main path passes to its left; right lane bypasses its front |
| Original Main Stage / Aftermovie | (−20, 0, −184), original scale/rotation | Viewing spawn (−18.5, 1.72, −160.5); approach (−18.5, 1.72, −156.5) |
| Team board reservation | (−35, 0, −78), faces +X | (−29, 1.72, −78); existing content /team |
| Contact booth reservation | (36, 0, −78), faces −X | (30, 1.72, −78); existing form /get-in-touch |
| Events reservation | (−58, 0, −131) | (−49, 1.72, −131) |
| Past Sponsors reservation | (58, 0, −132) | (49, 1.72, −132) |
| Accommodation reservation | (44, 0, −175) | (35, 1.72, −175); no route invented |
| Left stalls | (−46, 0, −96), (−51, 0, −118), (−49, 0, −146) | Seven-metre circulation lane |
| Right stalls | (45, 0, −96), (51, 0, −118), (48, 0, −146) | Seven-metre circulation lane |
| Physical return beside stage | Start (−18.5, 1.72, −153.5) | End (−18.5, 1.72, −149.5), turns back toward exit |

The stage and world shell remain mounted across both URL states. There is no
distant stage proxy and no second Aftermovie quarry. The stage's existing GLB,
trusses, speakers, LED screens, video/audio, barricades and fireworks are reused.
Its old 70 m black ground disc is disabled only in this shared-world adapter;
the standalone stage/recorder retains its default ground.

Team and Contact reserve 3 m interaction circles around their listed anchors,
stored in the same registry for Stage 5. No trigger/form activation is added
in Stage 1. Aftermovie's active interaction zone remains its registered bounded
viewing rectangle. The hub's rear walking limit at z = −194 reserves backstage
clearance; that area is visible in overview but is not a visitor route.

The preserved stage GLB SHA256 is
`C6FFDCAF05A7FB1F8CF47BC350FA4414615C6FBDFB38BDA83CD731FF8DAD2E5B`.

## Geometry, scale and circulation

- Irregular 24 m rock portal facade, about 13 m high, with an open arch,
  branding surface and continuous exterior rock connection into the quarry.
  No skulls, stairs or subway signage.
- Straight 42 m tunnel, approximately 9.4 m wide at floor level and 7 m high.
  Its shared profile joins the entrance and quarry opening. Ring variations
  are at most 0.16 m. The cinematic path stays near x = 0 at eye height.
  Five 5.1 × 1.6 m wall-surface reservations carry provisional artist names:
  Neha Kakkar, Chaar Diwaari, Ritviz, Khullar G and Twin Strings. These plaques
  prove placement, not final painted graffiti.
- Excavation footprint spans about 163 × 190 m, with walls 49–64 m tall
  and outward setbacks at heights 14/28/43 m. The rock rim is irregular;
  there is no roof across the chamber. Ground-level collision follows the
  same footprint used to generate the walls.
- Original 34 m stage rig faces the exit. Its origin is about 135 m from the
  walking hub and 153 m from the tunnel-exit reveal camera. From that straight-facing
  camera its center lies about 8° left; the scaffold is forward/right.
- Scaffold is 10 m wide, 11 m high, 2.8 m deep, with four footings, uprights,
  cross-members, diagonal braces and sign rails. Seven directional boards
  include straight and diagonal orientations. Arrows derive from the actual
  target anchors, compensating for board tilt.
- Main circulation path is 10 m wide; side lanes are 7 m wide. Six stalls
  reserve 7 × 4 m footprints with 3.5 m roofs and human-height counters.
  Team/Contact placeholders sit in the same daylight festival world.
- Sparse exit groups (8), stall groups (5 per stall), moderate hub circulation
  (32), and a dense stage zone. Far stage population uses inexpensive capsules;
  Aftermovie uses the original four baked human poses and density tiers.
  A 7.4 m center lane extends the original runway clearance through the crowd.
  Population models, pose baking and cache ownership otherwise remain intact.

Rock uses simple deterministic vertex-shaded blockout geometry. Props use
readable hemisphere/directional daylight and the existing stage lights.
There are no dynamic shadows, final textures, new postprocessing or photorealistic
lighting claims. The full chamber is intentionally large relative to human height.
Temporary label canvases are 512 × 96 with mipmaps. Each textured plane forms
the board's front cap; its backing has no competing front face, avoiding
distant/diagonal depth fighting.

## Cameras and visual evidence

All ten authoring cameras are in the registry; orientation is derived from
position and target. Fixed inspection cameras preserve the visitor's actual
walking pose and render the same world through the existing Canvas.

| View | Position (x, y, z), m | Target (x, y, z), m | Base vertical FOV |
| --- | --- | --- | --- |
| Landing | (0, 1.72, 24) | (0, 4, 0) | 58° |
| Tunnel near entrance | (0, 1.72, −3) | (0, 2.6, −42) | 58° |
| Tunnel midpoint | (0, 1.72, −22) | (0, 2.6, −52) | 58° |
| Tunnel exit reveal | (0, 1.72, −32) | (0, 5, −153) | 58° |
| Scaffold | (0, 1.72, −46) | (4, 6, −68) | 58° |
| Full quarry | (0, 1.72, −51) | (0, 10, −184) | 58° |
| Left stalls | (−30, 1.72, −89) | (−45, 2.2, −112) | 58° |
| Right stalls | (29, 1.72, −89) | (44, 2.2, −112) | 58° |
| Overhead | (0, 320, −104), portrait height fits complete rim | (0, 0, −104) | 65° |
| Stage back toward exit | (−18.5, 1.72, −158) | (0, 5, −42) | 58° |

At 390 × 844, normal-camera vertical FOV expands to approximately 93°
in the hub to retain the 52° horizontal field. Aftermovie retains its original
58° viewing/playback FOV. Overview height increases from 320 m
to fit the tall wall rim rather than crop the quarry. Exact rendered camera
poses, viewport and resource snapshots are in `captures.json`.

Reference photographs do not supply calibrated lens/pose metadata. These are
approximate framing comparisons, not survey alignment or quantitative image
matching. Before screenshots have different layouts/cameras; the review gallery
labels this difference explicitly. Screenshots are taken separately from the
performance journey so GPU readback cannot contaminate its steady windows.

[Open the before/reference/after review gallery](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/review.html).
It includes all ten desktop viewpoints and portrait entrance/exit/hub/overhead
comparisons. [Exact capture metadata](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/captures.json)
records the rendered poses rather than only the nominal camera configuration.

| View | Desktop capture | Portrait capture |
| --- | --- | --- |
| Landing | [Entrance](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-landing.png) | [Entrance](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/mobile-aspect-landing.png) |
| Tunnel near | [Near entrance](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-tunnel-near.png) | — |
| Tunnel midpoint | [Midpoint](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-tunnel-mid.png) | — |
| Tunnel exit reveal | [Exit](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-exit.png) | [Exit](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/mobile-aspect-exit.png) |
| Navigation scaffold | [Scaffold](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-scaffold.png) | — |
| Full quarry toward stage | [Quarry](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-quarry.png) | [Quarry](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/mobile-aspect-quarry.png) |
| Left stall anchor | [Left stalls](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-left-stalls.png) | — |
| Right stall anchor | [Right stalls](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-right-stalls.png) | — |
| Complete overhead | [Overhead](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-overview.png) | [Overhead](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/mobile-aspect-overview.png) |
| Stage toward quarry/exit | [Return view](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-stage-return.png) | — |

The fixed exit-reveal camera is ten metres inside the mouth, to include the
arched tunnel foreground as in reference 04. Scaffold and full-quarry cameras
sit outside the mouth. Overhead annotations are authoring-only geometry above
the actual destination anchors, not a separate map.

The blockout establishes tall excavation faces, an open sky, a distant original
stage to the left and a supported scaffold to the right. The supplied before
view used low-poly rock masses, a rectangular passage, a central stage proxy
and isolated Aftermovie surround; those major relationships are corrected.

Discrepancies requiring later production/review:

- Quarry faces remain broad regular facets; references show fractured vertical
  rock, deeper recesses, pronounced ledges, rubble and vegetated rims. Stage 2
  must add those forms without shrinking the chamber or blocking circulation.
- Daylight is warmer/readable but has much less contrast, overhead sun/shadow
  detail and exposure variation than the quarry reference. Static vertex shading
  is a blockout substitute; final materials/lighting are not approved.
- The entrance facade is more symmetric and its rock connection simpler than
  the organic portal references. Branding/artist plaques reserve surface area;
  they are not final spray-painted murals.
- The proposed 9.5 m tunnel is wider than the narrow graffiti-corridor photos.
  Confirm its 7 m height/42 m length and broad festival passage before Stage 3.
- The scaffold is offset right to keep the original stage visible on the left.
  Its boards are provisional type, with no final wear, hanging lamps, plants
  or detailed branding. Portrait framing uses a wider lens, so distant text is
  small; final direction graphics/readability belong to Stage 4.
- Stall counters/roofs and people are scale proxies. Strings of lights,
  tent forms, detailed vendors and population variety remain pending.
- Team/Contact geometry is physically connected; their live content still uses
  the preserved standalone routes until Stage 5 implements in-world activation.
- Confirm the proposed 135 m hub-to-stage distance and 49–64 m wall scale before
  detailed asset production. Photographs do not establish exact real dimensions.
- The unchanged 7.2-second welcome crosses about 75 m; it is a guided glide,
  faster than the local 4.2 m/s movement. Any timing revision needs a later
  choreography decision after geometry approval.

## Walking, navigation and preservation verification

Physical stage approach uses normal walking for the full quarry distance.
At commitment, guided departure ends at exactly the next approach pose, so the
covered handoff does not relocate the camera across the world. Physical return
rejoins the quarry beside the stage. Explicit map/URL destination selections
retain their existing covered transfers. Introduction remains 7.2 seconds.

The walkable region includes the quarry, carved tunnel and front landing.
Visitors can walk back through the same tunnel after returning from the stage.
Portal shoulders block entry outside the arch; the 7.2 m center passage leaves
clearance around the artist-surface reservations.

Capsule collision slides inside the excavation polygon and blocks stall/booth/
board footprints, scaffold footings, reserved sign posts and the stage enclosure.
Aftermovie keeps its existing bounded viewing area. Tests check both stall lanes,
Team/Contact access, every solid footprint/wall face, continuous commitment,
stage focus, history/readiness ownership, motion preferences and context recovery.

**Stage 7 issue retained:** the old narrow rear strip automatically commits a
return trip. Side/front limits clamp movement; they do not yet show a text-only
destination menu at every outer boundary. The new ANY-boundary menu with
Esc/Stay/destination choice is deliberately deferred to Stage 7.

Production browser checks cover physical approach/return, direct URLs,
map/history/back/forward, one persistent Canvas, media range/playback/Escape,
resize, touch movement/look, motion preferences and the native-video fallback.
The edge suite tests delayed/failed character assets, URL supersession, ten
round trips, actual WebGL context loss during boot, hub use and stage playback,
restored pose/Canvas identity, and playback after recovery. Deliberate failure
offers the existing 2D fallback.

Twenty-one runtime tests and thirteen payment tests pass. The payment browser
preview passes customer detail entry, QR/status flow, admin statement mapping/
validation/import, mobile overflow and desktop resizing with zero API mutations.
The protected/database-backed payment integration suite was not run; no payment
implementation or database schema was changed.

The production Next build, TypeScript/lint checks and Prisma generation pass.
Only pre-existing warnings remain in legacy components and Browserslist data.
One earlier rebuild hit a Windows Prisma DLL lock while a server was still
running; stopping the server and rebuilding resolved it.

The [live walking/content probe](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/walking-content.json)
passes reverse travel to the tunnel midpoint, side-wall contact, front landing,
quarry reentry and persistent Canvas identity using public keyboard controls.
It also verifies playback's unmute flag and that browser Back stops media,
then checks Team, Contact, the existing Sponsors/Merch redirects and admin login.
All seven checks pass, with no page errors or API mutations. Contact retains
three inputs and one textarea. Physical speaker output was not measured.
The same probe passes on the normal production build with authoring inspection
disabled (`inspection: false` in the recorded result).

Final unit output is in [unit-tests.log](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/unit-tests.log);
production compiler output is in [build.log](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/build.log).
The final build with inspection disabled also passes:
[normal-production-build.log](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/normal-production-build.log).

## Intel UHD 620 performance comparison

Measured with production Next, Chrome 155.0.8059.40 on an Intel Core i5-8265U,
ANGLE Intel UHD Graphics 620 / D3D11, Windows 10.0.26300. The NVIDIA MX130 is
not the measured renderer. Desktop is 1366 × 768 at device DPR 1. Mobile
emulation is 390 × 844, DPR 2, touch enabled and 4× CPU throttling on the same
Intel GPU; it is not physical mobile acceptance.

Before values are retained from
[environment-preparation/results.json](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/environment-preparation/results.json).
After values come from the final 512 × 96-label production run:
[Stage 1 results](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/results.json),
[desktop diagnostics](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/desktop-diagnostics.json)
and [mobile-emulated diagnostics](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/mobile-emulated-diagnostics.json).

These are 5.6-second moving windows. FPS is the reciprocal of mean rendered
frame interval; p95/max include actual sampled frame delays.

| Profile / location | FPS before → after | p95 ms before → after | Max ms before → after | After frames >34 ms |
| --- | --- | --- | --- | --- |
| Desktop hub | 59.64 → 56.91 | 17.0 → 17.8 | 24.2 → 18.7 | 0 |
| Desktop Aftermovie | 59.64 → 56.91 | 16.9 → 17.8 | 22.7 → 18.3 | 0 |
| Emulated mobile hub | 59.64 → 56.87 | 17.6 → 20.3 | 19.5 → 39.3 | 1 |
| Emulated mobile Aftermovie | 59.64 → 56.34 | 17.5 → 18.2 | 18.2 → 41.2 | 3 |

| Profile / location | Draw calls before → after | Triangles before → after | Textures before → after | Geometries before → after | DPR / tier before → after |
| --- | --- | --- | --- | --- | --- |
| Desktop hub | 60 → 140 | 11,348 → 65,704 | 8 → 27 | 82 → 158 | 1 / 0 → 1 / 0 |
| Desktop Aftermovie | 122 → 110 | 981,110 → 992,234 | 7 → 27 | 124 → 162 | .75 / 2 → .75 / 2 |
| Emulated mobile hub | 26 → 131 | 10,618 → 57,820 | 8 → 27 | 60 → 158 | 1 / 1 → .75 / 2 |
| Emulated mobile Aftermovie | 77 → 73 | 977,378 → 988,790 | 7 → 27 | 98 → 162 | .75 / 2 → .6 / 3 |

The hub now renders the real stage/rig instead of three proxy boxes and retains
the world sign surfaces. That increases hub draw/geometry/resource cost.
Merged wall geometry and instanced supports/stalls/population keep the new
blockout inexpensive relative to detailed individual props. The extended
center crowd lane slightly changes the existing pose distribution/triangle
mix while retaining models, four poses and density tiers.

**Performance is below the baseline:** mean FPS is about 4.6–5.5% lower;
emulated mobile uses lower DPR and has longer tails. No browser/navigation
failure was introduced in the measured journey, but those performance
regressions remain open for production optimization. The steady ~57 FPS
cadence was measured; its full cause was not isolated. Strict sustained
16.67 ms/60 FPS is not certified, and neither is a physical phone.

| Timing, ms | Desktop before → after | Emulated mobile before → after |
| --- | --- | --- |
| Cold landing ready | 1,622 → 2,128 | 2,753 → 4,088 |
| Welcome / entrance | 7,514 → 7,474 | 7,870 → 7,948 |
| Physical walking to commitment | 3,435 → 25,224 | 3,478 → 25,195 |
| Cold committed stage trip | 4,381 → 3,368 | 4,002 → 3,062 |
| Warm map travel | 1,497 → 1,482 | 1,798 → 1,743 |
| Direct Aftermovie ready | 1,986 → 2,494 | 3,508 → 4,560 |

The longer physical approach is the larger world being traversed on foot,
not a loading stall. The stage is loaded before landing now, while detailed
human poses still prepare behind the stage transition.

Cold hub texture initialization / shader preparation / warm render window
were **161 / 405 / 299 ms desktop** and **267 / 233 / 483 ms emulated mobile**.
First stage preparation was **1 / 89 / 861 ms desktop** and
**7 / 36 / 249 ms emulated mobile**. The warm window includes density/DPR
settling; it is not just compilation. Individual human pose bakes were
5.8–20.1 ms desktop and 38–67.3 ms under CPU throttling.
Critical shaders finished before the destination's first real draw in both profiles.

Stage reveal p95/max were 18.2/26.0 ms desktop and 20.7/44.4 ms emulated mobile
(two emulated reveal frames exceeded 34 ms). Main-journey long-task maxima
were 196/472 ms; early preparation stayed under the curtain.
Aggregate phase data includes screenshot readback and the deliberate lifecycle
probe's ~0.8-second gap; these are retained in diagnostics rather than removed
from the raw record. They are separate from the moving-window table above.
GPU timing was available, with 334/336 asynchronous samples and no discarded
disjoint samples in the main journeys.

[Ten-trip residency evidence](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1/residency.json)
shows 27 textures and 149 registered geometries at both first/last repeated
stage visits. First-use/preparation counts differ from stable repeated visits.
Active deduplicated geometry backing is 1,774,930 bytes (~1.69 MiB), compared
with 1,727,328 bytes before. Estimated mapped texture source storage is
**22.22 MiB**, compared with **17.97 MiB** before. These are source-buffer/
RGBA8-plus-mipmap estimates, not driver allocations or measured VRAM.
Post-GC heap after clearing recorded diagnostic samples rose by ~0.66 MiB
over ten trips (before ~0.90 MiB). Longer-term heap behavior remains unverified.

Actual hidden-tab/freeze events were not observed in this headless environment;
synthetic blur/freeze/resume held-input checks passed. Context loss during an
in-flight `compileAsync` and the full 45-second no-restore timeout remain
unverified, as in the original acceptance report. The delayed-bootstrap,
live-hub and playing-stage loss/restoration cases passed.

## Reproduce locally

Authoring inspection is enabled in development, or in a deliberate local
production preview built with `NEXT_PUBLIC_GULLYVERSE_INSPECTION=1`.
It also requires `?diagnostics`; a normal production build leaves it disabled.
There is no authoring camera button in the normal visitor flow.

```powershell
npm.cmd run test:immersive
npm.cmd run test:payments
$env:NEXT_PUBLIC_GULLYVERSE_INSPECTION='1'
npm.cmd run build
# Start in a separate terminal, and stop it before another Prisma-generating build:
npm.cmd run start -- --port 3000
```

Against that local preview:

```powershell
$env:GULLYVERSE_ARTIFACT_DIR='.gullyverse-artifacts/stage-1'
$env:GULLYVERSE_MODE='production-stage-1-final'
node scripts/perf-gullyverse.mjs
node scripts/capture-gullyverse-stage-1.mjs
node scripts/check-gullyverse-stage-1.mjs
npm.cmd run test:payments:browser
```

Run visual captures/probes separately from performance measurement.
For an interactive development overhead view, open
`http://localhost:3000/?diagnostics&inspect=overview`; other registered camera IDs
can replace `overview`. Resume view restores the saved walking pose.
For a normal production build, remove `NEXT_PUBLIC_GULLYVERSE_INSPECTION` before
`npm.cmd run build`.

## Blender and asset readiness

No Blender executable was found on PATH, in Program Files/Program Files (x86),
or the inspected local Programs folders. No editable `.blend` source exists
in this repository. No heavyweight tools or stock assets were installed.

The existing GLTFLoader wrapper clones cached scenes, retains loader-owned
geometry/materials (`dispose=null`), and shares texture/cache ownership. New
blockout geometries and sign textures dispose their owned resources; the original
human pose cache survives trips while instance buffers are disposed. Original
asset exports were not regenerated.

[The authoring contract](gullyverse-environment-pipeline.md) documents official
Blender setup, metre scale/Y-up export, named anchors and shared-world collections.
[validate_toolchain.py](../scripts/blender/validate_toolchain.py) is a safe,
not-yet-executed smoke script: it writes a one-metre cube `.blend`, GLB and version
manifest only to an empty `blender-smoke` directory. Installation, export/load
validation and editable source creation remain unverified until Blender is available.

## Exact Stage 2 work, after spatial approval

1. Lock reviewed footprint, rim heights, tunnel mouth, scaffold clearance,
   stage origin/distance, and desktop/portrait cameras before detailed assets.
2. Establish the approved Blender executable/version/checksum; execute the
   scratch source → GLB → browser smoke test and record a working toolchain.
3. Build an editable metre-based quarry master from reference 03, using the
   approved footprint and stage anchor. Sculpt excavation faces, uneven rim,
   ledges and floor transitions while keeping the tunnel opening/circulation clear.
4. Produce quarry rock UVs, natural roughness/strata, baked occlusion and
   warm overhead daylight with darker edges. Preserve the original stage.
5. Export the single quarry shell with collision/anchor metadata and suitable
   measured mesh/texture budgets; check GLB normals, scale and material support.
6. Replace only quarry blockout meshes, recapture the same registered viewpoints,
   repeat navigation/context/residency tests and compare UHD 620 performance.

Stage 3 owns finished portal/tunnel artist graffiti; Stage 4 owns scaffold
graphics/stalls/population; Stage 5 owns physical Team/Contact content; Stage 6
owns cinematic ascent/map UI; Stage 7 owns boundary menu/coherence; Stage 8
owns final performance and physical device acceptance. No work on those stages
has been automatically started.
