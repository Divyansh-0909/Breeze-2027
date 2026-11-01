# Gullyverse — Rev05A banner and organic audience correction

Date: 2026-10-25 UTC. Handoff: WORLD-BANNER-ORGANIC-CROWD-SHELVES-PENDING-20261025-05A.

**Status: PARTIAL — banner and crowd implemented; shop relocation awaits a narrow geometry exception.** No A/B/C direction has been selected and no final visual-art approval is implied.

## Baseline and preservation

The approved manual task is the latest shared-document targeted Blender correction, superseding the optional high-fidelity look-dev pilot. The exact Rev04 baseline is `source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend`, 3,914,135 bytes, SHA-256 `6041c26ac21fd990f14e2dae0fbe2cad15c21739f045d8cf56b7b8439a9e239a`. It is included unchanged for independent restoration and reproducibility. The original dated directory and earlier Drive checkpoints are untouched.

Website baseline: `/workspace/Breeze-2027-wip-push`, branch `work-in-progress-2027`, HEAD `e638140b37045a805b23b4d406d387a8870f8486`. All 1,213 protected website files and recorded Git status match the starting baseline (`evidence/website-baseline.json`). The original dirty navigation worktree is preserved. This revision changes only a separately saved Blender study. No website implementation, public/WIP promotion, commit, push, merge or deployment occurred.

## Implemented corrections

Only `Festival takeover banner` is removed. The screenshot matches that B-only large red plane at [0,-3,11.5], approximately 6.2m × 2.58m. There were no supports exclusive to that banner. The actual Aftermovie three-panel screen, centered GULLYVERSE navigation board, all shop signs and C's small festival wall poster are retained. A and C did not contain the removed plane, so they receive no invented deletion. Both frontal and oblique B comparisons show its removal. The source screenshot is retained with SHA-256 in the evidence package.

On save, Blender retires the deleted plane's now-unreferenced `Festival takeover banner / raster paint` material. Its original remains in the included Rev04 master. Every surviving material/node setting, world/node setting and packed image payload/color space compares exactly. The diagnostic finding and final read-only validation are retained; no shading tolerance is relaxed.

The audience retains its semicircular front-of-screen domain, but the exact three arcs are replaced by deterministic clustered placement, seed **2026102505**. Continuous radial sampling and local clusters create varied gaps, depth offsets and an asymmetric outline. Actual body footprints, including arms, determine placement rejection; no per-load randomness is used. The screen-facing direction varies by up to 11 degrees. The fixed lane/cypher people outside the audience remain unchanged.

| Variant | Audience before | Audience after | Triangles before | Triangles after | Occupied 2m cells before/after |
|---|---:|---:|---:|---:|---:|
| A | 48 | 144 | 44,824 | 73,624 | 42 / 63 |
| B | 56 | 152 | 47,960 | 76,758 | 48 / 64 |
| C | 52 | 148 | 46,028 | 74,828 | 44 / 63 |

Counts exclude the unchanged nine lane/cypher people. There are 144 shared main audience members plus eight B extras or four C extras. Across all collections, 156 audience instances use 1,248 body parts; 96 new shared people add 768 linked mesh instances. The existing 480 audience body-part transforms change. No new mesh source or texture collection is introduced. Clothing overrides are object-owned; shared material datablocks are not globally mutated. These are simple static proxies with three inherited gesture templates and five garment materials, so repeated low-detail silhouettes remain an artistic limitation.

2m cell occupancy is only a spatial measure, not a realism score. The maximum rises from two to six foot centers per 4m² cell. Near/middle/outer zones are measured from the screen anchor [0,45.8]: radii below 9m, 9–12m and at least 12m. After counts are A 40/47/57, B 42/51/59, C 40/49/59. The front zone is fuller while meaningful pockets and the center remain open. Whole-body placements avoid a **3.3m-wide central aisle**. The independent triangle-overlap test is separate from foot-center maps.

## Shop conflict: investigated, not silently applied

Sections 4–5 of the approved document require side-wall shelf placement while locking storefront architecture and other geometry. Actual inspection found that all five nominally open stores are solid building cuboids (8 vertices / 6 faces), with a decorative dark front plane and a shallow wood layer. They have no interior cavities. A ray at the middle of each existing opening hits the solid front at |X|=4m. Moving shelves into these blocks would hide them in masonry, failing the required visible stock and wall clearance.

The affected shops are left Y=-25,-7,+2 and right Y=-16,-7. There are 45 shelf boards and 180 associated cartons (225 stock objects total), plus five counters. **None of these stock, counter or building objects has moved in this delivered master.** The five counters and the DJ tabletop/legs have exact unchanged transforms and mesh/UV hashes in `evidence/preservation-audit.json`.

A concrete minimal exception is prepared: behind each existing opening, author a 3.8m-deep, 6.2m-wide, 2.85m-high interior recess, leaving exterior bounds, signs, shutters and all counters unchanged. Rotate each complete shelf/item group rigidly onto two interior side walls, preserving shelf/item relative offsets. This would change five building meshes, five front trim/recess meshes and the five wood backplane positions. Closed stores remain unchanged. The measured proposal is in `review/shop-interior-exception-proposal.png` and exact interface data in `evidence/shop-solid-host-and-recess-proposal.json`.

`source/prepare_shop_interior.py` is **guarded, conditional source only**, not an applied change. An unlinked diagnostic-copy test verifies a closed 16-vertex/14-face building cavity and 16-vertex/16-face front trim with positive signed volumes; this is not candidate topology or visual acceptance. Any approved application must still undergo full shelf/counter/visibility and layout testing, matched shop after renders and preservation audit. Current lighting is locked; no fill has been added to compensate for potential dark interiors.

An explicit question for that small architecture exception is pending. General continuation is not treated as an answer to the exception. The overall task is therefore incomplete and the five shop images are labelled **current/unchanged**, never falsely labelled relocated after images.

## Matched rendered evidence

`GALLERY.html` presents all full-resolution PNGs. The 28-page phone-friendly PDF is `review/Gullyverse-Rev05A-Banner-Crowd-Pending-Shops.pdf`. There are **21 matched before/after pairs** across A/B/C: frontal banner, oblique banner, human-eye audience, overhead plan, wide hub, lane landing and mobile-aspect lane. Fifteen additional before/current shop views cover all five shops in all variants. One supplementary high-angle C crowd preview is labelled as an unmatched inspection. Total: 58 actual rendered PNGs.

Blender 4.3.2, EEVEE, 16 samples; 1200×750 desktop / 540×960 mobile, resolution 100%, original world, exposure and lights. Matching validation confirms identical camera position, rotation, lens, sensor width, camera type, dimensions, exposure, engine and samples for every pair. New cameras are explicitly diagnostic, including the elevated hub shot. All original cameras remain unchanged. The manifest records each PNG hash, actual pose, settings and observed render duration. Rendering used the exact protected Rev04 and the authored intermediate; the review master adds only eight diagnostic cameras and pending-status metadata. No rendered image is substituted with generated concept art.

The original 40-second action remains exact; no new video is claimed. Rev04's previously backed-up actual-motion excerpt remains the historical motion evidence. The current study validates every action frame numerically. These are offline Blender images, not actual browser acceptance captures, live Aftermovie playback or hardware FPS.

## Validation

- **PASS:** actual 156 audience instances / 1,248 parts; 12,090 cross-actor pairs; zero triangle overlap pairs and zero audience/prop triangle overlaps. Standing floor contact is excluded appropriately. Body bounds remain in the front viewing region and outside the central aisle; feet within 0.002m of the floor and screen-facing angle within 11 degrees. Actual local matrices are used rather than stale inactive-collection caches.
- **PASS:** 960 frames per variant, X=0, monotonically forward Y, stable camera orientation/lens, no camera intersections within the existing 0.35m check. Maximum measured eye-height error approximately 0.00000065m. No tolerance relaxed.
- **PASS:** existing straight entry/screen, Team-right and Events-left route capsule/floor checks. Minimum measured route-ray clearance: entry 1.512m, screen >1.6m, Team 0.981m, Events 0.625m. These are survey ray results, not guaranteed continuous free-space radii or regulatory accessibility certification.
- **PASS:** non-target geometry/UVs/materials/transforms, lights/world, all original cameras and action unchanged; only the exact banner removed. All eight counter/table objects retain exact transforms/mesh hashes. Stock remains unmoved pending the exception.
- **PASS:** 24 referenced images packed; no missing external font dependency. Restored-master and file checks are recorded separately by the checkpoint verification receipt.

No browser build/navigation/playback test was required or changed by this Blender-only correction. The live website has no new code or assets. The offline checks do not certify browser collision, production art, animated crowd behavior or physical-device performance.

## Cost and remaining limitations

Additional evaluated geometry is 28,800 triangles in A/C and 28,798 in B (the removed banner costs two triangles). All 12 authoring lights and 24 packed images remain unchanged. Estimated unique image allocation remains **95.86MiB RGBA8+mips** in this Blender study; this is not measured web/GPU residency. Offline evaluated mesh/curve object counts A2,195/B2,290/C2,229 imply significant future batching/instancing work. No runtime draw-call estimate is invented. Software still-render durations in the manifest are not interactive frame-time distributions.

The audience is visibly denser and less regimented from overhead, and the large red banner is absent. The crowd, flat scene masses and stock remain blockout-quality; lighting/material fidelity was deliberately not changed. The main nav board still dominates the intended centered composition. A/B/C selection remains open. The shops cannot meet the interior-stock requirement while their solid architecture is locked. Do not call the overall correction complete or begin full look-dev automatically.

## Checkpoint and next action

New dated Drive task folder: https://drive.google.com/drive/folders/1omP_p-Cl2Dt_zvYghIwiI-Qf53xn0Hby

Review: https://drive.google.com/drive/folders/1cdx96DqpSuDXVt_DooSKouk7AQzlAlCy

Checkpoint: https://drive.google.com/drive/folders/1yWQdepeRqWzuvD23eWGujF2lDtI8cP25

The current packed review master opens independently. The exact Rev04 master, audience input data, inherited source/license manifests and portable scripts are included for reconstruction. Source/report and A/B/C image archives must all be extracted into one fresh directory for the complete HTML gallery. `RESTORE.md`, per-file hashes and the archive index explain restoration. Full download-back and independent extraction/open results are separate post-upload verification receipts; use those receipts to determine external backup verification, not an unverified assertion inside this document.

Stop at the pending narrow shop-interior exception and user visual review. No high-fidelity pilot, website work or next phase has started.
