from pathlib import Path
import json

root=Path.cwd(); output=root/'reports/stage-1-final-2026-10-11'; raw=output/'raw'
def read(name): return json.loads((raw/name).read_text())
def link(name,label=None): return f'[{label or name}](../reports/stage-1-final-2026-10-11/{name})'
def fmt(x): return '—' if x is None else f'{x:.2f}'
before=read('baseline-performance.json'); after=read('after-performance.json')
resources=read('resource-results.json'); browser=read('regressions/results.json'); diff=read('source-diff.json')
rows=[]
for label,data in [('Before',before),('After',after)]:
 for w in data['windows']:
  s=w.get('stats',{})
  rows.append('| '+ ' | '.join([label,w['name'],str(w['elapsedMs']),fmt(w.get('renderedFPS')),fmt(w.get('medianMs')),fmt(w.get('p95Ms')),fmt(w.get('p99Ms')),fmt(w.get('maxMs')),str(w.get('stallsOver100ms')),str(s.get('calls','—')),str(s.get('triangles','—')),str(s.get('textures','—')),str(s.get('geometries','—')),str(s.get('dpr','—')),str(w.get('snapshot',{}).get('quality','—'))])+' |')
cold_before=before['windows'][0];cold_after=after['windows'][0]
def transfers(w):
 entries=w.get('resources',[])+w.get('navigation',[])
 return sum(r.get('transferSize',0) for r in entries)
network_before=transfers(cold_before);network_after=transfers(cold_after)
alloc=[]
for c in resources['cycles']:
 s=c['settled'];gl=s['contexts'][0]['stats'];v=s['stats']
 alloc.append(f"| {c['cycle']} | {c['exit']} | {c['firstPlayMs']} | {v['textures']} | {gl['Texture']['active']} | {v['geometries']} | {gl['Program']['active']} |")
changes='\n'.join(f"- [{c['path']}](../{c['path']})" for c in diff['changesAgainstApprovedBaseline'])
new='\n'.join(f"- [{p}](../{p})" for p in diff['newSourceFiles'])
timing=browser['checks'][0]['evidence']['timing']['activationToLocalMs']
text=f'''# Gullyverse Stage 1 final acceptance — 2026-10-11

The current user-approved worktree is the visual and spatial authority. This delivery applies bounded runtime fixes and preserves the current environment. It does **not** grant visual approval or certify production art or physical-device performance. No commit, push, deployment, database mutation or Stage 2 environment production was performed.

## Exact starting baseline and preservation

Branch `codex/navigation-board`, HEAD `8919589d47385efd674ca91b52376f1ad310b797`; no staged changes. Starting modifications were `AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx`, `aerial.ts`, `blockoutGeometry.ts`, the layout JSON and `runtime.test.ts`; untracked `AftermovieEnvironment.tsx` and `reports/` existed already. They were preserved. See the exact {link('raw/baseline-state.json','starting status')}, {link('raw/baseline.patch','original working-tree patch')} and [current baseline document](gullyverse-current-user-approved-baseline.md).

A non-destructive {link('raw/current-approved-baseline.tar.gz','baseline archive')} contains 871 selected non-secret source/configuration/asset/evidence files, including important untracked files. All current `public`/`Assets` files are covered: {link('raw/asset-backup-coverage.json')}. No environment credentials were copied. Changes in this delivery are measured against this snapshot, **not** against Git HEAD: {link('raw/source-diff.json')} and {link('raw/changes-against-approved-baseline.patch')}. The snapshot comparison with the October 10 source manifest found no differences for overlapping files; this is evidence of the present content, not proof of who edited it or when. Historical audit files remain unchanged.

## Preserved composition and visual review

The shared manifest still defines the 97.8 × 123.5 m quarry, stage origin `[-12,0,-134.3]`, scaffold `[0,0,-70]`, current movement polygons, 25 rock masses, dry ground and left/right stalls. The 24 × 14.5 × 3.4 m scaffold and current GULLYVERSE/signboard hierarchy remain unchanged. No Main Stage/Accommodation signs were restored. Current tunnel bend, exterior, graffiti placements, lighting, fog, exposure and current aerial camera configuration remain the baseline. Exact configuration is reproduced in the baseline document.

All 362 current public/Assets files and locked HubScene, AftermovieEnvironment, aerial camera, blockout geometry, layout manifest, LED shader sources/dimensions, lockfiles, historical audit and payment/admin files pass snapshot preservation checks: {link('raw/locked-preservation.json')}. The original stage GLB, male/female crowd GLBs, video, principal stage placement, trusses, effects, LED dimensions/UVs/shader source and crowd pose times are preserved. Playback code changes concern ownership and camera restoration, not stage art. The current dark 49 × 39 m stage-local floor, cream return placard and mode-specific environment lighting/fog remain intentionally preserved. Their visible rectangular floor/atmosphere discontinuity is documented for explicit review rather than silently redesigned under historical instructions.

There are 23 matched fixed-view desktop/portrait pairs: {link('gallery.html','before/after gallery')}, {link('baseline/captures.json','baseline poses')} and {link('acceptance/captures.json','acceptance poses')}. These are actual production-browser captures at desktop 1366 × 900 and portrait 390 × 844, DPR .25, with recorded camera/FOV/tier. The opt-in review-camera diagnostic positions are not claims about visitor navigation. Public journey evidence is separate. Pixel differences are quantified in {link('raw/visual-comparison.json')}; animated LED content/practical lights and capture timing can change pixels. No claim of universal pixel identity is made. Original references and old audit frames are labelled historical context in the gallery.

Entrance and tunnel are still procedural blockouts: faceted rock silhouette, flat graffiti surfaces and limited roughness detail. Tunnel bend/delayed reveal remain functional; final irregular rock/PBR/graffiti art is unfinished. Quarry/stalls/hub capsule population remain temporary, with original stage crowd identity preserved. Higher-density reused crowd models were not introduced: no physical-GPU performance evidence justified that visual/resource change. No new paths, shadow system, postprocessing, lighting redesign or destination was added.

## Root causes and narrowly scoped fixes

| Problem | Evidence / root cause | Fix and affected code | Visible consequence |
| --- | --- | --- | --- |
| Held movement survives editable focus | Fresh baseline held D → actual textarea focus moved 1.88859 m; keyup could be lost and held ownership persisted. | `input.ts`: clear keys/touch/drag/velocity on focus into inputs, textarea, select, contenteditable or forms; guard composed path/active element; blur/freeze/suspension clears ownership; stale repeats cannot reacquire an unheld key. | Movement stops on focus; environment unchanged. |
| Navbar Home replays landing | Fresh baseline ordinary Home from Contact ended in `landing`. No explicit completed-entry routing policy existed across remounts. | `navigation.ts` owns URL/session entry policy; Navbar uses that coordinator href; `ImmersiveShell` records completed entry/history preserving Next fields. `/?arrival=hub` is explicit; fresh bare entry remains user-activated. | Requested Home behavior changes; layout/camera spawn preserved. |
| Video texture reallocation | Initial four untraced cycles plateaued; traced old-runtime cycles reproduced Three 26→29 / tracked GL 30→33. Disposed texture UUIDs remained sampled by three LED materials and were re-uploaded. Thus the race is timing-dependent, not inevitable every run. | `videoTextureOwnership.ts` producer/consumer leases; `useStageVideo.ts` retires producer, cancels pending activation/listeners/promises and releases source. `LEDScreens.tsx` retains through the existing fade, detaches all samplers to blank before final disposal; no arbitrary disposal timer. | Original segmented shared-video wall and fade retained. |
| Cinematics slow under low FPS | Entrance and travel accumulated the same ≤50 ms delta used by safe locomotion; baseline entrance action window 16.423 s. | `runtime.ts`: safe movement delta separate from active cinematic time; event-clock clips first frame to actual activation, smoothstep/yaw paths preserved. Suspension excludes hidden time; first resumed frame discarded. Exceptional foreground camera gaps >500 ms are covered and the existing cover fades back over bounded updates, so skipped path segments are not shown. The authored clock keeps progressing. `activeDeadline.ts` measures foreground readiness budget. | Authored pacing restored; very low FPS still looks discontinuous. No asset reveal before readiness. |
| Invalid map projection | October audit observed NaN/Infinity writes. Fresh browser sampling caught none; deterministic actual spawn/projection state produced clip W=0 and invalid old coordinates. Old projection reused cached results based on position/viewport while rotation/FOV could change. | `mapProjection.ts`: homogeneous finite/W/depth/frustum checks before division; `WorldOverlays.tsx` refreshes actual camera state, omits invalid SVG nodes/lines and non-visible focus targets. | Same actual-world aerial map; invisible/invalid markers safely omitted. |
| Irrelevant 404-image preload | Successful root DOM did not contain image. Missing local Vercel telemetry script responses were 404 pages with HTTP Link preload for the 4,586,644-byte image. | `notFound.tsx`: remove `priority`, use lazy loading. Real 404 page and image preserved; telemetry packages untouched. | No appearance change to successful landing. |
| Cancelled crowd preparation ownership | Interrupted/stale preparations could abandon private pose buffers; disposing shared GLTF/cache resources would be unsafe. | `Crowd.tsx` + `poseResources.ts`: finally clean CPU intermediate geometry/mixer; publish complete shared pose batch atomically; dispose only unpublished or losing owned batches, once; errors propagate to existing fallback. | Pose selection, model identity, density and materials preserved. |
| Playback/transition interruption | Rapid playback restart during camera restore could replace original walking anchor; interruption could reset covered opacity. | `runtime.ts` preserves original walking anchor through restart and current cover on interrupted departure; late play rejection guarded by current source identity. | Camera restoration becomes consistent; authored composition unchanged. |

Evidence: {link('raw/baseline-defects.json')}, {link('raw/map-projection-reproduction.json')}, {link('raw/baseline-preload-headers.json')}, {link('raw/baseline-video-trace.json')}, {link('raw/regressions/results.json')} and {link('raw/resource-results.json')}.

## Architecture and loading policy

```mermaid
flowchart TD
  URL[URL / history / session entry] --> NAV[Existing shared navigation coordinator]
  Controls[Navbar / hub thresholds / boundary options / map markers] --> NAV
  NAV --> RT[One immersive runtime: pose / phase / cover / input ownership]
  Manifest[Unchanged shared world registry] --> RT
  RT --> Canvas[ImmersiveShell persistent R3F Canvas]
  Canvas --> World[Persistent tunnel / hub / original stage]
  Canvas --> Crowd[Near crowd prepared behind cover; owned instance buffers]
  World --> LED[LED material sampler leases]
  Video[One active HTMLVideoElement + VideoTexture producer] --> LED
  RT --> Prep[Texture init / compileAsync / hidden rendered readiness]
  Prep --> RT
```

Browser tests check identity of the same Canvas across immersive travel/map/video; ordinary information routes unmount the immersive shell as before. No disconnected destination pages or scene-manager rewrite was introduced. Camera cinematic/player/map/movie modes remain in the existing runtime, with fixed registry poses, eased path interpolation and restored ownership.

Initial entry still mounts the persistent hub/tunnel shell, textures and low-detail original stage. Those distant stage assets are critical before first quarry sightline reveal, but some are not needed to draw the exterior entrance. Female/male crowd assets and four-pose preparation are destination-triggered, reused on later visits. Video is created on playback. Optional vendor/rock/hub population blockouts remain resident. Shader/texture preparation and hidden render warm-up are readiness, not network completion alone. No speculative full residency rewrite was performed; initial shell/stage deferral needs a separate measured design preserving first reveal.

Unpublished crowd resources are operation-owned; shared loader/pose caches are not indiscriminately cleared. Unit cancellation ownership and browser delayed-load/interruption/failure/context recovery checks are distinguished below. No JavaScript/Three counter can prove driver VRAM leak freedom. Post-GC JS heap increased from 14.43 to 15.28 MB across ten cycles while Nodes=330/Documents=2 and GL buffers/programs/shaders/VAOs stayed constant. That increase is reported, not dismissed as proof of no JS leak; extended retained-heap profiling remains open.

## Regression tests and lifecycle measurements

`npm run test:immersive`: **53 passing tests** (38 existing +15 new). `npm run test:immersive:browser`: **8 groups passing**, including native held-key/focus interactions with injected editable fixtures, actual touch input in portrait emulation, fresh-session click/Enter, reduced motion, map resize/finite attributes, playback anchor, boundary Stay/rearm, navbar/reload/direct URL/history and Canvas identity. Fresh entrance runtime activation → local took **{timing:.1f} ms**. Fixture forms are DOM input tests; no payment/contact submission was performed.

Initial browser failures were harness defects: action wall time included Playwright click waiting before actual activation, and a nominal fresh-entry test retained a completed-entry history marker. The corrected invariant measures actual runtime activation and uses a genuinely fresh browser context. Initial results remain available: {link('raw/browser-initial/results.json')} / {link('raw/browser-initial.log')}. Old boundary strict float equality is now 1e-6 m finite geometry tolerance; restoration is sampled at activation rather than before remaining inertia; movement tests wait for actual clearance/yaw, not fixed short sleeps. No actual allocation/focus assertions were removed.

Ten completed public playback/return cycles include five normal Exit+return and five navigation interruptions, then early exit, actual media-ended via near-end seek, controlled stale play rejection, failed transfer, recovery playback and SPA unmount. This is ten full **playback/return cycles**, not ten full-length screenings. Seek-generated native `ended` separately verifies completion. Settled counters must plateau from the second cycle onward; leaks are judged after disposal/render settlement, not by removing a React node.

| Cycle | Exit method | Start-to-playing ms | Three textures | Tracked GL textures | Three geometries | GL programs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(alloc)}

Raw allocations, program/shader/geometry statistics, media state, post-GC JS metrics and bounded UUID traces: {link('raw/resource-results.json')}. Before trace: {link('raw/baseline-video-trace.json')}. Baseline untraced plateau is retained: {link('raw/baseline-media-cycles.json')}. Driver memory bytes are unavailable. `activeTextureBytesEstimate` is image dimensions × RGBA × nominal mip factor, not measured GPU memory; `activeGeometryBytes` is deduplicated scene CPU array-buffer bytes, not driver allocations. Dispose trace sampler counts describe the previous completed draw; detachment earlier in a frame can leave that snapshot at three. The post-render disposed-sampler reuse event and settled allocations are the relevant checks. Stable counters are bounded evidence of application ownership, not a universal VRAM certification. Context-loss runs are excluded from create-minus-delete comparisons.

## Actual before/after performance

Same cloud host, Chromium 151.0.7922.173, Debian 13.6/Linux 6.18.44, AMD EPYC 9V74 host, cgroup 2 CPU cores/8 GiB, **SwiftShader software rendering**, no physical GPU. JavaScript `os.cpus()` count in raw logs is not the CPU quota. Functional/performance comparison uses 1366×900 requested/effective DPR .25 and unchanged adaptive quality settings; tier varies as logged. One browser at a time, cache enabled, no recording/screenshots/CPU throttle during timed windows. Loop samples are filtered to rendered frames; average FPS is rendered frames divided by complete action window (which can include cover/waiting), with cadence FPS also in raw data. Reported percentiles are rendered-loop intervals, not GPU execution time. Tail estimates for short windows are noisy; no repeated statistical performance claim is made.

Cold landing total browser ResourceTiming transfer (document + subresources): **{network_before:,} → {network_after:,} bytes** ({(network_before-network_after)/network_before*100:.2f}% reduction). Document-only and entry timing, each URL/transfer/duration and long tasks remain in raw files. ResourceTiming transfer can omit opaque cross-origin bytes; later rows contain cumulative resource entries, not per-window incremental transfer totals. The 404 preload removal is the narrow loading improvement; stage/lighting/quality have not been sacrificed for benchmark results.

| Revision | Window | Action ms | Avg rendered FPS | p50 ms | p95 ms | p99 ms | Max stall ms | >100 ms intervals | Draw calls | Triangles | Textures | Geometries | DPR | Quality tier |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Raw samples / readiness prep / phases / memory / long tasks: {link('raw/baseline-performance.json')} and {link('raw/after-performance.json')}. Separate native-DPR1 adaptive-quality diagnostic: {link('raw/native-dpr1-profile.json')}; it is **not** comparable to the .25 DPR run. No 60 FPS physical-device or Bruno-Simon-level smoothness claim is made. Software-frame stalls remain visible even when cinematic time is correct. The user’s Intel UHD 620 laptop, modern iPhone and mainstream Android are unavailable; their acceptance is **UNVERIFIED**. See {link('PHYSICAL-DEVICE-PROCEDURE.md')} for reproducible hardware validation.

## Builds, commands, failures and remaining acceptance

Production build and TypeScript checks pass: {link('raw/build-final.log')} / {link('raw/typecheck-final.log')}. Build emits existing repository lint warnings; unrelated warning cleanup was intentionally avoided. Pure payment tests (13) and event catalog tests (4) pass without live service mutations; standalone lint passes with existing warnings. Unit results: {link('raw/runtime-tests-final.log')}. Full command/test ledger and browser suites: {link('raw/commands.json')}, {link('raw/remaining-commands.json')}, {link('raw/extra-checks.json')}, {link('raw/browser.log')}, {link('raw/navigation.log')}, {link('raw/resources.log')}, {link('raw/edges-and-media.json')}, {link('raw/interruption.json')}. One added gap test initially hit exact 7.2-second floating-point accumulation; it now advances past the endpoint by one valid frame, with the original failing log retained. Initial diagnostic type error (`Object3D` supplied where `Scene` required) and initial fake-video fixture failures were corrected; their initial logs remain. This is not a claim every historical failed assertion was an application regression.

Synthetic blur/freeze/focus and runtime background suspension tests pass, but a headless context that never becomes `document.hidden` cannot certify actual mobile/browser background recovery. Controlled delayed/aborted downloads, stale navigation, playback failure and WebGL loss/restoration are scoped tests, not exhaustive device/network failure certification. Real payments/admin integrations and external production services were not exercised or altered. All browser API mutations are blocked by the harness; pure existing payment tests may be run separately without live data.

## Blender pipeline and production-art readiness

Current environment has Blender **4.3.2**, unlike historical environment-specific statements in the pipeline document. A separate, non-final one-metre cube was authored/exported with metric units, glTF Y-up, UVs and PBR material: {link('blender/blender-smoke/one-metre-cube.blend')}, {link('blender/blender-smoke/one-metre-cube.glb')} and {link('blender/blender-smoke/manifest.json')}. No original stage generator was run. The browser probe imports the existing `BlenderAsset` loader, measures scale/Y ground placement/UV/material/raycast and tests repeated mount/cache ownership: {link('raw/blender-browser.log')} and {link('blender/loader-smoke.png')}. Actual results and any limitations are recorded in the final result supplement below. Smoke asset is not inserted into the approved quarry.

Existing [environment pipeline contract](gullyverse-environment-pipeline.md) remains: metre-based master scene, separate critical shell/destination anchors/optional dressing, registry-compatible empties, offline transform extraction, owned scene instances/shared cache, texture initialization, compileAsync and hidden rendered readiness. Use segmentable rocks, shared atlases/instancing and explicitly selected LODs. PBR base color sRGB, normal/roughness/AO linear; authored UVs and graffiti/decal atlas. KTX2/Basis/Meshopt/Draco require local decoders and real-device tradeoff tests: none are newly installed or falsely claimed ready. Blender logs a missing optional Draco library, but the uncompressed GLB exports successfully. Khronos glTF Validator reports zero errors/warnings and one informational unused-UV notice: {link('raw/gltf-validator.json')}. Raycast smoke verifies basic collision geometry; imported GLBs still need explicit collision polygon/anchor export, not automatic runtime collision registration.

**Provisional budgets for the next approved pilot, not measured final-art limits:** one ≤2 MB compressed GLB, ≤50k visible triangles and ≤2 materials; no new lights/postprocessing. Incremental shell budgets to test: medium ≤150k visible triangles/low ≤75k, ≤20 extra draw calls, shared 1k–2k atlases with low 512–1k variants; optional dressing separately loaded. Inventory actual decoded texture bytes and benchmark alongside the existing ~1M-triangle stage crowd before approving aggregate budgets. Export LOD0/1/2 per rock segment with shared materials, remove hidden faces and preserve silhouette; compression/LOD policy must be validated on physical integrated GPU/mobile before full production.

Remaining production art: authored irregular shell/tunnel/exterior, UV/PBR rock/ground, authentic graffiti atlas, plausible scaffold joints/cables/weathering, stalls/dressing and consistent population. These are not runtime stabilization work. Preserve the user-approved positions and atmosphere during each pilot. No final asset pass has begun.

## Exact phase-only source changes

The following existed at baseline and changed in this delivery; earlier uncommitted visual edits in other files are **not** attributed to this task:

{changes}

New source/test files (report scripts and evidence live separately under the output directory):

{new}

`package.json` changes only test command discovery/browser runner. No dependency or lockfile upgrade. Payment/admin code, assets and current spatial/lighting configurations are checked in the hash inventory. Final user review is required for world composition and any authorization to begin production Blender work.
'''
(root/'docs/gullyverse-stage-1-final-acceptance.md').write_text(text)
print('Acceptance report generated; append measured final classifications/results supplement before delivery.')
