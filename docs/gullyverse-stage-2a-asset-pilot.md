# Gullyverse Stage 2A — reversible Blender rock pilot

Completed 2026-10-12; browser measurements captured October 11, 2026. This is one bounded authoring/engineering pilot. The user has already approved the current visual/spatial website baseline. No further Stage 1 visual gate applies. Physical benchmarks are **PENDING**, and do not block asset authoring. New asset visual review is required before Stage 2B or permanent substitution.

## Outcome and acceptance

The editable rock master, three runtime detail levels, original PBR maps, collision proxy, isolated preview, matched captures and resource measurements exist. **No original production source/configuration/asset was modified.** No commit, push or deployment occurred. The pilot is absent from the production route and default public journey (zero pilot asset requests in the fresh smoke test).

| Category | Result | Evidence / limit |
|---|---|---|
| Approved baseline preservation | PASS | 664 original source/config/assets, 243 pre-existing untracked review files, 4 prior docs and 126 historical audit artifacts match their recorded hashes |
| Blender authoring/export | PASS | Blender 4.3.2, editable master; five GLBs validate with zero errors/warnings |
| Original material/geometry construction | PASS | New geological field, fractured/stratified closed mesh and unique UV maps; no photo texture extraction |
| Production-quality geological realism | PARTIAL | Meaningful morphology/material detail, but long bands and slab edges can look regular/rounded; close-up grain, fracture bevels and cap mapping need human review/refinement |
| Exact production appearance | PASS for preservation | Production files/assets unchanged; new object exists only in isolated opt-in preview |
| Hub-lighting integration | PASS for technical rendering; asset appearance for review | Actual unchanged HubScene context and matched ACES/exposure; Aftermovie-global lighting has not been previewed on this new segment |
| LOD/proxy validity | PASS for data; PARTIAL for final policy | Three explicit LODs, valid enclosed proxy and raycast; no automatic screen-space LOD policy or production movement substitution |
| Pilot repeated resource lifecycle | PASS | 15 cycles plateau; dedicated cache retirement returns counters to ground-only baseline |
| Existing runtime regressions | PASS within tested browser scope | 57 unit checks, 8 browser groups and additional resource/recovery/fallback journeys |
| Home delay | PARTIAL | Reproduced and attributed into phases on software renderer; no confirmed narrow application fix; physical reproduction pending |
| Experimental transfer target | NOT MET | Combined GLB 4.13 MB exceeds older provisional 2 MB target; not a validated hardware acceptance limit |
| Physical laptop/iPhone/Android performance | UNVERIFIED / PENDING | No physical devices attached; SwiftShader results must not be used as hardware FPS limits |
| Full quarry replacement readiness | UNVERIFIED | One small segment does not establish world-scale budget, seamless joins or LOD policy |

[Browse the actual screenshot gallery](../reports/stage-2a-asset-pilot-2026-10-11/gallery.html). [Hardware profile](../reports/stage-2a-asset-pilot-2026-10-11/raw/hardware-profile.json), [integrity evidence](../reports/stage-2a-asset-pilot-2026-10-11/raw/integrity.json), [complete new-file inventory](../reports/stage-2a-asset-pilot-2026-10-11/raw/files-added.json).

## 1. Exact starting baseline and preservation

Branch **codex/navigation-board**, HEAD **e3dbbc233f1f12f5e4d96333db3b797e75da4760**. Starting staged and unstaged diffs were empty. Existing untracked items were `gullyverse-final-review-evidence.zip` and `reports/current-final-review-2026-10-11/` (243 files). Their origin is not inferred; they remain untouched.

A non-destructive source/config/asset snapshot was created before authoring: `reports/stage-2a-asset-pilot-2026-10-11/backup/approved-source-assets.tar.gz` (476,991,769 bytes), plus empty starting staged/unstaged patches and source/untracked SHA-256 indices. No credential/environment files were copied. The large local backup is deliberately excluded from the review ZIP; the evidence indices and final integrity results are included. HEAD/branch and empty tracked diff remain unchanged. All pilot code/assets are new files. Existing ignored documentation remains preserved; new report creation is not an automatic commit.

The supplied October 11 review, visual baseline, reference README and environment pipeline were read. Copies are included as [historical text context](../reports/stage-2a-asset-pilot-2026-10-11/historical/gullyverse-current-final-review.txt), [visual baseline](../reports/stage-2a-asset-pilot-2026-10-11/historical/gullyverse-current-visual-baseline.txt), [pipeline](../reports/stage-2a-asset-pilot-2026-10-11/historical/gullyverse-environment-pipeline.txt) and [reference instructions](../reports/stage-2a-asset-pilot-2026-10-11/historical/README.txt). Their old Blender-unavailable note and any additional Stage 1 approval request are superseded by actual Blender availability and the user's explicit approval.

Locked production facts retained: quarry registry footprint 97.8 × 123.5 m, the actual current 25 procedural rock masses and generated terrain; scaffold 24 × 14.5 × 3.4 m at [0,0,-70]; approved GULLYVERSE/sign hierarchy; Team/Contact second-stall positions; stage anchor [-12,0,-134.3]. Original stage GLB, original male/female crowd identities, baked poses, trusses/LED/video, restored stage floor and surroundings, tunnel geometry/bend/reveal, walking bounds/gates/menu, map cameras and navigation registry are untouched. The current lighting and fog are preserved even where older reports suggested changes. No payment/admin source or production data was touched.

Relevant unchanged source: `components/immersive/HubScene.tsx`, `blockoutGeometry.ts`, `world.ts`, `runtime.ts`, `navigation.ts`, `rendering.tsx`, `AftermovieScene.tsx`, `AftermovieEnvironment.tsx`, `WorldOverlays.tsx`, `mapProjection.ts`, and `components/three/BlenderAsset.tsx`. The original stage remains `public/models/breeze/aftermovie-stage.glb`; all existing public assets are hash-checked in the source index.

## 2. Hardware and measurement boundaries

Debian GNU/Linux 13, Linux 6.18.44, KVM VM exposing three AMD EPYC 9V74 vCPUs; Chromium **151.0.7922.173**. Renderer: ANGLE Vulkan SwiftShader Device (Subzero). `/dev/dri` and `/dev/nvidia0` were unavailable, including after the workspace resumed on October 12. No physical integrated-GPU laptop, iPhone or Android was accessible. These are **software-rendering diagnostic results**, not ordinary laptop/phone FPS. No GPU timer or reliable driver VRAM reading was available.

Pilot measurements use actual rendered frame deltas, 8-second windows after six covered warm draws, desktop 1366×900, fixed effective DPR 0.5, no CPU/network throttling, no recording/screenshots during measured windows. Three interleaved baseline/LOD0 windows reduce ordering bias but are short and not sustained/thermal certification. Actual screenshots also include DPR1 desktop and 390×844 portrait-aspect views. The preview has fixed quality and caps DPR at 1.25; Hub context is `quality=3`. Production regression requests use DPR0.25 with per-snapshot adaptive tier. Team/Contact's separate renderer settings override that request with a minimum DPR1; this explains why their costs cannot be compared directly with the isolated pilot windows.

Physical test procedure: [local operator checklist](../reports/stage-2a-asset-pilot-2026-10-11/PHYSICAL-DEVICE-PROCEDURE.md). Unmeasured hardware profiles remain open; they do not block bounded authoring. Do not compare these windows directly with historic Intel UHD 620 measurements.

## 3. Team/Contact → Home delay investigation

The October 11 report's roughly 30.5s/24.4s action windows lacked a DOM click timestamp. Fresh profiling separates Playwright actionability time from actual click → local hub. Team/Contact use separate page renderers; leaving them unmounts that Canvas, and returning creates the immersive Canvas. This differs from the persistent root ↔ Aftermovie journey. Team's `BackstageCorridor.tsx` uses DPR [1,1.5], shadows and Bloom/Vignette/Noise; Contact also uses its native page renderer. Existing appearance/settings were not tuned to SwiftShader.

The primary diagnostic trial used real directional SPA arrival to each webpage, then its actual Navbar Home link. Browser-only history instrumentation appended `diagnostics` to the Home query to observe existing preparation events before Canvas mount; it did not change route destinations or production files. Source GLTF loader caches survive this SPA trial.

| SPA return | Before actual click: automation wait | Click → Canvas removal | Click → new context | Context → first draw | First draw → arrival | Arrival → local | Actual click → local |
|---|---:|---:|---:|---:|---:|---:|---:|
| /team | 18.119s | 6.608s | 6.857s | 2.307s | 2.350s | 0.662s | 12.176s |
| /get-in-touch | 13.537s | 4.453s | 4.639s | 1.802s | 2.635s | 0.690s | 9.766s |


These milestones sum only along their sequential intervals; click → Canvas removal includes route scheduling and outstanding main-thread/renderer work, **not a measured teardown-only duration**. The source renderer loses its context later. The returned Hub had no new stage GLB network request, so repeat stage transfer is not responsible for this SPA delay.

Existing diagnostic spans: Team texture initialization **51.7ms**, `compileAsync` **40.5ms**, readiness-render window **2295.5ms**; Contact **63.3ms / 28.1ms / 2530.3ms**. Those spans are contained in the larger context-to-arrival intervals and must not be added twice. The readiness gate performs 12 actual covered warm renders; the broad GL hook also sees preparation draws. Largest post-click long task: Team **2303ms**, Contact **1512ms**. GPU completion/driver synchronization is not isolated by JavaScript GL-call duration.

A separate full-document direct-Team/Contact trial (loader cache reset by reload) measured actual click → local DOM **12.093s / 10.742s**, and automation waits before click **19.634s / 12.032s**. Its results are separate from the SPA trial. [SPA phase summary](../reports/stage-2a-asset-pilot-2026-10-11/raw/home-spa-summary.json), [full SPA events](../reports/stage-2a-asset-pilot-2026-10-11/raw/home-spa-diagnostics-profile.json), [direct-page summary](../reports/stage-2a-asset-pilot-2026-10-11/raw/home-delay-summary.json), [direct-page raw](../reports/stage-2a-asset-pilot-2026-10-11/raw/home-delay-profile.json).

Findings establish multiple software-renderer/scheduling costs and Canvas recreation, not an infinite coordinator wait or a verified physical-device defect. No narrowly proven application bug was found, so **no production fix was made**. First reproduce on a physical GPU with actual click timestamps. If the same post-click delay remains, investigate the native renderer's outstanding work/unmount boundary and readiness cost independently; preserving the renderer across ordinary routes would be a larger architecture change and is outside this pilot. Do not remove the readiness cover just to shorten the measurement.

## 4. Editable asset and reproducible authoring/export

Source: [quarry-rock-pilot.blend](../assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend) (**10,114,024 bytes**). Runtime: [combined GLB](../public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb) (**4,127,092 bytes**). [Source README and workflow](../assets-source/gullyverse/rock-pilot-2a/README.md), [anchor/LOD metadata](../assets-source/gullyverse/rock-pilot-2a/asset-manifest.json), [inventory and hashes](../reports/stage-2a-asset-pilot-2026-10-11/raw/asset-inventory.json).

Original deterministic morphology uses seed 20271011, irregular stratified layers, 16 angular fault slabs, eight interrupted fissures, recess/bevel boundaries, nonperiodic weathering and an irregular crown. Custom front, side and back surfaces form a closed mesh; this is not a stock primitive with only a noisy shader. Small material grain is encoded in original tangent normal maps. No third-party photograph was sampled or pasted into textures. Quarry photographs were used as morphology inspiration only.

Blender **4.3.2** is installed and successfully authored, exported and reopened the master. Collections retain `MASTER_SCULPT`, `RUNTIME_LODS`, `COLLISION_PROXY` and named `pilot_anchor`. Metres, identity object scale/rotation, Blender Z-up/front -Y → glTF Y-up/front +Z. Bottom-centre origin [0,0,0]. Approximate source extent **12.075 × 10.017 × 4.106 m** (width/height/depth; per-LOD bounds differ slightly). Editable master, all runtime LODs and proxy are closed, zero non-manifold edges, positive signed volume.

| Asset | Triangles | Source vertices | File bytes | Use |
|---|---:|---:|---:|---|
| Master sculpt | 100,992 | 50,498 | 10,114,024 (.blend incl. packed images) | Editable source, not runtime |
| [LOD0](../public/models/gullyverse/pilot-rock/rock-lod0.glb) | 32,616 | 16,310 | 3,616,000 | Near candidate |
| [LOD1](../public/models/gullyverse/pilot-rock/rock-lod1.glb) | 10,440 | 5,222 | 2,892,436 | Medium candidate |
| [LOD2](../public/models/gullyverse/pilot-rock/rock-lod2.glb) | 2,820 | 1,412 | 2,627,500 | Far candidate |
| [Collision proxy](../public/models/gullyverse/pilot-rock/rock-collision.glb) | 12 | 8 | 1,824 | Conservative box hull; isolated raycast |

Source vertices are not necessarily glTF vertices: UV/normal seams split exported attributes. The proxy conservatively encloses all runtime vertices. Raycast hit is recorded at [44.74449,5,-104]. It is not installed into production walking/collision boundaries.

Unique front UVs, lower-density side/back UV regions; no intentionally repeating tile atlas. Runtime normals/tangents/positions/UVs are finite; normal lengths ~1, max normal·tangent ≤0.00013. Khronos validator: **all five GLBs, zero errors and warnings**. [Validation](../reports/stage-2a-asset-pilot-2026-10-11/raw/glTF-validator.json), [fresh Blender master inspection](../reports/stage-2a-asset-pilot-2026-10-11/raw/master-inspection.json).

LOD reconstruction vs master using the shared front UV bilinear field (not Hausdorff or projected error): LOD0 RMS **0.0273m**, p95 **0.0612m**, max **0.2742m**; LOD1 **0.0450 / 0.1066 / 0.4880m**; LOD2 **0.0674 / 0.1586 / 0.5525m**. Maximum errors occur at narrow/high-contrast fractures. Do not infer seamless LOD switching or appropriate distances from mean error; a screen-space policy and manual switch review remain future work.

Reproduce from repository root:

```sh
python3 scripts/blender/rock_pilot_materials.py
blender --background --python scripts/blender/author_rock_pilot_2a.py
blender --background --python scripts/blender/inspect_rock_pilot_2a.py
node reports/stage-2a-asset-pilot-2026-10-11/scripts/preview-server.mjs
```

Ordinary Python used numpy 2.3.5 and Pillow 12.3.0; Blender supplies its own numpy. [Geological field](../scripts/blender/rock_pilot_surface.py), [map generation](../scripts/blender/rock_pilot_materials.py), [master/export script](../scripts/blender/author_rock_pilot_2a.py), [inspection script](../scripts/blender/inspect_rock_pilot_2a.py). These new scripts write only pilot directories. Do not repurpose the old all-stage generator: it can overwrite original stage assets. No package manifest/dependency or asset loader was changed.

## 5. PBR textures and limitations

Eight packed/source files are retained in the editable master/source directory: unique **2048px** base/normal/roughness/AO maps plus **1024px** runtime versions. Runtime base colour is sRGB JPEG; tangent normal is linear OpenGL +Y PNG, normal scale 0.7; packed linear ORM is AO-red/roughness-green/metallic-blue, metallic zero. Roughness approximately 0.76–0.99. No clearcoat/plastic gloss, displacement shader, realtime shadows or postprocessing was added.

Combined export embeds one visual stone material, three maps: normal PNG **1,388,991 B**, ORM PNG **893,824 B**, base JPEG **221,162 B**. Collision-only default material is implicit and hidden. Runtime stone is currently double-sided; testing back-face culling is a future bounded experiment, not a claimed optimization. At 12m face width, 1024px density is modest for very close hero views; side/back caps are not final hero faces.

Estimated decoded RGBA8 + full mip-chain payload is **16 MiB per unique three-map set**, excluding driver overhead/alignment, image decode copies, shared stage resources and framebuffer allocations. This is an estimate, **not VRAM measured**. JPEG helps network size, not decoded GPU payload. No Draco, Meshopt or KTX2 decoder/compression was assumed or configured. The current GLB is larger than the old proposed 2MB pilot target; report that shortfall rather than silently treating a provisional target as validated hardware budget.

## 6. Isolated integration, matched lighting and visual findings

[Preview source](../reports/stage-2a-asset-pilot-2026-10-11/preview/pilot.tsx.txt), [compiled standalone viewer](../reports/stage-2a-asset-pilot-2026-10-11/preview/pilot.js), [portable local server](../reports/stage-2a-asset-pilot-2026-10-11/preview/serve-preview.py). No production route or default import is added. The viewer imports the unchanged R3F `BlenderAsset`/GLTFLoader pipeline. Combined GLB is parsed once and cloned with shared geometry/material/texture cache. Exactly one named LOD is visible; `Rock_Collision` is hidden. **glTF does not encode visibility:** do not mount the unfiltered combined GLB in production, or all LODs overlap. Separate LOD GLBs are alternatives but loading all three duplicates texture caches.

Isolated inspection anchor [47.4,0,-104], yaw -π/2, is outside walking zones and not registered in production. Context mode renders unchanged `HubScene` behind the opt-in rock; original procedural wall remains present. No quarry silhouette, world registry, bounds, cameras, scaffold, stage or global lighting was replaced. Existing wall comparison crops exact original rock i7 vertex attributes without scaling/repositioning; it is much taller than this single 10m patch. Matched cameras are a material/detail comparison, **not matched silhouettes or a full wall-replacement proof**.

Exact current Hub global settings: background/fog #737d87, fog 205–520m; hemisphere #a9bfd4/#8a8274 intensity 1.35; directional [-70,37,-145] #efd0a4 intensity 1.35; scaffold practical point [0,9.75,-67.4] #ffc681 intensity 42, range21, decay2. ACES tone mapping, exposure1, output sRGB, no shadows. Medium camera [31,5.6,-98] → [46,5,-104], close [41.1,5.4,-103.4] → [45.9,5.4,-104], long [3,7,-87] → [46,5,-104], FOV58. Left/right-angle and portrait camera quaternions are in raw capture metadata. Preview is an inspection camera, not a modification of approved production composition.

Actual comparison evidence: [baseline wall](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/14-dpr1-existing-wall.png) vs [pilot medium DPR1](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/15-dpr1-pilot-medium.png); [close material DPR1](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/16-dpr1-material-close.png); [unchanged world context](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/17-dpr1-existing-world-context.png) vs [opt-in LOD0 context](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/18-dpr1-pilot-world-context.png); [left angle](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/06-pilot-angle-left.png), [right angle](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/07-pilot-angle-right.png); [long LOD2](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/05-pilot-long-lod2.png); [portrait LOD1](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/12-mobile-pilot.png). The gallery includes 18 final captures, exploratory captures and failure evidence; full PNG resolution is retained. Screenshots carry desktop/mobile-aspect labels, exact camera/quaternion/FOV/viewport/DPR and LOD metadata. Portrait captures are not physical-device benchmarks.

The candidate has layered relief, interrupted fault cracks, irregular crown and matte mineral colour; normals change response across angle views without special lights. It is darker than the existing flat vertex-colour rocks because of its albedo/AO/normals, not a global exposure change. Some bands and fault slabs still read like regular rounded blocks at close range; grain/UV density and long horizontal repetitions require asset-only review/refinement. Fracture sides can show LOD simplification and back caps need further work if made visible. **Photorealism is not established by these screenshots.** Hub-global lighting was verified; the separate darker Aftermovie-global mode is a remaining integration check for any future segment placed near the stage. This is not a reason to alter approved stage lighting.

## 7. Performance comparison and loading

| Window | FPS | p50 / p95 / p99 (ms) | Max (ms) | Calls | Visible triangles |
|---|---:|---|---:|---:|---:|
| baseline-medium-1 | 22.73 | 33.4 / 64.1 / 69.9 | 73.5 | 2 | 11,300 |
| pilot-lod0-medium-1 | 9.27 | 107.3 / 143.7 / 148.7 | 155.0 | 2 | 43,880 |
| baseline-medium-2 | 21.64 | 39.5 / 68.3 / 71.9 | 79.6 | 2 | 11,300 |
| pilot-lod0-medium-2 | 9.49 | 104.9 / 138.9 / 153.5 | 155.6 | 2 | 43,880 |
| baseline-medium-3 | 23.08 | 31.9 / 63.0 / 69.7 | 72.1 | 2 | 11,300 |
| pilot-lod0-medium-3 | 8.96 | 107.9 / 142.0 / 152.8 | 156.2 | 2 | 43,880 |
| pilot-lod1-medium | 12.84 | 84.3 / 94.1 / 95.5 | 100.5 | 2 | 21,704 |
| pilot-lod2-long | 27.43 | 28.1 / 62.0 / 64.8 | 69.7 | 2 | 14,084 |
| pilot-lod2-medium-matched | 15.07 | 72.9 / 85.7 / 88.4 | 92.7 | 2 | 14,084 |
| baseline-long-matched | 30.59 | 24.4 / 57.3 / 60.3 | 62.2 | 2 | 11,300 |
| original-HubScene-context-medium | 9.24 | 106.1 / 141.3 / 151.3 | 154.5 | 11 | 51,826 |
| pilot-lod0-HubScene-context-medium | 5.37 | 192.7 / 216.0 / 253.1 | 255.8 | 12 | 84,442 |


[Raw windows and rendered samples](../reports/stage-2a-asset-pilot-2026-10-11/raw/pilot-performance.json), [additional matched windows](../reports/stage-2a-asset-pilot-2026-10-11/raw/extra-preview.json), [frame-time plot](../reports/stage-2a-asset-pilot-2026-10-11/frame-times.png). Baseline+ground is 11,300 triangles (36 old wall +11,264 ground), 2 calls. Pilot LOD0+ground: 43,880 triangles, 2 calls; LOD1 21,704; LOD2 14,084. World context baseline/pilot: 51,826/84,442 triangles and 11/12 calls. These are **fragment/HubScene inspection renders, not the complete stage/crowd benchmark**. Existing production Stage counts in regression evidence are about 1.02M triangles/115 calls at quality3; the rock was never installed there.

The same-camera LOD0 makes this software renderer slower (three paired baseline FPS 21.6–23.1 vs 9.0–9.5); it is not a demonstrated production performance improvement. LOD2 at long distance and baseline long use the same long camera (27.43 vs 30.59 FPS). Do not attribute long-camera improvement over medium solely to LOD; distance changes pixel coverage. Context pair 9.24 vs 5.37 FPS demonstrates additional cost on SwiftShader; it does not certify physical cost. No sustained 60 FPS claim is supported.

Minimal cold counters: baseline 1 texture/2 geometries; mounted pilot 4 textures/2 visible geometries. All LODs warm in cache produce 4 GPU geometries incl. ground and 4 textures. Context windows both show 22 textures because the candidate's maps are already cached; this is **not zero additional texture memory**. Measured baseline geometry attribute payload 257,456B; LOD0+ground 1,362,320B; unique combined-cache geometry residency differs. Estimated texture payload including ground 1.33MiB baseline vs 17.33MiB pilot.

Local cache-cold GLB request: body **4,127,092B**, transfer **4,127,392B** incl. headers, duration **19.9ms**. Parse-to-loaded callback **41ms** includes parse/image decoding/scheduling; it is not pure geometry decode. First pilot texture-init CPU submission **17.7ms**, `compileAsync` **14.3ms**; complete six-real-draw covered gate **747.8ms**. These components overlap the total and are not additive. No GPU timer separated texture-upload completion or first render driver work. [Preparation/network records](../reports/stage-2a-asset-pilot-2026-10-11/raw/pilot-resource-lifecycle.json).

The preview gates reveal on async shader preparation and six covered real draws; captures are taken after readiness. No compilation artifact was evident in settled captures, but first-reveal perceptual hitching on physical GPUs remains unverified. Large SwiftShader stalls persist; correct preparation does not imply smooth frame pacing. Asset loading is opt-in: the default production cold transfer receives **zero pilot bytes**. No current-site initial loading optimization was attempted. There is no comparable whole-page before/after network improvement to claim.

## 8. Ownership, repeated mounts and movie preservation

[R3F pilot resource lifecycle](../reports/stage-2a-asset-pilot-2026-10-11/raw/pilot-resource-lifecycle.json), [counter plot](../reports/stage-2a-asset-pilot-2026-10-11/resource-cycles.png). All three LODs were warmed first, then **15 alternating mount/unmount cycles** run with the same dedicated URL/cache. Settled counts plateau throughout: **4 geometries / 4 textures / 3 programs**, with one parse before retirement. Invisible cached LOD resources are intentional bounded residency, not freed merely by removing React nodes.

Pilot clones use the unchanged `BlenderAsset` `dispose={null}` shared-loader contract. Ground geometry/map and cropped original wall geometry are scene-owned and disposed on unmount; shared production GLBs/textures are never cleared. After all pilot consumers were removed and mode was blank, explicit retirement disposed **4 owned geometries, 2 materials, 3 textures and closed 3 unique ImageBitmaps**, then cleared only the dedicated pilot GLTFLoader cache key. Renderer returned to **ground-only 1 geometry / 1 texture / 1 program**; tracked GL texture balance returned to5 including renderer-internal defaults. Subsequent reload succeeds. The disposal function is an isolated diagnostic operator action and must only be called after all consumers have unmounted; it is not a new global production cache-eviction policy.

Driver VRAM was not measured. CPU heap without forced GC is noisy; bounded diagnostics are still retained. JS heap after forced GC in ten actual production movie/return cycles rose from **13.77MiB** to **14.54MiB**, peaked **14.61MiB**, then fell slightly. That small growth includes retained bounded diagnostic/cache data and is not proven leak-free; continued longer-run heap inspection remains useful. All ten settled movie cycles retained **Three.js textures25 / tracked GL textures29 / geometries154**. No repeat monotonic texture growth was reproduced.

Actual movie time advanced before exit. Five cycles used Exit then return; five navigated during active playback. Early exit, real ended event after seeking near completion, stale rejected play promise, failed MP4 transfer/restart and SPA unmount cleanup passed. Movie appearance/material/source/stage/crowd code and assets are unchanged. [Movie lifecycle raw evidence](../reports/stage-2a-asset-pilot-2026-10-11/raw/resource-results.json). This verifies current existing fixes; no input/map/video/navigation subsystem was rewritten.

## 9. Regression checks, failure cases and honest limits

| Check executed | Result | Evidence |
|---|---|---|
| `npm run test:immersive` | 57/57 PASS | [unit log](../reports/stage-2a-asset-pilot-2026-10-11/raw/unit.log) |
| `npm run lint` | Completed; existing warnings retained | [lint log](../reports/stage-2a-asset-pilot-2026-10-11/raw/lint.log) |
| `npm run build` | Production build completed | [build log](../reports/stage-2a-asset-pilot-2026-10-11/raw/build.log) |
| `npx tsc --noEmit --incremental false` | Passed, no output | [typecheck log](../reports/stage-2a-asset-pilot-2026-10-11/raw/typecheck.log) |
| `GULLYVERSE_ARTIFACT_DIR=reports/stage-2a-asset-pilot-2026-10-11/raw/regressions npm run test:immersive:browser` | All 8 groups PASS | [browser results](../reports/stage-2a-asset-pilot-2026-10-11/raw/regressions/results.json), [log](../reports/stage-2a-asset-pilot-2026-10-11/raw/runtime-browser.log) |
| New report-only resources/interruption/production-smoke scripts | Exit0 each; 7+2+2 checks PASS | [commands/durations](../reports/stage-2a-asset-pilot-2026-10-11/raw/remaining-commands.json), [resources](../reports/stage-2a-asset-pilot-2026-10-11/raw/resource-results.json), [interruption](../reports/stage-2a-asset-pilot-2026-10-11/raw/interruption.json), [smoke](../reports/stage-2a-asset-pilot-2026-10-11/raw/production-smoke.json) |
| Blender master + all 5 GLBs | Validated | [inspection log](../reports/stage-2a-asset-pilot-2026-10-11/raw/master-inspection.log), [validator](../reports/stage-2a-asset-pilot-2026-10-11/raw/glTF-validator.json) |

The first four commands were a recorded multiline shell pipeline; overall status0 and individual success output are retained, but separate per-command exit codes were not captured for its earlier commands. The browser and remaining script statuses were captured separately. Build used command-scoped inert local Supabase placeholders; no environment file/production database was changed or contacted. New preview TSX is separate from the production tsconfig; it was built and exercised in actual Chromium rather than claiming production type checking covers it.

Real public journey: fresh landing click → tunnel → Hub → held W under scaffold through Aftermovie directional gate → original Stage → boundary menu → Return → Hub → Map → Aftermovie, same immersive Canvas, zero pilot URL requests. Browser groups also cover editable focus/held-key release/native typing, lost keyup/stale repeat, blur/freeze, interruption, map finite SVG/resize/destination selection, activation-time movie restoration/rapid restart, boundary Stay/Esc/hysteresis, browser Back/Forward, Navbar Home/reload/direct URL/session policy, touch-emulated entry/movement/map and reduced motion. Entrance diagnostic activation→local **7244.7ms** (automation window9224ms), largest sampled frame183.8ms; wall-clock pacing does not prove physical visual smoothness. Real hidden-tab visibility was not established by every automation check; do not promote emulated freeze to full browser-background/mobile suspension acceptance.

Additional fault injection: crowd loading delayed8s then public return cancels stale serial safely; actual WebGL context loss during movie restores saved walking pose under cover; failed critical stage GLB produces native fallback (zero Canvas/one native movie). [Native fallback capture](../reports/stage-2a-asset-pilot-2026-10-11/screenshots/critical-asset-native-fallback.png). The bundled Python localhost viewer was separately smoke-tested after the October 12 workspace resume: [portable viewer result](../reports/stage-2a-asset-pilot-2026-10-11/raw/portable-preview-smoke.json). This is a serving/loading check, not a replacement for October 11 frame-time samples. These checks are browser evidence, not replacement claims from unit tests.

New harness failures are retained transparently: initial profiler accessed a not-yet-ready diagnostic object; a second probe missed the aria-labelled Home click; an initial SPA script syntax defect; preview world-context font URL decoding defect. Only **new report/preview tooling** was corrected. Eight valid performance windows from the first preview pass were retained; later capture/resource portions reran after correcting that server. [First-pass record](../reports/stage-2a-asset-pilot-2026-10-11/raw/pilot-performance-first-pass.json), raw logs/failed profiler JSON are included. A report-generation helper also initially confused the Git status string with a check result, then encountered differing raw-window schemas; these were new reporting-tool errors, corrected without changing application data. No original application defect was silently fixed. There is no known new production functional regression in the tested scope; physical GPU/mobile, sustained thermal performance and driver VRAM remain unverified.

## 10. Scaling constraints and provisional Stage 2B budgets

These are experiment proposals, not hardware-certified limits. A unique 1024px PBR triplet costs ~16MiB decoded with mips. Twenty unique sets would be ~**320MiB** before existing stage/crowd/framebuffers/CPU decode copies. Twenty LOD0 segments would add **652,320 triangles**; one segment passing does not justify that residency. GLB transfer and texel density already need tradeoffs. Same-material clones can share data, but this preview does not batch all distinct meshes into instances and draw calls grow with visible meshes. Combined LODs share textures but can retain all warmed geometry; separate GLB loading risks duplicated texture sets.

For the next bounded experiment: retain one material/map set per geological family where feasible; start with ≤2 close LOD0 segments (~65ktri), ≤6 mid LOD1 (~63k) and ≤8 far LOD2 (~23k), at most16 additional visible stone draws before measured batching work. Start with ≤4 resident unique 1024px map sets (~64MiB estimated), target ordinary GLB transfer toward ≤2MB/segment and revise after measured quality/codec tradeoffs. These caps are deliberately provisional and must include the already-resident original stage/crowd costs. Author new assets incrementally rather than preload every high-detail wall at landing.

Before any compression proposal, independently validate required DRACO/Meshopt/KTX2 loader support, decode/upload latency, visual fidelity and failures; none is currently enabled by this pilot. Choose LOD distances from matched screen-space fracture/silhouette evidence, with hysteresis; preserve anchor/collision contracts and existing navigation. Segment joins and roof silhouette must be reviewed without altering approved world dimensions.

## 11. Remaining risks and Stage 2B recommendation

**Required before a permanent substitution:** review this new rock's close/medium/long geology, improve slab/bedding regularity if requested, inspect cap UVs, measure real-screen LOD switching, test the current Stage-global lighting if the asset will be visible there, and confirm no seam/occlusion or collision-envelope change at a chosen existing anchor. The current combined GLB requires explicit LOD filtering. Its 4.13MB size/16MiB material-set estimate are not validated final budgets.

**Useful in parallel with bounded authoring:** physical laptop/iPhone/Android baseline, actual-click Team/Contact reproduction, longer heap/profile sessions, isolated compression and culling experiments. Unavailable physical hardware is reported as pending and does not prohibit further bounded asset authoring once the new candidate is reviewed.

**Production art still untouched:** full quarry walls, rocky entrance/tunnel refinements, final graffiti atlases, ground detail, scaffold connection/detail passes, stalls/population and stage surroundings. Existing procedural blockout/stalls/capsule Hub people remain the approved baseline; original concert assets are retained. Do not restart those areas or reinterpret old lighting recommendations as authorization.

Recommendation: the **technical authoring/export/isolated loading contract is usable**, but this candidate is **not declared a finished photorealistic production wall**. Stop here for human review of the new rock segment. If approved, Stage 2B can begin with one reversible non-critical wall-panel trial at an existing anchor, seam/LOD review and measured residency, while physical benchmarks are collected in parallel. No full-quarry replacement, final entrance/tunnel production, extra destinations or permanent placement is authorized by this pilot. Stage 1 visual approval is already complete and is not requested again.

## 12. Deliverable paths and exact source changes

Only additions: four `scripts/blender/*pilot*.py` authoring/inspection scripts; `assets-source/gullyverse/rock-pilot-2a/` editable master/maps/metadata/README; `public/models/gullyverse/pilot-rock/` five GLBs/manifest; this document; `reports/stage-2a-asset-pilot-2026-10-11/` backup, isolated preview, profiling scripts, raw results, gallery and captures; root review ZIP. [Enumerated new files](../reports/stage-2a-asset-pilot-2026-10-11/raw/files-added.json). No existing source, shader, loader, light, camera, stage/crowd texture/video, navigation registry or unrelated functionality was changed.

The self-contained `gullyverse-stage-2a-asset-pilot-review.zip` includes the report, all new captures/metadata, raw timing/lifecycle/test evidence, reference copies, portable bundled preview, editable master and exported assets, maps and reproducible authoring scripts. It excludes the large local backup, credentials, Python caches and automatic `.blend1` draft backup. Open `reports/stage-2a-asset-pilot-2026-10-11/gallery.html` after extraction. `PACKAGE-MANIFEST.json` indexes payload SHA-256; package verification is recorded separately. Original historical audit and prior review ZIP are preserved.
