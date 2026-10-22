# Gullyverse Stage 2C.9 — Native-scale scanned-rock composition

**Private, reversible implementation benchmark. Public C5.1 and approved C8 3× are preserved. No commit, push, merge or deployment.**

## Starting baseline and preservation

Inspected 2026-10-17 21:39:13 UTC on branch `codex/navigation-board`, HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. Nothing staged. `components/immersive/ImmersiveShell.tsx` and `components/immersive/QuarryFoundationSession.ts` were already modified before this task. There were **2,405 untracked paths**. The starting diff and complete inventory are retained separately; existing modifications are not attributed to C9.

Evidence root: `reports/stage-2c9-scanned-rock-composition-2026-10-17/`. `raw/starting-state.json`, `raw/starting-tracked.patch` and `raw/starting-hashes.json` record the state and 63 relevant source/config/runtime/master hashes. `backup/current-source-assets.tar.gz` is a 48,516,337-byte recoverable local snapshot, excluding credentials, environment files, dependencies and build output. Original source masters also remain in place with recorded hashes. The backup is excluded from the distributable ZIP.

`raw/preservation.json` verifies no missing original untracked paths and no changed historical assets. Only the two existing private-preview integration files differ among inspected sources. Branch and HEAD are unchanged. World registry, collision/travel rules, floor, stage, crowd, playback, scaffold, signs, stalls, Team/Contact, tunnel, cameras, map, global lights, exposure, fog and sky were not edited. Unrelated routes, forms, payment and admin code were not edited.

## Comparison modes

| Label | Private query | Geometry | Material |
|---|---|---|---|
| Public | ordinary URL / `foundation-refined` | C5.1 | Public baseline |
| A | `rock-calibration` | Original C6.2 | Original C6.2 |
| B | `scanned-material-multi` | Original C6.2 | Approved C8 **3×** |
| C | `material-continuity` | Original C6.2 | C8.1 optional contact, **3×** |
| D | `scanned-composition` | New local C9 crop and joins; remaining excavation retained | Approved C8 **locked 3×**, local LOD bake |

Use `/?arrival=hub&diagnostics&quarryReview=scanned-composition` with the existing development-preview gate enabled. Ordinary public URLs have no C9 controls or asset requests. C6/C6.1/C6.2, rejected C7 and failed C8 diagnostic modes remain available. C9 never loads failed `relief-region.glb`, does not use C7 geometry, and does not load a second complete-world GLB. A/B/C remain untouched comparisons, including their known physical geometry limitations. Actual browser hashing confirms A/B/C geometry is identical and only the three lower14 LOD buffers change in D; upper15 and all unrelated runtime meshes remain byte-identical.

## Source selection and real dimensions

All three actual C8.1 downloads were inspected, not just provider thumbnails. Units below are Blender X/Y/Z metres, Z-up.

| Genuine CC0 3D source | Native dimensions | LOD0 / LOD1 / LOD2 / LOD3 triangles | C9 assessment |
|---|---|---|---|
| [Coastal Cliff 01](https://polyhaven.com/a/coastal_cliff_01) | 91.980 × 10.967 × 10.326 | 461,824 / 230,912 / 115,455 / 57,726 | **Selected native crop**; recognizable broken beds, projecting ledges and real undercuts |
| [Mountainside](https://polyhaven.com/a/mountainside) | 10.209 × 5.247 × 10.522 | 153,472 / 76,735 / 38,366 / 19,182 | Plausible physical size, but the inspected surface has finer wrinkled/rilled relief than this benchmark needs |
| [Coastal Cliff 04](https://polyhaven.com/a/coastal_cliff_04) | 86.772 × 24.247 × 11.000 | 1,537,429 / 768,962 / 384,480 / 192,240 | Much heavier; terrain/caps/fragments complicate this small local interface without a demonstrated benefit |

These are open captured surfaces, not assumed watertight solid rocks. License: [Poly Haven CC0](https://polyhaven.com/license), permitting commercial use and redistribution. Provider provenance remains in `assets-source/gullyverse/quarry-material-continuity/research-sources/`; C9 records the selected file's SHA-256 in `source-provenance.json`. Original downloads are unchanged. This is scan-derived composition, **not a newly captured photogrammetry scan**.

A native Coastal Cliff 01 crop centred around source X −30 m measures approximately **10.390 × 4.992 × 8.419 m**. Four restrained, nonparallel trim planes select existing geology. One disconnected six-face trimming fragment, only **0.0334 m** across, is discarded in the working copy. No substantial opening is filled or hidden. The original source is untouched. `research/coastal-crop-selection.png` documents several genuine native crop options; it is an offline source diagnostic, not browser acceptance imagery.

The selected crop uses one **uniform 0.9× scale**, rigid rotation and translation. Its transformation singular values are 0.9/0.9/0.9; measured float32 transformation residual is approximately **0.00000426 m**. No 5–7× horizontal enlargement or depth flattening occurs. `research/source-placement.json` records the exact 4×4 Z-up matrix, native crop bounds and Y-up world bounds. The native feature occupies approximately X −47.987…−40.899, Y 0.55…8.627, Z −70.363…−60.809 m. Local wall arc centre is 327 m. The short host transition extends beyond the native crop footprint; it does not expand the study to the entire 35.557 m C6.2 region.

## Composition and joining method

The existing continuous excavation remains the spatial foundation. C9 modifies only a local portion of the lower `Wall_14` visual mesh. `Wall_15`, the upper rim, outer study boundaries and remaining quarry are retained. A source scan is allowed to provide the lower cliff formation rather than being stretched to the quarry's entire height.

1. Preserve the actual C6.2 outer boundary and original per-LOD host faces outside the selected footprint.
2. Trim a suitable native scan portion using plane cuts, preserving its genuine 3D ledges and recesses.
3. Rotate/translate it at uniform0.9 scale to the local wall inclination; preserve all physical aspect ratios.
4. Remove the covered host faces. The new rock is not placed over a still-exposed duplicate wall.
5. Connect the source boundary to the retained host hole using a short oriented 3D topological annulus. A minimum-cost triangle connection follows actual boundary vertices, including captured undercuts, without flattening the source into a chart.
6. Retain the buried lower foot and exact external interfaces. A local existing-face split near Y0.18 m gives the transition access to the toe without consuming protected perimeter vertices.

There is **no Boolean union, random rock field, source-width normalization, C7 folded-plane model, displacement-noise cliff generator or full-world duplicate**. The source remains one connected formation with the host, rather than a collection of decorative boulders. The connecting triangles are still a practical art limitation: topology-safe does not mean geologically convincing. Close and along-wall views deliberately expose them.

The high-detail local composite has **63,989 triangles**: 46,911 native source triangles plus retained host and 1,558 connecting triangles. The original full source and cropped high-detail geometry remain in the editable master. Runtime models use provider LODs plus bounded interior error-minimizing decimation, protecting their boundary vertices. This is geometry optimization, not artist-directed retopology of every fracture; that distinction matters when judging angular distant facets.

## Blender source and runtime assets

Editable packed master: `assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend`.

Reproducible scripts:

- `scripts/blender/author_scanned_composition.py`: native source selection, uniform placement, local host surgery, joins and three runtime levels.
- `scripts/blender/finish_scanned_composition.py`: selective UV1 normal baking and local glTF export.
- `reports/stage-2c9-scanned-rock-composition-2026-10-17/scripts/pack-master.py`: removes inherited unrelated objects **from the new master only**, then packs its used images. Historical masters are untouched.

`assets-source/gullyverse/quarry-scanned-composition/README.md` gives exact commands. `scripts/blender/export_scanned_composition_master.py` also exports directly from the packed master into a separate review folder, without reading historical masters. The portable export passes glTF validation and reproduces every geometry/normal/tangent/UV/index array exactly; differences are whole-file metadata/encoding. `C9_NATIVE_SOURCE_AND_HIGH` and `C9_RUNTIME_LOCAL_ONLY` separate source/authoring and runtime objects. The master is a self-contained local authoring asset, not an entire duplicate website scene. `raw/master-packed-images.json` records image packing. Initial packing found stale image paths inherited from historical unused C6 source objects; removing those unused objects from the new master resolved this without modifying historical files.

Runtime directory: `public/models/gullyverse/quarry-scanned-composition/`:

- `composition-region-geometry.glb`: lower14 plus retained upper15, all three levels, merged into the existing foundation owner.
- `composition-lod0.glb`, `composition-lod1.glb`, `composition-lod2.glb`: separate validation/review exports, **not independently downloaded in normal C9 loading**.
- `composition-bake.glb`: tiny ownership proxy with one 1024² UV1 normal image; no new albedo/ORM family.
- `manifest.json`: names, material/LOD assignments, protected registry hash, source matrix, bytes and hashes.

Coordinates remain metre-based. Blender Z-up → glTF Y-up is `[X,Z,-Y]`. Stable `Foundation_Wall_14_LOD0/1/2` and retained `Foundation_Wall_15_LOD0/1/2` node names satisfy the existing replacement contract. Collision remains owned by the unchanged world registry; these visual meshes are not new collision meshes.

## Approved scanned material and natural shades

C9 reuses the exact C8 official CC0 `marble_rock_03` + `rock_face_03` family. Existing `multi-colour.jpg`2048², `multi-normal.png`1024² and `multi-orm.png`1024², source calibration and provenance are unchanged. `material-manifest.json` in the C8 source directory remains authoritative. C9's pattern scale is locked at **3×**; source albedo/normal/ORM sampling remains aligned. Albedo is sRGB, non-colour maps linear, stone non-metallic, with the existing matte roughness response. No additional broad AO darkening is introduced.

The reference images `design/references/03-open-roof-quarry/quarry-warm-dappled-light.jpeg` and `quarry-open-sky-geometry.jpeg` show broad dark neutral stone, selectively exposed grey-brown faces, restrained warmer weathering and darker joints. Much bright amber colour is illumination, not a mandate for orange/brown albedo. C9 retains the approved C8 geology-aware scanned mixture and surrounding darker family. It adds no random per-object colours, camouflage mask or new texture collection. Reference pixels are not copied into runtime maps.

New surfaces use metre-scale UV0 with compatible side/undercut projection. UV0 is rebased by **an even10 whole approved material periods**, preserving phase, mirror orientation and density while reducing float-coordinate precision loss. This is not a scale change. Some close undercut grain transitions remain visible; a valid tangent frame alone does not prove ideal artistic UV continuity.

Only middle/far new surfaces receive fresh UV1 charts and geometry-only high-to-low normals. The new 1024 atlas copies the original lower half exactly, preserving unchanged lower-wall bake pixels; its two upper quadrants contain new patch bakes. Retained upper15 continues using the original atlas. Fine scan normals are not baked twice. One new thin distant facet required a local geometric corner-frame repair before baking. Near UV0 and final middle/far UV1 tangents are validated, rather than inventing unit tangent values. The Khronos validator reports zero errors/warnings.

## LODs, resources and loading ownership

Only one visual LOD per runtime part is selected by the existing screen-space/distance policy, with hysteresis and adaptive quality. Shared fixed external borders remain identical across levels. C9 does not add a new LOD controller or change map/camera rules. An automatic-distance inspection recording and selection trace accompany the screenshots.

The runtime contains **no scanned source master/high-poly object**. It replaces covered local host geometry and keeps frustum culling. Position/UV data remain float32. Normals/tangents use the already supported signed16bit `KHR_mesh_quantization`; there is no new Draco/Meshopt/KTX2 dependency or unmeasured displacement shader.

The existing `QuarryFoundationSession` owns the reused C8 holder, local replacement geometry and one additional normal proxy. The C9 baked material borrows the holder's existing albedo/ORM wrappers and owns the new normal via that same holder. Rendered clones borrow resources; they do not dispose source caches. Interrupted/rejected loads are disposed before publishing. The persistent Canvas, covered texture/shader preparation and stage cache remain unchanged. A private selector and locked3× controls are added to `ImmersiveShell`; the ordinary C5.1 fallback is unchanged.

## Visual assessment and art gate

The review gallery contains actual production-build Chromium images at matched camera pose, FOV, viewport, effective DPR, quality and approved lights. Fixed inspection poses are diagnostic only; normal visitor images use the validated public positions `[-18,1.72,-55]`, `[-18,1.72,-62]` and `[-17,1.72,-69]`. Existing stalls remain in view even where they occlude rock. Additional inspection views, behind-stall views, both joins, foot, rim, hub/scaffold, tunnel exit, map and portrait are labelled. No offline render substitutes for browser evidence.

The neutral diagnostic temporarily disables fine maps and normal maps, uses neutral grey rock materials and separate neutral lighting, then restores the original scene. It is not a production-light change. The source-derived lower formation retains actual thickness, recesses and protrusions without its texture. This is a stronger proportional foundation than C6.2's stretched native rock models and C7's engineered planes.

However, the first neutral and dusk views still show angular joining facets, local UV grain changes and a change in relief character beside the older stretched geology. The scan is a coastal lower cliff, not a complete tall excavated quarry face. It cannot by itself supply the approved quarry's entire geological height or repair every neighbouring C6.2 manufactured cut within this small scope. Texture detail remains easier to judge close up than behind stalls at ordinary walking distance. The selected scan's physical proportions are now defensible, but that does not automatically make this composition better overall than the approved C8 appearance.

**Art verdict: KEEP APPROVED C8; C9 NOT READY FOR ROLLOUT.** Native proportions and genuine local relief improve, but the visitor-distance gain is modest and the joining facets do not yet read as convincing continuous excavated geology. The approved B material preview remains the safer visual foundation. No adoption or public promotion is implied by passed tests. Photorealism and quarry-wide readiness are not claimed.

Compared with the project references, this coastal crop has more weathered pockets and scalloped breaks and fewer strongly jointed angular excavation beds. The tall surrounding cliff still inherits C6.2's stretched formations. Rock-foot contact is grounded but remains a narrow transition into a relatively clean festival floor, without the reference images' localized scree and sediment. The aerial form is intentionally preserved rather than redesigned. Increasing texture resolution, uniformly roughening the cliff or stretching the scan would not resolve these artistic differences.

## Verification scope and diagnostic limits

Strict actual-export ray survey: six visitor locations × seven pitches ×120 azimuths = **5,040 rays**, checking everyLOD. Zero unexpected horizontal perimeter gaps, zero inverted visible hits and zero cross-LOD hit/miss differences. The original tunnel opening remains the only allowed horizontal opening. Protected lower 315 and upper 265 boundary vertices are checked against `artist-protected-interfaces.json` at everyLOD with the unchanged **2e−5 m** tolerance. Clearance checks find no new intrusion into the preserved visitor floor. These are sampling checks, not exhaustive self-intersection or pixel-visibility proof.

A supplementary **10,920-ray** survey adds the other two public poses and close/diagonal cameras. It finds no gaps, no cross-LOD hit/miss disagreement and no inverted hit on the new lower14. Its strict status remains **FAIL**: nine inherited upper15/terrain first-visible hits persist, compared with eleven under the identical original C6.2 control. There are no newly introduced inverted-hit keys. `raw/expanded-survey-comparison.json` preserves that distinction. An initial along-wall camera `[-36,3,-54]` was behind the retained cliff and produced invalid front-side diagnostics; it is retained as rejected evidence and replaced by front-side `[-31,3,-58]` for acceptance. Tolerances were not loosened.

The direct binary-accessor topology check uses **exact float32 position identity, zero merge tolerance**. EveryLOD has manifold interior topology, finite UVs/unit normals/tangents, and only its expected protected outer boundary. The newly composed lower14 has zero inconsistent winding edges. A stricter edge-orientation audit found five pre-existing winding discontinuities in retained upper15 at eachLOD; the original C6.2 exports show the same five. These were preserved, not silently repaired outside the local scope, and the visibility survey finds no inverted first-visible hits. They remain a historical technical limitation. An initial Blender reimport/weld diagnostic reported disconnected attribute seams; its failure logs are retained. It is not used to loosen geometry checks: the final exported-position/index check directly verifies the actual shipped bytes. The reimport diagnostic's precise splitting cause was not established. Geometry normals/UV validity and visibility surveys are reported separately from artistic integration.

<!-- BEGIN_MEASURED_RESULTS -->
## Measured engineering results

The frozen production build, explicit TypeScript check and existing lint policy pass. The immersive suite passes **97/97**. Existing unrelated lint warnings remain; no lint rule was weakened. The five C9 runtime GLBs pass Khronos validation with **zero errors and zero warnings**. Portable re-export from the packed master also passes, and every exported position/normal/tangent/UV/index array exactly matches the current runtime arrays, although whole-file metadata bytes differ.

| Browser check | Result | Scope |
|---|---|---|
| A/B/C/D runtime contracts | PASS | All linked programs valid; A/B/C buffers identical; D changes only lower14 LOD0/1/2; 3× locked, correct sRGB/linear and UV1 bake |
| Entry/input/map/history/touch/reduced motion | PASS | 8 real-browser groups; touch is emulation |
| Preview ownership | PASS | Ten covered enable/disable cycles, retirement/reload, full non-3D unmount |
| Repeated travel | PASS | Five Aftermovie/hub round trips, persistent Canvas and settled caches |
| Actual video playback | PASS | Three short playback/exit cycles, camera restore and preview change during playback |
| Context/failure/fallback/public control | PASS | 9 groups, including C9 normal-holder failure/retry and unchanged public C5.1 |
| Original strict perimeter/clearance survey | PASS | 5,040 rays, unchanged 2e−5 m protected border tolerance, zero new floor incursions |
| Expanded visibility survey | FAIL — inherited | 10,920 rays: C9 nine inherited upper/terrain hits versus eleven C6.2 hits; no new C9 inverted hits/gaps/LOD hit differences |
| Physical laptop / iPhone / Android | PENDING | No accessible physical hardware; no hardwareFPS inferred |

See raw test JSON/logs and `browser-queue.json` for exact runs. Context loss uses the real WebGL extension. Some focus/freeze events are deliberately synthetic; these are not claims of physical background-app testing. Short playback cycles do not test a complete movie duration.

### Geometry and bytes

| Representation | C6.2 / C8 region triangles | C9 region triangles | New lower14 only |
|---|---:|---:|---:|
| LOD0 | 35,998 | 47,200 | 29,201 |
| LOD1 | 11,998 | 16,166 | 10,167 |
| LOD2 | 4,398 | 6,088 | 3,889 |

| C9 file | Bytes |
|---|---:|
| `composition-bake.glb` | 991,084 |
| `composition-lod0.glb` | 1,622,184 |
| `composition-lod1.glb` | 843,728 |
| `composition-lod2.glb` | 325,472 |
| `composition-region-geometry.glb` | 2,790,448 |

Only the combined geometry and normal-holder files are fetched by D: **3,781,532 bytes** of local runtime files, replacing the old **1,966,096-byte** region file; net raw increment **1,815,436 bytes**. Separate LOD exports are review/validation files, not three extra downloads. The unchanged base foundation and approved C8 material holder/maps remain shared dependencies. Full raw selected-asset bytes are not the same as compressed HTTP transfer.

One additional 1024² geometric normal image adds approximately **5.33 MiB** RGBA8-with-mipmaps estimate: B/C 85.33 → D 90.67 MiB in this measured combination. There is no new unique4K collection or runtime source-scan mesh. This is an estimated decoded pixel payload, not measured VRAM.

### Texture/material ownership

| Variant | Active material wrappers | Active texture wrappers | Unique image sources | Unique decoded image estimate, MiB | Linked programs |
|---|---:|---:|---:|---:|---:|
| A C6.2 | 3 | 7 | 7 | 53.33 | 23 |
| B approved C8 | 4 | 16 | 10 | 85.33 | 23 |
| C C8.1 | 4 | 10 | 10 | 85.33 | 24 |
| D C9 | 5 | 17 | 11 | 90.67 | 23 |

Texture wrapper counts are not unique image counts. Existing legacy materials and ground maps still have active consumers and were not retired. The C9 baked material borrows existing albedo/ORM wrappers and adds one normal image. No extra shader sampler or global triplanar system is introduced; D has 23 linked programs versus B 23, while the optional C8.1 custom contact has 24 in its sampled view.

### Exact diagnostic environment

**Chromium 151.0.7922.173 built on Debian GNU/Linux 13 (trixie)**, Debian GNU/Linux13, x86_64 virtual AMD EPYC9V74, three exposed vCPUs with **two-CPU cgroup quota**. Renderer: `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)`. No `/dev/dri` physical GPU and no physical phone/laptop connection. WebGL GPU timer is unavailable. Matched measurements use 1366×900, effective DPR 0.5 and fixed quality 3; captures use 1366×900/390×844, DPR 1 and quality 0. Lifecycle/regression tests use DPR 0.25. No artificial network/CPU throttling is applied. Dedicated HTTP-cache tests remove Playwright routing and use CDP blocking, explicitly enable caching, clear for cold and revisit for warm. Performance windows run sequentially, without recording or competing Blender/PDF work.

### Matched frame windows — software diagnostics only

One 10-second sample per window/variant. Short software runs are noisy and do not establish a hardware regression ratio or a production FPS guarantee. Draw calls and triangles are whole rendered-scene counters at the sampled view, not wall-only totals.

| Variant | Window | Mean FPS | p50 ms | p95 ms | p99 ms | Draw calls | Visible triangles |
|---|---|---:|---:|---:|---:|---:|---:|
| A | hub | 4.97 | 197.70 | 233.00 | 251.60 | 166 | 123,002 |
| A | visitor-benchmark | 4.69 | 206.50 | 250.70 | 273.40 | 35 | 114,705 |
| A | hub-keyboard-movement | 5.19 | 193.30 | 235.70 | 253.00 | 166 | 123,002 |
| A | aerial-map | 3.53 | 287.30 | 339.70 | 354.00 | 187 | 123,896 |
| A | stage-looking-back | 2.96 | 332.60 | 393.90 | 397.90 | 75 | 1,045,486 |
| B | hub | 4.81 | 203.40 | 241.30 | 265.10 | 166 | 123,002 |
| B | visitor-benchmark | 4.35 | 215.80 | 290.00 | 292.60 | 35 | 114,705 |
| B | hub-keyboard-movement | 5.04 | 195.50 | 251.30 | 263.30 | 166 | 123,002 |
| B | aerial-map | 3.38 | 293.80 | 358.80 | 371.00 | 187 | 123,896 |
| B | stage-looking-back | 2.96 | 331.30 | 388.30 | 390.80 | 75 | 1,045,486 |
| C | hub | 5.01 | 197.40 | 253.10 | 253.90 | 166 | 123,002 |
| C | visitor-benchmark | 4.10 | 242.30 | 280.20 | 282.30 | 35 | 114,705 |
| C | hub-keyboard-movement | 4.86 | 201.10 | 266.10 | 268.40 | 165 | 122,992 |
| C | aerial-map | 3.44 | 290.70 | 319.80 | 339.50 | 187 | 123,896 |
| C | stage-looking-back | 3.09 | 308.40 | 375.40 | 381.70 | 75 | 1,045,486 |
| D | hub | 4.65 | 203.30 | 267.60 | 282.60 | 166 | 123,002 |
| D | visitor-benchmark | 4.25 | 228.20 | 286.50 | 288.70 | 35 | 118,873 |
| D | hub-keyboard-movement | 5.08 | 194.20 | 266.40 | 273.70 | 166 | 123,002 |
| D | aerial-map | 3.32 | 299.20 | 369.80 | 371.30 | 187 | 125,586 |
| D | stage-looking-back | 2.87 | 347.00 | 388.90 | 389.00 | 75 | 1,049,654 |

The raw timeline, long tasks, selectedLODs, effective rendererDPR and resource snapshots are retained in `raw/a-performance.json` through `d-performance.json`. These are deliberately not compared with historical physical GPU figures.

### Cold/warm loading and preparation

| Variant/cache | Ready ms | Total transferred bytes | Encoded body bytes |
|---|---:|---:|---:|
| rock-calibration-cold | 10,422 | 13,458,535 | 13,448,035 |
| rock-calibration-warm | 9,018 | 2,400 | 13,423,522 |
| scanned-material-multi-cold | 10,179 | 17,943,602 | 17,932,202 |
| scanned-material-multi-warm | 9,432 | 3,300 | 17,907,689 |
| material-continuity-cold | 10,620 | 17,945,808 | 17,934,108 |
| material-continuity-warm | 9,985 | 3,300 | 17,909,595 |
| scanned-composition-cold | 10,622 | 19,458,158 | 19,446,458 |
| scanned-composition-warm | 9,210 | 3,600 | 19,421,945 |

Ready includes app initialization, asset fetching and covered preparation; it is not an isolated GLB decode benchmark. HTTP-warm does not guarantee warm GPU driver state. Localhost timing is not a mobile-network budget.

| Cold variant | Material parse callback ms | New bake callback ms | Local geometry callback ms | Texture init ms | Shader compile ms | Covered ready ms |
|---|---:|---:|---:|---:|---:|---:|
| rock-calibration-cold | 353.90 | — | 2.90 | 44.20 | 46.50 | 2,435.90 |
| scanned-material-multi-cold | 384.40 | — | 2.40 | 71.80 | 37.70 | 2,606.80 |
| material-continuity-cold | 321.00 | — | 3.10 | 73.30 | 38.60 | 2,726.10 |
| scanned-composition-cold | 347.60 | 104.90 | 3.10 | 77.90 | 37.10 | 2,717.70 |

Loader parse-callback walltime can include referenced-map fetch/image decode, so it is not pure CPU JSON parsing. Texture-init/shader/cover durations are CPU wall-clock proxies around the existing preparation, not hardware GPU timestamps. Four hidden warm renders remain covered. Original stage/video resources and behavior are unchanged. First Aftermovie travel/return are exercised, but separate end-to-end cold/warm travel-duration samples were not collected in this run.

### LOD and lifecycle findings

The automatic inspection selects **LOD0 at6/15m, LOD1 at30m, LOD2 at65/110m, then1→0 on return** under its recorded settings. One visualLOD per part is active. Fixed external borders agree acrossLOD. Recorded changes are inspectable; the result is not declared pop-free.

| LOD | New surface + join triangles | High-surface sampled p95 distance m | Sampled max m |
|---|---:|---:|---:|
| 0 | 13,681 | 0.0067 | 0.0844 |
| 1 | 5,023 | 0.0362 | 0.2240 |
| 2 | 1,983 | 0.0954 | 0.3023 |

Centroid-to-high distances sample 1,800 new-surface faces perLOD, including joins; this is not an exhaustive Hausdorff/silhouette bound. Middle/far exceptional errors around0.22/0.30m can affect sharp recesses and need visual judgment.

Ten preview cycles settle at **39 renderer textures / 263 geometries** for the C9 cohort, with identical post-warmup GL texture/buffer/program counters. Retirement reduces textures to **28** and geometries to **195**, freeing exactly11 unique image allocations. Five travel round trips and three playback cycles also plateau after warmup; the same Canvas and camera restoration are verified. The full fallback unmount disposes its owner with zero consumers.

Observed preview-lifecycle JS heap range: **70.69–103.90 MiB**, without forcing GC. Heap can fluctuate; neither stable allocation counters nor this range certify leak-free driver/VRAM behavior. Global texture-byte diagnostics can double-count wrappers, so the unique-image estimates above are reported separately.

### Scaling constraints and next acceptance gate

The present combined file includes retained 35.557 m host/upper geometry because it uses the existing local replacement owner. **Do not multiply its full2,790,448-byte payload per 10 m patch.** Future local additions must share that host/material owner, use native-scale crops and pack several geometric bakes together. The retained high-detail source is never shipped. The local core targets roughly 12.5k/4.2k/1.4k triangles plus joins; whole-region totals include unchanged host geometry. These are experimental counts, not certified device budgets.

The added normal atlas currently costs 5.33 MiB even though part preserves old pixels. Replicating one atlas per segment is not a production memory plan. Share/pack bakes and eventually retire legacy material consumers deliberately; do not dispose shared maps while any wall still uses them. Current all-LOD residency is retained. No broad streaming rewrite or compression loader was added.

Physical-device acceptance remains **PENDING**. `PHYSICAL-DEVICE-PROCEDURE.md` gives an operator-ready procedure: exact device/GPU/OS/browser/DPR/quality/power, repeated matched wall/hub/map/stage windows, genuine cold/warm cache, navigation/playback/resource cycles and raw diagnostics. No device benchmark was fabricated, inferred from emulation, or used to block this bounded asset experiment.

### Final recommendation

**KEEP APPROVED C8. Do not promote C9 or scale it across the quarry.** This experiment establishes safe native-scale scan composition and a reusable packed source/export path, but its outer geological transitions and modest visitor-distance gain do not meet the art gate. The available coastal scan has genuine physical relief; it does not automatically supply compatible tall excavated-quarry beds. Preserve it privately for review and compare the valid front-side join views before authorizing any further targeted asset selection/integration. No external artist or user-authored source mesh is required as a condition for reviewing this result.
<!-- END_MEASURED_RESULTS -->

## Remaining production work and next step

Do not extend this candidate around more sectors or silently adopt it. Preserve approved C8 3× as the material reference and C6.2 as the earlier physical comparison. The decision should be based on the matched visitor views and the geometry-only evidence, especially the two joins and the wall-foot/upper continuation.

If the reviewer prefers C9, the next bounded task is a targeted joining/UV correction using this same native-scale scan and protected interface, followed by another fixed-pose art review; it is not permission for a full quarry rebuild. If C8 remains stronger, keep it. The concrete limitation is creating compatible tall-quarry geological transitions from the available lower coastal capture, not lack of subdivisions or texture resolution. No generic displacement/noise cycle or demand that the user hire an artist is proposed.

Any eventual wider rollout should use source-scale crops with varied genuine formations, shared approved materials, local geometry owners, protected common borders and measured visibility-driven detail. A source-derived normal atlas should be shared or packed across several regions rather than added independently for each 10 m segment. Retire obsolete material families only when their final consumers are gone. Physical laptop/iPhone/Android performance and final artistic acceptance remain separate gates.
