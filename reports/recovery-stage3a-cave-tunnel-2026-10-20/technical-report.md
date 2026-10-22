# Gullyverse — Stage 3A private cave and tunnel recovery

Created 2026-10-21T05:23:21.850672+00:00. Handoff `STAGE3A-20261021T052321Z-1aa3fd6a`.

**Private candidate delivered for visual review; NOT production-ready.** C9 and the user-approved C8 3× appearance are preserved. The 42 m rocky passage, entrance-clearance correction, shared resources and navigation work privately. The entrance still has an engineered joining collar and thin captured cliff edges; the supplied cave concepts are not yet faithfully matched. Exact graffiti PNGs for all seven artists remain unavailable. No generic replacement artwork was invented. Art approval and physical-device acceptance are pending.

## Starting baseline and preservation

Branch `codex/navigation-board`, HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. The starting snapshot at 2026-10-20 13:26 UTC contains 4,590 files. 4,587 remain byte-identical, with no deletions. Exactly three existing files changed for private integration: ImmersiveShell.tsx, HubScene.tsx and AftermovieScene.tsx. Every other addition is a new cave-specific file or evidence. Prior modified/untracked user work is preserved.

The user-approved selected quarry is `quarryReview=geology-fidelity`, accepted on 20 October after handoff PHASE3-20261020085923Z-a8992350. It incorporates the native uniform 0.9× hero; the original recovered `scanned-composition` remains an independent historical comparison. Ordinary URLs still select public C5.1. No selected C9 rock, UV1 bake, material holder, light, world layout, collision registry, map, stage, crowd, video, destination, original source master or previous backup was replaced. Preservation hashes are in raw/preservation.json and raw/starting-state.json.

## Reference inspection and reconstruction limits

Five actual recovered images were inspected and copied with provenance into assets-source/gullyverse/c9-cave-recovery/references: the approved landing concept, approved tunnel concept, real cave mouth, tall tunnel entrance and rocky interior photograph. The landing concept supplies an asymmetric, thick stone mouth and deep throat; its oversized physical GULLYVERSE lettering is expressly rejected. The interior references show broad eroded planes, locally thick broken bodies, uneven vaults, recessed joints and a comfortably clear granular floor. Mineral variation must be distinguished from sunlit surfaces and shadow.

The latest Doc's phrase “no visible tunnel ceiling” was interpreted with the user's detailed instructions and recovered Stage3A prompt as a natural enclosed rock vault with no artificial ceiling panels or visible light fixtures. That working interpretation was disclosed; the 42 m passage remains enclosed until the existing reveal. The small existing BREEZE 2027/GULLYVERSE interface branding and CTA remain. The quarry scaffold lettering and its unrelated lighting remain untouched.

The old Stage3A implementation report is available, but its original Blender/GLB assets, exact painting PNGs and original 62-page screenshot package did not survive in this workspace. Actual authenticated/local searches did not recover them. Before images therefore show the **surviving approved C9 quarry with the legacy entrance/tunnel**, not a fabricated reconstruction of the rejected old Stage3A. The historical report's costs are quoted only as historical data, not a current matched measurement.

## New entrance and immediate geological connection

The editable entrance starts from authentic Poly Haven Coastal Cliff 04 CC0 geometry, native dimensions 86.77198 × 24.24743 × 10.99971 m. It is uniformly transformed by **1.7× XYZ**, then cropped around the protected route. The 1.7× exception is deliberate: the native roughly 11 m vertical capture supports the existing approximately 18 m entrance mass; width is cropped rather than fitted. The final visible envelope is 15.90 m tall. Native source and transformed authored meshes remain in the master. A tightly localized foot brush moved 17 vertices by at most 0.402 m to bury a captured fin; the result is not falsely described as an untouched rigid scan.

The asymmetric mouth is cut into the same authored rock surface; a shared 257-parameter cut edge returns into the rock throat. There is no Boolean union, no 5–7× horizontal fitting, no C7 folded-plane cliff and no decorative ring of boulders. The old tunnel interior is removed only after the new private owner is ready, retaining its outer landscape body. That retained exterior borrows the same approved material without moving its positions/normals. The connection is structurally valid but still **too smooth and collar-like** in the neutral front inspection. Some captured cliff edges read thin and angular. These are new candidate art limitations, not inherited C9 fixes.

## Local terrain obstruction correction

Actual runtime/CPU hits found **both Foundation_Terrain_1_2 and Foundation_Terrain_2_2** in front of the mouth, rather than only the historically reported 2_2. A private attributed-triangle clip affects their six LOD nodes inside WebGL volume `lo=[-4.5,-0.12,-7.5], hi=[4.5,7.5,13]`. The underground bottom edge is buried below the unchanged authoritative floor; no collision/nav registry changed.

LOD0 tile 1_2 retains 952 of 959 triangles untouched and clips seven; tile 2_2 retains 940 of 946 and clips five. The same interface is applied across all three LODs. The 108-pose eye-height path survey falls from **six obstructing hits to zero**. The exported local overlay is 397,124 bytes, SHA-256 `53393e5234f7fc622ef702a69314ae66fc27d5c92853393a4fdf856dee0116d7`. A neighboring terrain/rock contact outside the cut box remains visually weak at the left foot; this bounded clearance correction is not a whole-entrance art approval.

## Rocky tunnel and walking surface

The unchanged bent route runs [0,0] → [-2.2,-8] → [-6,-16] → [-6,-24] → [-2.6,-34] → [0,-42]. Existing camera choreography, walking half-width 2 m plus 0.38 m player radius, eye height and reveal timing remain authoritative. Visual sides remain at least 2.55 m from the route; the protected 2.38 m envelope is untouched.

Four jointly authored passage sections span 6–15, 15–24, 24–33 and 33–42 m after the entrance throat. Physical surface relief comes from native-scale Coastal Cliff 01 geometry (91.97974 × 10.95954 × 10.32364 m), sampled at 0.15 m with **1 metre per source metre**, its broad coastal slope removed at 0.85 m Gaussian scale. 216 missing samples of 24,428 were interpolated locally. This is **scan-derived cave retopology, not scanned cave photogrammetry**: front-envelope transfer loses hidden source undercuts, and composing it around a passage does not supply all of the reference caves' interlocking 3D bodies. Neutral geometry shows real medium relief but also regular passage proportions.

A diagnosed throat fold was repaired locally with pinned shared boundaries; the failed first survey and exact repair parameters remain in the evidence. No random displacement is used. The floor uses existing dry terrain images on a thin dust/gravel visual overlay 0.012 m above the unchanged walking plane, feathered with vertex alpha. It adds no obstacles. Ground contacts remain cleaner and more uniform than the real photographs; no photorealistic claim is made.

## Approved material and 3× contract

The selected C8 marble_rock_03/rock_face_03 scanned multi-material holder is borrowed unchanged: **0.061782042468605296 repeat**, equal to the original 0.18534612740581588 / 3. New rock geometry supplies **one UV unit per 2 metres**. The effective atlas period is 32.371866 m, exactly the approved 3× contract; this enlarges features rather than tripling repeats. Albedo/normal/ORM remain aligned, albedo sRGB and non-colour maps linear. The C9 geometric bake on UV1 is unchanged. Projection islands are separated by exact tile periods, preventing arbitrary-offset phase seams. Vertex colour COLOR_0 is present and neutral on stone; floor alpha supplies dust fade only.

An intermediate cave trial accidentally applied the material repeat twice in geometry UVs; it was corrected before the final captures. It never changed the selected quarry material or C9 appearance. Trial images are retained but excluded from the curated final gallery. The existing non-metallic, matte dark neutral brown-grey palette is preserved. Lighter/warmer mineral variation comes from the existing scans, not random per-face colours or painted fake shadows. No new PBR texture collection is introduced.

## Lighting without visible fixtures

There are **zero new lights, zero ceiling/hanging fixtures, zero additional shadow maps**. Existing global quarry lights, sky, exposure and fog are byte-identical. Exterior material response is unchanged. Interior/floor material wrappers use a bounded analytical opening/overburden response: direct lighting multiplier 0.10 + 0.90 exp(-depth/6.5), indirect 0.55 + 0.45 exp(-depth/11), where depth is distance to the nearer opening in [0,42]. This is an inexpensive local spill/occlusion approximation, **not baked GI or a physically measured light transport solution**. It changes local reflected light, not the shared scan albedo or AO.

Separate actual-browser neutral inspection, approved dusk and unfiltered ambient captures are provided. Neutral diagnostics temporarily replace materials/lights and do not ship as production illumination. The strength-zero performance view uses the same compiled shader, so its timing is not presented as a clean subtraction of shader cost. Deep areas still rely on support illumination; the cave does not reproduce the reference sunlight or exposure, because the global dusk direction is locked.

## Exact graffiti status

All seven final artworks are **PENDING ORIGINAL IMAGE FILES**: Neha Kakkar, Khullar G, Nikhitha Gandhi, Ritviz, Twin Strings, Chaar diwari and Yellow diaries. Old attachment filesystem paths no longer contain the originals and authenticated recovery searches did not find them. The five historical authorized wall positions are retained in graffiti-slots.json; new placements for the additional two artists are not invented. No generic font, emissive sign, rectangular painting or invented final graffiti is rendered in the private candidate. Therefore per-artwork close/walking/mobile acceptance images cannot honestly be supplied yet. Historical generic graffiti remains available outside this private mode.

## Editable assets, LODs and shared ownership

Editable packed master: assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend, 44,922,834 bytes, SHA-256 `bf18482a3c019eddf9e1c4a64d7b69177af215c6443b1ea0dda2ba78806eff5f`. It contains native references, authored high-detail rock, runtime LODs, the embedded contract and all nine packed authoring images. Original CC0 providers and scanned maps live in the protected prior checkpoint dependencies and are identified by exact SHA in provenance. Restoring the final assets requires no regeneration/download. Blender reproduction uses scripts/blender/author_cave_recovery.py with its scan-surface/shared-frame helpers and the existing offline Three MikkTSpace module. Cross-version decimation/binary identity is not promised.

Runtime cave GLB: **4,603,424 bytes**, SHA-256 `1aa3fd6afd38996937a3f3da47ed63ab2c95a3a5d25d0fdf0638268a84719fc6`. Combined with the terrain overlay: **5,000,548 bytes**. Near/mid/far cave triangles: **48,736 / 23,836 / 12,536**, seven independently culled parts, 21 cached LOD meshes. The small floor is 736 triangles per LOD. Shared PBR image allocations added: **0**. Three cave material wrappers borrow existing images and are disposed separately; no borrowed quarry image is retired by the cave owner.

The authored pre-runtime composition has132,216 triangles (22,936 entrance,6,144 throat, four25,600-triangle passage sections and736floor), plus the separate untouched native reference meshes. Those reference/high meshes are retained in Blender and are not shipped to visitors.

The session subclasses the unchanged selected C9 owner. It never downloads another complete-world GLB. Local terrain geometry is overridden only for the six declared nodes, using the original terrain materials. Persistent Canvas, leases, covered shader preparation, frustum culling, context recovery and retry/fallback remain. A cold direct Aftermovie URL defers cave geometry entirely; first hub/map activation requests it under the existing preparation cover, once.

## Geometry, frames and inherited defects

Final GLBs validate with **0 glTF errors and 0 warnings**. All 21 local meshes have zero non-manifold edges, degenerate triangles, zero-area UV triangles or protected-walking intrusions. Valid unit normals/tangents and COLOR_0 are present. Shared positional/UV interfaces are exact across all nine adjacent LOD combinations at each partition; the unchanged positional tolerance is 2e-5 m.

Additional frame inspection caught independently calculated one-sided normals differing by up to 83.63 degrees despite matching positions. The repair derives common angle-weighted normals from the adjoining LOD0 faces, applies them to all LODs and regenerates genuine MikkTSpace frames. Blender's loop-space normal compression caused a further 0.000704 vector discrepancy; canonical float32 vectors are now carried into the exported GLB **without loosening the 1e-4 frame gate**. Final maximum matched normal-vector error: 0.0; maximum UV difference: 0.0; normalized float64 angular residual 1.20741827e-06 degrees. Earlier failed logs remain. This corrects shading attributes without changing rock positions, triangles, protected clearance or UVs.

The full local visibility survey casts **75,852 horizontal/upward/diagonal rays** across three LODs: zero new inverted first hits, zero uncovered interior rays and zero clearance failures. The seven known C9/terrain visibility defects were independently replayed with the original Blender/BVH convention and remain **inherited and unchanged**. Whole-world visibility is therefore **not an all-pass result**. New stone uses FrontSide; double-sided materials were not used to hide failed cave geometry. Open captured exterior boundaries and remaining art seams are described rather than falsely represented as a watertight natural rock body.

## Source and browser regressions

| Check | Result | Duration |
| --- | --- | --- |
| typecheck | PASS | 9.25 s |
| lint | PASS | 2.21 s |
| immersive-unit | PASS | 5.95 s |
| production-build | PASS | 44.23 s |

All 97 immersive unit tests passed. Existing lint warnings are retained; no dependency upgrades or loader additions were made. The local build uses non-secret invalid Supabase placeholders, so payment/backend/live service behaviour is not certified by this build.

| Browser group | Result | Duration |
| --- | --- | --- |
| direct-stage-gate | PASS | 117.65 s |
| review-captures | PASS | 663.00 s |
| cave-diagnostics | PASS | 194.26 s |
| private-regressions | FAIL | 351.64 s |
| directional-travel | PASS | 79.15 s |
| ownership-recovery | PASS | 178.41 s |
| preview-persistence | FAIL | 189.92 s |
| walkthroughs | PASS | 279.50 s |
| matched-performance | PASS | 340.80 s |

The direct-stage loading gate is intentionally more nuanced than its runner exit code: see raw/direct-stage-loading-gate.json in full. The prior approved C9 baseline hit its existing 45-second critical preparation limit in SwiftShader; the private cave direct-stage path initially also failed until offscreen local loading was deferred. Final measured gate status: **HAS_DEADLINE_FAILURE**. A passing candidate run is not a guarantee of reliable laptop/phone cold-start performance; the baseline deadline failure and narrow software margin remain recorded. No timeout, quality default, stage asset or strict test tolerance was increased to obtain a pass.

| Direct-stage check | Actual result | Navigation wall ms |
| --- | --- | --- |
| approved-c9 cold direct stage | FAIL_PREPARATION_DEADLINE | 46695 |
| natural-cave cold direct stage | PASS | 48060 |
| Deferred cave is adopted under cover before map/hub, same Canvas and C9 | PASS | n/a |

Navigation wall time starts before the app's active critical-preparation interval, so it must not be compared directly to the45second internal limit. The recorded phase timestamps in this final gate are the authority; the candidate's boot→arrival interval remains extremely close to the limit. A single pass with essentially no margin is not a reliable device-performance acceptance.

The navigation evidence uses real entry controls, pointer/key movement, map targets, playback/exit, history/direct reload, repeated travel and the same Canvas. C9 selection and material scale 3 are asserted throughout. Ownership evidence checks abandoned-load disposal, delayed/invalid assets, retries, context loss/recovery, repeated cache plateau and ordinary C5.1 loading without private assets. The first interrupted or failed browser cohorts are retained and explicitly superseded by the final build/results, not deleted.

**Two final combined browser groups are not all-pass.** The private-regression group passed7desktop/input/map/playback/history checks but timed out waiting for the mobile landing while an already-loaded desktop context remained active. The isolated mobile group uses exactly the same original assertions/timeouts with the other scene inactive: result **PASS**, retained separately in raw/mobile-isolated/results.json. The combined failure remains recorded; a successful isolated run does not erase concurrent-context startup limitations.

Preview persistence passed hub/map/playback/return, Back/Forward and hard reload, then a fresh direct Aftermovie URL hit “Critical scene preparation exceeded45seconds.” The saved phase log shows boot→error45.918seconds with roughly0.56–0.86second software frames; local cave downloads are already deferred. The separate default direct-stage gate passed once with only about134ms boot→arrival margin. This is a **flaky cold-start gate**, not a solved performance issue, and no new deadline or default-quality override was adopted.

The repeated stage/playback/return and critical-stage-failure assertions that were blocked by that cold-start error are run separately in raw/repeat-stage-and-fallback.json: **PASS**. That continuation requests existing tier3 under cover after runtime start and explicitly does not certify default-quality cold start. The original combined failures remain in the browser-suite table. Full journey and automatic LOD recordings passed independently.

## Matched loading and rendering diagnostics

**Chromium 154 SwiftShader software rendering only. Physical integrated-GPU laptop and phone acceptance: PENDING.** Fixed measurement settings: 1366×900, actual DPR 0.5, quality tier 3, sequential 8-second settled windows. Review stills separately use DPR 1 / tier 0 at 1366×900 or 390×844; mobile aspect is not a physical phone test. Cold/warm localhost transfer includes actual navigation/resource sizes and covered preparation logs. Estimated decoded image footprint counts unique images with RGBA8/mips; it is not driver-reported VRAM.

| Mode | Cache | Ready ms | Transfer bytes | Local cave bytes | Unique images | Estimated decoded |
| --- | --- | --- | --- | --- | --- | --- |
| approved-c9 | cold | 17641 | 23385597 | 0 | 31 | 119.39 MiB |
| approved-c9 | warm | 16892 | 3000 | 0 | 31 | 119.39 MiB |
| natural-cave | cold | 23526 | 26230072 | 2844475 | 24 | 116.05 MiB |
| natural-cave | warm | 20614 | 3600 | 600 | 24 | 116.05 MiB |

| Mode | View | FPS diagnostic | p50 / p95 / p99 ms | Draw calls | Visible triangles |
| --- | --- | --- | --- | --- | --- |
| approved-c9 | entrance | 1.97 | 487.50 / 625.10 / 625.10 | 184 | 154888 |
| approved-c9 | mid-passage | 1.86 | 473.40 / 818.40 / 818.40 | 179 | 166593 |
| approved-c9 | hub | 3.10 | 304.00 / 351.50 / 394.20 | 167 | 190993 |
| approved-c9 | aerial-map | 2.27 | 417.20 / 494.80 / 494.80 | 186 | 154794 |
| approved-c9 | original-stage | 1.23 | 805.30 / 879.00 / 879.00 | 134 | 1040175 |
| natural-cave | entrance | 1.58 | 617.80 / 669.10 / 669.10 | 179 | 174632 |
| natural-cave | mid-passage | 1.93 | 504.80 / 539.50 / 539.50 | 177 | 191829 |
| natural-cave | unfiltered-opening-comparison | 1.94 | 511.30 / 549.10 / 549.10 | 177 | 191829 |
| natural-cave | cave-geometry-hidden-diagnostic | 3.58 | 282.00 / 296.00 / 299.70 | 172 | 160893 |
| natural-cave | neutral-material-cost-diagnostic | 2.27 | 426.60 / 479.90 / 479.90 | 177 | 191829 |
| natural-cave | hub | 3.06 | 306.80 / 404.70 / 421.10 | 167 | 187661 |
| natural-cave | aerial-map | 2.16 | 454.80 / 510.50 / 510.50 | 181 | 159838 |
| natural-cave | original-stage | 1.24 | 804.40 / 809.60 / 809.60 | 134 | 1040190 |

All detailed image/material/texture-wrapper counts, renderer stats, frame samples, preparation phases and responses are retained in raw/matched-cave-performance.json. Geometry-hidden and texture-neutral views are labelled cost-isolation diagnostics, never accepted visual alternatives. The old Stage3A report's approximate 31–36% software slowdown is historical context, not claimed as a matched measurement against missing assets.

Measured cold transfer rises23,385,597→26,230,072bytes (+2,844,475bytes,12.16%). Unique scene images fall31→24 and the decoded RGBA8+mips estimate119.39→116.05MiB because the private mode omits the old generic paintings; it adds no source PBR images. Local cave material wrappers reuse existing texture objects. Entrance p50 rises487.5→617.8ms (26.7%); hub p50 is304.0→306.8ms and stage805.3→804.4ms in these particular software windows. The8second windows contain very few rendered frames, so p95/p99 and FPS are coarse diagnostics, not statistically stable device comparisons. **The new entrance is more expensive than the surviving C9-only landing**; no performance win over missing historical Stage3A assets is claimed.

## Actual-browser gallery, PDFs and recordings

Open gallery.html in the report directory after extracting all review archives. It provides full-resolution paired images with pose/FOV/viewport/DPR/tier/light metadata, references separately labelled, diagnostics, the phone PDF, full screenshot PDF and complete technical report PDF. Every final candidate screenshot is checked against the actual downloaded GLB body SHA. Matched comparisons use identical camera/FOV/DPR/tier/global lights; JSON signed-zero canonicalization does not permit pose rounding. Public walking and temporary non-public inspection positions are labelled individually.

review-position-classification.json checks the actual unchanged movement/collision registry. Hub, scaffold, C9 visitor, stage and exit-lookback positions pass its strict1e-6m position test. Tunnel stills are fixed inspection orientations inside the **public entry choreography corridor**, not ordinary controllable hub walking positions. Forecourt/side/rim/foot inspection cameras are labelled separately; the actual landing UI and map are genuine public camera frames. These validated classifications supersede the rough initial public-position annotations retained in raw capture records. The walking recording uses actual permitted input after reaching the hub.

The full-resolution PNGs include landing/UI, diagonal mouth, both geological connections, raised rock, rim and foot; first/deeper/mid/vault/bend/backward/final tunnel views; quarry reveal, look back, C9 visitor view, hub/scaffold, aerial map, original Aftermovie and mobile contexts. Neutral geometry, normal RGB, wireframe, forced LODs and unfiltered local lighting are separate diagnostics. No generated concept or Blender render substitutes for renderer evidence.

videos/visitor-journey.mp4 records Landing → Enter → 42 m tunnel → selected C9 → real keyboard walk → Map → original Aftermovie playing → return to C9. videos/automatic-lod-inspection.mp4 is a separately labelled non-public inspection with automatic screen-space switching. Both derive from real browser WebM without speed changes; their state/LOD assertions are retained.

## Art-quality decision and exact next step

**Do not promote this candidate. Stop for user visual review.** The tunnel has more genuine relief than the surviving smooth tube, the obstructing terrain is corrected locally, oversized entrance letters and visible fixtures are absent, and the C9/3× world journey is preserved. Nevertheless the entrance still reads as a captured cliff with an engineered mouth return, some thin edges/diagonal faces and a smoother connection than the approved thick eroded cave. The source-derived vault retains some regular tube rhythm, the floor is too clean and its contact too crisp, and there is no final exact graffiti. Dark dusk readability and scan repetitions remain visible limitations. Passing tests is not visual acceptance.

The next authorized action is **review this evidence**, not Stage3B or quarry rollout. A later bounded cave-art correction should target the mouth's thick erosion/return and immediate foot using the supplied natural cave references, retaining the route/interfaces and safe resources. Exact original PNGs are needed before recreating the seven authorized artworks. These are recommendations only; no further art phase or public promotion is started.

## Independent checkpoint and restoration

New phase folder: https://drive.google.com/drive/folders/1zDrBmlXW1x8NQzgq022jNqS2JrDFdKej

Final checkpoint subfolder: https://drive.google.com/drive/folders/1y-fLFkJthsB9gMOr5fZNseZXSg_2B24a

Review PDFs/screenshots/video: https://drive.google.com/drive/folders/1XkV6VnEIOAsmxVKxOpm9AbF_U0V_3VOf

The final checkpoint is dependency-explicit on the protected complete accepted quarry-fidelity restore and its exact Phase1/2/3 chain. It includes final code, packed source/master, local GLBs, references, scripts/tests, all required prior user additions, screenshots/videos and failed/final evidence. Real original LFS Blender masters, stage/media and source scan assets are accounted for in the protected dependencies; a Git bundle is not substituted. Credentials/.env, dependencies/build output and redundant caches are excluded, not deleted.

Earlier working ZIPs remain immutable historical snapshots; they are **not the final restore set**. Use checkpoint-index.json, stage3a-file-manifest.json, DEPENDENCIES.json, SHA256SUMS.txt, RESTORE-STAGE3A.md and apply-stage3a.py from the final subfolder. The restore script validates all source/baseline hashes and conflicts before any write, uses atomic replacements, is idempotent and preserves independent user work. A clean independent restoration verifies the entire required current tree and reopens the packed master read-only.

FINAL C-review archives are stored in the03Visual-Review subfolder; A/B/D and restoration metadata are in02Complete-Cave. Both belong to the same dated phase parent, and the index/receipt identifies every required archive and remote parent. Download and extract **all C parts together** for a self-contained gallery; they are independent ZIPs, not binary fragments. The phone, full screenshot and technical PDFs are also uploaded separately for immediate review.

**External verification authority:** the separate final DRIVE-BACKUP-RECEIPT.json and restore-verification.json record actual full download-back SHA-256/name/size/parent checks and independent restore results. This report is sealed before those receipts to avoid self-referential hashes; upload success alone is not an externally verified claim. The latest shared Doc contains the verified completion status and exact final links. All prior protected checkpoints are unchanged. No commit, push, merge, deploy, reset, clean or public-default promotion occurred.
