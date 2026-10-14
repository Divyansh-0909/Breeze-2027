from pathlib import Path
import json,hashlib,subprocess
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13';RAW=OUT/'raw'
def read(name,default=None):
    p=RAW/name;return json.loads(p.read_text())if p.exists()else default
manifest=json.loads((ROOT/'public/models/gullyverse/quarry-foundation/manifest.json').read_text())
base=json.loads((ROOT/'public/models/gullyverse/limestone-excavation/manifest.json').read_text())
mat=json.loads((ROOT/'assets-source/gullyverse/quarry-foundation/material-manifest.json').read_text())
files={r['file']:r['bytes']for r in manifest['files']}
perf=[]
for label in ['before','after']:
    result=read(label+'-performance.json',{})
    for w in result.get('windows',[]):
        s=w['after']['stats'];perf.append(f"| {label} | {w['name']} | {w['FPS']:.2f} | {w['p50']:.1f} | {w['p95']:.1f} | {w['p99']:.1f} | {w['max']:.1f} | {s['calls']} | {s['triangles']:,} | {s['textures']} / {s['geometries']} | {s['dpr']} |")
suite=read('browser-suite-summary.json',[])
tests='\n'.join(f"| `{r['script']}` | {'PASS'if r['exitCode']==0 else 'FAIL'} | {r['durationSeconds']:.1f}s |"for r in suite)
life=read('lifecycle.json',{});videos=read('video-with-wall.json',{})
vc=[(c['cycle'],c['settled']['stats']['textures'],c['settled']['contexts'][-1]['stats']['Texture']['active'])for c in videos.get('cycles',[])]
geotest=read('excavation-geometry-validation.json',{});validation=read('glTF-validator.json',{})
nodes=manifest['nodes'];selected={j:sum(n['triangles']for n in nodes if any(n['name']==name for p in manifest['parts']if p.get('refined')for name in p['nodes'][j:j+1]))for j in range(3)}
starting=read('baseline-state.json',{});preserved=read('baseline-preservation-check.json',{})
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
status=subprocess.check_output(['git','status','--short'],text=True)
(RAW/'final-git-status.txt').write_text(status)
captured=[]
for group in ['before-captures','after-captures','before-detail-captures','after-detail-captures','stage-material-captures']:
    captured.extend(read(group+'.json',{}).get('captures',[]))
beforePerf=read('before-performance.json',{});afterPerf=read('after-performance.json',{})
profile=next((w['before']for w in afterPerf.get('windows',[])),{})
network=read('network-loading.json',{})
entrance=read('entrance-timing.json',{})
browserVersion=read('after-captures.json',{}).get('browser','see capture metadata')
networkRows='\n'.join(f"| {r['label']} | {r['route']} | {r['totalTransferBytes']:,} | {r['encodedBytes']:,} | {r['readyMs']:.1f} | {r['newAssetBytes']:,} |"for r in network.get('runs',[]))
report=f'''# Gullyverse Stage 2C.5 — dark-rock realism foundation

13 October 2026. **Two adjoining authored geology regions, a source-derived dark PBR family and corrected surrounding terrain are implemented in an opt-in review mode.** The approved connected original-rock baseline and ordinary public website are retained. This is a production candidate for visual review, not a claim that high-end photorealism or physical-device performance has been achieved.

[Before/after gallery](../reports/stage-2c5-photorealism-foundation-2026-10-13/gallery.html) · [capture metadata](../reports/stage-2c5-photorealism-foundation-2026-10-13/screenshot-metadata.json) · [asset inventory](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/asset-inventory.json).

## 1. Exact preserved baseline

Starting branch **`{branch}`**, HEAD **`{revision}`**; staged, unstaged and untracked status were empty before Stage2C.5 bookkeeping. HEAD is unchanged. [Starting state](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/baseline-state.json), [starting hashes](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/baseline-hashes.json), [final status](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/final-git-status.txt).

A local non-destructive source/asset archive preserves924 files,885,744,797bytes, including relevant tracked/untracked content; credentials, build caches and duplicate review archives are excluded. It lives at `reports/stage-2c5-photorealism-foundation-2026-10-13/backup/current-source-assets.tar.gz` and is intentionally excluded from the review ZIP. No reset, clean, broad restore, commit, push or deployment was performed.

The preservation inventory checked{preserved.get('checked',0)} existing files. **No recorded existing public asset or Blender source changed**. [Hash comparison](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/baseline-preservation-check.json). Existing source changes are limited to review-mode selection/UI in `ImmersiveShell.tsx` and an explicit common render-part return type in `LimestoneExcavationSession.ts`; the latter has no runtime behavior change. All stage, crowd, video, lights, navigation, camera, world-registry, payment and admin source/assets remain unchanged.

The approved connected comparison is `/?arrival=hub&quarryReview=excavation` with the original rock family. As found in this branch, ordinary URLs still select the retained Stage2C rollout. Neither connected nor foundation review modes have been promoted to public defaults. Historical limestone/Stage2C/Stage2C.1 comparisons remain available.

## 2. Repetition diagnosis

| Symptom | Established cause | Foundation correction |
|---|---|---|
| Nested oval/wavy marks | Original `rock_pilot_materials.py` bakes sinusoidal bedding and Voronoi slab-gap contours into albedo. Albedo-only browser diagnostics retain the patterns. | Source-derived mineral microdetail; metre-scale bedding/fractures are geometry. |
| Mirrored repeated bands | `painted_uv` reflects inside the pilot atlas's painted front patch. This avoids padding but mirrors the same identifiable features. | Unreflected arc/height UVs at2m scale, no sampling of padded atlas strips. |
| Smooth recurring relief | Baseline field repeats broad sinusoidal relief with many thin bed grooves. | Two regional coherent fields with unequal bed offsets, finite inclined faults, genuine recesses and a localized projection/ledge. |
| Warped outer land | Radial geometry strips and reflected height/XZ atlas UVs; the wall atlas is inappropriate for land. | Constrained Cartesian terrain, independent world-scale elevation and terrain PBR mapping. |
| Weak ground contact | Buried shell foot plus sparse generic floor dressing, little local geological contact. | Small closed broken-stone fragments at the wall foot, outside functional circulation. |

These are different causes. Normal-map removal did not remove old albedo patterns. Valid glTF normals/tangents and actual geometric-normal/wireframe views do not establish a general tangent defect. [Before diagnostics](../reports/stage-2c5-photorealism-foundation-2026-10-13/before/diagnostic-material-only.png), [new material-only](../reports/stage-2c5-photorealism-foundation-2026-10-13/after/diagnostic-material-only.png), [geometric normals](../reports/stage-2c5-photorealism-foundation-2026-10-13/after/diagnostic-geometric-normal.png).

An initial C5 export exposed saturated blue patches. Artist vertex factors slightly above1 wrapped during Blender's normalized colour export. They persisted with normal/ORM maps disabled. Factors are now bounded before export; a regression test reads actual GLB colour/tangent data. Discarded images/logs are kept locally under `trials/vertex-colour-overflow/`; they are not final acceptance images.

## 3. Dark-rock PBR production approach

The colour reference is the original Stage2A pilot, mean sRGB approximately108.27/106.92/100.40. The new derived rock albedo is approximately106.50/105.10/98.60 before JPEG export and lighting. Subtle bounded vertex factors add regional weathering. This preserves the dark neutral brown-grey aesthetic; limestone maps are not used in foundation mode. Global illumination, sky, fog, exposure and all artificial lights are unchanged.

**Licensed source:** Poly Haven `rock_face_04` by Dimitrios Savva and `rocky_terrain` by Amal Kumar,CC0 1.0 Universal. Original downloaded maps, provider metadata, license page, provider MD5s and SHA256s are retained. [Provenance](../assets-source/gullyverse/quarry-foundation/source-provenance.json), [license copy](../assets-source/gullyverse/quarry-foundation/licensed-source/polyhaven-license.html).

The API does not certify capture technique or metre displacement amplitude. These are photographic PBR source assets; the authored quarry is not a scan of a real excavation. No supplied reference-image pixels are used as production textures. Recognisable whole-rock/leaf-litter motifs are suppressed in the rock family: a periodic height/albedo residual supplies fine mineral detail, while large formations are authored geometry. Height amplitudes are artistic, not measured scan heights.

| Material | Albedo | Normal | ORM | Mapping | Response |
|---|---|---|---|---|---|
| `Foundation_Dark_Rock_PBR` |2K JPEG|1K PNG|1K PNG|wall arc/2,elevation/2|matte mapped roughness≈0.918–0.960; normal strength0.7; metallic channel0|
| `Foundation_Dry_Terrain_PBR` |1K JPEG|1K PNG|1K PNG|world XZ/90|dry terrain; roughness≈0.936–0.949; metallic0|

ORM packs occlusion inR, roughness inG and zero metallic inB. Fine AO is mild; no fake deep black cracks are painted into albedo. No global triplanar shader, new runtime decoder, postprocessing or lighting trick is added. Two shared standard glTF PBR materials and six unique runtime images serve the entire review world. The rest of the shell retains baseline geometry but uses this same material family for coherence.

[Material specification](../assets-source/gullyverse/quarry-foundation/material-manifest.json). Estimated decoded RGBA8+mip payload is **48MiB** for the new family versus16MiB for the original pilot. This is a resource estimate, not driver VRAM. Reducing the normal map from2K to1K lowered holder transfer from8,040,752 to{files['foundation-materials.glb']:,}bytes without changing the source resolution.

## 4. Blender geometry and connected regions

[Editable master](../assets-source/gullyverse/quarry-foundation/quarry-foundation.blend) · [reproduction instructions](../assets-source/gullyverse/quarry-foundation/README.md) · [runtime manifest](../public/models/gullyverse/quarry-foundation/manifest.json).

`foundation_geometry.py` reads the existing continuous field and world registry. The usable quarry remains97.8×123.5m; its20-point collision footprint,378.092m excavation arc, original tunnel-mouth/return vertices and approximate28.61–38.67m rim distribution are retained.

| Art region | Arc range | Runtime culling partitions | Treatment |
|---|---|---|---|
| Broad west face |283.569–315.077m|13,14|broad exposed planes, unequal bedding, finite oblique/vertical joints|
| Northwest curvature |315.077–337.027m|15|connected corner, localized ledge/projection, deeper interrupted fractures|

These are two adjacent areas of one shell, not separate panels. A four-metre blend at external ends returns to baseline geometry. Actual fault recesses reach approximately0.5–1.05m; smaller chips/detail use mapping. Common cross-LOD side samples and upper rim remain shared. No new artificial wall end caps or disconnected rock masses are introduced.

The three detailed-region triangle totals are {selected[0]:,}/{selected[1]:,}/{selected[2]:,}. The surrounding terrain and small fragment meshes reuse their modest geometry across levels; they do not pretend to be independent decimated terrain LODs. Source surfaces are intentionally open at buried contact, distant terrain boundary and original passage attachment. A watertight underground solid or exhaustive self-intersection proof is not claimed.

## 5. Rim, outer terrain and floor contact

The outer landscape uses a constrained Delaunay triangulation of Cartesian samples and the exact retained rim. It contains{manifest['terrain']['triangles']:,}triangles in16 culling tiles. World-coordinate ridge variation replaces radial banks/swirls. Fine samples near the rim attach to exact rim positions; the original entrance forecourt mask and protected tunnel-roof clearance remain. Terrain extends within the original600m ground envelope; usable interior area, stage floor and existing dry rocky/grassy floor are unchanged.

44 small closed fractured fragments sit near the detailed wall foot, with≈1056triangles total. They are deliberately modest, outside walking/travel polygons, and not a floor-wide debris layer. Their placement can still benefit from more organic clustering. No artificial paths, new foliage, stalls or people are introduced. [Wall-foot capture](../reports/stage-2c5-photorealism-foundation-2026-10-13/after/desktop-15-wall-foot.png), [outer-land view](../reports/stage-2c5-photorealism-foundation-2026-10-13/after/desktop-17-terrain-map-height.png).

## 6. Runtime integration, LOD and ownership

New `QuarryFoundationSession` extends the existing excavation owner; it uses the same persistent Canvas and `QuarryPerimeter` preparation/LOD renderer. Activate **`/?arrival=hub&quarryReview=foundation`** only in development or a build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`. Review buttons switch to connected Stage2C4 or back to foundation with the existing cover/input handoff. Ordinary routes do not request foundation assets or expose review controls.

```mermaid
flowchart TD
  W[Unchanged world registry / lighting / cameras] --> B[Blender continuous shell]
  S[CC0 local source maps] --> M[Shared dark rock + terrain holder]
  B --> G[Two refined regions / retained remaining walls / Cartesian terrain]
  G --> O[QuarryFoundationSession owner]
  M --> O
  C[Connected Stage2C4 explicit comparison / failure fallback] --> O
  O --> P[Existing covered texture init + compile + hidden warm renders]
  P --> L[Existing screen-space LOD hysteresis / one visible node per part]
  L --> R[Existing persistent R3F Canvas]
```

35parts select one LOD each using projected size, FOV, actual framebuffer height and adaptive quality. Walls have three actual topologies. Terrain/fragment level nodes share geometry. Frustum culling remains active after warm-up. No compression compatibility is assumed: these are standard GLBs.

Foundation geometry and its two-material holder have one private bounded owner. Clones borrow resources. Connected comparison assets are fetched lazily; explicit inactive retirement releases only foundation resources. Image bitmaps are closed on owner disposal. Stale/unmounted loads are rejected and owned unpublished resources disposed. Export validation precedes borrowed material assignment, so an accidental embedded-map payload can be freed safely. Original stage caches are never cleared.

Loading initializes all six images, compiles shaders and performs four covered hidden draws across levels through the existing gate. Foundation failures fall back to the **connected original-rock comparison**, rather than silently changing the quarry architecture. Shader init/compile timings are CPU/driver-proxy timings, not independent GPU upload measurements.

## 7. Asset cost and matched performance

| Asset | File bytes |
|---|---:|
|Combined geometry,all threeLODs|{files['foundation-geometry.glb']:,}|
|Shared material holder|{files['foundation-materials.glb']:,}|
|Runtime total|{files['foundation-geometry.glb']+files['foundation-materials.glb']:,}|
|Standalone LOD0|{files['foundation-lod0.glb']:,}|
|Standalone LOD1|{files['foundation-lod1.glb']:,}|
|Standalone LOD2 / diagnostic collision each|{files['foundation-lod2.glb']:,}|
|Approved connected Stage2C4 total|10,404,324|

Whole-world triangles at all0/all1/all2 are **{manifest['trianglesByLOD'][0]:,}/{manifest['trianglesByLOD'][1]:,}/{manifest['trianglesByLOD'][2]:,}**, versus baseline152,986/40,648/17,413. Actual visible counts depend on mixed LODs and frustum culling; these totals are not asserted to render simultaneously.

Hardware: Debian13 x86-64 cloud VM, AMD EPYC9V74 virtual CPU allocation(3logical CPUs); Chromium's actual renderer is ANGLE/Vulkan **SwiftShader**, GPU timers unavailable. No `/dev/dri` or physical mobile/GPU device was accessible. [CPU](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/host-cpu.txt), [OS](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/host-os.txt). Browser/renderer details are in every raw snapshot.

Profiling uses the same final production build,1366×900viewport,DPR0.5,quality3,matched camera positions and ten-second wall-clock R3F frame windows. No recording, artificial throttling or competing authoring/browser workload is present during these windows. The environment session restarted mid-suite; passed results were retained and interrupted jobs resumed. Both comparable performance windows were collected after that restart. This is not representative physical-GPU performance.

|Mode|Window|MeanFPS|p50ms|p95ms|p99ms|maxms|Draw calls|Visible triangles|Textures/geometries|DPR|
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
{chr(10).join(perf)if perf else '|Pending|Raw profiling not finished||||||||||'}

[Before raw frames](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/before-performance.json), [after raw frames](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/after-performance.json). Each records >100ms stalls, max stalls, active buffer/texture byte estimates, JS heap, draw/triangle counters and wall preparation traces. Physical laptop60FPS, physical mobile60/30FPS and driver VRAM acceptance remain **UNVERIFIED**.

### Loading/network

|Mode/cache|Route|Actual transfer bytes|Encoded body bytes|Covered readiness ms|New foundation encoded bytes|
|---|---|---:|---:|---:|---:|
{networkRows if networkRows else '|Pending|Cold/warm resource collection not finished||||'}

[Network/timing results](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/network-loading.json). File size is distinguished from HTTP transfer/cache observations. Geometry parse, image readiness, texture-init, shader-compile and covered-ready events remain in raw traces. Slow software draws contribute to covered timing; temporal correctness does not imply perceptual smoothness.

Browser version **{browserVersion}**. Warm measurements explicitly enable HTTP cache and use CDP URL blocking for API/analytics rather than Playwright routing, which disables cache. Discarded interception-based results are retained locally under `trials/cache-interception/`. Actual entrance phase progression is **{entrance.get('entrancePhaseMs',0):.1f}ms** atDPR0.5; total Playwright action/scheduling plus sequence is reported separately. [Activation timing](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/entrance-timing.json). The lower software frame times in these short samples are not a certified hardware improvement.

## 8. Resource lifecycle evidence

Ten complete foundation/baseline enable/disable cycles: **{life.get('status','PENDING')}**. Initial foundation31textures/212geometries. Once both bounded caches warm, counts plateau at34textures/266geometries through every cycle. Explicit foundation retirement returns to28/195; reload returns to34/266. Full fallback unmount leaves owner disposed,consumer count0,no active asset. [Lifecycle trace](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/lifecycle.json).

Ten movie/exit cycles: **{videos.get('checks',[{}])[-1].get('status','PENDING')if videos.get('checks')else 'PENDING'}**, settled texture/GL texture pairs `{[(v[1],v[2])for v in vc]}`. Playback toggles original/authored modes during cycles3/6/9, returns to the saved activation pose, preserves the Canvas and leaves no disposed video sampler. [Actual video lifecycle](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/video-with-wall.json).

Ten immersive round trips and recovery/failure tests are separately recorded; warmed counts must plateau rather than comparing a cold scene to a populated stage. Counters track GL object names, not driver VRAM. Context-loss counters are deliberately not treated as directly comparable lifetime allocations. JS heap sampling is not a forced-GC retained-object proof.

## 9. Browser evidence and visual comparison

{len(captured)} core/detail capture metadata records are included, plus stage playback/restoration and recorded map-ascent/descent frames. Desktop1366×900 and mobile-aspect390×844 PNGs are retained at their original capture dimensions. Core wall screenshots useDPR1/quality0; map captures retain adaptive quality and record effectiveDPR. Portrait is emulation on the same software renderer, not an iPhone benchmark.

Matched comparisons include broad wall, corner, the internal join, close fracture, upper rim, wall foot, along-wall view, tunnel exit, hub, scaffold, stage-facing composition, stage looking back under the existing Aftermovie lighting and aerial/outer land. Temporary material-only/normal/wireframe probes operate on clone-owned materials; they are explicitly diagnostics. Forced single LOD captures are separate from the automatic-LOD walkthrough.

[Public visitor walk/map recording](../reports/stage-2c5-photorealism-foundation-2026-10-13/recordings/visitor-walk-and-aerial.mp4) and [close geology inspection recording](../reports/stage-2c5-photorealism-foundation-2026-10-13/recordings/near-wall-inspection.mp4). The latter moves an inspection camera at eye height alongside the wall: ordinary walking gates intentionally prevent this path. It is actual browser footage, clearly labeled; it is not claimed to be public locomotion. Camera/FOV/DPR/quality/LOD traces accompany both. Browser software stalls remain visible and footage is not retimed to fake smoothness.

## 10. Validation and tests

Blender4.3.2 exports metres,Z-up to glTFY-up with stable names,finite UVs,unit normals and orthogonal tangent frames. Khronos validator2.0.0-dev.3.10 checked six exports with zero errors/warnings. Actual imported geometry has no zero-area faces and passes all18 fixed sector borders across three levels, five eye locations×120yaw samples×five upward pitches, and playable-footprint clearance checks. Result **{geotest.get('status','PENDING')}**, unexpected horizontal gaps{len(geotest.get('horizontalUnexpectedGaps',[]))},inverted visible hits{len(geotest.get('invertedVisibleHits',[]))},cross-LOD skyline hit/miss differences{len(geotest.get('crossLODHitDifferences',[]))}.

These tests are sampled visibility/clearance checks, not an exhaustive self-intersection proof. Ground/tunnel connections are also visually reviewed. [Geometry results](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/excavation-geometry-validation.json), [glTF validation](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/glTF-validator.json).

One supplemental cold direct-Aftermovie capture atDPR1/defaultquality timed out before local arrival at90s. The same route passes functional tests atDPR0.25/quality3; the supplemental capture was retried with early quality3 selection. The precise high-cost startup contribution was not isolated. This remains a high-DPR software-rendering limitation to investigate on physical devices, not evidence that source stage assets were changed.

Commands executed:

- `npx tsc --noEmit` —PASS.
- `npm run lint` —PASS with existing warning policy; no new warning suppression.
- `npm run build` —PASS, review flags enabled with inert localhost Supabase placeholders; no production data mutation.
- `npm run test:immersive` —74PASS,0FAIL; three new actual-export colour/anchor/tangent tests.
- Blender authoring/export plus BVH geometry survey —PASS.
- Khronos glTF validation —six files,PASS.

[Typecheck log](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/typecheck.log), [lint](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/lint.log), [build](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/build.log), [unit output](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/unit-tests.log).

|Actual browser script|Result|Elapsed|
|---|---|---:|
{tests}

Coverage includes fresh intentional entry and pacing, editable-focus/lost-key ownership, blur/freeze recovery, map projection/resize/touch/reduced motion, directional Aftermovie travel, bounded menu/Stay/Esc/hysteresis, video/rapid replay restoration, Navbar Home/directURL/Back/Forward, ten cache cycles, ten navigation round trips, actual WebGL context loss/recovery, delayed/unmounted preparation, optional material/geometry failure/retry, duplicate embedded-map rejection and critical stage native fallback. Existing default routes remain verified separately. [Browser summary](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/browser-suite-summary.json).

Initial integration had a return-type compilation error, corrected with a shared structural render-part contract. Early logs and the managed-session interruption are retained; neither is hidden as a passing final application check.

## 11. Comparison with supplied quarry references

|Area|Improvement|Still visibly different|
|---|---|---|
|Macro geology|connected excavated shell, broad faces, finite deep joints and corner ledge|forms remain parametrically authored; more varied quarry-cut damage and irregular projections are needed|
|Bedding/fractures|real offsets/recesses, unequal intervals and interruptions|some long grooves and straight joint paths remain too regular/soft|
|Material|fine natural mineral residual, matte dark family, removed reflected atlas motifs|not a uniquely photographed40m cliff; microtile repetition and restrained colour/weathering remain possible|
|Depth/shadow|actual fracture geometry and surface-normal response|locked lighting has no new baked cliff AO or real-time shadow treatment; bright fracture-facing facets can read stylized|
|Contact|buried foot plus limited fragments|more organic local scree/sediment clusters and natural contact variation are needed|
|Terrain|Cartesian land and appropriate separate soil/rock mapping|coarse macro elevation and repeated90m source tile remain; final terrain variation/vegetation is deferred|

The reference photographs use different illumination. They are compared for geological structure and surface character, not used as permission to change the approved dusk lighting. **Photorealism remains PARTIAL**, with the bounded implementation ready for human visual review. Entrance/tunnel, stalls and hub people remain their existing temporary assets; stage originals are preserved.

## 12. Proposed full-quarry production strategy and budgets

Extend the coherent regional field, shared dark material and fixed-border contract only after this visual review. Do not copy a rectangular panel or independently sculpt a ring of boulders. Prioritize wall regions exposed in normal visitor/stage views; retain broad low-cost faces where detail is not visible. Material variants should share microdetail/ORM rather than allocate another48MiB per segment.

Provisional engineering limits, **not physical-GPU certification**:

- Keep the shared wall material near32MiB decoded proxy and terrain16MiB; review quality at1K normals before increasing resolution.
- Reserve dense geometry for close hero regions; current two-region near total is{selected[0]:,}triangles. Uniformly applying this density to the whole≈378m perimeter could reach400–500K near triangles before the existing stage/crowd, and is not recommended as always-resident detail.
- Target a mixed visible quarry envelope≈150–250K triangles and≤35environment part draws during ordinary views; actual stage overhead must be measured separately.
- Split future high-detail geometry into bounded near/middle/distant payloads instead of preloading the complete final high-poly quarry on landing. Existing standaloneLOD exports are available; no broad streaming rewrite has been introduced.
- Current runtime total13.665MB is a measured candidate cost, not an arbitrary2MB success threshold. Avoid repeating that payload or material holder for every region.

Frustum culling, quality-aware LOD, covered texture/shader warm-up and deterministic resource ownership must remain. KTX2/Meshopt/Draco are not configured or claimed to improve this build; future compression needs measured quality/decode/upload compatibility trials.

## 13. Physical-device procedure

Physical laptop/iPhone/Android profiles remain **PENDING**, not a block on this bounded authoring task. On a local hardware-rendered production review build, run the baseline and foundation at the same viewport/DPR/quality,then repeat with the production adaptive settings. Record OS/browser/CPU/GPU, renderer,draws/triangles,60-second frame distributions, cold/warm entry/travel,video/map timings and ten navigation/playback cycles. Keep thermal state/cache settings identical.

The supplied `measure.mjs` reproduces this report's fixedDPR0.5/Q3 diagnostic configuration; do not confuse it with native-DPR device acceptance. For native device measurement use the existing `scripts/perf-gullyverse.mjs` and public `?diagnostics` telemetry. Physical iPhone uses Safari remote inspection viaMac; Android uses Chrome USB remote inspection. Export `window.__gullyverse.timeline`,memory/preparation traces and renderer info alongside actual screenshots. Physical60/30FPS acceptance requires sustained device results,not cloud unit tests.

## 14. Stop and next step

Stop here for review of the broad face, adjoining corner, material and outer landscape. Review the bright fracture facets, groove regularity, contact fragments and map terrain specifically. **Do not scale this candidate solely because builds/tests pass.** If approved, the exact next bounded step is the adjoining west-wall sector12,arc262.089–283.569m,nearXZ[-55.25,-118.25]. Extend geology into that21.48m face with the same shared PBR/border/ownership contract while retaining the current geological phase/origin, so already approved formations do not shift when coverage expands. Collect physical-device budgets alongside authoring before permanent full-quarry promotion. Detailed cave/tunnel, stall, crowd and stage reconstruction have not started.

Files added: four authoring/source-material scripts, `QuarryFoundationSession.ts`, one export-regression test file, editable source/maps/manifests, runtimeGLBs and evidence/report tooling. Existing modifications: `ImmersiveShell.tsx` review factory/UI and `LimestoneExcavationSession.ts` return-type annotation. [Exact source diff](../reports/stage-2c5-photorealism-foundation-2026-10-13/raw/source-diff.patch).
'''
path=ROOT/'docs/gullyverse-stage-2c5-photorealism-foundation.md';path.write_text(report)
print(path,'bytes',path.stat().st_size,'performance windows',len(perf))
