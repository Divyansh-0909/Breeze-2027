# Gullyverse Stage 2B — one wall geometry correction

Date: 2026-10-12. **Material preserved; geometry candidate awaits visual approval.** The normal/default website retains its approved procedural quarry. No commit, push or deployment occurred. No other wall section, entrance, tunnel, stage, stall or population asset was replaced.

## Starting state and preservation

Branch **`codex/navigation-board`**, HEAD **`e3dbbc233f1f12f5e4d96333db3b797e75da4760`**. The starting worktree already modified `AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx` and `rendering.tsx`; prior wall helpers, tests, Blender sources, runtime exports and reports were untracked. Nothing was reset, restored or cleaned. The snapshot status was recorded after creating this evidence directory, before production edits. [Exact initial status/diffs](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/starting-state.json) and [recoverable source/asset snapshot](../reports/stage-2b-wall-geometry-correction-2026-10-12/backup/current-wall-candidate.tar.gz).

A 100-file hash comparison preserves **94 files exactly**, including the original stage/crowd/media assets, locked maps, old pilot sources/exports, world configuration and lighting sources. Six targeted runtime/test files differ from that starting snapshot. [Preservation check](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/preservation-check.json); [task-only source patch](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/task-source-changes.patch). This patch distinguishes this task from the existing dirty worktree.

Current dimensions, world anchors, global Hub/Aftermovie lighting, fog, exposure, navigation, movement polygons, camera compositions and map policy remain unchanged. `rendering.tsx` was not edited further. Existing payment/admin/forms/routes were untouched.

## Geometry and actual neighboring surfaces

The prior candidate replaced only the inward pentagonal face with an approximately 2 m deep capped panel. Its ends and join with the occluding procedural neighbors read as a flat applied patch.

The correction authors **one entire existing Rock 4 as a closed volume**. Its inward face wraps onto five original return faces; unequal geological units, finite branching fractures, localized chips and unequal recesses replace the former uniform depth. It carves inward within the original solid rather than expanding the quarry. Original 20 host corners and outer skyline edges are retained. The host's existing bounds are approximately **x 40.670–63.876, y −10.526–22.792, z −76.079–−50.220 m**. Its unchanged anchor is **[42.1893349, 6.4880474, −63.6718422]**.

Actual topology inspection identified the adjacent Rocks 3 and 5. Four local contact faces are replaced with fitted carved skins, retaining their original perimeter and original untextured material colors. Rock 3's visible intersection lies inside its face, beyond the shared corner edge; ray inspection exposed a remaining straight occluder, so its **narrow intersection band** is also carved. This changes the underlying joining surfaces, without adding camouflage boulders. Rear closures stay embedded in their existing original solids. All three closed components intentionally retain the original rocks' internal overlaps.

The preview removes **144 original vertices / 48 triangles**: host range 216–323 and contact ranges 126–134, 135–143, 351–359 and 378–386. Every unrelated source attribute is byte-exact. Removing these surfaces prevents a duplicate exposed procedural wall under the new geometry. There is no separate plane in front of the original face. The wall meets existing terrain by intersection; no ground, route or rubble system was changed.

Source: [author](../scripts/blender/author_corrected_wall_section.py), [geology](../scripts/blender/corrected_wall_geometry.py), [fitted contacts](../scripts/blender/corrected_wall_joins.py). [Actual original host topology](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/host-topology.json); [visible contact ray investigation](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/visible-joins.log).

## Locked limestone and UV treatment

**All eight original image-file hashes are unchanged. The approved glTF material JSON, three embedded image byte streams and decoded pixels match the prior candidate exactly.** Normal strength remains approximately **0.58**; metallic remains zero; approved roughness/normal/color maps remain intact. No global light, exposure, sky or fog adjustment was made. [Material/geometry validation](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/geometry-material-validation.json).

UV changes are confined to fitting new geometry: adjacent faces unfold metrically; boundary UVs reflect into existing interior texels to avoid the old image's edge termination. Central body UVs remain unchanged; the existing **12 × 10 m** fine normal coordinates retain grain scale. The limestone has not been repainted. Original green host/contact material remains on retained exterior surfaces, which still contrasts visibly with the authored limestone.

Runtime maps remain one 1024² JPEG base color, one 1024² PNG normal and one 512² PNG packed AO/roughness/metalness. They share approximately **12.0 MiB** decoded RGBA-plus-mipmap payload by estimate, not measured driver VRAM. No new texture set or compression/loader requirement was introduced.

## Blender, glTF, LOD and collision validation

Editable [master](../assets-source/gullyverse/first-wall-corrected/first-wall-corrected.blend), packed [material-only library](../assets-source/gullyverse/first-wall-corrected/approved-limestone-material.blend), [reproducible author/export instructions](../assets-source/gullyverse/first-wall-corrected/README.md), [anchor/material manifest](../public/models/gullyverse/first-wall-corrected/manifest.json).

| Asset | Triangles | Export bytes |
|---|---:|---:|
| Editable master | 298,692 | .blend 47,190,432 |
| Near LOD0 | 32,000 | 2,893,100 |
| Middle LOD1 | 10,000 | 2,098,024 |
| Far LOD2 | 4,000 | 1,883,712 |
| Compound original-solid proxy | 108 | 6,220 |
| Combined runtime GLB | Three visual alternatives plus hidden proxy | 3,476,816 |

Blender **4.3.2**, metre units, identity object transforms, Blender Z-up → glTF Y-up. All source/master/LOD/proxy meshes are closed with **zero non-manifold edges and positive signed volume**. Exported visual meshes also pass exact-position welded topology checks across material/UV seams: no open/non-manifold edges, consistent winding and positive volume for each closed component. Five GLBs pass Khronos Validator **2.0.0-dev.3.10**, **zero errors and warnings**. Informational notices concern unused UV/tangent attributes on untextured retained-color primitives. Textured limestone normals/tangents and both UV sets are validated; unused green tangents do not drive a normal map. [Master inspection](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/master-inspection.json), [exported topology](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/exported-topology-validation.json), [glTF validation](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/glTF-validator.json), [inventory](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/asset-inventory.json).

Only one LOD root renders at a time. Each contains three material primitives, not overlapping visible LODs. Existing projected-pixel thresholds, adaptive quality scaling and hysteresis are retained; new bounds cover the visible limestone. All alternatives warm sequentially under cover, share maps, and are frustum culled after preparation. Collision is a separate hidden **108-triangle original-solid proxy**, verified by browser raycast; existing walking polygons remain authoritative.

Outer host-edge deviation after decimation is at most **3.80 mm** in sampled tests. Contact perimeters have measured LOD-dependent deviations up to **36.68 mm**; this is not a mathematical guarantee of perfectly welded neighbors. Actual assembled scene BVH tests found zero newly uncovered old wall hits in sampled Hub, long and stage views. Two rays at the top border of the close inspection reveal sky after local carving. [Seam/ray measurements](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/scene-seam-validation.json). Browser inspection did not show flickering duplicate faces; this does not prove all possible angles free of intersections.

## Browser evidence and visual verdict

[Before/after browsable gallery](../reports/stage-2b-wall-geometry-correction-2026-10-12/gallery.html) contains original-resolution PNGs at identical cameras: front, close, left/right diagonals, top/bottom, adjacent formations, Hub, long quarry view and public aerial map. Desktop viewport **1366 × 900**, near views effective DPR **1**, FOV **58°**, quality **0**. Public map uses its existing camera (about y **165.934 m**, FOV **64°**, DPR **0.6**) in both versions. Additional actual LOD0/1/2 and **390 × 844 portrait** views record their effective DPR, quality and responsive FOV. Metadata: [before](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/before-captures.json), [after](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/after-captures.json), [LOD/mobile](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/extra-captures.json).

Recordings: [Public keyboard approach/retreat](../reports/stage-2b-wall-geometry-correction-2026-10-12/recordings/page@0648ae88934e21c08b4c39f8baaff19a.webm); [Eye-height side inspection dolly](../reports/stage-2b-wall-geometry-correction-2026-10-12/recordings/page@1058fc87cb15424e19ea9632af3bd95a.webm). Public W/A/S movement stays inside unchanged Hub bounds and records automatic LOD changes. The wall is outside the existing close-access walking zone; the second recording is explicitly a **diagnostic eye-height camera dolly**, not normal player walking or changed camera configuration. Recordings use the real browser renderer and are excluded from performance windows.

**Geometry/integration visual verdict: PARTIAL, pending review.** Depth and geological returns improve the rejected panel. Unequal edges and local contact carving reduce its straight termination. Some close-up chips remain triangular/saw-toothed; some broad units still read as block-like. The untouched green blockout neighbors and material transitions remain conspicuous from certain views. This is not photorealism, and the stricter requirement that no artificial patch can be perceived from every ordinary view is not proven. Do not scale this candidate across the quarry before human review.

## Matched software-renderer comparison

Debian 13 cloud VM; **3 AMD EPYC virtual CPUs**, Chromium **151**, ANGLE **SwiftShader Vulkan software rendering**. No accessible physical GPU, iPhone or Android device. Physical desktop/mobile acceptance remains **UNVERIFIED**. [Hardware profile](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/hardware.json).

Same localhost production setup, **1366 × 900**, effective DPR **0.5**, quality **0**, three fixed matched camera windows of 10 seconds, no recording or CPU/network throttling. Raw animation-frame samples are bounded by window start/end. FPS is counted frames / observed duration; quantiles use sorted actual frame intervals. These are small software-renderer samples, not sustained hardware or walking benchmarks.

| View | FPS before → after | p50 ms | p95 ms | p99 ms | Draw calls | Visible triangles |
|---|---:|---:|---:|---:|---:|---:|
| near | 1.60 → 2.39 | 624.0 → 415.7 | 670.2 → 484.9 | 670.2 → 486.4 | 12 → 14 | 81,717 → 92,172 |
| medium | 2.16 → 2.59 | 472.2 → 379.7 | 549.9 → 477.0 | 586.2 → 481.3 | 17 → 19 | 97,769 → 102,434 |
| hub | 2.43 → 2.69 | 414.3 → 372.2 | 470.6 → 438.1 | 472.6 → 454.6 | 17 → 19 | 97,769 → 102,434 |

Old combined asset **2,812,828 bytes** versus **3,476,816 bytes** corrected. Texture count remains **28** in matched active views; settled geometry count is **146 → 152**, explained by six additional material primitives across the three LODs. Corrected geometry deliberately costs more triangles and two extra calls in these views. Any observed software FPS improvement is not a certified speedup; scheduling, coverage and warm-up affect these single samples. Raw: [before performance](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/before-performance.json), [after performance](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/after-performance.json).

| First optional preparation | Load-ready ms | Parse/decode ms | Texture init CPU ms | Compile promise ms | Covered warm ms |
|---|---:|---:|---:|---:|---:|
| Previous | 772.6 | 261.5 | 13.5 | 44.8 | 3451.4 |
| Corrected | 671.2 | 377.9 | 9.9 | 43.7 | 2943.0 |

Load-ready includes local delivery and parse; compile promise is not GPU execution timing; covered preparation includes multiple hidden renders and software scheduling. No GPU timer/driver VRAM measurement was available. Whole-site cold transfer was not re-benchmarked; the default path is verified to request neither candidate GLB. Full uncompressed optional payload is the combined GLB size above.

## Ownership, tests and preserved interactions

The optional session owns a bounded GLTF cache. Clones borrow its geometries/materials; no shared stage/cache eviction occurs. Ten final preview off/on cycles plateau at **28 textures / 152 geometries** and GL texture/buffer/program proxies **(32, 582, 24)**. Cache retirement returns to original **25 textures / 143 geometries**, GL proxies **(29, 528, 22)**, matching original **(29, 528, 22)**. Off alone intentionally retains the reusable cache. Heap samples are included, without forced collection or a leak-free JS-heap claim. [Lifecycle results](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/lifecycle.json).

Ten movie/exit cycles with the corrected runtime and preview changes during playback plateau at **28 Three textures / 32 tracked GL textures**, with restored activation pose. This suite ran before the final localized contact-band carve; rendering code, material ownership and video code were unchanged by that geometry-only refinement. Final preview cycles, GLB/mesh checks, recordings and matched measurements were rerun afterward. [Playback results](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/video-with-wall.json).

* `npx tsc --noEmit`: PASS. `npm run test:immersive`: **62/62 PASS**, including a new test proving the host/contact cut leaves all unrelated quarry attributes exact.
* `npm run lint`: PASS with repository warnings; none reported in the six modified runtime/test files. Production `npm run build`: PASS, rerun against final manifest/assets. Builds use inert local Supabase placeholders and opt-in preview/inspection flags; environment files are not edited and production data is not accessed.
* Existing browser suite: all eight groups PASS: deliberate entrance/tunnel, editable focus release, blur/visibility, map/projection/resize, playback restoration, boundary/hysteresis, Home/direct/history and touch/reduced motion.
* Corrected opt-in checks: seven PASS: proxy raycast, directional stage travel/same Canvas, movie/Escape, boundary/map/history, context recovery, failed optional GLB retry and abandoned load disposal. Additional default critical-asset fallback, delayed stage navigation interruption and context loss during playback PASS. Portrait touch pad/map/boundary PASS.

[Browser command journal](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/browser-command-results.json); [final candidate reruns](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/final-candidate-browser-commands.json); [final validation/build commands](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/final-validation-commands.json); [unit log](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/unit-final.log); [typecheck](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/typecheck-final.log); [lint](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/lint-final.log); [build](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/final-build.log); [opt-in results](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/opt-in-regressions.json); [touch](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/touch-optin.json); [loading interruption](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/interruption.json); [production default/fallback](../reports/stage-2b-wall-geometry-correction-2026-10-12/raw/production-smoke.json).

Early authoring trials and one serialization failure are retained in raw/trials, clearly excluded from final acceptance. The initial right inspection fixture was inside an existing neighboring rock; it was repaired to an outside pose and both candidate captures were repeated. No test assertion was weakened to accept application failures.

## Exact source changes and stop

| File | Purpose |
|---|---|
| `components/immersive/wallSection.ts` | Corrected/previous URLs, full-host/local-contact removal, fit validation; existing cache ownership retained |
| `components/immersive/QuarryWallSection.tsx` | Group-based multi-material LOD roots, approved material discovery and sequential covered warm-up |
| `components/immersive/HubScene.tsx` | Select original/face/volume geometry copy only |
| `components/immersive/AftermovieScene.tsx` | Pass replacement mode; stage JSX/assets unchanged |
| `components/immersive/ImmersiveShell.tsx` | Explicit previous-candidate opt-in for matched comparisons |
| `tests/immersive/wall-section.test.ts` | One additional exact preservation regression test |

New files are the three authoring scripts, corrected source/export directory, this report, and evidence/reproduction scripts under `reports/stage-2b-wall-geometry-correction-2026-10-12`. Original candidate, texture files and prior reports are intact.

Preview: `/?diagnostics&wallPreview=limestone`; preserved previous: add `&wallCandidate=previous`. Local production review builds require `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`; ordinary URLs show the original approved quarry. The preview's **Original quarry** button restores it immediately.

**Stop here for visual approval.** Remaining work is review of fracture/chip quality, limestone-to-blockout continuity and LOD seam visibility on a physical GPU. No further section is authorized. Keep shared materials and measured per-section LOD limits when considering scaling; three more primitives per distant segment and high-detail stage/crowd residency must be budgeted together. This pilot does not establish a full-quarry capacity or physical 60 FPS guarantee. The self-contained review ZIP contains the report, PNGs, metadata, recordings, final source/exports and reproducible authoring inputs, without credentials or unrelated application data.
