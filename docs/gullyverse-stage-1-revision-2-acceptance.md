# Gullyverse — Stage 1 Revision 2 acceptance

Revision 2 corrects the rejected Stage 1 composition and navigation. It remains
a procedural environment blockout awaiting human visual review. Stage 2 has
not started, no new Blender production assets are claimed, and no changes have
been committed. The [original Stage 1 report](gullyverse-stage-1-spatial-acceptance.md)
and `.gullyverse-artifacts/stage-1/` evidence remain intact.

## Authority and preservation

Read the three earlier immersive reports, the [reference manifest](../design/references/README.md),
the actual Stage 1 `results.json` and `captures.json`, and the Revision 2 brief.
The two natural cave photographs supplied inline control the entrance's rock
mass/opening composition; they are not local texture sheets. Reference group 04
controls scaffold structure/sign hierarchy, group 02 controls tunnel/paint,
group 08 controls camera ascent, and original screenshots preserve content/stage.
The new dusk requirement supersedes the prior daylight decision.

One persistent R3F Canvas, one connected entrance/tunnel/quarry, and the original
stage GLB remain. Existing trusses, speakers, LED panels/video, crowd pose cache,
readiness coverage, media controls, context recovery, history, URLs and 2D fallback
retain their ownership. No second stage/quarry or separate map world was added.
Payment APIs and original content routes were not rewritten.

The original `public/models/breeze/aftermovie-stage.glb` SHA256 remains
`C6FFDCAF05A7FB1F8CF47BC350FA4414615C6FBDFB38BDA83CD731FF8DAD2E5B`.

## Shared world and geometry revisions

The metre-based [layout registry](../public/models/gullyverse/blockout.layout.json)
feeds geometry, collision, camera references, destination arrows and map markers.
`+Y` is up and initial forward is `−Z`; eye height remains 1.72 m and capsule
radius remains 0.38 m. The original stage's unchanged model is repositioned to
`(−34, 0, −184)`, 14 m left of its Stage 1 anchor, to remain visible beside the
new centered scaffold. All Aftermovie poses and perimeter points shift with it.

| Element | Stage 1 | Revision 2 |
| --- | --- | --- |
| Landing eye position | `(0, 1.72, 24)` | `(0, 1.72, 11.5)` |
| Exterior rock mass | separate 24 × 13 m facade | continuous irregular 58 × 18 m formation |
| Tunnel floor width / height | approximately 9.4 / 7 m | approximately 5.9 / 5.6 m |
| Tunnel centerline | straight, z = 0 to −42 | bent continuous excavation, same entrance/exit |
| Tunnel walking half-width | 3.6 m | legal eye-center offset ±2 m, retaining wall clearance |
| Navigation scaffold | `(5, 0, −74)`, 10 × 11 × 2.8 m | `(0, 0, −76)`, 15.4 × 12.8 × 3.4 m |
| Original stage origin | `(−20,0,−184)` | `(−34,0,−184)`; original GLB/rig retained |
| Normal hub movement | entire quarry/tunnel/landing | local eight-sided hub around `(0, −51)` |
| Stage approach activation | at physical stage, approximately 25 s walking | local directional boundary; distant stage remains in place |
| Aftermovie boundary | old narrow rear automatic return strip | entire chamfered perimeter stops and asks for a destination |
| Artificial paths | visible pale strips | obsolete registry paths removed; no rendered strips |
| Overview | 320 m / 65°, portrait approximately 392 m | actual-rim responsive camera fit |

The tunnel centerline is `[(0,0), (−2.2,−8), (−6,−16), (−6,−24),
(−2.6,−34), (0,−42)]` in x/z. The introduction follows the same bend at eye
height. Irregular profile rings and continuous exterior rock join the portal to
the quarry; the rock bend physically blocks the initial direct sightline.
There is no artificial black view-hiding layer. Initial darkness comes from the
enclosed rock and dusk lighting; the ordinary travel curtain still covers loading.
The opening emerges as the camera rounds the latter bend.

The quarry footprint and original stage model retain their Stage 1 scale.
Entrance relief, ground variation and material detail remain lightweight procedural
approximations. Final fractured rock, calibrated roughness, authored UVs and
editable Blender source are Stage 2 dependencies.

## Camera composition and portrait projection

Fixed authoring camera IDs include landing, tunnel-near, tunnel-mid,
tunnel-first-exit-reveal, exit, scaffold-front, scaffold-diagonal, quarry,
left-stalls, right-stalls, overview, stage-front and stage-return.
Position/target pairs live in the registry; `captures.json` records the actual
rendered pose, effective FOV, viewport, quality/resource snapshot and saved player
pose. Nominal camera values are not substituted for the rendered evidence.

| Review camera | Position x/y/z, m | Target x/y/z, m | Nominal vertical FOV |
| --- | --- | --- | ---: |
| Landing | `(0,1.72,11.5)` | `(0,3.5,0)` | 58° |
| Tunnel near | `(−0.825,1.72,−3)` | `(−4,2.3,−12)` | 58° |
| Tunnel mid | `(−6,1.72,−22)` | `(−2.6,2.4,−34)` | 58° |
| First exit reveal | `(−4.64,1.72,−28)` | `(0,3.1,−42)` | 58° |
| Exit | `(−1.3,1.72,−38)` | `(0,5.3,−76)` | 58° |
| Scaffold front | `(0,1.72,−46)` | `(0,6.3,−76)` | 58° |
| Scaffold diagonal | `(−10,1.72,−52)` | `(0,6.3,−76)` | 58° |
| Quarry | `(0,1.72,−51)` | `(0,6.6,−120)` | 58° |
| Left stalls | `(−30,1.72,−89)` | `(−45,2.2,−112)` | 58° |
| Right stalls | `(29,1.72,−89)` | `(44,2.2,−112)` | 58° |
| Overview | Responsive actual-rim fit | Quarry/entrance midpoint | 64–80° |
| Stage front | `(−32.5,1.72,−160.5)` | `(−34,5.9,−178)` | 58° |
| Stage return | `(−32.5,1.72,−158)` | `(0,5,−42)` | 58° |

The prior blanket 52° minimum horizontal field expanded portrait vertical FOV
to approximately 93°. Revision 2 uses composition-specific horizontal fitting:
34° in the enclosed tunnel and 42° for entrance/quarry compositions, capped at
82° vertical. Aftermovie keeps its original 58° viewing/film lens. Aerial fitting
is separate from eye-height fitting and considers actual rim/portal extents.
Thus portrait landmarks use an intentional lens while retaining enclosure and
avoiding the former very wide common projection.

Actual captured overhead altitude is **209.90 m / 64° desktop** and
**299.13 m / 80° portrait**, compared with 320/392 m before. Portrait entrance,
exit and scaffold use 79.43°; the tunnel uses 66.98°. The complete rim fits without
requiring manual zoom. Fitting its full width leaves more vertical space in a
portrait viewport; this framing remains a human-review decision.

## Scaffold, paint, dusk and ground

The scaffold is centered on the tunnel exit axis and widened to a supported
festival landmark. Its top carries GULLYVERSE graffiti with smaller BREEZE 2027;
MAIN STAGE is primary; Events/Team occupy the left, Aftermovie/Contact Us the
right, with Accommodation/Past Sponsors integrated low on the installation.
There is no extra standalone Aftermovie board below it. Directional arrows use
nearby travel-zone intent and the shared destination geometry rather than random
button symbols. Metal braces, board mounts, warm lamps and cable connections
establish the reference hierarchy without adding shadow-casting light arrays.

Branding and the five artist names use the repository's graffiti font and
procedural transparent paint/weathering. Neha Kakkar, Chaar Diwaari, Ritviz,
Khullar G and Twin Strings reserve varied rock locations. Framed artist plaques
are removed. Paint can be replaced by final authored textures without changing
the world coordinate plan.

The existing `public/fonts/Fatal Fighter.ttf` supplies graffiti; directional
boards use condensed Arial Narrow with Arial fallback.
Critical font readiness is awaited through the scene's Suspense preparation
before paint canvases, texture initialization and shader warm-up. Graffiti uses
transparent 512 × 128 paint textures; surface placement follows the actual rock.

Lighting is late evening approaching dusk: cooler shadow fill, restrained warm
directional light and warm scaffold/stall practicals. Original stage identity
and effects remain. Ground uses compact dirt/gravel coloring, sparse grass and
small rock fragments, with a walkable surface instead of painted navigation
strips. This is not a glossy wet-floor or complete nighttime treatment.

Current dusk fill is `#a9bfd4` / `#8a8274` at hemisphere intensity 1.35, with a
warm `#efd0a4` directional source at `(−70,37,−145)`, intensity 1.35.
Sky/fog is `#737d87`. Three scaffold bell lamps share one warm point source;
small emissive stall/string bulbs have no costly individual shadow lights.
Procedural rock and gravel source canvases are 512 × 512. Ground remains at
local y = 0 under the hub/tunnel and actual Aftermovie viewing polygon for
navigation agreement; 340 instanced small fragments and 180 sparse grass tufts
supply visual variation without raising collision terrain. The 600 × 600 m
terrain patch keeps its far edge outside the aerial frame without changing the
camera fit or adding denser subdivisions. Old logical path/route/reentry fields
were removed after replacing their interaction model.

Hub people remain explicitly **capsule placeholders** for scale and density.
Their exit/stall/circulation/stage anchors remain available for production.
The near-stage crowd retains the original four baked human poses and quality
tiers; heavy human meshes were not copied into every hub cluster.

## Bounded hub travel and truthful destinations

The local hub polygon in x/z is `[(-8,-44),(8,-44),(18,-49),(18,-59),
(8,-64),(-8,-64),(-18,-59),(-18,-49)]`, with capsule inset. It allows natural
local movement and looking while avoiding a 100 m trek to the stage.
Swept outward threshold crossing selects a destination. Turning in place does
not select; edge ranges have gaps and outward-intent tests reject tangent sliding
into adjacent sectors. The hub shows no boundary destination menu.

| Destination | Boundary center x/z | Result |
| --- | --- | --- |
| MAIN STAGE primary forward sign | `(1.12, −64)` | Existing covered Aftermovie transition |
| Aftermovie right-hand sign | `(12.5, −61.75)` | Same Aftermovie destination via its side travel sector |
| Events | `(−12.5, −61.75)` | Existing `/events` content route |
| Team | `(−18, −51.85)` | Existing `/team` content route |
| Contact Us | `(18, −51.5)` | Existing `/get-in-touch` content route |
| Accommodation | `(−5.84, −64)` | Coming soon; remain in hub |
| Past Sponsors | `(18, −56.9)` | Coming soon; existing middleware redirects `/sponsors` |

Content routes remain their existing pages; Events/Team/Contact world rooms are
not claimed complete. Accommodation and Past Sponsors are disabled in map/menu
selection, and crossing their reserved zones displays truthful unavailability.
Navigation uses the shared destination registry and state machine. Covered content
handoff uses its actual original route, not an invented empty 3D scene.
The local database URL contains an unreachable placeholder host, so live event
listings are **blocked**, not accepted. Browser testing exposed an existing
uncaught catalog connection error. A narrow read helper now catches only Prisma
initialization/connectivity failures on the existing landing, category and detail
pages and shows `Event listings are currently unavailable. Please try again later.`
It preserves original queries/data/cart behavior when the database is available
and rethrows unrelated failures. No API, schema, credentials or database data
were changed. Reachable fallback pages do not prove real event data/registration.
Six destination IDs use seven travel segments: MAIN STAGE and the side Aftermovie
sign both reach the same original stage. This avoids a forward stage arrow leading
into Accommodation/Events merely because the physical stage stands far left.

## Aftermovie perimeter interaction

The outer viewing polygon is radius-aware and includes chamfered corners.
Any attempted outward crossing clamps the player first, clears movement, dims
the scene and opens `Where to next?`. It does not automatically return or move
the camera. The UI is typography over the existing world, with no board,
rectangular modal background or floating geometry. Current Aftermovie is omitted;
available destinations, Return to Hub, Entrance, disabled coming-soon choices,
`ESC — Stay here` and a touch-compatible Stay Here control remain.

Escape prioritizes the destination overlay before map or movie cancellation.
Dismissal retains pose and exposure and restores input. A boundary latch prevents
immediate reactivation until the player moves away and deliberately crosses again.
Destination selection submits the same covered navigation state machine and
retains URL/back/forward semantics. Internal props are not boundary detectors.
The former physical GULLYVERSE return sign is removed; this menu owns perimeter
departure choices.

## Same-world aerial map

M and the map control preserve the exact walking pose, clear normal input and
animate the existing camera through ascent, open overview and descent. Escape/M
close the map and smoothly restore that saved pose. The fit samples ground and
tall rim points plus entrance/portal; it does not fit the oversized ground plane.
Landscape uses the viewport's wide axis for the quarry's long axis; portrait
keeps the long axis vertical. Orientation changes continuously during ascent
and reverses on descent, with shortened transitions for reduced motion.

Destination dots project their actual world coordinates through the same R3F
camera. DOM labels use collision spacing and leader lines without inventing marker
positions. The full-screen interface includes stall zones, scaffold and tunnel
exit as landmarks. It has no alternate drawn diagram or small scrollable modal.
Unavailable destinations remain disabled and marked Coming soon. Capture metadata
records ascent progress and actual camera before/after screenshot readback.

## Real browser image evidence

[Open the new before/reference/current gallery](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/review.html).
[Exact camera metadata](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/captures.json)
accompanies all 15 desktop and 7 portrait views plus six ascent moments.
Geometry/framing changes intentionally prevent exact pixel matching to the rejected
Stage 1 cameras; the gallery identifies those comparisons. Ascent moments replay
the same public M action from an unchanged player pose. Fixed authoring cameras
are separate from live control and performance checks.

| View | Desktop | Portrait |
| --- | --- | --- |
| Landing | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-landing.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-landing.png) |
| Tunnel near | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-tunnel-near.png) | — |
| Tunnel mid | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-tunnel-mid.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-tunnel.png) |
| First exit reveal | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-tunnel-first-exit-reveal.png) | — |
| Exit | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-exit.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-exit.png) |
| Scaffold front | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-scaffold-front.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-scaffold.png) |
| Scaffold diagonal | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-scaffold-diagonal.png) | — |
| Quarry | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-quarry.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-quarry.png) |
| Left stalls | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-left-stalls.png) | — |
| Right stalls | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-right-stalls.png) | — |
| Overview | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-overview.png) | — |
| Stage front | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-stage-front.png) | — |
| Stage return | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-stage-return.png) | — |
| Boundary menu | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-aftermovie-boundary-menu.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-aftermovie-boundary-menu.png) |
| Map with markers | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-map-with-markers.png) | [Image](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-map.png) |

Map rise moments are [early](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-map-ascent-early.png),
[middle](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-map-ascent-middle.png),
[late](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-map-ascent-late.png) on desktop
and [early](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-map-ascent-early.png),
[middle](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-map-ascent-middle.png),
[late](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-map-ascent-late.png) in portrait.

## Verification and performance

The production build, relevant runtime tests, browser checks, payment previews,
recovery and frame-time measurements are recorded with their final evidence below.
The immersive runtime suite passes 37/37, including actual generated portal/tunnel
ray tests: landing/near-entry rays toward the exit, scaffold and stage hit rock
first; midpoint/first-reveal exit rays are clear. Other cases cover swept outer
faces/corners, trigger intent/hysteresis, map fitting through actual generated
quarry vertices at three aspects, pose preservation and covered navigation.
[Runtime unit output](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/unit-tests.log)
and [production compiler/type/lint output](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/build.log)
are retained. The first production attempt encountered a pre-existing Windows
Prisma DLL lock while an old local server remained running; stopping that server
resolved it, and the final preview build passed. The initial log is preserved.

The final [normal production build](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/normal-production-build.log)
also passes with authoring inspection disabled. Its [four public-control smoke checks](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/normal-production-smoke.json)
verify inspection rejection, aerial ascent/exact pose restoration, forward Main
Stage travel and boundary-menu ESC stay with one persistent Canvas; no page errors
or API writes occur. The localhost server was left running with this normal build.
The existing payment unit suite passes 13/13. Browser validation aborts every
non-GET/HEAD API request; no production payment data is submitted. Authenticated
database integration is not part of this environment revision.
The four event-catalog helper tests distinguish successful data, missing results,
expected connectivity failure and unrelated exceptions. The first live probe also
caught an ambiguous test-only `role=status` selector; it was narrowed and the
initial failed run retained under `first-browser-attempt/` before the full rerun.

The final [public-control browser evidence](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/browser-checks.json)
contains **34 passing checks, zero page errors and zero API mutations**. It covers
all eight cardinal/diagonal Aftermovie approaches, four specifically aimed
chamfer segments, Stay/ESC and hysteresis, deliberate crossings of all seven hub
segments, covered route/history travel, media/unmute ownership, reduced motion,
and touch map/Stay controls. Both map profiles verify button bounds and lack of
overlap, and compare each actual world dot with a Three.js projection within 2 px.
Events landing/categories/detail render the explicit unavailable state under the
current database configuration; that result does not certify live catalog data.
The [28-capture manifest](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/captures.json)
records all required 22 views and six ascent moments, with no page errors or writes.

Visual comparison confirms the larger dark entrance, physical bent passage,
sprayed artist text, centered scaffold hierarchy, left stage visibility, and
full-screen same-world map. Differences from the references remain visible:
rock forms and crack tiling are procedural and smoother than fractured natural
excavation; dusk has less sunset color/shadow variation; scaffold weathering,
cables and lamps are much simpler than the photograph; vendor and population
detail is sparse. Intermediate ascent can reveal the far terrain patch horizon.
These images demonstrate the revised composition, not photographic equivalence
or approval on the user's behalf.

Stage 1 baseline is the retained actual JSON, not rounded text from an earlier
report: desktop hub 56.91 FPS / p95 17.8 ms / 140 calls / DPR 1; desktop Aftermovie
56.91 FPS / p95 17.8 ms / 110 calls / DPR 0.75; touch-emulated hub 56.87 FPS /
p95 20.3 ms / 131 calls / DPR 0.75; touch-emulated Aftermovie 56.34 FPS /
p95 18.2 ms / 73 calls / DPR 0.6. Touch emulation uses the desktop Intel GPU.

[Event-catalog tests](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/events-catalog-tests.log)
and [payment unit output](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/payment-unit-tests.log)
are available separately. The first performance journey's touch-look assertion
started while the newly animated map was still descending. The harness now waits
for movement ownership to return; its initial partial measurements/error remain
under `first-perf-attempt/`. This correction does not shorten or bypass the ascent.

### Final Intel UHD 620 measurements

The completed [production performance journey](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/results.json)
uses Chrome 155.0.8059.40, Intel Core i5-8265U and ANGLE Intel UHD Graphics 620 /
D3D11 on Windows 10.0.26300. Desktop is 1366 × 768 / DPR 1. Touch emulation is
390 × 844 / device DPR 2 with 4× CPU throttling on the same Intel GPU. These are
5.6-second movement windows, not sustained performance or physical-phone acceptance.

| Profile / area | FPS Stage 1 → R2 | p95 ms before → after | Maximum ms before → after | R2 frames >34 ms |
| --- | --- | --- | --- | ---: |
| Desktop hub | 56.91 → 56.75 | 17.8 → 17.8 | 18.7 → 47.4 | 1 |
| Desktop Aftermovie | 56.91 → 56.93 | 17.8 → 17.8 | 18.3 → 20.6 | 0 |
| Touch-emulated hub | 56.87 → 54.61 | 20.3 → 20.9 | 39.3 → 175.8 | 3 |
| Touch-emulated Aftermovie | 56.34 → 56.90 | 18.2 → 18.1 | 41.2 → 22.7 | 0 |

R2 p99 values are respectively 21.9 / 18.3 / 32.1 / 18.8 ms. The emulated hub
has a significant 175.8 ms outlier and approximately 4% lower mean FPS. It is
retained in the evidence. Strict 16.67 ms / 60 FPS acceptance has not passed.

| Profile / area | Calls before → after | Triangles before → after | Textures before → after | Geometries before → after | DPR / tier before → after |
| --- | --- | --- | --- | --- | --- |
| Desktop hub | 140 → 139 | 65,704 → 94,944 | 27 → 27 | 158 → 151 | 1 / 0 → 1 / 0 |
| Desktop Aftermovie | 110 → 113 | 992,234 → 1,017,554 | 27 → 27 | 162 → 155 | .75 / 2 → .6 / 3 |
| Touch-emulated hub | 131 → 133 | 57,820 → 87,336 | 27 → 27 | 158 → 151 | .75 / 2 → .75 / 2 |
| Touch-emulated Aftermovie | 73 → 76 | 988,790 → 1,014,110 | 27 → 27 | 162 → 155 | .6 / 3 → .6 / 3 |

Draw calls remain close to Stage 1. The denser excavation/portal/tunnel geometry,
ground grid, conforming paint and instanced grass/gravel increase triangle and
buffer cost. Desktop Aftermovie additionally selected tier 3 / DPR .6, reducing
image resolution from the previous .75. This is a visual compromise, not proof
of unchanged rendering cost. The unchanged governor's phase trace shows the
downgrades occurred during covered first-stage preparation; its warm window
took 1,159 ms versus 861 ms before. The initial archived run selected the same
desktop tier. Shader preparation remains covered; no features were removed to
hide the performance cost. The full cause of bootstrap outliers and the extra
desktop quality reduction remains an optimization risk.

| Timing, ms | Desktop Stage 1 → R2 | Touch-emulated Stage 1 → R2 |
| --- | --- | --- |
| Cold landing ready | 2,128 → 2,886 | 4,088 → 7,737 |
| Entrance choreography | 7,474 → 7,436 | 7,948 → 7,877 |
| Hub walking to stage commitment | 25,224 → 3,400 | 25,195 → 3,463 |
| Cold committed stage travel | 3,368 → 2,864 | 3,062 → 2,144 |
| Warm map travel | 1,482 → 2,882 | 1,743 → 3,552 |
| Direct Aftermovie ready | 2,494 → 3,671 | 4,560 → 11,280 |

The former 25 seconds measured quarry walking after the separate 7.2-second
welcome, not entrance choreography. Nearby sectors remove that trek without
increasing 4.2 m/s walking speed. Warm map travel now includes the intentional
camera ascent. Cold landing and direct entry regress substantially, especially
under CPU throttling, and require startup optimization before production.

Initial texture / shader / warm-render preparation was **212 / 526 / 317 ms
desktop** and **192 / 234 / 563 ms emulated**. Cold stage preparation was
**1 / 87 / 1,159 ms desktop** and **5 / 40 / 247 ms emulated**. Individual human
pose bakes were 4.3–13.9 ms desktop and 37.4–78 ms emulated. Main-journey long-task
maxima were 254 / 1,019 ms. Readiness preparation explains part of startup cost;
preparation records do not isolate every procedural generation, font, React or
asset-initialization task. No timer reveals an unfinished scene.

[Desktop diagnostics](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/desktop-diagnostics.json)
and [touch-emulated diagnostics](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/mobile-emulated-diagnostics.json)
retain full phase timelines, preparations, resource samples and long tasks,
including lifecycle/screenshot gaps outside dedicated movement windows. GPU
timers produced 234 / 237 samples with zero discarded disjoint queries.

[Ten-trip residency evidence](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/residency.json)
retains **27 textures / 155 geometries at both first and last visits**. Active
geometry backing is 3,198,724 bytes (~3.05 MiB), versus ~1.69 MiB before;
estimated mapped source-texture storage is ~26.97 MiB, versus 22.22 MiB before.
These are buffer/RGBA-plus-mipmap estimates, not measured VRAM. Post-GC heap
after clearing recorded diagnostics rose from 13,911,148 to 14,618,776 bytes
(~0.67 MiB) over ten trips; this does not certify longer sessions.

The [11 edge/recovery checks](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/edge-cases.json)
pass delayed/failed assets, interrupted travel, actual context loss/restoration
during delayed bootstrap, hub and playback, persistent Canvas/pose ownership,
repeat travel and fallback. Profiling attempted zero API writes. Native hidden-tab
and freeze events were not observed in headless Chrome; synthetic held-input
blur/freeze/resume checks passed. In-flight shader-compilation loss, the full
45-second no-restoration timeout, physical audio output and physical mobile
remain unverified.

The [payment browser preview](C:/Users/neera/Downloads/Divyansh/Breeze-2027/.gullyverse-artifacts/stage-1-revision-2/payment-browser.log)
passes detail entry, QR/pending status, admin statement mapping/import preview,
mobile overflow and zero API mutations. It uses local preview behavior, not a
production payment or authenticated database reconciliation.

## Reproduce the review

Build a deliberate local authoring preview with inspection enabled, then start
the production server in its own terminal. Stop that server before another
Prisma-generating build on Windows.

```powershell
npm.cmd run test:immersive
npm.cmd run test:payments
$env:NEXT_PUBLIC_GULLYVERSE_INSPECTION='1'
npm.cmd run build
npm.cmd run start -- --port 3000
```

Run the browser journeys separately to avoid GPU contention and keep screenshot
readback out of the dedicated performance windows:

```powershell
node scripts/check-gullyverse-stage-1-revision-2.mjs
node scripts/capture-gullyverse-stage-1-revision-2.mjs
$env:GULLYVERSE_ARTIFACT_DIR='.gullyverse-artifacts/stage-1-revision-2'
$env:GULLYVERSE_MODE='production-stage-1-revision-2'
node scripts/perf-gullyverse.mjs
$env:PAYMENT_TEST_ARTIFACT_DIR='.gullyverse-artifacts/stage-1-revision-2/payment-preview'
npm.cmd run test:payments:browser
```

Fixed cameras require `?diagnostics` and either development or that deliberate
preview flag. Normal production is rebuilt with the flag absent or `'0'`, so
authoring inspection is disabled. A browser's real movement and map controls
remain available without the inspection flag.

## Remaining placeholders, risks and next-stage gate

The environment is not production ready or visually accepted. Human review must
approve the actual entrance, tunnel reveal, foreground scaffold, stage relationship,
dusk readability and desktop/portrait map composition. Procedural rock facets,
paint/weathering, simple stalls, placeholder hub people and sparse ground dressing
remain replaceable blockout assets. Reference photographs cannot establish exact
real-world lens, dimensions or exposure. The scaffold reference's material richness
and vegetation require later production; rendering its hierarchy is not exact
photographic equivalence.

Strict sustained 60 FPS, physical iOS/Android/Safari, long-session thermal behavior,
driver VRAM usage and final-art memory budgets remain unverified. Count stability
and short desktop-GPU windows do not certify those targets. Blender remains a
later toolchain/source dependency; no new `.blend` or final GLB was produced.
Stage 2 begins only after human visual approval and covers production quarry
geometry, authored materials, believable rock surfaces and final environmental
lighting, followed by the same camera/control/recovery/performance checks.
