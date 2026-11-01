# Stage 3A — Dried-up canal material-only study

Handoff: `CANAL-MATERIAL-SHOOTOUT-20261023-01`. Private comparison; **no final material selected**.

## Preserved baseline

`work-in-progress-2027` at `e638140b37045a805b23b4d406d387a8870f8486`. The existing WIP default remains the current cave, corrected native-scale C9 composition and approved C8 quarry sampling at 3×. The ordinary main-branch C5.1 default is unchanged. No commit, push, merge, deployment or default promotion was performed.

The two pre-existing modified historical trace ZIP entries remain untouched. New work is isolated to the cave-local material module, two private-review routing/UI integrations, authoring assets/scripts, tests and evidence. The original dirty `/workspace/Breeze-2027-navigation` source remains preserved; editing used the existing isolated WIP tree with hardlinks detached before source changes.

All **438 protected original files** pass size/SHA-256 checks. This includes all tracked source/runtime assets, cave and quarry GLBs, Blender masters, floor/world registry and unchanged immersive/navigation/lighting source. Runtime selection checks retain the exact cave geometry objects for every material and scale. No vertices, topology, floor material, collision, route, camera choreography or global lights change.

The previous incomplete WIP preservation backup was separately finished: https://drive.google.com/drive/folders/1G-LsAHgaKyRZb7mgn8nG0atL2rNrxXR3 . Its verified receipt is https://drive.google.com/file/d/1FUjawhbuzqo4G8eGgtYZAvpND7SLO9Mb/view . This is preservation, not art approval. Only redundant generated local archive copies were reclaimed after full remote hash verification; all original assets and Drive checkpoints remain intact.

## Reference analysis

The actual latest Google Doc prompt and both embedded phone screenshots were inspected. See [reference analysis](../reports/canal-material-study-2026-10-23/REFERENCE-ANALYSIS.md). The target is dry grey/greige, taupe and chalky beige coating with shallow pitting, mineral wear and restrained staining. Phone UI and flash-like exposure are not geometry or lighting instructions. No reference photo is copied into a runtime texture.

The existing organic silhouette cannot become the reference constructed canal arch through materials alone. That mismatch, faceted transitions and inherited terrain/visibility limitations are shown honestly. No new graffiti, floor experiment, visible light fixture or geometry workaround was introduced. The exact seven final artist artworks remain unavailable and were not invented.

## Sources and PBR preparation

Authentic Poly Haven 2K diffuse, OpenGL normal and roughness files were downloaded using the official API and checked against provider size/MD5 and local SHA-256. License: CC0 1.0, https://polyhaven.com/license . Full author credits, source URLs, native dimensions and per-map hashes are in [provenance manifest](../assets-source/gullyverse/canal-material-study/provenance-manifest.json). Source maps remain unmodified.

The initial default-user-agent API requests returned HTTP403. A normal named application User-Agent and dated API query succeeded. No proxy/policy bypass or thumbnail substitution was used. All eight requested candidates were then prepared and captured. Additional catalog research selected Chipped Concrete; Dirty Concrete (mud/twigs/floor grit) and Grey Plaster (redundant/moss) were not shortlisted. All ten prior-study albedos/metadata were reviewed; Quarry Wall is the retained coarse mineral control.

| Candidate | Native scan coverage, m | Selected-family transfer, MiB | Role |
|---|---:|---:|---|
| Cracked Concrete Wall | 1.000 × 1.000 | 12.83 | Requested candidate |
| Concrete Wall 006 | 2.000 × 2.000 | 11.75 | Requested candidate |
| Worn Plaster Wall | 1.800 × 1.800 | 9.10 | Requested candidate |
| Plastered Stone Wall | 2.500 × 2.500 | 11.49 | Requested candidate |
| Plaster Stone Wall 02 | 2.120 × 2.120 | 11.00 | Requested candidate |
| Rock Embedded Concrete Wall | 1.760 × 1.760 | 13.00 | Requested candidate |
| Concrete Wall 008 | 2.710 × 2.710 | 5.92 | Requested candidate |
| Scuffed Cement | 1.620 × 1.620 | 8.56 | Requested candidate |
| Chipped Concrete | 2.002 × 2.002 | 9.88 | Additional dry-pitting candidate |
| Quarry Wall | 1.800 × 1.800 | 12.73 | Earlier-study control, verified source reuse |

Runtime maps: albedo JPEG in sRGB; OpenGL normal PNG in linear/non-colour space; linear ORM PNG with R=255, G=roughness, B=0. Stone/cement is non-metallic. AO is not multiplied into albedo or reapplied. No height displacement, parallax, extra PBR atlas or vertex modification is used. All maps share UV0 orientation and transforms, flipY=false, repeat wrapping; the protected geometric UV1 data is unchanged. Roughness retains the licensed scan response rather than an arbitrary global brightness/roughness grade. Normal strength is 0.7 on both axes.

Some official filtered normal-map vectors are not unit-length before sampling. The initial image-only unit-vector assertion was therefore inappropriate. Validation now checks finite nonzero source vectors and the actual Three.js `normalize(tbn * mapN)` shader path after normal strength; normalized output meets 1e-6 error. No strict geometry test or tolerance was changed.

## Cave-local sampling and private selection

New selector: `/?diagnostics&entranceReview=canal-material&quarryReview=geology-fidelity&caveMaterial=chipped_concrete&caveFeatureScale=1`. Valid IDs are in `components/immersive/canalMaterialStudy.ts`. This is a local/private build selector, not a new deployed URL. Historical selectors and the current WIP default remain intact.

The new comparisons use a common 2.023241625 m square tile at 1× on the existing 2 m/UV host charts. The nominal 2m period was corrected to the nearest compatible exact phase: the original entrance UV island offset is 8 / approvedUVRepeat = 129.487464 UV units. Fitting 128 whole tiles to that offset makes both 1× and 2× phase-aligned, without editing UV attributes or adding shader instructions. The initial unaligned pass is retained separately in raw/attempt-01-unaligned-period and excluded from the final gallery. All selected scans are square, so this comparison normalizes coverage uniformly without stretching one axis. Native scan sizes remain explicit above: common test coverage is not falsely described as native for every scan. At 2×, the repeat is halved once, making a 4.04648325 m tile. Six scale-study candidates receive both sizes: Cracked Concrete Wall, Plastered Stone Wall, Scuffed Cement, Chipped Concrete, Concrete Wall 006 and Concrete Wall 008. **The baseline keeps its exact existing sampler rather than being normalized to the new test period.** C8/C9 quarry sampling remains 3× and is never mutated.

One candidate owns three texture sources/wrappers and two shared materials (outside and inside). The inside retains the existing analytical cave-opening response exactly; there are no new lights or lighting parameters. All wall/roof/entrance consumers use that same cave-local family; the floor is excluded. Retired families close only after covered replacement; failed/superseded downloads drain their own images and retain the functional cave/C9 owner. Direct stage entry still defers invisible cave assets.

Review params persist through the existing history/travel helper. The canal session contains no geometry-replacement or pilot path; a stale `caveGeometry=pilot` is ignored/not carried. No complete quarry GLB is duplicated.

## Actual-browser review

**136 full-resolution browser comparisons**, all from the same running production build: baseline plus ten candidates at 1×, and six scale-study candidates at 2×. Eight views per version cover landing pose, left/right walls, vault, walking-depth, close inspection, 390×844 mobile landing and tunnel. Desktop is 1366×900; actual DPR1 and quality0 are fixed. Pose/FOV/viewport/light/quality equality is asserted against the baseline for each view; geometry UUIDs/counts remain identical within each capture session; resumed sessions use the exact same source GLB SHA-256 and production build.

Stills use fixed development inspection cameras with review UI hidden so the wall is unobstructed. The landing pose is the exact approved [0,1.72,11.5], yaw0/pitch0.15. The close lateral view is explicitly diagnostic, not advertised as a public free camera. All other tunnel inspection positions follow the protected route at visitor eye height. The real journey recording/UI context is separately labelled with lower software-rendering settings.

[Contact-sheet PDF](../reports/canal-material-study-2026-10-23/review/Gullyverse-Dried-Canal-All-Materials.pdf) · [Full-resolution gallery](../reports/canal-material-study-2026-10-23/review/index.html) · [Per-shot metadata](../reports/canal-material-study-2026-10-23/raw/captures.json) · [Matched-setting assertions](../reports/canal-material-study-2026-10-23/raw/matched-settings.json).

## Art assessment — recommendations, not selection

1. **Scuffed Cement** — Closest quiet, dry taupe cement coating; no masonry courses or obvious panel grid. It preserves the existing rocky relief without strong fake crack shapes. Its fine wear is subtle at visitor distance and can look too plain; compare both feature sizes rather than assuming 2× wins.
2. **Concrete Wall 008** — The lighter muted grey coating is readable on the entrance and closer to the grey/off-white reference family. It has source construction seams and formwork marks visible on inspection, so it is a useful alternative, not an unqualified recommendation. The added 2× comparison makes that pattern risk explicit.
3. **Cracked Concrete Wall** — Strongest visibly weathered/chalky option, with genuine scan detail and peeling mineral-like patches. The 2× version reduces small busy repetition, but its light albedo and high-contrast damage can be too pale/blotchy compared with the subdued reference. Review as the more weathered alternative.
4. **Chipped Concrete** — Good neutral grey tone and clear dry pitting. Actual close views reveal a regular stippled/tooling pattern that can resemble an artificial finish, especially when enlarged. Do not confuse scan detail with a convincing final cave coating.
5. **Concrete Wall 006** — Authentic worn cement with small pits and scratches, but darker than the desired readable coating in this scene. Recurring construction joints/formwork details are a further risk. Both feature sizes are included; it is weaker at the landing than its catalog/source appearance suggests.
6. **Worn Plaster Wall** — Recognisable damaged plaster but large repeated peeled patches read as camouflage-like spotting on the cave, and the source has a recurring construction joint. Less coherent than the references at normal viewing distance.
7. **Plaster Stone Wall 02** — Dusty plaster palette is relevant, but exposed stone courses imply arranged masonry. It does not preserve the desired unstructured cement-covered-rock appearance.
8. **Plastered Stone Wall** — Weathered scan with subdued variation, but nearly black under the unchanged scene lighting. Both sizes demonstrate that enlarging features cannot solve low material readability; not a recommended final coating.
9. **Quarry Wall — earlier-study control** — Retains coarse geological grain and a dark mineral response, but reads as quarry rock rather than aged canal cement. Useful for comparison with earlier work; not a dried-canal finalist.
10. **Rock Embedded Concrete Wall** — Strong orange/brown aggregate and arranged stone forms read as masonry or a repeated stone skin. It conflicts with the restrained grey-beige coating target despite being a valid licensed scan.

Review Scuffed Cement and Concrete Wall 008 first as contrasting subdued and lighter cement options. Cracked Concrete Wall at larger features is the optional strongly weathered alternative. Every recommendation has the limitations above; none is selected, visually approved or promoted. No candidate exactly reproduces the photographs on this locked organic mesh under the existing dark lighting.

The unchanged dusk/cave opening response makes the middle passage substantially darker than the camera-lit references. Some coating differences are easiest to judge on the entrance or side-wall views; this is documented rather than compensated by changing global light or exposure. No candidate is called photorealistic or production-approved.

## Performance and memory

The full ten-candidate runtime library is 106.25 MiB, but it is **not preloaded**. One selected 2K family costs 64 MiB estimated RGBA8 including full mipmaps (three unique images), versus 256 MiB for one 4K family in the previous study. This is additional to retained C9/quarry resources, not a claim that the entire scene is only 64 MiB. Texture compression was not introduced without a validated loader path. Shared roughness/metalness wrappers avoid duplicate image allocations; inactive families retire after coverage.

New geometry transfer/triangles: zero. New dynamic lights: zero. New global blending/triplanar/displacement shader: zero. The same Standard PBR variants are used for every candidate. Measured browser calls/triangles, texture allocations and software frame distributions are below.

| Version | Calls | Visible triangles | Texture allocations | Frame p50 / p95 / p99, ms | Software FPS |
|---|---:|---:|---:|---:|---:|
| control 1× | 177 | 279548 | 28 | 1562.2 / 2129.9 / 2238.5 | 0.62 |
| cracked_concrete_wall 1× | 177 | 279548 | 31 | 1560.9 / 1790.1 / 1837.2 | 0.65 |
| concrete_wall_006 1× | 177 | 279548 | 31 | 1610.3 / 2464.7 / 2662.2 | 0.60 |
| worn_plaster_wall 1× | 177 | 279548 | 31 | 1512.3 / 2062.5 / 2218.4 | 0.65 |
| plastered_stone_wall 1× | 177 | 279548 | 31 | 1485.9 / 1625.6 / 1638.9 | 0.69 |
| plaster_stone_wall_02 1× | 177 | 279548 | 31 | 1498.5 / 2209.7 / 2516.3 | 0.65 |
| rock_embedded_concrete_wall 1× | 177 | 279548 | 31 | 1544.1 / 2245.1 / 2262.6 | 0.62 |
| concrete_wall_008 1× | 177 | 279548 | 31 | 1565.9 / 2237.2 / 2461.0 | 0.63 |
| scuffed_cement 1× | 177 | 279548 | 31 | 1617.1 / 2082.2 / 2144.8 | 0.61 |
| chipped_concrete 1× | 177 | 279548 | 31 | 1569.4 / 2296.2 / 2384.0 | 0.61 |
| quarry_wall 1× | 177 | 279548 | 31 | 1598.0 / 1772.6 / 1901.3 | 0.64 |

Timings are 32 RAF intervals at the identical 1366×900/DPR1/tier0 walking-depth pose, unthrottled SwiftShader. p99 is effectively the maximum of this small diagnostic sample. Full-DPR software rendering is slow and does not establish hardware acceptance or a trustworthy physical-device speed ranking. Source validation/backup I/O may also contend for this cloud host. Physical laptop/integrated-GPU and phone results remain PENDING.

Cold/warm loading uses a separate explicitly labelled DPR0.25/tier3 covered-preparation diagnostic. Raw resource transfer/decoded-body/timing data, not inferred hardware FPS, are in [loading evidence](../reports/canal-material-study-2026-10-23/raw/loading.json). The test distinguishes the unchanged ordinary WIP default (no canal maps) from the selected three-map preview.


Measured loading totals (resource entries across the entire page, including unchanged parent resources; software covered preparation at DPR0.25/tier3):

| Mode | Cold / warm reload, s | Cold / warm transfer, MiB |
|---|---:|---:|
| Unchanged WIP default | 10.771 / 10.360 | 25.02 / 25.02 |
| Private Chipped Concrete | 10.812 / 10.286 | 34.90 / 34.90 |

The local warm reload still records transferred response bodies under the existing local server cache policy; it is not claimed to be a zero-network cache hit. Only three selected-family map URLs are requested; the other nine families are absent. Loading quality/DPR differ from the matched still/frame-time test and are explicitly separate.

## Validation and inherited limits

TypeScript, lint (existing warnings), production build and 106 immersive tests pass. See [build/test logs](../reports/canal-material-study-2026-10-23/raw/build-tests/). Material/source checksum, GLTF structure/required vertex attributes, normal-map path and all 438 protected-file hashes pass. No Blender mesh was authored or regenerated in this material-only phase; existing editable masters are preserved through the protected parent checkpoint. The unchanged cave is also rechecked using the original full mesh/normal/tangent/cross-LOD/clearance and horizontal/upward-ray survey. Its original tolerance values are retained. The seven separate inherited quarry-component defects are replayed explicitly and remain failures, not repairs.

**Navigation/map/playback/history/touch:** Fresh click entry, authored pacing and initial persistent Canvas: PASS; Held-key focus release, all editables/forms, native typing, lost keyup and stale repeat: PASS; Blur, visibility/freeze, focus restoration and interrupted input: PASS; Map invalid SVG guard, open/close, resize and same Canvas destination: PASS; Playback restores actual activation pose; rapid restart cannot change walking anchor: PASS; Boundary Stay/Escape, hysteresis, return and immersive Back/Forward: PASS; Navbar Home, reload session, direct URL, history and explicit Entrance policy: FAIL; Fresh-session Enter and touch entry/movement/map; reduced motion: PASS.
**Ownership/switching/failure/context recovery:** Material switching preserves C9 sampler/source IDs and plateaus after family retirement: PASS; WebGL loss/recovery preserves selected material, C9 and persistent Canvas: PASS; Inactive retirement releases study ownership and allows a fresh covered reload: PASS; Native fallback unmount closes selected images once: PASS; Failed material channel retains functional cave/C9 and retry recovers: PASS; Unmount during delayed material decoding does not adopt images or double-close: PASS.
**Cold/warm loading/default preservation:** Ordinary WIP default never downloads canal candidate maps: PASS; Private cold/warm selected family loads exactly three maps, never the catalog: PASS.

Any FAIL above is not hidden or converted into a pass by changing an application deadline/tolerance. Existing C9 upper-wall, mouth/transition and cold-preparation limitations remain inherited where identified by previous reports. Byte-identical meshes preserve the old visibility/clearance/cross-LOD results; this task does not claim to have repaired those defects.

## Follow-up of the direct-route regression

The first navigation run passes seven of eight groups. The direct-route group fails while entering Aftermovie: it reaches the existing critical-loading fallback. A fresh unchanged-default direct Aftermovie probe also enters fallback after 46.707 s with the original 45 s critical-preparation deadline; **no canal candidate is selected**. This reproduces an inherited default-path failure under this software renderer rather than establishing a new material regression. Separate private control and cracked-material direct-stage attempts subsequently reached local stage (46.689 s and 49.728 s); this intermittent result does not erase the failed regression. The original deadline is unchanged. Exact phase scheduling during automatic quality fallback differs from total wall-clock load time. Real-device behaviour remains unverified.

See `raw/regressions/results.json`, `raw/default-direct-route-deadline.json` and `raw/direct-route-diagnostic.json`. The first follow-up harness attempted to read a runtime after fallback had unmounted it, producing a diagnostic TypeError; that is distinct from an application exception. The preserved evidence and revised replay script distinguish missing runtime/fallback DOM safely. The browser page-error collection was empty. In-session navigation/map/history/touch, actual video playback/return and the recorded full journey passed. **Direct cold-stage reliability remains unresolved.**

## Independent checkpoint and restoration

New phase: https://drive.google.com/drive/folders/1R5rLb3nM2R-Yc3qrN2H_pxjkcEC_DZ0A

Review: https://drive.google.com/drive/folders/1ao9oY8aVlYS__2gZBH6o8n--mhWoSBRn

Checkpoint: https://drive.google.com/drive/folders/1iD2YTzDHLORsF_X-mS-fA3f6xcEJE9Jy

This is a delta on the independently verified e638140b WIP checkpoint and its explicit parent recovery chain. It includes every changed/new source file, reproducible material-preparation script, exact downloaded licensed maps/metadata, runtime textures, tests, raw PNGs, PDF/gallery, recordings, technical evidence, restoration README and SHA manifests. Source/runtime pixel archives were frozen before the small phase-metadata correction; the final Application-Source overlay (restored after Source-Materials and Runtime-Materials) deliberately replaces their two material-metadata JSON files after extraction. All PBR pixel files remain byte-identical. Review-and-Evidence is the final docs/evidence overlay. Existing protected assets are reused by exact hash from the parent; no source-art LFS pointer is represented as a payload.

Join labelled binary parts in numeric order per archive family; verify both part and whole-archive SHA-256 before extraction. Extract into a NEW staging directory, restore the protected parent into a separate project, then apply the verified delta. Do not overwrite the sole surviving workspace. Check `DRIVE-BACKUP-RECEIPT.json` for final full download-back verification and `restore-verification.json` for independent archived-member restoration checks. A folder URL alone is not a completion receipt. No private .env, credential, dependency or build cache is included.

## Stop condition

The private comparison remains available for user selection. Do not promote a material, change geometry/lighting, push/deploy or begin another phase without explicit approval. After a material and feature size are chosen, any next step should be a bounded cave-local material adoption/optimization, preserving the locked C9 quarry.

## Direct review links

All-material comparison PDF (51 pages): https://drive.google.com/file/d/11D2rPXpZSGoHPvn45j_W8m7Vsi-Y5jD1/view

All 136 original full-resolution PNGs: https://drive.google.com/drive/folders/12aIIOjKrPu5BjzXEeXnau3aWXaffznuZ

Actual browser journey (MP4, lower-DPR software recording): https://drive.google.com/file/d/18_BhOrx4I7YB3aYLmOszgonM5LE3mEO4/view

Final application source overlay is `Canal-Application-Source-v2.zip` (20 files); the earlier v1 remains archived as history. Apply Source-Materials, Runtime-Materials, Application-Source-v2, then Review-and-Evidence. The final two material metadata files override the earlier nominal-period metadata, not any texture pixels. The checkpoint index and verification receipt identify exact part links and hashes.
