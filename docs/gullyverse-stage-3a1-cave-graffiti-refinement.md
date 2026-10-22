# Gullyverse Stage3A.1 — short native-rock pilot and tunnel sampling

Handoff: STAGE3A1-PILOT-20261021-647eddc5

## Decision and scope

**NO-GO: FAIL VISUAL AND NEW VISIBILITY. Do not expand this pilot or promote it.**

A true native-triangle formation was integrated into the existing6–15m passage. It has deeper physical relief than the old envelope-derived wall, but neutral browser images expose stretched return faces, thin ribbons and an isolated patch. Strict first-hit validation also fails. The prompt explicitly requires stopping at this gate; therefore full42m extension, entrance-collar/foot refinement and subsequent art work were not attempted. This is a completed bounded pilot evaluation, not a completed entrance/tunnel overhaul or approved production art.

The reversible private selector is `/?diagnostics&quarryReview=geology-fidelity&entranceReview=deep-rock`. Prior Stage3A remains `entranceReview=natural-cave`. Ordinary public C5.1 and the selected C9 quarry remain unchanged. No commit, push, merge, deployment, public promotion or next phase occurred.

## Exact starting baseline and preservation

Branch `codex/navigation-board`; HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. Started from completed Stage3A handoff `STAGE3A-20261021T052321Z-1aa3fd6a` plus all surviving user work. Starting snapshot:5,076files,4,125,155,103bytes. Preservation check: PASS; 5072starting files unchanged, four scoped existing source files changed and zero missing files. New code, art and evidence are additional files.

The scoped existing edits are CaveEntrance.tsx, CaveEntranceSession.ts, ImmersiveShell.tsx and caveReview.ts. Quarry footprint, blockout registry, collision, floor path, cameras, navigation, scaffold, destination positions, global lighting/fog/exposure/sky, stage/crowd/video, public C5.1, historical C8/C9 and completed Stage3A assets retain their recorded starting hashes. `raw/preservation.json` and the complete starting inventory provide file-level proof. Historical reports and failed experiments are retained.

C9 uses the accepted `geology-fidelity` selection and its uniform0.9scan transform. This phase does not alter its rock mesh, geometry-normal UV1 bake, LOD rules or material. The C8 quarry sampler remains exactly `.061782042468605296` on both axes, representing approved3x feature size.

## Reference assessment and remaining target

The preserved approved concepts and real-cave photographs were inspected alongside the prior23-page Stage3A review. Their entrance has a thick asymmetric mouth integrated with neighbouring rock, substantial shoulders and ground contact. The real interiors have broad connected stone bodies, irregular but readable sidewalls, physical fractures, recessed crevices and ceiling mass; fine grain supports those forms. Grey-brown/charcoal stone, restrained warmer exposed faces and selective lighter surfaces follow geology and illumination. The reference shade distribution is not a licence for random colour patches or artificial painted shadows.

Existing Stage3A still has a smooth connecting collar, thin captured edges, repeated vault rhythm and weak floor contact. This pilot improves local relief depth but does not solve the reference's continuous rock-body composition. It fails before materials are considered: neutral map-free images still show an artificial joining construction. Dusk materials can make this less obvious, which is why no material or lighting change was accepted as a cure.

No large physical GULLYVERSE word or visible ceiling/hanging fixture was added. The previous Stage3A assets already omit them; quarry scaffold lettering and ordinary UI branding are preserved. Existing tunnel lighting is unchanged. There are zero new dynamic lights, fixtures or new global-light settings.

## Modelling method and source proportions

The pilot uses authentic Poly Haven Coastal Cliff01, CC0-1.0: https://polyhaven.com/a/coastal_cliff_01 . Original source: `assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend`, SHA256 `091b3d5a8a1b649b56c5a07f6bc43fe61893695f2b5ecb512ba7d58641763aef`.

Measured native LOD2 dimensions:91.97974x10.95954x10.32364m,115,455triangles. A6.2x3.2m irregular crop is taken near nativeX−27,Z4.6m, with uniformXYZ1.0scale. Two rigid rotations align it to the left passage near station11.2m; a rigid wall-depth translation places the nearest formation outside the protected corridor. Exact origin, matrices, eight crop corners and translation are in the runtime manifest. The native scan and original high passage remain editable in the new Blender masters.

Actual captured triangles and their re-entrant depth are retained. This is not a new front-envelope heightfield, Gaussian displacement, random noise cliff, C7 folded plane, C8 Boolean union or stretched source chart. The formation nevertheless requires joining to a different cave surface. Boundary topology is ordered intrinsically through genuine scan undercuts; its607parameters are shared with a local cut in the old passage. Local cut T-junctions are resolved; the return reaches2.206m depth. Those long returns and their interaction with the surrounding surface are the concrete modelling failure. Position-welded, manifold topology alone does not guarantee an unself-intersecting, visually credible solid.

The final metadata records2,776cropped source triangles. An early log erroneously labelled the remaining22,852shell triangles as source triangles. That bookkeeping error is corrected in the final manifest and VALIDATION-STATUS.json; the shipped GLB is unchanged. Initial failed export/UV attempts and two Blender crashes are preserved as evidence.

## Editable master, UVs and runtime production

New assets are confined to `assets-source/gullyverse/c9-cave-deep-relief/` and `public/models/gullyverse/c9-cave-deep-relief/`.

- `cave-deep-pilot-authoring.blend`: editable pre-unwrap continuous surface, native reference and original high body.
- `cave-deep-pilot.blend`: editable high source and runtime LODs. Both open successfully, with no missing linked images; source-accessibility status PASS.
- `cave-deep-pilot.glb`:21cave parts/LODs, no embedded PBR images; SHA256 `647eddc5c9b2f814febc56eeda237712ffb768439a51af4118060982ed38c713`.
- `scripts/blender/author_cave_deep_pilot.py` and `cave_native_graft.py`: reproducible local authoring; existing shared-frame and genuine MikkTSpace tools remain preserved.

A single high-mesh UV unwrap pins the established end rings before LOD generation. Runtime interpolation preserves that UV layout. True fracture edge splits and common adjacent frames are retained. Early cube-projection seams produced invalid tangent derivatives and were rejected. Ground-contact vertices are protected during reduction after a nearly flattened floor triangle caused a second strict derivative failure. Final exported normal/tangent lengths and dot checks pass; counts of zero-area UV faces, degenerate triangles and non-manifold interior edges are all zero in the runtime validator. No fake tangents or DoubleSide workaround was used.

The rest of the cave reuses previous geometry in this local cave export; no complete quarry GLB is duplicated. The previous private mouth terrain-clearance overlay is shared unchanged. Its local eye-height obstruction remains0 versus the historical6; this phase did not claim a new terrain repair.

## Tunnel-only2x material sampling

`CaveTextureSampling` consolidates the five borrowed glTF map wrappers into3owned sampler wrappers sharing the parent's source images. Albedo, OpenGL normal and ORM channels halve repeat once to `.030891021234302648`; roughness, metalness and AO reuse the same ORM wrapper. Colour spaces, offsets, orientation and channel assignments are preserved. The operation does not compound under repeated1x→2x→2x switching. Quarry wrappers are never mutated or disposed by the cave. The GLB-decoded parent repeat is actually .06178204218546549 because the authoring transform was quantized to float32; the local repeat is exactly half of that, .030891021092732746. The nominal figures above describe the same accepted3x ratio. No geometry threshold is changed for this representation detail. Geometry-derived quarry UV1 remains independent.

This enlarges features2x relative to Stage3A sampling rather than adding repeats. Entrance exterior and floor retain their previous treatment. No new material image collection, new source image, AO multiplication or dynamic displacement shader is introduced. Source sharing is proven in the unit test and actual runtime diagnostics. A first allocation probe found redundant ORM aliases (5owned wrappers) and an over-strict decimal-constant assertion. The cave-local helper now reuses only genuinely equivalent views, including channel, colour-space and sampler settings; different UV1 or sRGB interpretations remain separate. The first failed probe is retained; the final repeated-switch result is authoritative. The image probe deduplicates ImageBitmap objects in the current scene, including invisible LOD clones; cache-only unmounted owners may not be included, so this is not total driver residency. Driver allocations and measured texture counters are reported separately; image sharing is not a claim of zero shader/upload cost.

The pilot's unwrap differs from Stage3A internally, so old-versus-new textured images do not isolate geometry alone. The mandatory neutral comparisons do. New-pilot1x versus2x comparisons use identical geometry, UVs, camera, lighting and quality and isolate the sampler change. Larger grain does not repair the failed physical join.

## Geometry, clearance and visibility gate

Strict original thresholds are unchanged. glTF validator:0errors,0warnings. All21runtime meshes pass topology, nonzero UV-area, finite normal/tangent and protected-envelope checks. Shared boundaries remain within2e−5m; adjacent part/cross-LOD shared positions match exactly. No walking-envelope intrusions or new uncovered interior rays were found.

The75,852-ray survey reports **22/21/20new inverted first hits** at LOD0/1/2, all in Passage1. These are new pilot failures, distinct from the seven inherited unrelated C9 upper-quarry defects. The original Stage3A local survey had0such new hits. Corrected terrain hits remain0. The validation result is FAIL regardless of the successful glTF, tangent, collision and seam checks. `raw/full-cave-geometry-validation.json` retains every failing eye, ray, point, part and face. No tolerances were relaxed.

The neutral browser result also fails independently: connecting ribbons, folded returns, an isolated coarse patch and abrupt relief-density changes remain. Do not expand this joining algorithm along42m. The underlying mismatch between an open coastal capture and the desired continuous cave body needs compatible local surface topology and deliberately retopologized geological breaks; merely repeating this crop or adding subdivisions/noise will not solve it.

## Actual-browser review evidence

50primary full-resolution PNGs plus4final resource-verification PNGs in the gallery, 23-page phone PDF and 52-page full screenshot PDF are available with gallery.html. The full PDF embeds original PNGs losslessly; the phone PDF uses reading derivatives, retaining original files separately. All acceptance evidence uses the real browser renderer; native-source analysis images are separately labelled authoring diagnostics.

Desktop1366x900 and mobile390x844, actualDPR1, tier0, FOV58. These50images predate the resource-only ORM-wrapper consolidation; geometry, UVs, map images and sample transforms are unchanged. Four final-build re-renders and their pixel comparison are recorded separately. Both dusk images and the neutral side image match every pixel. The neutral walking image differs only at the far-right distant Passage4, whose automatic hysteresis selectedLOD0 instead ofLOD1 (+3,500visible triangles); pilot geometry remainsLOD0 and its pixels are unchanged. Whole-frame pixel identity is not claimed for that view. No review PNG was altered. Thirty matched pairs are checked in matched-pose-verification.json:20old/new comparisons and10same-geometry1x/2x comparisons. Actual camera/quaternion, FOV, viewport, DPR, quality and lighting match. Neutral views remove albedo/normal/ORM maps and use a clearly temporary neutral setup. Approved dusk views preserve all default environmental lighting.

The cameras are protected entry-choreography inspection positions, not ordinary25m hub visitor viewpoints. Along-wall offsets are additionally diagnostic. The current work is tunnel art; it does not redefine approved public movement bounds. Parallax A/B, side fracture, walking trajectory, approach and vault views are included. The full entrance pp2–7 overhaul and broader tunnel pp8–13 extension are deferred by the failed pilot gate; original Stage3A context is preserved in its protected gallery rather than relabelled as new Phase3A.1 work.

## Graffiti and scope limits

The exact supplied transparent artwork assets for Neha Kakkar, Khullar G, Nikhitha Gandhi, Ritviz, Twin Strings, Chaar Diwari and Yellow Diaries are still pending in the current recovered task assets. No generic final graffiti or two new placements were invented. Missing art did not block the geological pilot. This phase adds no exterior artist names, painted signs, new ceiling fixtures or new quarry branding.

## Geometry and transfer budget

Stage3A totals were 48,736/23,836/12,536triangles. Pilot totals are 54,335/26,935/14,035; the changed part alone is11,999/5,999/2,999. Added triangles are 5,599/3,099/1,499. These increments are not accepted as worthwhile because the art gate fails.

Local GLB bytes: previous cave 4,603,424; pilot 5,062,404; shared clearance 397,124. Combined current local payload 5,459,528 versus5,000,548B, a 9.18% increase. Additional PBR download bytes0 and new unique image payload0. All three LODs remain cached by the existing owner; screen-space selection and frustum culling remain active. No new loader dependency, texture compression system, tessellation or full-world streaming architecture was added.

## Default cold-stage and context-pressure investigation

Existing45s gate and default initial tier0 were preserved; neither timeout nor assertions were weakened. The direct-stage candidate requests no local cave GLB until first hub/map visibility. It then adopts the same cave and C9 owners under the existing cover with the same Canvas. This isolates unseen cave loading from direct-stage startup.

- approved-c9 cold direct stage: FAIL_PREPARATION_DEADLINE; elapsed 47116ms.
- deep-rock cold direct stage: PASS; elapsed 44455ms.
- Deferred cave is adopted under cover before map/hub, same Canvas and C9: PASS; elapsed not applicablems.

In the passing candidate direct-stage sample, recorded GLB parse/decode includes a576.8ms sample, texture initialization69.4ms and shader compilation14.9ms. The readiness render window dominates at38,058.2ms, within a44,455ms overall cold load. The gate flushes2frames and measures12frames at each automatically selected tier; a slow software renderer can traverse four tiers, requiring up to56render frames before readiness. This is the measured bottleneck here, not evidence that real laptop loading takes the same time. The quarry-only cold sample failed at47,116ms and remains an inherited deadline failure. A narrowly passing software sample is not reliable default acceptance.

The combined desktop/mobile regression retains its concurrent contexts and original90s landing assertion. Its raw result below is authoritative; isolated or forced-tier3 continuation is not substituted for that default gate. The separate journey and profiling runs explicitly use tier3 to gather bounded functional/performance diagnostics. No claim of fixed deadline stability or physical-device acceptance is made.

## Build, regression, resource and playback results

TypeScript and production build pass after fixing a new descriptor typing mismatch. Lint passes with preserved existing warnings. All100immersive unit tests pass, including shared sampler ownership/noncompounding behavior and private selector carry-through. Initial failed build/type logs are retained beside final successful logs.

- direct-stage-cave-gate.mjs: exit 0, 114.7s (DONE).
- candidate-regressions-cave.mjs: exit 1, 538.0s (DONE).
- record-cave-walkthroughs.mjs: exit 0, 274.8s (DONE).
- cave-ownership-recovery.mjs: exit 0, 255.9s (DONE).
- preview-persistence.mjs: exit 1, 128.0s (DONE).
- directional-travel-cave.mjs: exit 0, 89.1s (DONE).
- profile-cave-comparison.mjs: exit 1, 250.9s (DONE).

- composition-browser-checks.json: Fidelity uses the original35.557m local region, shared C8 maps and unchanged non-target geometry: PASS; Ten C8/C9 cycles plateau; native geometry and shared image IDs are reused: PASS; Actual context loss/recovery preserves C9, pose, images and Canvas: PASS; Explicit inactive retirement and reload free only owned C9 resources: PASS; Complete fallback unmount releases local geometry and one bake without double-close: PASS; Failed fidelity-region.glb retains C8 and retries without another complete quarry download: PASS; Failed fidelity-bake.glb retains C8 and retries without another complete quarry download: PASS; Invalid local geometry with embedded PBR images is rejected and its own images closed: PASS; Delayed local geometry stays covered until both material and local owners are ready: PASS; Unmount during delayed local loading drains unpublished resources: PASS; Failed local c9-cave-deep-relief/cave-deep-pilot.glb preserves accepted C9 and retries: PASS; Failed local c9-cave-recovery/entry-clearance.glb preserves accepted C9 and retries: PASS; Unexpected embedded cave textures are rejected and closed without touching shared C8: PASS; Unmount during delayed cave loading drains unpublished geometry: PASS; Ordinary public URL remains C5.1 without C8/C9 assets or controls: PASS
- preview-persistence.json: FAIL
- directional-travel.json: Public held-key directional Aftermovie gate, covered travel and same Canvas: PASS; Actual boundary clamp, Esc stays, hysteresis re-entry and covered Return to Hub: PASS
- browser-walkthrough.json: PASS
- automatic-lod-walk.json: PASS
- repeated-tunnel-sampling.json: PASS

Additional default preview-persistence travel failed with the original45s stage-preparation error at automatic quality2; this is a candidate failure with the same readiness pattern as the quarry-only cold failure, not a claim of a resolved regression. Later history assertions in that script were not reached. The separately recorded journey and seven passing combined-suite groups do not override it.

Browser results are in raw/regressions/results.json and per-script JSON/logs. The queue runs browser suites sequentially to limit unrelated contention, except for the historical combined suite's intentionally concurrent desktop/mobile contexts. Inspect check-level status, not exit code alone: the direct-stage script deliberately records HAS_DEADLINE_FAILURE while continuing the other checks. Failed first-hit geometry is independent of browser navigation success.

The final post-consolidation production build is WkDLrfjIEo-S3ibJCUS6-. Final profiling is PASS across15settled windows and4cold/warm loads; repeated tunnel sampling is PASS for12switches with3owned wrappers and unchanged24unique images. Final ownership/recovery checks were rerun after consolidation; consult run-ownership-final.log and composition-browser-checks.json. The earlier queued profiling exit1 is the retained pre-consolidation allocation probe, not the final profile.

## Matched software performance and loading

All samples are SwiftShader diagnostics, not physical integrated-GPU or phone certification. Profile configuration:1366x900, requestedDPR0.5, tier3, sequential settled8-second windows, cold browser cache cleared and warm reload retained. Screenshot tier0/DPR1 and default-gate tests are separately labelled. Actual driver VRAM is unavailable; unique decodedRGBA8+mips is an estimate. Localhost transfer is not an Internet guarantee.

- natural-cave / entrance: 13frames, 1.51 softwareFPS; p50/p95/p99 617.2/792.2/792.2ms; draws 179, visible triangles 174632, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave / mid-passage: 14frames, 1.73 softwareFPS; p50/p95/p99 533.5/683.2/683.2ms; draws 177, visible triangles 191829, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave / pilot-passage: 19frames, 2.32 softwareFPS; p50/p95/p99 389.1/620.4/620.4ms; draws 27, visible triangles 140566, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave / hub: 20frames, 2.47 softwareFPS; p50/p95/p99 352.9/577.0/577.0ms; draws 167, visible triangles 187661, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave / aerial-map: 17frames, 2.05 softwareFPS; p50/p95/p99 454.5/604.7/604.7ms; draws 181, visible triangles 159838, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave / original-stage: 10frames, 1.23 softwareFPS; p50/p95/p99 810.2/856.6/856.6ms; draws 134, visible triangles 1040190, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / entrance: 13frames, 1.52 softwareFPS; p50/p95/p99 607.5/644.2/644.2ms; draws 179, visible triangles 176131, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / mid-passage: 14frames, 1.73 softwareFPS; p50/p95/p99 499.6/779.1/779.1ms; draws 177, visible triangles 191829, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / pilot-passage: 19frames, 2.27 softwareFPS; p50/p95/p99 393.9/793.4/793.4ms; draws 27, visible triangles 146165, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / unfiltered-opening-comparison: 18frames, 2.14 softwareFPS; p50/p95/p99 398.4/684.9/684.9ms; draws 27, visible triangles 146165, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / cave-geometry-hidden-diagnostic: 55frames, 6.40 softwareFPS; p50/p95/p99 131.9/181.6/282.8ms; draws 23, visible triangles 109030, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / neutral-material-cost-diagnostic: 26frames, 3.14 softwareFPS; p50/p95/p99 311.2/350.1/354.5ms; draws 27, visible triangles 146165, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / hub: 26frames, 3.23 softwareFPS; p50/p95/p99 302.7/325.0/340.3ms; draws 167, visible triangles 187661, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / aerial-map: 15frames, 1.82 softwareFPS; p50/p95/p99 479.4/749.1/749.1ms; draws 181, visible triangles 161337, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- deep-rock / original-stage: 10frames, 1.24 softwareFPS; p50/p95/p99 796.9/822.1/822.1ms; draws 134, visible triangles 1040190, texture counter 28; unique images 24, estimated RGBA8+mips 116.05MiB.
- natural-cave cold: ready 21359ms, measured localhost transfer 26233154B; cave transfer 2844475B.
- natural-cave warm: ready 19425ms, measured localhost transfer 3600B; cave transfer 600B.
- deep-rock cold: ready 24713ms, measured localhost transfer 26514627B; cave transfer 3125948B.
- deep-rock warm: ready 22214ms, measured localhost transfer 3600B; cave transfer 600B.


## Independent checkpoint and restoration

The new phase folder is https://drive.google.com/drive/folders/1o-exjjnTHRic88qhhLdn_SGIog4b8rIO and pilot subphase https://drive.google.com/drive/folders/1XTOTiwpfbJkpVhVHDG9T_CPWxpGnxCAk . REVIEW and CHECKPOINT are distinct children. Earlier phase folders and verified files are not renamed or overwritten.

The checkpoint is an exact overlay on the protected FINAL Stage3A dependency chain, not a pointer-only Git bundle. It includes every new/changed source file, both editable masters, native-source provenance, real runtime GLB, material contract, tests, raw failed and successful logs, original PNGs, PDFs, gallery and recordings. The full-current-tree inventory accounts for unchanged inherited user work and authentic parent LFS/stage/media/source assets. Exact dependency archive indexes/hashes are in DEPENDENCIES.json.

Download every archive and metadata file in checkpoint-index.json, verify SHA256SUMS.txt, restore the complete protected Stage3A parent in a new location, extract this overlay separately and run apply-pilot-checkpoint.py. It preflights every conflict before writes and atomically replaces only expected files; unrelated files remain. Do not concatenate independent ZIPs. Secrets/private.env, dependencies, build output and redundant caches/autosaves are excluded without deleting them from the workspace.

The final loose restore-verification.json records independent reconstruction, full-tree hashes, idempotent replay and conflict refusal. DRIVE-BACKUP-RECEIPT.json records full remote download-back SHA256, size and parent checks. Consult those final receipts for actual backup certification; a folder link or this report alone does not certify the transfer. The shared Doc handoff links the verified outputs. No claim is made that the user has downloaded a personal copy until they do so.

## Recommendation

Keep C9 and the original Stage3A comparison intact. The sampler change is technically isolated and available for visual review, but the integrated geometry pilot is **not ready for adoption**. The principal remaining limitation is the local source-to-cave topology and composition, exposed under neutral light and confirmed by first-hit defects. Do not extend this surface, add another noise pass or hide it with exposure/DoubleSide. A future authorized attempt must first establish a compatible continuous cave-side surface and geological cut boundaries with safe local retopology; it must pass the same short neutral and first-hit gates before any full-route extension.

Stop for user review. Entrance-collar/foot overhaul, full42m deep geology, exact graffiti integration, real-device performance and the inherited C9 defects remain unresolved. This report does not label the pilot photorealistic or mark the larger Stage3A.1 art request complete.
