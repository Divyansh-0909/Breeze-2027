# Breeze 2027: first immersive vertical slice

This is the original vertical-slice baseline. The subsequent loading/profiling/recovery revision and pending reference-art acceptance are documented in [immersive-environment-acceptance.md](immersive-environment-acceptance.md). Original measurements below are retained for comparison.

## Dependency decision (before architecture changes)

The installed baseline was React / React DOM 18.2.0, Fiber 9.6.1,
postprocessing 3.0.4, Next 15.3.8, and Three 0.169.0. Fiber declares React
`>=19 <19.3`; postprocessing declares React `^19.0` and Fiber `^9.0.0`.
Next 15.3.8 declares support for React 19. The installed Radix, Motion,
React Hook Form, Lucide, and Font Awesome peer ranges accept React 19.

Use matching React / React DOM **19.0.8** (stable patched 19.0 series),
React types 19.0.14, and React DOM types 19.0.6. The full peer tree additionally
exposed Radix menu/select's pinned `react-remove-scroll@2.6.0`, which rejects
React 19. Override just that transitive package to stable 2.6.3, whose published
peer range includes React 19. Preserve Next, Fiber,
postprocessing, Three, and unrelated direct dependency versions. No alpha packages,
WebGPU, TSL, physics library, or new rendering engine.

Primary references: [Fiber compatibility](https://r3f.docs.pmnd.rs/getting-started/introduction),
[Next 15.1 React 19 support](https://nextjs.org/blog/next-15-1).
The local installed peer manifests, not latest package suggestions, determine
the compatibility decision. Run npm peer validation, TypeScript, build, and
browser regression checks after installation. Both lockfiles must agree with
the manifest; the pnpm lock was already stale relative to the payment changes.

## Preservation decision (before adapting Aftermovie)

`ConcertStageHero` currently owns a Canvas, its camera, a staged mount schedule,
and video lifecycle. A second destination Canvas would destroy renderer
continuity. Extract its scene and video behavior into reusable components so
the public experience can host those exact stage children in one persistent
Canvas. Keep the original standalone wrapper for the existing recorder.

Preserve Stage and its GLB, Trusses, Speakers, Barricades, Crowd's baked poses
and instancing, LEDScreens' three panels and single shared VideoTexture,
Lights, and Fireworks. Replace only camera ownership and page-level travel
choreography in the public experience. Optional density/effects may be scaled
by the shell's quality governor without changing the stage composition.

## Visual status

No new real tunnel/cavern reference photography or authored environment GLBs
were attached to this request. The movement proof uses an explicitly temporary
blockout. It is not a realism submission and cannot satisfy visual acceptance.
Do not approve it as final environment art.

## Implemented world and navigation

The public ClientLayout retains one `ImmersiveShell` across `/` and
`/aftermovie`. Ordinary content and admin routes keep their existing layout.
Only two stable location IDs exist: `hub` and `aftermovie`. The navigation
graph owns their bounds, arrival poses, bidirectional thresholds and travel
pacing. Decorative labels for other destinations do not instantiate scenes.

The shell owns one WebGL2/WebGLRenderer Canvas. `ImmersiveRuntime` owns a
mutable eye-height pose, input axes, velocity, elapsed travel time and discrete
UI/navigation snapshots. `useSyncExternalStore` subscribes only to phase,
location, map, quality, motion preference and movie changes. There are no per-frame player
coordinates in React state. Keyboard, pointer drag and basic touch buttons
feed the same axes. Blur/background, travel, movie focus and the modal map
clear held input. Quality changes preserve held input.

Landing has no walking controls. Enter, Space, click/tap on the entrance
button or rendering surface starts the ~7.2 second authored anchor path.
Reduced motion substitutes a short covered relocation. The tunnel is the only
primary entry tunnel. It opens into a large open-roof bowl; temporary stalls,
crowd and stage silhouettes establish festival composition. Wayfinding uses
textured physical boards, steel uprights, crossbeam and hangers, not projected
HTML. Only the Aftermovie route commits travel.

The hub is bounded. Crossing the Aftermovie threshold captures camera pose
and walking velocity, rejects further local input and starts guided travel.
The Aftermovie viewing rectangle stays clear of stage/runway/backstage, with
a designed return strip behind the visitor. Map selection calls the exact
same `runtime.request(locationId, source)` as thresholds and URLs. It has no
independent router. Direct links use preparation plus a short arrival,
without the introduction. Native history integration updates the URL after
arrival; popstate and pathname changes submit the same request. New requests
supersede old trips; stale readiness completions carry an invalid serial and
cannot reveal the wrong scene. Escape exits playback or closes the map;
there is no separate Escape-to-cancel travel UI.

## Handoff and readiness

`departure` moves from the exact current pose while an opaque curtain rises.
Only once it is fully opaque does the runtime select and instantiate the
destination and its arrival-start pose. The outgoing detailed scene unmounts.
The destination remains covered until every critical loader and all four
crowd variants resolve. The readiness gate initializes mapped and shader
textures, awaits `compileAsync`, then flushes two upload frames and measures
four real renders behind the curtain at the chosen DPR. If the stage's render
window exceeds budget, it reduces quality and repeats that short preparation
before restoring controls. `arrival` continues guided motion
and lowers the curtain; `local` restores input. Physical travel uses longer
camera paths than map/URL travel, without a forced seven-second video wait.
Cold loading may extend the covered hold. No timer overrides readiness to
reveal an incomplete scene. A 45-second preparation timeout, critical loader
error or lost graphics context offers native video and existing content links.

The gate exercises render paths rather than guaranteeing every browser/driver
variant or future optional asset is compiled. Scene loading still uses the
main thread for GLB parsing and pose baking. Those tasks occur while covered.
Future authored assets require fresh profiling; readiness is not a proof that
all hardware meets the frame-time target.

## What was preserved and replaced

Preserved: `Stage.tsx` / `aftermovie-stage.glb`, `Trusses`, `Speakers`,
`Barricades`, existing crowd models and baked poses, the three LED screens and
their original shader/composition, stage light rig and pyro fixtures.
The shared video hook preserves click-to-play, the 900ms camera focus move,
`preload=none`, HTTP range/progressive media, actual-playing-triggered pyro,
muted autoplay recovery, end/error cleanup, and Escape cancellation. Playback
returns to the visitor's prior bounded pose. An explicit sound button supports
the existing muted recovery. `ConcertStageHero` retains its standalone Canvas
wrapper and original camera/effects for other uses; its media hook is shared.
The recorder route and its capture behavior were not changed.

Replaced in the public slice: old GateHero landing/tunnel choreography,
independent Aftermovie page Canvas and minimum-duration crowd travel overlay,
fixed/parallax crowd camera, and old gate-specific performance script logic.
Their source components remain available. The public shell omits the prior
bloom/vignette/particle stack to avoid applying theatrical effects to the new
natural environment. It retains principal stage geometry and screen behavior.

Small resource adaptations: LED-generated textures/materials, moving-head
materials, generated pyro sprite textures/point geometries and the barricade's
shared segment geometry/material now dispose on unmount; LED video uniforms stop sampling the released
media texture after the original exit fade. Crowd instance buffers dispose
without disposing the four shared baked geometries. Density is a prop using
the original deterministic crowd distribution and poses.

## Resource ownership and adaptive quality

Only the current critical scene is resident; the next scene's instantiation is
covered. Code/HTTP/useLoader caches retain the small known shared model set,
stage GLB and logo, plus four baked crowd geometries for repeat travel. There
is no future-destination asset preload. Shared GLB resources are not disposed
by cloned scene instances. Scene-owned blockout geometry/materials, sign/paint
textures, LED prompt/loading/blank/glow textures and instance buffers are
released on outgoing scene unmount. The video hook owns one media element and
one VideoTexture shared by all panels; it pauses, removes the source, aborts
loading and disposes textures/timers on exit/unmount.

The quality governor samples normal local frame windows, with hysteresis and
cooldown. It reduces DPR from 1.25 to 1, 0.75 and 0.6, caps it by device DPR,
reduces stage crowd from 900 to 600/300 and hub silhouettes from 140 to 60, and
disables optional active pyro at lower tiers. Touch starts at the moderate
tier. No dynamic shadows or new postprocessing are added. Quality changes do
not reset the player's input or recreate the rendering context.

## Reproduction and acceptance

Run `npm run test:immersive`, `npm run build`, `npm start`, then
`GULLYVERSE_MODE=production npm run perf:immersive` (PowerShell uses `$env:`).
The existing `scripts/perf-core-flow.mjs` delegates to the new runner, retaining
`PERF_BASE_URL` and repeat-count input. This runner measures actual R3F-rendered
frame deltas, not a separate rAF counter that could hide a parked renderer.
Diagnostics are enabled with `?diagnostics`; normal visitors do not allocate
the sample ring. Reports and screenshots live in `.gullyverse-artifacts`.

Implementation tests cover ownership, delta-aware motion, boundaries,
velocity continuity, route requests, stale readiness, background delta clamp,
direct entry, reduced motion and playback pose restoration. Browser checks
cover the entire physical loop and map loop, direct links, back/forward,
resize, held-key blur interruption, tab switching, touch, media range playback,
asset delay/failure, context loss, superseding trips and ten round trips.

Visual realism and reference matching are **not achieved**: the required new
reference photographs and authored environment assets are absent. Physical
iOS/Android device certification is **not achieved** by Chrome mobile emulation.
Long-session thermal/battery behavior and arbitrary driver/browser coverage
remain unmeasured. There is no claim of Bruno Simon-level perceived smoothness
or final-art performance certification.

## Measurements: 8 October 2026

Production Next 15.3.8, Chrome 155.0.8059.40 headless, Windows
10.0.26300, Intel i5-8265U / **Intel UHD Graphics 620** confirmed through
WebGL's renderer string. The machine also has an MX130, but this run used the
integrated GPU. Each movement segment sampled roughly 5.6 seconds / 321–322
actual rendered frames after a ten-second stage stabilization period. These
are one complete run per profile, not a cross-device certification or an
input-to-photon measurement.

| Profile / segment | Mean FPS | p95 frame | Maximum frame | Frames >50ms |
| --- | ---: | ---: | ---: | ---: |
| Desktop 1366×768, hub | 56.89 | 17.8ms | 18.2ms | 0 |
| Desktop 1366×768, Aftermovie | 56.90 | 17.8ms | 18.1ms | 0 |
| Touch emulation 390×844, CPU 4× slower, hub | 56.83 | 18.4ms | 27.6ms | 0 |
| Touch emulation 390×844, CPU 4× slower, Aftermovie | 56.69 | 18.2ms | 47.7ms | 0 |

Desktop used DPR 1 in the hub and 0.75 / 300 crowd instances at the stage;
the touch profile settled to the same stage tier. The touch profile kept the
desktop integrated GPU, so its results are not mobile GPU measurements. It
also checked landscape 844×390; desktop checked resizing to 1024×700.
Movement changed the pose on the first observed frame: 2.4–3.6ms after keydown
in the desktop samples and 5.7–12.8ms in the emulated profile. That timing
observes runtime pose delivery, not physical screen latency.

| Measured interval | Desktop | Touch + CPU throttle |
| --- | ---: | ---: |
| Initial landing preparation | 1.53s | 3.23s |
| Entrance (including browser interaction overhead) | 7.47s | 7.75s |
| Cold Aftermovie trip after committing the threshold | 4.50s | 4.76s |
| Warm map trip (including opening/selecting the map) | 1.44s | 1.94s |
| Warm direct `/aftermovie` page load + arrival | 2.51s | 3.75s |

The ten-trip browser audit stayed at **7 textures / 124 geometries** on every
Aftermovie visit. It exposed and verified fixes for the original generated
pyro texture and point-geometry leaks and the barricade geometry's missing
disposal. The ordinary flow also preserved the exact same Canvas element
through threshold travel, returns, map requests and back/forward. Actual media
playback requested `Range: bytes=0-` and Escape restored the saved viewing pose.

Both full profile runs and edge cases passed. Edge cases included cold direct
entry with a delayed critical GLB, superseding a trip via URL, ten round trips,
deliberate WebGL context loss and an aborted critical asset request. Errors
offered the 2D fallback. There were no scene/shader/application errors in the
normal flows. Existing Vercel analytics and speed-insights script endpoints
return 404 on local `next start`; the runner records those exact localhost
URLs separately and does not suppress other failed assets.

Eight runtime tests, TypeScript/build validation, targeted lint, npm peer
validation and `npm ci --dry-run` passed. The pnpm frozen-lock offline check
passed. Existing payment unit tests passed 13/13; the existing Edge browser
suite passed customer/admin previews, responsive layout, and zero preview API
mutations. Additional Chrome smoke checks passed `/team`, `/get-in-touch`,
`/merch` (its existing home redirect), and `/admin/login` with HTTP 200 and no
page errors. A final live preference-change check confirmed reduced motion
publishes immediately during local movement, without needing a navigation
event. The production build retains existing unrelated lint warnings.
Authenticated admin/database integration was not exercised against real data.

Raw artifacts: [profile results](../.gullyverse-artifacts/results.json),
[ten-trip and failure-path checks](../.gullyverse-artifacts/edge-cases.json),
[desktop hub capture](../.gullyverse-artifacts/desktop-hub.png),
[desktop stage capture](../.gullyverse-artifacts/desktop-aftermovie.png).
These artifacts are retained locally and ignored by Git; this report keeps
the measured summary in version control.

Acceptance limits and remaining performance risks:

* **Strict 60 FPS is not achieved/certified** in these headless measurements:
  both scenes average about 57 FPS. The settled desktop samples are regular,
  but that is not a claim of a measured 60 FPS pass.
* Cold trips exceed the initial 2.5–4s pacing target. Their covered hold waits
  for real asset/GPU preparation; warm trips are shorter. Main-thread cold
  parsing/compilation remains costly: whole-flow long-task maxima were 1001ms
  desktop and 438ms with CPU throttling, including loading. This must be
  remeasured with authored environments and slower networks.
* The short hidden quality sample can underestimate the arriving view's cost;
  the local governor may still make a further adjustment shortly after arrival.
  Long-session/thermal behavior, final art density and high-tier pyro-onset
  shader variants remain risks requiring additional real-device measurement.
* Headless tab switching did not report `document.hidden=true`. Blur/focus
  input clearing and background delta clamping were verified; true OS/browser
  background/restore remains unverified. Physical mobile 60/30 FPS and Safari
  behavior remain unverified.
* Reference-matched visual realism, authored environmental occlusion and the
  final reveal's perceived continuity remain unapproved blockout work. No new
  realistic tunnel/quarry GLB or KTX2 texture delivery is claimed.

Next work, within this same vertical slice: author and review reference-based
tunnel/quarry GLBs and spatial manifests using
[the environment pipeline](gullyverse-environment-pipeline.md); then measure
the final assets on this integrated GPU and real mobile devices. Add no new
destination environments until the user approves this slice.
