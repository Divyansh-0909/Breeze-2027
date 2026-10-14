from pathlib import Path
import json,subprocess
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-1-rock-realism-refinement-2026-10-14';RAW=OUT/'raw'
REL='../reports/stage-2c5-1-rock-realism-refinement-2026-10-14'
def read(name,default=None):
    p=RAW/name;return json.loads(p.read_text())if p.exists()else(default if default is not None else{})
state=read('baseline-state.json');cost=read('asset-cost-comparison.json');preserved=read('preservation-check.json')
before=read('before-performance.json');after=read('after-performance.json');network=read('network-loading.json');geometry=read('excavation-geometry-validation.json')
suite=read('browser-suite-summary.json',[]);videos=read('video-with-wall.json');life=read('lifecycle.json');nav=read('navigation-cycles.json')
fractures=read('fracture-field-diagnosis.json');old_shading=read('before-shading-diagnosis.json');new_shading=read('after-shading-diagnosis.json')
captured=json.loads((OUT/'screenshot-metadata.json').read_text())if(OUT/'screenshot-metadata.json').exists()else[]
profile=next((w['after']for w in after.get('windows',[])),{})
perfrows=[]
for label,result in [('C5 before',before),('C5.1 after',after)]:
    for w in result.get('windows',[]):
        s=w['after']['stats'];perfrows.append(f"|{label}|{w['name']}|{w['FPS']:.2f}|{w['p50']:.1f}|{w['p95']:.1f}|{w['p99']:.1f}|{w['max']:.1f}|{s['calls']}|{s['triangles']:,}|{s['textures']}/{s['geometries']}|")
networkrows='\n'.join(f"|{r['label']}|{r['totalTransferBytes']:,}|{r['encodedBytes']:,}|{r['readyMs']}|"for r in network.get('runs',[]))
testrows='\n'.join(f"|{r['script']}|{'PASS'if r['exitCode']==0 else'FAIL'}|{r['durationSeconds']:.1f}s|"for r in suite)
settled=[(r['settled']['stats']['textures'],r['settled']['contexts'][0]['stats']['Texture']['active'])for r in videos.get('cycles',[])]
border=max((r['maximumSharedBorderErrorM']for r in geometry.get('seams',[])),default=0)
report=f'''# Gullyverse Stage2C.5.1 — rock realism, fracture and continuity refinement

14 October2026. **A separate opt-in candidate refines the same two adjoining C5 geology regions, the local rim/slope and outer terrain.** The accepted dark-rock foundation, all original assets and the normal website remain available. Final production-art approval and physical GPU performance are not claimed.

[Matched gallery]({REL}/gallery.html) · [original PNG/camera metadata]({REL}/screenshot-metadata.json) · [matched-pose checks]({REL}/raw/matched-capture-validation.json).

## Exact preserved baseline

Branch `{state['branch']}`, HEAD `{state['head']}`. Staged files: none. Starting tracked modifications: `ImmersiveShell.tsx` and `LimestoneExcavationSession.ts` from C5. There were{state['untrackedFileCount']} untracked files, including C5 source/master/maps/exports/reports. No human authorship is inferred from Git labels. [Exact starting state]({REL}/raw/baseline-state.json), [full status]({REL}/raw/baseline-git-status.txt), [tracked/untracked hashes]({REL}/raw/baseline-hashes.json).

The local non-destructive snapshot contains{state['snapshotFiles']} mutable source/configuration/asset files and{state['snapshotBytes']:,} compressed bytes. `backup/current-source-assets.tar.gz` is deliberately excluded from the review ZIP; credentials, environment files, dependencies and build caches are excluded. All other existing files were inventoried and left in place. No reset, clean, overwrite restore or deployment was performed. After implementation and verification, the user separately authorized committing, pushing and merging into `work-in-progress-2027`; this supersedes the earlier Git restriction. Exact delivery revisions are recorded in the Git history.

Preserved97.8×123.5m usable quarry registry,20-point footprint,378.092m continuous arc, stage coordinates/assets, scaffold/signs, stalls/Team/Contact, tunnel path/connector, camera/map composition, walking polygons, gates, boundary menu, both Hub/Aftermovie light/fog presets and exposure. Existing stage/crowd/video/payment/admin assets and source are unchanged. [Preservation check]({REL}/raw/preservation-check.json).

Only **two existing source files** changed relative to the captured worktree: [ImmersiveShell](../components/immersive/ImmersiveShell.tsx) adds the opt-in selector/label; [QuarryFoundationSession](../components/immersive/QuarryFoundationSession.ts) accepts a configuration selecting the retained C5 or new C5.1 manifest/directory. It keeps the same private cache, preparation and disposal paths. The pre-existing `LimestoneExcavationSession.ts` modification was not changed in this phase. Source-before text copies and the source diff accompany the evidence.

## Root cause of bright fracture edges

The original `rock_relief` has six narrow notch profiles, approximately0.25–0.51m half-width and0.51–1.05m depth, with vertical extents of5–12m about their centres. Smooth inclined side faces run for many metres and turn toward the existing warm key light. The displayed result is a bright, near-straight cut.

Evidence distinguishes causes:

- Material-only images do not contain the long bright cuts; normal-map removal does not remove them.
- Geometric-normal/wireframe images place the brightness on the narrow turning faces. This is diffuse orientation response, not a metallic/specular-white paint stripe.
- Actual imported C5 and C5.1 detailed meshes each have **one outer boundary loop and no internal fracture hole** after welding validation-only attribute duplicates at10micrometres. No open fault boundary/backface exposure was found. [Boundary evidence]({REL}/raw/fracture-boundary-validation.json).
- Final glTF data has finite orthogonal normal/tangent frames, valid winding in visible rays and no new UV padding/mirroring problem. Remaining warm facets are physical lit facets, not patched black paint.

In a fixed850×700 field sample, lateral-slope p99 falls{fractures['before']['slopeP99']:.3f}→{fractures['refined']['slopeP99']:.3f} and area with slope magnitude>2 falls{fractures['before']['steepSideFractionAbove2']*100:.4f}%→{fractures['refined']['steepSideFractionAbove2']*100:.4f}%. These are diagnostic shape statistics, not an art-quality acceptance score. [Field results]({REL}/raw/fracture-field-diagnosis.json).

## Geological modelling changes

The new [shared field](../scripts/blender/refined_foundation_geometry.py) retains the existing partition/arc/stitch pipeline. It does not distribute new expensive detail to other walls.

- Same broad west region arc283.569–315.077m and adjoining northwest-curvature region315.077–337.027m, runtime sectors13/14/15. A4m external blend returns to the retained shell; the internal join samples one common field.
- Six unequal, finite faults use changing loci, variable widths, local bridges and interrupted oblique branches. Recess depth is approximately0.42–0.62m; branch depth is smaller. Chipped edges and local throws interrupt their side surfaces.
- Final close-up inspection still showed one overly continuous bright leg in the first iteration. Unequal solid bridges now interrupt each main notch, and the first fault has a less regular locus. Material maps and mesh density are unchanged; captures, profiling, export checks and all eight browser scripts were rerun for this final geometry. The superseded iteration remains in the local trials archive.
- Unequal bedding intervals contain finite projecting/recessed sections. Local throws offset beds at faults.51 bounded asymmetrical chips mix with broad exposed faces; geometric relief handles metre-scale structure and the accepted maps handle fine grain.
- Selected wall inclination/recess changes and one partial ledge refine excavation character. Local rim displacement is bounded by the0.43m/0.22m components; the functional floor/foot remains unchanged. No full ring of terraces, detached rocks or rectangular slabs is introduced.
- Remaining wall **positions and indices match the original runtime export** in unit tests. Fine density is unchanged, rather than increased to hide weak forms.

[Editable master](../assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend), [author/export script](../scripts/blender/author_refined_quarry_foundation.py), [workflow](../assets-source/gullyverse/quarry-foundation-refined/README.md), [runtime manifest](../public/models/gullyverse/quarry-foundation-refined/manifest.json). Blender4.3.2, metre units; Blender `(x,-z,y)` exports glTF Y-up. The low collision-reference export is diagnostic; authoritative walking/collision polygons are retained.

## Material preservation and terrain continuity

**The three accepted C5 cliff image payloads are byte-identical in the exported material holder.** Rock albedo, normal/ORM, roughness, normal strength0.7,2m arc/height UV scale, metallic0 and the dark neutral/brown-grey style are preserved. No global light, fog, sky or exposure change is made. [Material manifest](../assets-source/gullyverse/quarry-foundation-refined/material-manifest.json).

The outer-land source remains CC0 PolyHaven `rocky_terrain`; rock remains `rock_face_04`. Original C5 provider maps/provenance/license remain unchanged. These are source-derived PBR maps and authored geology, not a certified physical scan of this quarry.

Outer terrain corrections are local to the review asset:

- Graded, jittered Cartesian sampling reduces regular triangle bands. Weighted rim-height interpolation replaces nearest-sample stepping. Shared exact rim normals remove the previous shading break; contact-height error is0 in authoring data.
- Independent broad ridges, a local gully and a restrained shoulder replace a broad annular interpolation bank. The original entrance forecourt mask and tube-roof clearance are retained.
-90m UV mapping enlarged identifiable photo motifs. A first22m attempt made repeated photo tiles too evident, so it was rejected and preserved under `trials/terrain-unfiltered/`.
- Final22m mapping uses filtered periodic albedo/height residuals from the same source, with low-contrast world-space erosion/landform colour variation. Terrain mean colour and original roughness/AO ORM are retained; the two outer-land albedo/normal files change. **Still six unique runtime images and two shared materials**, no extra texture family per wall. [Terrain derivation](../scripts/blender/refined_foundation_terrain_material.py), [specification](../assets-source/gullyverse/quarry-foundation-refined/terrain-material-refinement.json).
-45 small closed fragments are arranged in five uneven clusters outside circulation,900triangles versus the previous44 fragments/1056triangles. Original fragment top/bottom cap winding was reversed relative to the outward sides; final caps face correctly and have an exported regression test. They do not fill the floor or alter collision logic.

## Readability under approved lighting

The fixed central screenshot ROI has mean display luminance{old_shading['approved-lighting']['meanDisplayLuminance']:.4f} under approved lighting,{old_shading['no-ao-or-normal']['meanDisplayLuminance']:.4f} with AO/normal maps removed, and{old_shading['neutral-lighting']['meanDisplayLuminance']:.4f} under temporary neutral hemisphere/key lighting. This is an uncalibrated screenshot diagnostic, not a physical illumination measurement. [Original diagnosis]({REL}/raw/before-shading-diagnosis.json).

The new fixed ROI remains similarly dark:{new_shading['approved-lighting']['meanDisplayLuminance']:.4f} under approved lighting,{new_shading['no-ao-or-normal']['meanDisplayLuminance']:.4f} without AO/normal and{new_shading['neutral-lighting']['meanDisplayLuminance']:.4f} under neutral lighting. [After comparison]({REL}/raw/after-shading-diagnosis.json). The neutral setup changes key-light direction toward the inspected wall; it reveals detail that the dark cliff, largely facing away from the approved key, does not reveal strongly. AO/normal attenuation is a smaller contribution. Broken faces change local contrast; **substantial dark, low-contrast areas remain**. Making all surfaces read like the neutral diagnostic would require a separate lighting/aesthetic decision. No such change is included. Neutral lights are added only in an instrumented browser and removed immediately; the production code has no diagnostic-light path.

## LOD, seams and clearance

The existing `QuarryPerimeter` chooses one LOD per part using projected size, actual DPR/FOV/viewport and quality-tier hysteresis.35 culling parts remain. Wall LODs have distinct topology; modest terrain/scree geometry is shared among level nodes. Fixed sector-side samples and the common rim prevent LOD gaps. Forced-level screenshots are marked as inspection diagnostics; recordings separately exercise automatic LOD.

Final actual GLB BVH checks: all18 boundaries across levels,5 visitor locations×120 yaw directions×5 pitches, zero unexpected horizontal gaps, zero inverted visible hits, zero cross-LOD skyline hit/miss differences and no playable-footprint incursions. Maximum shared-border float32 error{border:.9f}m, tolerance0.00002m. [Full geometry/clearance evidence]({REL}/raw/excavation-geometry-validation.json), [Khronos glTF results]({REL}/raw/glTF-validator.json).

Sampling does not prove exhaustive self-intersection freedom or every pixel's seam quality. The buried foot, far terrain edge and original tunnel attachment are intentionally open surfaces; this is not a watertight underground solid. Relief remains a connected radial height field, not a fully sculpted network of undercut caves. The mesh still has softened close-detail features and view-dependent warm fracture facets that need visual review.

## Transfer and memory cost

|Runtime resource|C5 before|C5.1 after|
|---|---:|---:|
|Combined three-LOD geometry|8,623,064bytes|8,530,404bytes|
|Two-material holder|5,041,508bytes|4,659,808bytes|
|Total runtime asset files|13,664,572bytes|13,190,212bytes|
|All-LOD0/1/2 triangle totals|180,317 /53,715 /26,834|178,635 /52,033 /25,152|
|Outer-terrain triangles|11,170|9,644|
|Unique mapped images|6|6|
|Estimated RGBA8+mipmap payload|48MiB|48MiB|

File reduction is474,360bytes(3.47%).48MiB is an estimate of texture payload, **not measured driver VRAM**. All three wall LODs are still downloaded/resident in this bounded owner; this phase does not introduce a streaming rewrite. [Cost inventory]({REL}/raw/asset-cost-comparison.json).

## Matched production performance

Debian13.6/KVM VM,3logical AMD EPYC9V74 vCPUs; Chromium{read('after-captures.json').get('browser','see raw browser profile')}, ANGLE/Vulkan **SwiftShader software rendering**. No physical GPU, Intel laptop, iPhone or Android device was accessible. No physical60/30FPS or driver-memory acceptance is claimed.

Same final production build,1366×900viewport,DPR0.5,quality3,matched cameras,10second rendered-frame windows. No concurrent authoring/browser workload during the windows; no recording or artificial throttling. Snapshot counters are observed after each window. Frame quantiles are short software diagnostic samples, not sustained GPU benchmarks.

|Mode|View|MeanFPS|p50ms|p95ms|p99ms|maxms|Calls|Triangles|Textures/geometries|
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(perfrows)}

[Raw before]({REL}/raw/before-performance.json), [raw after]({REL}/raw/after-performance.json). The new terrain/region bounds change culling: these samples expose2–8 more calls and up3218 more triangles in some views despite lower whole-asset totals. Hub/aerial software samples are slightly faster; left-wall/stage-back are slower. No causal physical-GPU performance conclusion follows from this single short A/B run. Software regressions are reported rather than hidden. Significant>100ms stalls, JS heap and tracked GL objects/payload proxies remain in the raw traces.

### Loading

|Mode/cache|Actual transfer bytes|Encoded body bytes|Covered readiness ms|
|---|---:|---:|---:|
{networkrows}

HTTP cache is explicitly enabled. Cold cache cleared once per mode; same-context warm revisit. CDP blocks API/analytics without Playwright routing, which would disable cache. Encoded cached bodies are not counted as new transfer. Localhost network figures do not model mobile radio/CDN latency. [Network traces and parse/compile/hidden-warm preparation]({REL}/raw/network-loading.json).

Authored entrance active phase: {read('entrance-timing.json').get('entrancePhaseMs','pending')}ms. Actionability overhead is separate. Covered preparation still initializes six maps, compiles and draws all LOD variants before reveal; late loading stays covered. [Entrance timing]({REL}/raw/entrance-timing.json).

## Runtime ownership and browser verification

The new config uses the same private foundation geometry/material owner. Render clones borrow resources; cache retirement is allowed only after covered restoration. Rejected/unpublished assets are disposed by their owner. Original stage caches are never cleared. Same persistent Canvas across Hub/Aftermovie/map transitions.

Ten enable/disable cycles: {life.get('status','PENDING')}. Warmed comparison caches plateau at34 textures/266 geometries. Explicit inactive retirement returns to28/195; reload returns to34/266. Full native fallback unmount leaves owner disposed, zero consumers and no active asset. [Lifecycle]({REL}/raw/lifecycle.json).

Ten actual movie/exit cycles settled `(Three textures, tracked GL textures)`:
`{settled}`. Playback includes authored/off toggles during cycles3/6/9, preserves original playback/restore and leaves no disposed sampler. [Video ownership]({REL}/raw/video-with-wall.json).

Ten navigation round trips: {nav.get('status','PENDING')}; settled Hub counts plateau at31 textures/223 geometries after stage/map warm-up. [Navigation cycles]({REL}/raw/navigation-cycles.json). Context loss/restore, failed/delayed optional loads/retry/unmount, invalid duplicate-map rejection, critical stage/native fallback and ordinary-URL isolation are independently checked. Counters are allocation proxies, not a VRAM leak proof; JS heap is not a forced-GC retained-object analysis.

|Browser script|Result|Duration|
|---|---|---:|
{testrows}

[Suite summary]({REL}/raw/browser-suite-summary.json), [public controls/focus/history/touch/reduced-motion checks]({REL}/raw/regressions/results.json), [directional travel]({REL}/raw/directional-travel.json), [recovery]({REL}/raw/recovery.json).

TypeScript, lint(existing warning policy), production build and79 immersive unit tests pass. Five new tests inspect actual export scope/preserved cliff pixels/unchanged remaining-wall topology/normal+tangent frames/outward scree caps. Six GLBs including the holder validate with zero Khronos errors/warnings. [Unit log]({REL}/raw/unit-tests.log), [typecheck]({REL}/raw/typecheck.log), [lint]({REL}/raw/lint.log), [build]({REL}/raw/build.log).

One intermediate build failed because source-before audit copies were saved with`.tsx` extensions and the project's broad TypeScript glob tried to compile them without neighbouring modules. Those artifact copies now use`.tsx.txt`; no application typecheck rule was weakened. The failed log is retained separately. Final build/type checks were rerun successfully. [Artifact-only failure]({REL}/trials/build-artifact-naming.log).

## Visual evidence and acceptance limits

{len(captured)} original-resolution PNG metadata records currently accompany the gallery. Desktop1366×900 and touch-emulated portrait390×844. Matched pairs check camera position/yaw/pitch/FOV, viewport, effectiveDPR, tier and Hub/Aftermovie preset. Fixed source hashes establish identical global light/fog/exposure configuration. Diagnostics are separated in the gallery and have clear filenames. No brightness correction or generated image substitutes are used.

[Visitor walking/map recording]({REL}/recordings/visitor-walk-and-aerial.mp4) is real public mouse/WASD/Map input. [Near-wall recording]({REL}/recordings/near-wall-inspection.mp4) is a labeled eye-height inspection-camera traverse with automatic LOD; ordinary directional gates prevent visitors walking this close, so it is not presented as a public locomotion path. Software pauses and actual timing are retained. MP4 is H.264 for mobile review; these browser recordings are silent.

|Category|Assessment|
|---|---|
|Fracture geometry correction|Implemented; original long smooth cuts replaced, visual approval pending|
|Bedding/relief|Improved interrupted offsets/chips; some surfaces still soft and broad|
|Seams/LOD/clearance|PASS sampled export and browser checks; pixel-level art review pending|
|Dark material preservation|PASS exported cliff image payload identity; local terrain map changes disclosed|
|Rim/outer terrain|Improved topology/mapping/contact; still a restrained macro surface|
|Whole excavation shape|Functional footprint retained; remaining perimeter intentionally not detailed|
|Dusk detail readability|PARTIAL; diagnostic comparison documents the lighting/orientation tradeoff|
|Physical desktop/mobile performance|UNVERIFIED; software results are diagnostic only|
|Final production realism|NOT APPROVED / not claimed|

Compared with supplied project quarry reference imagery, the candidate still lacks the dense hierarchy of broken angular planes, mineral/weathering variation, accumulated scree and ecological land cover. Some fine shared-grain repetition and warm fracture facets remain noticeable. Floor-to-wall dressing is restrained because approved circulation must remain clear. Existing tunnel/entrance/stalls/hub capsules and the original stage are untouched. The rest of the rim remains smoother/oval; this bounded change does not pretend to solve the full-perimeter art pass.

## Review modes, remaining work and next milestone

- New candidate: `/?arrival=hub&quarryReview=foundation-refined`.
- Original C5: `/?arrival=hub&quarryReview=foundation`.
- Connected original-rock C4: `/?arrival=hub&quarryReview=excavation`.

Use development or the existing `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` build flag. Removing the query retains the ordinary public default found in this branch. No new destination, navigation machine, public substitution or final-art rollout is enabled.

Before extending the treatment, review the broken edges, bedding/ledge softness, rim contact and dusk readability. If approved, extend the coherent field into the adjoining retained west area using common arc phase, metre mapping and exact LOD borders; do not repeat independent panels. Treat the measured13.19MB/48MiB/35parts as this candidate's cost, not a certified full-quarry budget. Future detail should reuse the three cliff maps, reserve near geometry for actual visitor screen-space size and avoid multiplying unique2K families. Lower-LOD-first downloads/hero-region residency need a separate measured owner/cache change, not a silent streaming rewrite here.

Physical local-operator procedure: run the same opt-in production build on the integrated-GPU laptop, record exact CPU/GPU/browser/OS, clear cache for one cold run, then compare the two queries at identical viewport/nativeDPR/quality. Collect60second movement/map/stage windows and10 return/playback cycles using existing diagnostics, including p50/p95/p99, draw/triangle/resource counters and network. Repeat on physical iPhone/Android without browser emulation and identify thermal/power state. Do not compare those numbers to SwiftShader as equivalent hardware.

**Stop:** two adjoining refined regions and associated transitions only. No full-quarry detail rollout, cave/tunnel/stall/crowd/stage reconstruction or deployment. Human visual review is required before propagation. The later user request authorizes committing/pushing this completed work and a fast-forward merge into the existing `work-in-progress-2027` branch; it does not authorize any additional art rollout or deployment.
'''
(ROOT/'docs/gullyverse-stage-2c5-1-rock-realism-refinement.md').write_text(report)
print('report written')
