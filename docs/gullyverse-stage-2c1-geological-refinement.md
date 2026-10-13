# Gullyverse Stage 2C.1 — Geological silhouette and continuity proof

2026-10-13 · **Two adjoining sections only, opt-in, awaiting human visual approval.** No commit, push or deployment. Physical GPU testing remains pending and does not block this bounded authoring proof.

## Preserved starting state

Branch `codex/navigation-board`, HEAD `e3dbbc233f1f12f5e4d96333db3b797e75da4760`. Staging was empty. Four tracked files already had changes (`AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx`, `rendering.tsx`); earlier pilot/rollout source and assets were untracked. [Exact initial status](../reports/stage-2c1-geological-refinement-2026-10-13/raw/starting-state.json), [initial hashes](../reports/stage-2c1-geological-refinement-2026-10-13/raw/baseline-hashes.json), [final preservation check](../reports/stage-2c1-geological-refinement-2026-10-13/raw/preservation.json).

**459 of 462 protected files are byte-identical; three existing integration files changed.** Original Stage 2C GLBs/master/maps, original stage/crowd/video, ground, scaffold/signs, stalls/Team/Contact placement, tunnel/passages, coordinates, lighting/fog/exposure, cameras/map and movement/travel systems are preserved. Payment/admin/routes were not edited. The recoverable initial snapshot, including relevant untracked work, is at `reports/stage-2c1-geological-refinement-2026-10-13/backup/current-stage-2c-baseline.tar.gz` (workspace-only; excluded from the review ZIP to avoid unrelated source). Credentials/environment files are excluded.

Walking-area extent remains 97.8 × 123.5 m; original surrounding-solid bounds remain 142.62 × 159.36 m. Stage origin remains `[-12, 0, -134.3]`. The two visual regions span approximately −122.8° to −93° around `[-0.9, 0, -103.75]`, at the left perimeter outside player bounds. Their original terrain contact is retained; the upper contours are intentionally changed as authorized. No global enlargement, shrinkage or lighting correction was made.

## Root causes and bounded correction

| Finding | Evidence and correction |
| --- | --- |
| Independent pointed masses | Stage 2C retained extreme pentagonal-envelope corners and carved each envelope radially. That preserved pointed peaks and unrelated inclined faces. The new pair uses a **shared broad excavation curve**, uneven crest and finite bedding/joint networks across both anchors. It does not globally smooth the other walls or add noise to conceal them. |
| Dark wedges | Baseline meshes are closed/consistently wound with no detected self-intersections in these two sections. One small LOD2 corner-normal disagreement is recorded. Browser normal-disabled views still retain large dark shapes. The approved colour/ORM atlas contains **olive unpainted padding outside a pentagonal island**; rectangular UV reuse sampled it. New UV0 stays in the painted interior, at the same UV derivative/grain scale. [Diagnosis](../reports/stage-2c1-geological-refinement-2026-10-13/raw/baseline-geometry-diagnosis.json), [browser diagnostics](../reports/stage-2c1-geological-refinement-2026-10-13/raw/before-shading-diagnostic.json), [approved colour atlas](../reports/stage-2c1-geological-refinement-2026-10-13/raw/approved-embedded-map-2.jpg). |
| Artificial join | Separate closed region meshes drew a thin division even with matching contour samples. The two regions are now **one welded watertight volume**, with internal duplicate caps removed and continuous normals/UVs. Both regions share one LOD selection. |
| Early closing-surface folds | Sparse UV-domain triangle fans crossed concave physical boundaries. Closures now follow their actual outlines; collinear boundary samples remain, and the curved crown retains coherent rows. Failed candidates and their coverage results remain under `trials/`; they are not represented as final passes. |

The new crest tops out at approximately 30.7 m across this pair (old region maxima approximately 34.85 / 28.24 m). Broad height variation, open roof and functional clearances remain. Interrupted, unequal fractures and localized chips provide medium-scale forms; the approved fine-normal texture supplies small detail. Geological realism is **not certified** by density or PBR alone.

## Material, source and exports

The exact current `Approved_Cool_Grey_Limestone_Family` is **borrowed from the live Stage 2C asset**, including base colour, ORM, normal texture, normal strength ~0.58 and all material values. Original map bytes remain unchanged. Normal UV1 retains 12 × 10 m scale. UV0 alone is remapped into the painted island (`u 0.22–0.72`, `v 0.24–0.75`); no pixels, exposure, fog, sky or light settings are changed. Surface highlights can differ because geometry/normals and previously invalid atlas sampling differ.

[Editable Blender master](../assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend) · [workflow](../assets-source/gullyverse/quarry-refinement/README.md) · [runtime GLB](../public/models/gullyverse/quarry-refinement/refined-pair.glb) · [manifest](../public/models/gullyverse/quarry-refinement/manifest.json) · [inventory/hashes](../reports/stage-2c1-geological-refinement-2026-10-13/raw/asset-inventory.json).

Blender **4.3.2**, metres, Z-up authoring → glTF Y-up. Separate editable region masters are retained; runtime exports use `Refined_Pair_LOD0/1/2`. Four final GLBs pass Khronos validation with zero errors/warnings; unused UV/tangent attributes on the deliberately geometry-only placeholder are informational. Original material-bearing exports and unquantized geometry are retained beside the source.

| Export | Actual file size | Visual triangles |
| --- | ---: | ---: |
| Combined runtime | 1,210,456 bytes | All three alternatives cached; one drawn |
| Near LOD0 | 669,276 bytes | 21,784 (old pair 24,000) |
| Middle LOD1 | 317,288 bytes | 9,368 (old pair 10,000) |
| Distant LOD2 | 224,760 bytes | 6,100 (old pair 2,400) |

The distant level costs more to retain crest/contact continuity. Near/middle counts decrease. Native `KHR_mesh_quantization` uses the existing loader; no Draco/Meshopt/KTX2 dependency is added. No new texture download/upload is required: the shared three-map family is approximately **12 MiB decoded RGBA+mip estimate**, **0 incremental texture payload**. This is not measured driver VRAM.

## Integration, collision and LOD

Review URL: `/?arrival=hub&quarryReview=geology`, permitted in development or a build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`. The review panel switches **Stage 2C baseline / Refined pair**. Default URLs keep Stage 2C and do not request this asset. `?quarry=original` remains the prior reversal. Leaving the immersive shell/reloading without the opt-in query restores the default.

Only baseline parts 22/23 are removed from the render clone; all other quarry/collar/tunnel parts remain. There is no second rock panel placed in front of them. The joined volume uses one screen-space LOD based on actual FOV, drawing-buffer height, distance, adaptive tier and existing hysteresis (720/220 pixel thresholds, tier scaling, 78%/72% retention). Only one alternative draws. The retained original movement polygons/solid proxies remain the collision authority; the new wall is outside active travel/walking/tunnel clearances.

[GLB topology](../reports/stage-2c1-geological-refinement-2026-10-13/raw/exported-topology-validation.json) confirms closed consistently wound positive-volume meshes. [Shape/seam checks](../reports/stage-2c1-geological-refinement-2026-10-13/raw/shape-seam-validation.json) find no detected self-intersections, opposed normal loops or missing shared contour samples. [Perimeter coverage](../reports/stage-2c1-geological-refinement-2026-10-13/raw/perimeter-coverage.json) retains all **301 horizontal source-blocked rays** with zero new gaps, plus the upward survey. **6,942 local ray samples** have zero exposed LOD hit disagreements. Tangent differences hidden *before the new wall* by unchanged neighbors are explicitly retained in the raw data; they are not silently counted as exposed passes.

The 13 original-envelope upward differences and existing full-world LOD differences remain recorded. Four coarse Stage 2C→candidate visibility samples gain coverage; no new loss is reported in that coarse comparison. This is sampled evidence, not a universal no-gap claim. [LOD walkthrough](../reports/stage-2c1-geological-refinement-2026-10-13/raw/lod-walkthrough.json) observes actual LOD0 → LOD1 → LOD2, with the distant level reached through the public aerial map.

## Browser comparison and recording

[**Open the comparison gallery**](../reports/stage-2c1-geological-refinement-2026-10-13/gallery.html): **15 matched pairs / 30 PNGs**, plus normal/wireframe diagnostics and three LOD captures. Original PNG resolution is retained. Desktop 1366 × 900; mobile portrait 390 × 844, **touch emulation**, not physical mobile. Primary views include frontal wall, join, close fractures, medium distance, low-angle crest, along-wall, quarry context, aerial and stage lighting. Camera position/quaternion/FOV, requested/effective DPR and tier are recorded. [Exact pose/viewport/tier comparison](../reports/stage-2c1-geological-refinement-2026-10-13/raw/capture-pair-validation.json) · [before metadata](../reports/stage-2c1-geological-refinement-2026-10-13/raw/before-captures.json) · [after metadata](../reports/stage-2c1-geological-refinement-2026-10-13/raw/after-captures.json) · [stage lighting pair](../reports/stage-2c1-geological-refinement-2026-10-13/raw/stage-lighting-comparison.json).

[Actual browser walkthrough — MP4](../reports/stage-2c1-geological-refinement-2026-10-13/recordings/geology-inspection-walkthrough.mp4) · [original WebM](../reports/stage-2c1-geological-refinement-2026-10-13/recordings/geology-inspection-walkthrough.webm). The recording uses labelled inspection positions alongside the wall, then the **public aerial map**, with the real LOD selector. It is not evidence that normal walking bounds permit visiting those inspection positions. Separate public-controls movement/travel is tested below. No offline/concept/AI images replace website evidence.

The selected wall reads as a broader excavation, with less pointed crest and fewer wedge-like faces. A highlighted near-vertical joint still deserves visual review in close angled views; welded topology does not by itself establish visual realism. Neighboring sharp Stage 2C masses and their atlas artifacts remain intentionally unchanged. No pixel-identical or photorealism claim is made.

## Matched software-renderer performance

Chromium 151.0.7922.173 built on Debian GNU/Linux 13 (trixie); Debian 13 Linux VM, AMD EPYC 9V74 host, **two-vCPU quota**, 8 GiB container limit. Actual WebGL renderer is ANGLE/Vulkan **SwiftShader**; no `/dev/dri` or physical mobile was available. The comparison uses fresh production-browser contexts, identical fixed cameras, 1366 × 900, DPR **0.5**, quality **3**, no artificial throttling, sequential ten-second windows and no competing Blender/recording workload. It compares the current Stage 2C default with this opt-in pair; it does **not** compare historical three-vCPU results as equivalent hardware.

| View | Mean FPS before → after | p50 ms | p95 ms | p99 ms | Calls | Visible triangles |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wall | 2.86 → 2.82 | 327.4 → 351.7 | 448.5 → 400.2 | 466.0 → 407.7 | 33 → 32 | 153,756 → 153,124 |
| medium | 2.32 → 3.06 | 410.0 → 316.8 | 497.7 → 392.6 | 507.8 → 396.0 | 31 → 30 | 151,500 → 150,868 |
| context | 3.59 → 3.99 | 274.4 → 243.4 | 317.8 → 326.7 | 318.3 → 355.8 | 154 → 153 | 161,202 → 160,570 |

A single paired run is noisy; mean/median improvement in some windows does not prove hardware smoothness. Tail stalls remain substantial. Fresh active geometry counts change 222 → 219 because six old visual alternatives are replaced by three joined alternatives; active geometry payload proxy is approximately 18.43 → 18.45 MB. Textures remain 28, total scene decoded texture estimate 57.61 MB. Heap snapshots are retained, not a retained-heap leak proof. [Before raw frames](../reports/stage-2c1-geological-refinement-2026-10-13/raw/before-performance.json) · [after raw frames](../reports/stage-2c1-geological-refinement-2026-10-13/raw/after-performance.json) · [hardware](../reports/stage-2c1-geological-refinement-2026-10-13/raw/hardware-profile.json).

Cold cache-disabled localhost transfer is **14,859,731 → 15,665,328 bytes**, including response overhead; landing+asset readiness is **6845.7 → 6966.8 ms**. The opt-in adds geometry, not duplicate maps. One review run records parse **2.1 ms**, combined load **131.0 ms**, shader preparation **40.8 ms** and covered preparation **2072.9 ms**. GPU shader caches may persist between contexts. [Network/preparation evidence](../reports/stage-2c1-geological-refinement-2026-10-13/raw/network.json).

**Physical desktop/integrated GPU, iPhone/Android and sustained 60/30 FPS acceptance: PENDING.** [Reproducible local procedure](../reports/stage-2c1-geological-refinement-2026-10-13/raw/local-hardware-procedure.md). Those profiles do not block the authoring proof, as instructed.

## Ownership and regression results

The base shell owns its original asset/material cache; refinement owns only three geometries. A parsed placeholder material is disposed before binding the borrowed family. Scene clones do not dispose shared resources. Failed candidate loading restores Stage 2C, abandonment disposes unpublished geometry, and covered restoration precedes retirement. All three new LODs remain resident/warmed; no streaming manager was introduced.

Ten enable/disable cycles plateau after warm-up at **28 textures / 225 geometries / 32 tracked GL textures / 1024 buffers / 22 programs**. Explicit refinement retirement returns **222 geometries**, retaining texture counts. Ten Hub↔Aftermovie map round trips and ten actual playback/exit/restored-camera cycles also plateau; repeated toggles during playback preserve stage/video. [Toggle counters](../reports/stage-2c1-geological-refinement-2026-10-13/raw/lifecycle.json) · [navigation](../reports/stage-2c1-geological-refinement-2026-10-13/raw/navigation-cycles.json) · [playback](../reports/stage-2c1-geological-refinement-2026-10-13/raw/video-with-wall.json). This does not certify driver VRAM as leak-free.

| Verification | Result |
| --- | --- |
| Type check, lint, production build | PASS; existing lint warnings. Build requires project Supabase configuration; the first missing-config admin prerender failure is preserved. Inert local build values were used, with no backend/admin source or data change. |
| Unit tests | **66 PASS**, including two new substitution/borrowed-resource ownership cases. |
| Existing browser groups | **8 default + 8 opt-in PASS**: entry timing/Canvas, held focus/input, blur/recovery ownership, map validity/resize, playback restore, boundary/hysteresis/history, Home/direct/reload, touch/reduced motion. |
| Public directional travel | PASS: actual KeyS gate → covered Aftermovie → boundary/Esc/re-entry → Return to Hub. Walking+travel takes 18.11s in this software renderer, not a physical-device acceptance time. |
| Recovery/failure | **6 PASS**: actual context loss/restore, quarry failure/retry, delayed native abandonment, refinement failure/retry, refinement abandonment and critical-stage fallback. |
| Resource cycles | **10 toggles + 10 round trips + 10 playback/exit cycles PASS**. |
| Asset/topology/coverage | PASS within the documented sampled scope. |
| LOD recording | PASS after harness correction: the first camera path remained in LOD1 because of valid hysteresis; the public aerial map now proves LOD2. Original failed recording/JSON are retained. |
| Physical hardware / complete-quarry visual approval | PENDING / outside this two-section proof. |

[Summary and commands](../reports/stage-2c1-geological-refinement-2026-10-13/raw/test-summary.json) · [main browser command log](../reports/stage-2c1-geological-refinement-2026-10-13/raw/browser-commands.json) · [extra browser commands](../reports/stage-2c1-geological-refinement-2026-10-13/raw/extra-browser-commands.json) · [directional controls](../reports/stage-2c1-geological-refinement-2026-10-13/raw/directional-travel.json) · [recovery](../reports/stage-2c1-geological-refinement-2026-10-13/raw/recovery.json). No unresolved reproduced functional regression remains in these checks. Historical/failed trials are preserved, not hidden.

## Files changed and next recommendation

Existing integration files: `ImmersiveShell.tsx` adds opt-in review creation/controls; `QuarryPerimeter.tsx` substitutes the render clone, coordinates LOD and waits for geometry preparation; `wallSection.ts` exposes publication to the bounded subclass. [Exact diff against the initial worktree](../reports/stage-2c1-geological-refinement-2026-10-13/raw/source-changes.patch).

New files: `RefinedQuarrySession.ts`, `refined_quarry_geology.py`, `prepare_refined_pair.py`, `author_refined_quarry_pair.py`, `pack_refined_quarry.py`, `quarry-refinement.test.ts`, source/exports/manifests, report and evidence scripts. Original stage, navigation, camera, input and lighting implementations are unchanged.

Recommended next step is **human review of this pair**, then controlled propagation of the shared excavation/crest/fault and atlas-island technique if approved. Preserve the existing footprint and world features. Use small joined groups to avoid independent tips/caps and mismatched adjacent LODs, while checking group radius/frustum effects. This proof's near/middle budget is about 22k/9.4k triangles per ~32m group; distant 6.1k remains a tradeoff, not a validated production budget. Do not multiply it across the whole quarry as a certified device limit.

Initial Stage 2C transfer/residency is still large. Future measured improvements can separate shared maps from geometry, prioritize middle/distant geometry before reveal, prefetch near detail in the covered approach, and reduce duplicated LOD data. The geometry-only borrowed-material pilot demonstrates avoiding repeated maps. **No broad streaming rewrite is made here.** Compression changes require separate decoder/quality/upload measurements.

Remaining visual work: unrefined perimeter masses, close-range artist refinement of fractures/mineral geometry, edge/terrain transitions in later groups, and the deferred entrance/tunnel/stall/population art. Ground, scaffold, stage and all approved styling remain locked. Physical GPU/mobile profiling is a release-readiness requirement, not a reason to undo approved visuals.

**Stop here. Do not propagate the pair until the user approves it.**
