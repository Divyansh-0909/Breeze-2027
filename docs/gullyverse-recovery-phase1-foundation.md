# Gullyverse recovery Phase 1 — original masters and C5.1 checkpoint

18 October 2026. **Original source recovery and baseline verification are complete.** The three requested Blender masters are authentic recovered Git LFS objects, not regenerated files. The surviving C5.1 website is preserved. C8, C9 and Stage 3A have not been reconstructed. No commit, push, merge, deployment, branch checkout, reset or clean was performed.

The independently restorable checkpoint is ready to download. **Off-cloud backup remains PENDING USER DOWNLOAD.** No external storage upload was made; files remaining under `/workspace` are not an independent backup.

## 1. Actual starting state and preservation

- Repository: `/workspace/Breeze-2027-navigation`; origin `https://github.com/Divyansh-0909/Breeze-2027.git`.
- Branch: `codex/navigation-board`.
- HEAD: `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`, “Show Stage 2C.5.1 quarry refinement by default on WIP.”
- Starting index/worktree: clean, 3,278 tracked files, no untracked user source to recover. The approved Phase 0 assessment and file/hash/LFS inventories were read before restoration.
- Final preservation check: **3,266 files remain byte-identical; 12 original `.blend` pointers are expanded to their exact recorded LFS payloads; zero unexpected tracked content changes.** Git considers the expanded payloads unchanged. The new Phase 1 report is an untracked authorized deliverable; generated dependency/build files are ignored.
- No application, registry, runtime GLB, material, lighting, navigation, original stage, crowd or video source was edited. Both dependency lockfiles remain unchanged. The report and verification/checkpoint scripts are this phase's new work.

Protected registry SHA-256: `9a8adfdbfc52f3336a05e0745a776e2e96e46d14ada3f998329b091283ebef7d`. Quarry registry span remains 97.8×123.5 m. Stage origin remains [-12,0,-134.3]; scaffold [0,0,-70]; hub spawn [0,1.72,-51]. The original 42 m bent tunnel, 2 m walking half-width and 0.38 m player radius remain unchanged. Current global Hub/Aftermovie lighting, fog, sky, cameras and destination coordinates are preserved by full-file hashes.

Evidence: `raw/starting-state.json`, `starting-file-hashes.json`, `final-preservation.json`.

## 2. Authentic LFS recovery

| Original master | Actual bytes | Verified SHA-256 |
|---|---:|---|
| `assets-source/gullyverse/quarry-foundation/quarry-foundation.blend` | 38,322,354 | `caca8007c303392e7fa2c9779ef7ed064b9e07294d65820880a70272fe4b09de` |
| `assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend` | 37,706,010 | `eff2e7ad48dde1403e1b0923dbec8d6c8fc6426885abf8721196d7aabeff954e` |
| `assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend` | 10,114,024 | `f97be25be57f7ae2c63036afa87be5186dcf0cd642f7831b736c54dfb81a5617` |

Selective `git lfs fetch --include=<three exact paths> --exclude='' origin <HEAD>` retrieved 86,142,388 bytes. Objects were size/hash-verified in the LFS cache **before** `git lfs checkout <the three files>` expanded the pointers. This was LFS payload materialization, not a Git branch checkout. `git lfs install --local --skip-smudge` configured only local filters/hooks. No LFS object was uploaded.

For the complete retained editable source catalogue, a second exact-path fetch recovered nine additional original `.blend` objects, 516,784,254 bytes. All **12 retained LFS Blender masters total 602,926,642 bytes**, with exact original OIDs and sizes. Historical review ZIPs were not bulk-fetched. Earlier limestone sources remain historical comparison assets; recovering their files does not activate them.

Evidence: `raw/lfs-fetch.log`, `lfs-cache-verification.json`, `lfs-recovered-objects.json`, `checkpoint-additional-lfs-selection.json`, `checkpoint-additional-lfs-verified.json`.

## 3. Blender access and supporting resources

Blender 4.3.2 opened all three requested originals using `--background --factory-startup --disable-autoexec`, `use_scripts=False`. Their headers are `BLENDER-v403`. The pilot contains 5 mesh objects and 4 packed images; C5 and C5.1 each contain 107 mesh objects and 6 packed images. All required images are packed; no missing external image or linked-library dependency was found. Finite vertex data and UV-layer presence were inspected. SHA-256 before and after opening is identical. **No master was saved or exported.**

The nine additional historical masters were also opened without saving. Legacy missing-link findings: **0 masters**. Details, including original image paths and packed status, are retained in `raw/blender-additional-master-validation.json`; these findings are separate from the three required masters' clean results.

The checkpoint retains original source textures, licensed-source provenance and authoring scripts in archive B. After extraction into a new directory, the three required masters are opened again from their restored location to verify portable packed-resource access; the external checkpoint verification record accompanies the archive set.

## 4. C5.1 runtime and material integrity

All six exported files match their manifest sizes and SHA-256 values. `blockout.layout.json` matches `worldRegistrySHA256`. The combined geometry contains 105 expected named mesh nodes, 35 parts per LOD, and the required `POSITION`, `NORMAL`, `TANGENT`, `TEXCOORD_0` and `COLOR_0` attributes.

| Runtime | Bytes | SHA-256 |
|---|---:|---|
| `foundation-geometry.glb` |8,530,404|`134cbf9609e77df09cea1feb28b9e52f3c880c3320ba79f63ecb84ecbe53586f`|
| `foundation-materials.glb` |4,659,808|`56345a4165738d991ff302fab9b6ecf811e6f397ce5636ccb0651cce4c6fca87`|

The six original embedded material images remain shared: one 2048² albedo and five 1024² images. Estimated RGBA residency with mipmaps is 48 MiB; this is a source-payload estimate, not measured driver VRAM. Geometry embeds no duplicate PBR images. Original dark-rock/dry-terrain materials, map channels and source-derived appearance are unchanged. This is the C5.1 `rock_face_04`/`rocky_terrain` family, **not** C8's later approved 3× material.

Khronos glTF Validator 2.0.0-dev.3.10 reports zero errors and zero warnings for all six C5.1 GLBs and the retained C5 shared holder. The tool was installed in an isolated verification directory, without changing project dependencies.

Original stage/crowd/video files remain unchanged, including `aftermovie-stage.glb`, `Man.glb`, `Animated-Woman.glb` and the 52,291,090-byte `after-movie.mp4`. Their full hashes are in the checkpoint per-file manifest and preservation evidence.

## 5. Geometry and clearance verification

The retained Blender validation script was copied with **only its output directory changed**. Original thresholds and modelling code were not changed.

- LOD triangles:178,635 /52,033 /25,152. Zero zero-area triangles, zero short normals, finite exported positions and UVs at all levels.
- 18 shared wall borders checked against original expected landmarks at every LOD; maximum error **0.0000078335 m**, below the unchanged 2e−5 m threshold.
- 3,000 horizontal/upward rays from five established visitor locations, each cast against all three actual exported LODs: zero unexpected horizontal gaps, zero inverted visible hits, zero cross-LOD hit/miss differences.
- Original wall-clearance survey: zero wall samples intruding into the preserved playable boundary.
- Detailed fracture-sector boundary test: `PASS`. Each sampled C5/C5.1 sector has one intended outer boundary loop, no additional fracture-hole loops, zero non-manifold interior edges and zero boundary-degree errors after welding only the validation copy at 10 µm.

These are bounded surveys, not a proof of all self-intersections or every pixel/pose. Buried wall feet, outer terrain borders and the original tunnel attachment intentionally have open boundaries. Original passage occlusion is retained. No tolerances were loosened.

## 6. Installation, type checking, lint and build

`npm ci --no-audit --no-fund` used the existing `package-lock.json` as directed by the project README. No dependency upgrades or lockfile edits were made. Node 24.19.0, Next 15.3.8 and Prisma 5.22.0 were used.

| Check | Fresh result |
|---|---|
| TypeScript | PASS after standard Next-generated image declarations existed |
| Lint | PASS; existing 21 warnings retained, warning policy unchanged |
| Immersive unit tests |79 PASS, 0 failed/skipped |
| Production build | PASS with isolated non-secret local verification environment |

The first standalone typecheck, before a Next run generated ignored `next-env.d.ts`, reported three unresolved static image/SVG declarations. Next generated its normal image declarations; the subsequent standalone typecheck passed without application changes. The generated helper is included for cold restoration.

The first build compiled successfully but failed prerendering `/admin/breeze-admin/contact` because no Supabase URL/key was configured. A second build used `NEXT_PUBLIC_SUPABASE_URL=https://recovery-verification.invalid` and a clearly non-secret placeholder anon key, and passed. No `.env` file or credential was written. Private inspection flags were enabled only for local verification; ordinary C5.1 selection stayed unchanged. Backend/admin/payment/contact service integration is not certified by placeholders.

Logs retain both initial failures and successful follow-ups. Existing lint warnings and stale Browserslist data were not hidden or “fixed” through unrelated changes.

## 7. Actual-browser functional and lifecycle results

Chromium 151 used the actual R3F/WebGL renderer, with SwiftShader software rendering. Functional harnesses use 1366×900 or 390×844 and requested DPR0.25; stills and profiling record their own conditions. API writes were blocked during functional checks. Tests ran serially.

| Existing suite | Result | Duration |
|---|---|---:|
| `public-stabilization` | PASS | 401.34s |
| `candidate-regressions` | PASS | 360.39s |
| `directional-travel` | PASS | 64.49s |
| `lifecycle` | PASS | 47.20s |
| `video-cycles` | PASS | 195.80s |
| `navigation-cycles` | PASS | 246.87s |
| `recovery-foundation` | FAIL — see recorded explanation | 81.17s |

The public and explicit C5.1 comparison suites each passed all 8 groups: fresh landing-to-hub entry, authored 7.2s choreography, persistent Canvas, keyboard/editable focus/lost-key handling, blur/freeze, map open/close/resize, stage video and rapid replay, boundary destination menu, return travel, Back/Forward, navbar/reload/direct URL and mobile touch/reduced motion. Directional held-key fast travel, 10 material-owner enable/disable cycles, explicit retirement/reload and fallback unmount were also exercised. Playback and navigation cycles retain their measured allocations and assertions in the corresponding JSON evidence.

The historical recovery harness produced these individual results:

| Recovery case | Result |
|---|---|
| Actual WebGL loss/recovery preserves foundation pose and persistent Canvas | PASS |
| Failed foundation-geometry.glb retains connected dark baseline; explicit retry | PASS |
| Failed foundation-materials.glb retains connected dark baseline; explicit retry | PASS |
| Delayed load stays covered; fallback unmount disposes unpublished resources | PASS |
| Duplicate embedded texture payload is rejected and owned resources disposed | PASS |
| Critical original stage failure reaches native video fallback | PASS |
| Ordinary public URL never requests foundation assets or exposes review controls | FAIL |

**The last harness assertion is obsolete, not concealed.** It expects ordinary public URLs never to request foundation assets. HEAD14f 36 intentionally promotes C5.1 to the public default, so the unchanged baseline correctly requests its foundation files. The original harness failure and exit code remain in evidence. Application code was not changed to satisfy it.

A separately labelled current-default control loaded `/?arrival=hub` **without diagnostics or review selectors**:35 C5.1 parts active, both refined geometry/material URLs requested, one Canvas, no review controls, no inspection overlay and no diagnostics object. Result: **PASS**. The six actual loss/failure/retry cases and current public selection are reported separately from the old expectation.

Evidence: `raw/browser-suite-summary.json`, `public-stabilization/results.json`, `candidate-regressions/results.json`, `directional-travel.json`, `lifecycle.json`, `video-with-wall.json`, `navigation-cycles.json`, `recovery.json`, `current-public-default-control.json` and their full logs.

## 8. Fresh screenshot gallery

Gallery: `/workspace/recovery-phase1/2026-10-18/gallery.html`. Phone PDF: `Gullyverse-Recovery-Phase1-Review.pdf`. Archive D restores these under `phase1-review/`; raw per-frame metadata is in archive A under `recovery/phase1/raw/baseline-captures.json`.

**17 actual-browser captures**, covering the requested landing, original tunnel, exit reveal, hub/scaffold, left/right walls, stage-facing inspection, aerial map, original Aftermovie and representative mobile views. The baseline's old physical entrance lettering and generic graffiti are intentionally preserved in this phase; the future cave-art task is separate.

| View | Full-resolution file | Actual quality / renderer DPR |
|---|---|---|
| Landing entrance (desktop) | `screenshots/desktop-01-landing.png` | Q0 / 1 |
| Existing tunnel (desktop) | `screenshots/desktop-02-tunnel.png` | Q0 / 1 |
| Quarry reveal (desktop) | `screenshots/desktop-03-quarry-reveal.png` | Q0 / 1 |
| Hub and scaffold (desktop) | `screenshots/desktop-04-hub-scaffold.png` | Q0 / 1 |
| Left quarry wall — stall context (desktop) | `screenshots/desktop-05-left-wall.png` | Q0 / 1 |
| Right quarry wall — stall context (desktop) | `screenshots/desktop-06-right-wall.png` | Q0 / 1 |
| Stage-facing composition (desktop) | `screenshots/desktop-07-stage-facing.png` | Q0 / 1 |
| Navigation scaffold (desktop) | `screenshots/desktop-08-scaffold-front.png` | Q0 / 1 |
| Aerial map (desktop) | `screenshots/desktop-09-aerial-map.png` | Q0 / 1 |
| Left wall — clear public view (desktop) | `screenshots/desktop-11-left-wall-clear.png` | Q0 / 1 |
| Right wall — clear public view (desktop) | `screenshots/desktop-12-right-wall-clear.png` | Q0 / 1 |
| Original Aftermovie stage (desktop) | `screenshots/desktop-10-aftermovie-stage.png` | Q3 / 0.6 |
| Landing entrance (mobile) | `screenshots/mobile-01-landing.png` | Q0 / 1 |
| Existing tunnel (mobile) | `screenshots/mobile-02-tunnel.png` | Q0 / 1 |
| Hub and scaffold (mobile) | `screenshots/mobile-04-hub-scaffold.png` | Q0 / 1 |
| Aerial map (mobile) | `screenshots/mobile-09-aerial-map.png` | Q0 / 1 |
| Original Aftermovie stage (mobile) | `screenshots/mobile-10-aftermovie-stage.png` | Q3 / 0.6 |

The first screenshot collection stopped after 9 frames because its unguarded diagnostics read occurred during a brief scene-handoff teardown. The original failed attempt and log remain in `raw/baseline-captures-first-attempt.json` and `post-browser-verification.json`. Only the new collector wait was guarded; completed captures were retained and the remaining views were completed successfully. A subsequent cold direct-stage still at DPR1 exceeded the 90-second readiness wait while the original highest-tier crowd warmed under coverage. Probe snapshots showed covered boot, completed texture/shader setup and no JavaScript error. Stage stills then selected the existing Q3 crowd tier before preparation, with original assets and lighting unchanged; this limits software work and is recorded per image. The original adaptive cap can lower the effective renderer DPR to 0.6; image metadata reports the real canvas resolution rather than claiming a native DPR1 render. Both earlier attempt results and probe evidence remain available. No application change or test suppression was used.

Desktop 1366×900, mobile 390×844, requested DPR1: Q0 for rock/context views and existing Q3 for the two stage stills. Each record contains actual camera XYZ/yaw/pitch/quaternion/FOV/near/far, viewport, effective canvas resolution/DPR, current quality, scene, lighting inventory, selected LOD nodes, draw calls, allocations and requested resource URLs. Controlled route cameras and poses outside ordinary local walking bounds are explicitly labelled. The public map is opened through its real UI, not replaced by an offline view. Controlled stills use the existing development inspection camera and hide its debug label; normal local controls are suppressed by that existing inspection state. Scene art and lighting are unchanged. Landing and map views retain their actual interface.

## 9. Loading and software-renderer baseline

Matched localhost diagnostics used 1366×900, requested DPR0.5, Q3 and 8-second windows, without another browser, Blender or compression workload running. Cache is explicitly enabled; CDP blocks API/analytics. Loading includes the actual application/runtime request set, not only GLB bytes.

| Cache | Ready ms | Total transferred bytes | C5.1 encoded resource bytes |
|---|---:|---:|---:|
| cold | 14,395 | 11,203,178 | 10,253,740 |
| warm | 12,100 | 2,100 | 10,253,740 |

| View | Software FPS | Frame p 50/p 95/p 99 ms | Draw calls | Visible triangles |
|---|---:|---|---:|---:|
| hub | 3.89 | 256.20 / 278.20 / 355.80 | 166 | 123,846 |
| aerial-map | 2.72 | 364.40 / 434.90 / 472.40 | 188 | 121,638 |
| aftermovie-stage | 1.36 | 726.10 / 787.20 / 787.20 | 134 | 1,040,175 |

Full preparation timing, geometry/texture allocation estimates, resource responses and warm-cache flags are in `raw/current-baseline-loading-performance.json`. These are SwiftShader/local-host diagnostics, **not physical GPU FPS or Internet-loading guarantees**. Physical integrated-GPU and phone acceptance remain pending.

## 10. Inherited limitations and changes deliberately deferred

- The current source is the recovered committed C5.1 foundation, not the lost later workspace. C8's 3× atlas, selected C9 native-scale composition and Stage 3A authored cave still require their separately authorized recovery phases.
- The fresh landing image visibly retains a faceted front facade and angular terrain/rock overlap at the cave mouth. This is a pre-existing C5.1 visual defect, not a new recovery change. The quarry ray survey does not cover every landing/tunnel-mouth view; passing it does not certify this overlap as resolved. A future separately scoped cave-mouth correction is still needed.
- The original tunnel/entrance art and C5.1 geology have known artistic limitations. This phase does not add cave fixtures, remove branding, replace graffiti, repair the later C9 mouth obstruction or alter quarry art. Historical C9 visibility defects cannot be declared solved or reproduced here because C9 is absent.
- The geometry survey is sampled; it is not exhaustive topology/visibility acceptance for future replacements. No geometry tolerance or collision rule was relaxed.
- The old recovery harness public-isolation assertion is recorded as failed; its premise predates the approved default change. Current default behavior is independently verified.
- Cold direct-stage preparation at DPR1/highest initial crowd tier exceeded the 90-second screenshot wait on SwiftShader; probes remained covered, without JavaScript errors. Lower-DPR functional tests passed; stage stills used existing Q3 with requested DPR1 and the actual adaptive renderer DPR recorded. This software readiness/performance limit is not declared fixed, and high-DPR hardware acceptance remains pending.
- Real backend credentials/services and physical-device performance are outside this isolated verification result. No production deployment was tested or changed.
- Historical C8/C9/Stage 3A reports and current partial recovery evidence are retained; missing native later art is not invented. The separate companion visual packages and original exact graffiti artwork remain missing inputs for later visual recovery.

## 11. Complete source-and-asset checkpoint

Version prefix: `Gullyverse-Recovery-Phase1-2026-10-18`.

| Archive suffix | Contents | Required role |
|---|---|---|
| `A-source.zip` | Current tracked code/config/lockfiles/docs/tests/scripts; new report; generated image declarations; technical results; recovery reference reports; restore README, provenance and per-file hash manifest | Required |
| `B-blender-source-art-*.zip` | All 12 expanded original LFS Blender masters, retained trial masters, local source geometry/maps/licenses and authoring inputs | Required for complete editable source |
| `C-runtime-assets-*.zip` | All retained public/runtime assets and imported `Assets/`, including original stage/crowd/Aftermovie/media | Required |
| `D-review-evidence-*.zip` | Retained non-trace historical visual evidence/trials plus current full-resolution gallery and PDF | Retain for complete historical file set; optional to run website |

All parts of A+B+C restore the website and editable art independently of GitHub or LFS. All parts of A+B+C+D restore the complete included tracked-file set and current additions. Exact file counts/bytes are in `checkpoint-index.json`; every included project file has its actual SHA-256 and size in `project-file-manifest.json` and `FILE-SHA256SUMS.txt`. The external `ALL-FILES-SHA256SUMS.txt` additionally covers every archive member, including metadata and new review evidence. Archive SHA-256 values are in the accompanying `SHA256SUMS.txt` and index. No required Blender payload is a pointer.

The 17 explicit tracked exclusions are 13 redundant root review ZIPs, three old browser-trace ZIPs and one Windows `desktop.ini`. This includes the 14 unneeded LFS review ZIP pointers, whose original metadata remains recorded rather than masquerading as recovered archives. No required source/model/material/media file is excluded. Private live `.env` contents, credentials, `.git`, `node_modules`, `.next`, temporary caches and redundant backup archives are not packaged. A high-confidence credential-pattern screen of tracked text found no literal credential/private-key matches; it is not a universal secret-detection guarantee.

This is an independently restorable file snapshot with branch/HEAD/ref provenance. It does not duplicate the 1.42GB Git-history bundle. That bundle alone is not enough to restore LFS art; the full real source/runtime files are supplied here.

Each numbered part is a separate ZIP, not a spanned archive; extract every part into the same new parent folder. Parts are capped at 384 MiB uncompressed to keep every download below 512 MB. The archive set is extracted into a **new separate restore directory** and every expected project file is rehashed, with original masters reopened from that restored location. Fresh archive integrity/hash checks and `checkpoint-restoration-verification.json` accompany the set. The report intentionally points to the external archive-hash manifest instead of embedding self-referential archive hashes inside an archive containing this report.

## 12. Download and external preservation

1. Download A+B+C+D, the index, checksum files and `RESTORE-README.md` from the supplied artifact links. Save them to Files → iCloud Drive or a computer folder outside Codex.
2. Verify downloads using `shasum -a256 -c SHA256SUMS.txt` or PowerShell `Get-FileHash -Algorithm SHA256`, comparing every archive. The README contains exact commands and archive names.
3. Extract into one **new empty folder**. Run `python3 recovery/verify-restoration.py`; for an intentional A+B+C-only restore, use `--core-only`.
4. Keep originals unchanged. Supply private backend environment configuration separately. Install with the existing npm lockfile, then follow the included build/test/start instructions. Nothing automatically commits, uploads or deploys.

**External-backup status: PENDING.** Downloadable artifacts are prepared and locally verified; no claim is made that you have saved them externally. No automatic upload to iCloud/Drive/other storage was performed.

## 13. Readiness for Phase 2

**C5.1 technical foundation is ready for the next bounded recovery phase, after the downloadable checkpoint is secured.** The original editable masters, retained runtime, navigation, map, stage playback and resource-recovery foundations are verified within the limits above.

The next implementation target remains the approved C8 scanned multi-material at 3×, privately and reversibly, preserving this C5.1 public default. Its later source assets/compatibility host must be recovered or reconstructed transparently; do not repeat rejected C7 art, invalid C8 Boolean geometry or stretched-source modelling. **Phase 2 has not begun.** This phase stops with the report, gallery, real source/assets and recoverable checkpoint.
