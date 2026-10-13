from pathlib import Path
import json
root=Path.cwd();r=root/'reports/stage-2c1-geological-refinement-2026-10-13';raw=r/'raw';rel='../reports/'+r.name
load=lambda n:json.loads((raw/n).read_text())
state=load('starting-state.json');pres=load('preservation.json');inv=load('asset-inventory.json');manifest=inv['manifest'];a=load('before-performance.json');b=load('after-performance.json');network=load('network.json');life=load('lifecycle.json');coverage=load('perimeter-coverage.json');shape=load('shape-seam-validation.json');record=load('lod-walkthrough.json');video=load('video-with-wall.json');direction=load('directional-travel.json');hardware=load('hardware-profile.json')
assert life['status']==record['status']==shape['status']==coverage['status']=='PASS'
assert len(life['cycles'])==len(video['cycles'])==10
assert all(x['status']=='PASS'for x in video['checks']+direction['checks'])
checks=[]
for name in ['default-regressions','candidate-regressions']:
 data=json.loads((raw/name/'results.json').read_text());assert len(data['checks'])==8 and all(c['status']=='PASS'for c in data['checks'])and not data['errors'];checks.append({'group':name,'checks':data['checks'],'errors':data['errors']})
recovery=load('recovery.json');assert all(x['status']=='PASS'for x in recovery['checks']);assert len(recovery['checks'])==6
summary={'status':'PASS','typecheck':'npx tsc --noEmit (pass)','unit':'npm run test:immersive — 66 pass, 0 fail','lint':'npm run lint — pass, existing warnings','build':'npm run build — pass with review flag and inert local Supabase build configuration; original missing-configuration failure preserved','browserGroups':checks,'recovery':recovery['checks'],'tenToggleCycles':'PASS','tenNavigationRoundTrips':'PASS','tenPlaybackExitCycles':'PASS','directionalTravel':direction['checks'],'LOD0LOD1LOD2':'PASS','glTFValidation':'4 exports, 0 errors/0 warnings; unused attributes informational','geometryAndCoverage':'PASS; inherited/authorized skyline differences separately published','physicalGPU':'PENDING','physicalMobile':'PENDING','recordingHarnessCorrection':'First attempt did not reach LOD2 due hysteresis, final public aerial-map path reaches all 3 levels; original failed evidence retained.'}
(raw/'test-summary.json').write_text(json.dumps(summary,indent=2))
perf=[]
for x,y in zip(a['windows'],b['windows']):
 old=x['after']['stats'];new=y['after']['stats'];perf.append(f"| {x['name']} | {x['FPS']:.2f} → {y['FPS']:.2f} | {x['p50']:.1f} → {y['p50']:.1f} | {x['p95']:.1f} → {y['p95']:.1f} | {x['p99']:.1f} → {y['p99']:.1f} | {old['calls']} → {new['calls']} | {old['triangles']:,} → {new['triangles']:,} |")
files={Path(x['path']).name:x for x in inv['files']if x['path'].startswith('public/')};size=lambda n:f"{files[n]['bytes']:,} bytes"
net0,net1=network['runs'];trace=net1['details']['wall']['trace'];timings={x['event']:x.get('ms')for x in trace if'ms'in x}
counts=life['cycles'][2]['refined']['counters'];afterRet=life['afterRetirement']['stats'];newTriangles=[next(x['triangles']for x in manifest['nodes']if x['name']==f'Refined_Pair_LOD{i}')for i in range(3)]
text=f'''# Gullyverse Stage 2C.1 — Geological silhouette and continuity proof

2026-10-13 · **Two adjoining sections only, opt-in, awaiting human visual approval.** No commit, push or deployment. Physical GPU testing remains pending and does not block this bounded authoring proof.

## Preserved starting state

Branch `{state['branch']}`, HEAD `{state['HEAD']}`. Staging was empty. Four tracked files already had changes (`AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx`, `rendering.tsx`); earlier pilot/rollout source and assets were untracked. [Exact initial status]({rel}/raw/starting-state.json), [initial hashes]({rel}/raw/baseline-hashes.json), [final preservation check]({rel}/raw/preservation.json).

**{pres['byteIdenticalFiles']} of {pres['protectedFiles']} protected files are byte-identical; three existing integration files changed.** Original Stage 2C GLBs/master/maps, original stage/crowd/video, ground, scaffold/signs, stalls/Team/Contact placement, tunnel/passages, coordinates, lighting/fog/exposure, cameras/map and movement/travel systems are preserved. Payment/admin/routes were not edited. The recoverable initial snapshot, including relevant untracked work, is at `reports/{r.name}/backup/current-stage-2c-baseline.tar.gz` (workspace-only; excluded from the review ZIP to avoid unrelated source). Credentials/environment files are excluded.

Walking-area extent remains 97.8 × 123.5 m; original surrounding-solid bounds remain 142.62 × 159.36 m. Stage origin remains `[-12, 0, -134.3]`. The two visual regions span approximately −122.8° to −93° around `[-0.9, 0, -103.75]`, at the left perimeter outside player bounds. Their original terrain contact is retained; the upper contours are intentionally changed as authorized. No global enlargement, shrinkage or lighting correction was made.

## Root causes and bounded correction

| Finding | Evidence and correction |
| --- | --- |
| Independent pointed masses | Stage 2C retained extreme pentagonal-envelope corners and carved each envelope radially. That preserved pointed peaks and unrelated inclined faces. The new pair uses a **shared broad excavation curve**, uneven crest and finite bedding/joint networks across both anchors. It does not globally smooth the other walls or add noise to conceal them. |
| Dark wedges | Baseline meshes are closed/consistently wound with no detected self-intersections in these two sections. One small LOD2 corner-normal disagreement is recorded. Browser normal-disabled views still retain large dark shapes. The approved colour/ORM atlas contains **olive unpainted padding outside a pentagonal island**; rectangular UV reuse sampled it. New UV0 stays in the painted interior, at the same UV derivative/grain scale. [Diagnosis]({rel}/raw/baseline-geometry-diagnosis.json), [browser diagnostics]({rel}/raw/before-shading-diagnostic.json), [approved colour atlas]({rel}/raw/approved-embedded-map-2.jpg). |
| Artificial join | Separate closed region meshes drew a thin division even with matching contour samples. The two regions are now **one welded watertight volume**, with internal duplicate caps removed and continuous normals/UVs. Both regions share one LOD selection. |
| Early closing-surface folds | Sparse UV-domain triangle fans crossed concave physical boundaries. Closures now follow their actual outlines; collinear boundary samples remain, and the curved crown retains coherent rows. Failed candidates and their coverage results remain under `trials/`; they are not represented as final passes. |

The new crest tops out at approximately 30.7 m across this pair (old region maxima approximately 34.85 / 28.24 m). Broad height variation, open roof and functional clearances remain. Interrupted, unequal fractures and localized chips provide medium-scale forms; the approved fine-normal texture supplies small detail. Geological realism is **not certified** by density or PBR alone.

## Material, source and exports

The exact current `Approved_Cool_Grey_Limestone_Family` is **borrowed from the live Stage 2C asset**, including base colour, ORM, normal texture, normal strength ~0.58 and all material values. Original map bytes remain unchanged. Normal UV1 retains 12 × 10 m scale. UV0 alone is remapped into the painted island (`u 0.22–0.72`, `v 0.24–0.75`); no pixels, exposure, fog, sky or light settings are changed. Surface highlights can differ because geometry/normals and previously invalid atlas sampling differ.

[Editable Blender master](../assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend) · [workflow](../assets-source/gullyverse/quarry-refinement/README.md) · [runtime GLB](../public/models/gullyverse/quarry-refinement/refined-pair.glb) · [manifest](../public/models/gullyverse/quarry-refinement/manifest.json) · [inventory/hashes]({rel}/raw/asset-inventory.json).

Blender **4.3.2**, metres, Z-up authoring → glTF Y-up. Separate editable region masters are retained; runtime exports use `Refined_Pair_LOD0/1/2`. Four final GLBs pass Khronos validation with zero errors/warnings; unused UV/tangent attributes on the deliberately geometry-only placeholder are informational. Original material-bearing exports and unquantized geometry are retained beside the source.

| Export | Actual file size | Visual triangles |
| --- | ---: | ---: |
| Combined runtime | {size('refined-pair.glb')} | All three alternatives cached; one drawn |
| Near LOD0 | {size('refined-lod0.glb')} | {newTriangles[0]:,} (old pair 24,000) |
| Middle LOD1 | {size('refined-lod1.glb')} | {newTriangles[1]:,} (old pair 10,000) |
| Distant LOD2 | {size('refined-lod2.glb')} | {newTriangles[2]:,} (old pair 2,400) |

The distant level costs more to retain crest/contact continuity. Near/middle counts decrease. Native `KHR_mesh_quantization` uses the existing loader; no Draco/Meshopt/KTX2 dependency is added. No new texture download/upload is required: the shared three-map family is approximately **12 MiB decoded RGBA+mip estimate**, **0 incremental texture payload**. This is not measured driver VRAM.

## Integration, collision and LOD

Review URL: `/?arrival=hub&quarryReview=geology`, permitted in development or a build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`. The review panel switches **Stage 2C baseline / Refined pair**. Default URLs keep Stage 2C and do not request this asset. `?quarry=original` remains the prior reversal. Leaving the immersive shell/reloading without the opt-in query restores the default.

Only baseline parts 22/23 are removed from the render clone; all other quarry/collar/tunnel parts remain. There is no second rock panel placed in front of them. The joined volume uses one screen-space LOD based on actual FOV, drawing-buffer height, distance, adaptive tier and existing hysteresis (720/220 pixel thresholds, tier scaling, 78%/72% retention). Only one alternative draws. The retained original movement polygons/solid proxies remain the collision authority; the new wall is outside active travel/walking/tunnel clearances.

[GLB topology]({rel}/raw/exported-topology-validation.json) confirms closed consistently wound positive-volume meshes. [Shape/seam checks]({rel}/raw/shape-seam-validation.json) find no detected self-intersections, opposed normal loops or missing shared contour samples. [Perimeter coverage]({rel}/raw/perimeter-coverage.json) retains all **301 horizontal source-blocked rays** with zero new gaps, plus the upward survey. **6,942 local ray samples** have zero exposed LOD hit disagreements. Tangent differences hidden *before the new wall* by unchanged neighbors are explicitly retained in the raw data; they are not silently counted as exposed passes.

The 13 original-envelope upward differences and existing full-world LOD differences remain recorded. Four coarse Stage 2C→candidate visibility samples gain coverage; no new loss is reported in that coarse comparison. This is sampled evidence, not a universal no-gap claim. [LOD walkthrough]({rel}/raw/lod-walkthrough.json) observes actual LOD0 → LOD1 → LOD2, with the distant level reached through the public aerial map.

## Browser comparison and recording

[**Open the comparison gallery**]({rel}/gallery.html): **15 matched pairs / 30 PNGs**, plus normal/wireframe diagnostics and three LOD captures. Original PNG resolution is retained. Desktop 1366 × 900; mobile portrait 390 × 844, **touch emulation**, not physical mobile. Primary views include frontal wall, join, close fractures, medium distance, low-angle crest, along-wall, quarry context, aerial and stage lighting. Camera position/quaternion/FOV, requested/effective DPR and tier are recorded. [Exact pose/viewport/tier comparison]({rel}/raw/capture-pair-validation.json) · [before metadata]({rel}/raw/before-captures.json) · [after metadata]({rel}/raw/after-captures.json) · [stage lighting pair]({rel}/raw/stage-lighting-comparison.json).

[Actual browser walkthrough — MP4]({rel}/recordings/geology-inspection-walkthrough.mp4) · [original WebM]({rel}/recordings/geology-inspection-walkthrough.webm). The recording uses labelled inspection positions alongside the wall, then the **public aerial map**, with the real LOD selector. It is not evidence that normal walking bounds permit visiting those inspection positions. Separate public-controls movement/travel is tested below. No offline/concept/AI images replace website evidence.

The selected wall reads as a broader excavation, with less pointed crest and fewer wedge-like faces. A highlighted near-vertical joint still deserves visual review in close angled views; welded topology does not by itself establish visual realism. Neighboring sharp Stage 2C masses and their atlas artifacts remain intentionally unchanged. No pixel-identical or photorealism claim is made.

## Matched software-renderer performance

{hardware['browser']}; Debian 13 Linux VM, AMD EPYC 9V74 host, **two-vCPU quota**, 8 GiB container limit. Actual WebGL renderer is ANGLE/Vulkan **SwiftShader**; no `/dev/dri` or physical mobile was available. The comparison uses fresh production-browser contexts, identical fixed cameras, 1366 × 900, DPR **0.5**, quality **3**, no artificial throttling, sequential ten-second windows and no competing Blender/recording workload. It compares the current Stage 2C default with this opt-in pair; it does **not** compare historical three-vCPU results as equivalent hardware.

| View | Mean FPS before → after | p50 ms | p95 ms | p99 ms | Calls | Visible triangles |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(perf)}

A single paired run is noisy; mean/median improvement in some windows does not prove hardware smoothness. Tail stalls remain substantial. Fresh active geometry counts change 222 → 219 because six old visual alternatives are replaced by three joined alternatives; active geometry payload proxy is approximately 18.43 → 18.45 MB. Textures remain 28, total scene decoded texture estimate 57.61 MB. Heap snapshots are retained, not a retained-heap leak proof. [Before raw frames]({rel}/raw/before-performance.json) · [after raw frames]({rel}/raw/after-performance.json) · [hardware]({rel}/raw/hardware-profile.json).

Cold cache-disabled localhost transfer is **{net0['CDPLocalEncodedBytes']:,} → {net1['CDPLocalEncodedBytes']:,} bytes**, including response overhead; landing+asset readiness is **{net0['at']:.1f} → {net1['at']:.1f} ms**. The opt-in adds geometry, not duplicate maps. One review run records parse **{timings['refinement-parse-ready']:.1f} ms**, combined load **{timings['refinement-load-ready']:.1f} ms**, shader preparation **{timings['shader-compile']:.1f} ms** and covered preparation **{timings['covered-ready']:.1f} ms**. GPU shader caches may persist between contexts. [Network/preparation evidence]({rel}/raw/network.json).

**Physical desktop/integrated GPU, iPhone/Android and sustained 60/30 FPS acceptance: PENDING.** [Reproducible local procedure]({rel}/raw/local-hardware-procedure.md). Those profiles do not block the authoring proof, as instructed.

## Ownership and regression results

The base shell owns its original asset/material cache; refinement owns only three geometries. A parsed placeholder material is disposed before binding the borrowed family. Scene clones do not dispose shared resources. Failed candidate loading restores Stage 2C, abandonment disposes unpublished geometry, and covered restoration precedes retirement. All three new LODs remain resident/warmed; no streaming manager was introduced.

Ten enable/disable cycles plateau after warm-up at **{counts['textures']} textures / {counts['geometries']} geometries / {counts['Texture']} tracked GL textures / {counts['Buffer']} buffers / {counts['Program']} programs**. Explicit refinement retirement returns **{afterRet['geometries']} geometries**, retaining texture counts. Ten Hub↔Aftermovie map round trips and ten actual playback/exit/restored-camera cycles also plateau; repeated toggles during playback preserve stage/video. [Toggle counters]({rel}/raw/lifecycle.json) · [navigation]({rel}/raw/navigation-cycles.json) · [playback]({rel}/raw/video-with-wall.json). This does not certify driver VRAM as leak-free.

| Verification | Result |
| --- | --- |
| Type check, lint, production build | PASS; existing lint warnings. Build requires project Supabase configuration; the first missing-config admin prerender failure is preserved. Inert local build values were used, with no backend/admin source or data change. |
| Unit tests | **66 PASS**, including two new substitution/borrowed-resource ownership cases. |
| Existing browser groups | **8 default + 8 opt-in PASS**: entry timing/Canvas, held focus/input, blur/recovery ownership, map validity/resize, playback restore, boundary/hysteresis/history, Home/direct/reload, touch/reduced motion. |
| Public directional travel | PASS: actual KeyS gate → covered Aftermovie → boundary/Esc/re-entry → Return to Hub. Walking+travel takes {direction['checks'][0]['walkingAndTravelMs']/1000:.2f}s in this software renderer, not a physical-device acceptance time. |
| Recovery/failure | **6 PASS**: actual context loss/restore, quarry failure/retry, delayed native abandonment, refinement failure/retry, refinement abandonment and critical-stage fallback. |
| Resource cycles | **10 toggles + 10 round trips + 10 playback/exit cycles PASS**. |
| Asset/topology/coverage | PASS within the documented sampled scope. |
| LOD recording | PASS after harness correction: the first camera path remained in LOD1 because of valid hysteresis; the public aerial map now proves LOD2. Original failed recording/JSON are retained. |
| Physical hardware / complete-quarry visual approval | PENDING / outside this two-section proof. |

[Summary and commands]({rel}/raw/test-summary.json) · [main browser command log]({rel}/raw/browser-commands.json) · [extra browser commands]({rel}/raw/extra-browser-commands.json) · [directional controls]({rel}/raw/directional-travel.json) · [recovery]({rel}/raw/recovery.json). No unresolved reproduced functional regression remains in these checks. Historical/failed trials are preserved, not hidden.

## Files changed and next recommendation

Existing integration files: `ImmersiveShell.tsx` adds opt-in review creation/controls; `QuarryPerimeter.tsx` substitutes the render clone, coordinates LOD and waits for geometry preparation; `wallSection.ts` exposes publication to the bounded subclass. [Exact diff against the initial worktree]({rel}/raw/source-changes.patch).

New files: `RefinedQuarrySession.ts`, `refined_quarry_geology.py`, `prepare_refined_pair.py`, `author_refined_quarry_pair.py`, `pack_refined_quarry.py`, `quarry-refinement.test.ts`, source/exports/manifests, report and evidence scripts. Original stage, navigation, camera, input and lighting implementations are unchanged.

Recommended next step is **human review of this pair**, then controlled propagation of the shared excavation/crest/fault and atlas-island technique if approved. Preserve the existing footprint and world features. Use small joined groups to avoid independent tips/caps and mismatched adjacent LODs, while checking group radius/frustum effects. This proof's near/middle budget is about 22k/9.4k triangles per ~32m group; distant 6.1k remains a tradeoff, not a validated production budget. Do not multiply it across the whole quarry as a certified device limit.

Initial Stage 2C transfer/residency is still large. Future measured improvements can separate shared maps from geometry, prioritize middle/distant geometry before reveal, prefetch near detail in the covered approach, and reduce duplicated LOD data. The geometry-only borrowed-material pilot demonstrates avoiding repeated maps. **No broad streaming rewrite is made here.** Compression changes require separate decoder/quality/upload measurements.

Remaining visual work: unrefined perimeter masses, close-range artist refinement of fractures/mineral geometry, edge/terrain transitions in later groups, and the deferred entrance/tunnel/stall/population art. Ground, scaffold, stage and all approved styling remain locked. Physical GPU/mobile profiling is a release-readiness requirement, not a reason to undo approved visuals.

**Stop here. Do not propagate the pair until the user approves it.**
'''
(root/'docs/gullyverse-stage-2c1-geological-refinement.md').write_text(text)
print('Wrote report',len(text),'bytes')
