from pathlib import Path
import json,hashlib
ROOT=Path.cwd();REPORT=ROOT/'reports/recovery-phase3-c9-2026-10-19';RAW=REPORT/'raw'
def read(name):return json.loads((RAW/name).read_text())
manifest=json.loads((ROOT/'public/models/gullyverse/recovered-c9-composition/manifest.json').read_text())
geometry=read('composition-validation.json');preservation=read('preservation.json');assets=read('asset-contract-validation.json');master=read('master-validation.json')
cold=read('cold-stage-diagnostic.json')
cold_rows='\n'.join(f"| {r['mode']} / {'default'if r['initialQualityOverride']is None else 'Q'+str(r['initialQualityOverride'])} | {r['milliseconds']:,} | {r['data']['state']['phase']} |"for r in cold['runs'])
review=json.loads((REPORT/'matched-pose-verification.json').read_text());perf=read('matched-performance.json');browser=read('browser-suite-summary.json');ownership=read('composition-browser-checks.json');journey=read('browser-walkthrough.json');persistence=read('preview-persistence.json');gltf=read('gltf-validation.json')
assert review['status']=='PASS' and geometry['status']=='PASS' and assets['status']=='PASS' and preservation['status']=='PASS'
def fmt(n):return f'{n:,.2f}'if isinstance(n,(float,int))else str(n)
tri='\n'.join(f"| {r['LOD']} | {r['retainedHostTriangles']:,} | {r['sourceTriangles']:,} | {r['joinTriangles']:,} | {r['triangles']:,} |"for r in manifest['LODs'])
frames='\n'.join(f"| {r['mode']} / {r['name']} | {fmt(r['fps'])} | {fmt(r['p50'])} | {fmt(r['p95'])} | {fmt(r['p99'])} | {r['after']['stats']['calls']:,} | {r['after']['stats']['triangles']:,} | {r['after']['stats']['textures']} |"for r in perf['windows'])
loads='\n'.join(f"| {r['mode']} / {r['cache']} | {r['readyMs']:,} | {r['totalTransferBytes']:,} |"for r in perf['loads'])
tests='\n'.join(f"| {r['name']} | {'PASS'if r['exitCode']==0 else'FAIL'} | {r['seconds']:.1f} s |"for r in browser)
inherited='\n'.join(f"| {r['LOD']} | {r['eye']} | {r['pitch']} / {r['yaw']} | {r['candidate'][r['LOD']]['mesh']} | {r['candidate'][r['LOD']]['normalDotRay']:.6f} |"for r in geometry['inheritedInvertedHits'])
max_normal=max(r['maximumProtectedNormalAngleDegrees']for r in geometry['topology']);owner_pass=sum(r['status']=='PASS'for r in ownership['checks'])
originals='\n'.join(f"| `{Path(r['path']).name}` | {r['bytes']:,} | `{r['sha256']}` |"for r in assets['sourceOriginals'])
md=f'''# Gullyverse Recovery Phase 3 — selected C9 native scanned-rock composition

**Decision: recovered selected C9 direction, ready for user visual review as a private candidate.** This restores the native Coastal Cliff 01 composition method with uniform **0.9× geometry** and the approved **C8 3× material**. It is a reconstruction on surviving C5.1, not a byte-identical or pixel-identical restoration of the missing C6.2/C9 files. The user's selection of C9 supersedes the old report's KEEP C8 artistic recommendation. No new artistic approval or quarry-wide rollout is asserted.

The ordinary public/default environment remains C5.1. **Stage 3A has not been started. No commit, push, merge or deployment occurred.** Seven visibility hits on unchanged legacy surfaces remain unresolved; full-scene visibility is explicitly **FAIL_INHERITED**, while the new local candidate gates pass. Physical laptop/phone acceptance remains **PENDING**.

## Review and restore

- [Phone review PDF](../reports/recovery-phase3-c9-2026-10-19/Gullyverse-Recovery-Phase3-C9-Review.pdf)
- [Full screenshot PDF](../reports/recovery-phase3-c9-2026-10-19/Gullyverse-Recovery-Phase3-C9-Full-Screenshots.pdf)
- [Full-resolution offline gallery](../reports/recovery-phase3-c9-2026-10-19/gallery.html)
- [Actual-browser visitor journey](../reports/recovery-phase3-c9-2026-10-19/videos/visitor-journey.mp4)
- [Automatic LOD inspection, non-public camera](../reports/recovery-phase3-c9-2026-10-19/videos/automatic-lod-inspection.mp4)
- [Matched camera/render metadata](../reports/recovery-phase3-c9-2026-10-19/matched-pose-verification.json)
- [New Phase 3 Drive checkpoint](https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A)

External verification is established by the separate `DRIVE-BACKUP-RECEIPT.json` and completion index accompanying the archives, after full download-back SHA-256 checks. Upload success alone is insufficient. The report/archive hashes remain immutable; the later receipt records their verification without a circular self-hash.

## 1. Exact baseline and preservation

Branch `codex/navigation-board`; HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. This began with the recovered, uncommitted Phase 2 working tree, including its existing changes to `ImmersiveShell.tsx` and `QuarryPerimeter.tsx`. It did not start from a clean checkout. Current production-verification build: `{review['build']}`.

The starting snapshot inventories **{preservation['startingFiles']:,} files**. Final preservation checks find **{preservation['byteIdentical']:,} byte-identical**, with only three authorized pre-existing source changes: the shell's gated selector/controls, the quarry consumer's covered-preparation dependency, and the private-selector URL carry helper. No other starting file changed or disappeared. Original C5/C5.1 Blender masters, C5.1 runtime geometry/materials, all Phase 2 textures/master, stage/crowds/video, registry, scaffold/signs, navigation, floor, tunnel, global lights/fog/sky/exposure and unrelated routes remain protected. Exact before/after hashes: `raw/preservation.json`; original state and untracked paths: `raw/starting-state.json` and `raw/starting-hashes.json`.

Protected external baselines remain separate:

- Phase 1: https://drive.google.com/drive/folders/1OdGXZvpfHCdYpWesgya3x_lTupKsB_HI
- Phase 2: https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-

No reset, clean, branch checkout, unrelated overwrite or deletion was used. New authoring caches/automatic `.blend1` files are retained locally but excluded from the checkpoint as reproducible intermediate data; the final editable master and authentic originals are included.

## 2. Historical evidence recovered and inspected

Both authenticated Drive downloads passed the user's hashes **before extraction**, then ZIP CRC/path checks, and were extracted separately under `/workspace/recovery-reference/2026-10-19-historical-c8-c9/` without overwriting project data:

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| C8 Evidence ZIP, Drive `1YJplmjx7cBGrRg-8D4Sz1_bLz5AeVmOu` | 17,964,208 | `e9b67adf3ab5656fdec7599ab56e33218d3202c36feec07cbc051faf812a5815` |
| C9 Evidence ZIP, Drive `12xi4iOo887gOc5yUembJN9r5RE3P0Dim` | 13,437,677 | `24d37c280844e7f5a30fef700f205955255d5323ddb564286dfefd370af664eb` |

The C8 162-page comparison and nine-page technical report were read/inspected, distinguishing approved 3× pages from older 1×/2×/4× and failed physical diagnostics. The original C9 Markdown report, 54-page comparison and 57.72-second browser walkthrough were inspected. The C9 report comes from the recovery core; the C9 ZIP contains its gallery and walkthrough, not a Blender master or runtime source. Verification receipts and original embedded PDF image bytes are retained in this review. Historical PDF compression is labelled; those images are not newly generated substitutes.

The original walkthrough mostly faces the hub/right-side context rather than isolating the selected lower scan. It is useful navigation evidence, not sufficient proof of the scan's close-up quality. The new journey records C9 owner/geometry/material selection as well as its actual visitor appearance.

## 3. Historical C8 versus reconstructed Phase 2

Historical approved C8 used `marble_rock_03` + `rock_face_03`, documented luminance gains 1.3489028164 / 0.8928655525, a 10.790622 m shared atlas, 2K colour / 1K OpenGL normal and ORM, non-metallic stone, AO R=1, normal strength 0.7, and user-approved threefold feature magnification. These specifications agree with the reconstructed Phase 2 family. Its runtime GLB remains exactly SHA-256 `ff330dcfe418436d324535675472b7e10ca34e8f4cb924faf40e7748bea5feee`.

**3× means cached UV0 repeats divided by three**, not three times more repetition. Original repeat is approximately 0.1853461274, approved repeat 0.0617820422. The six marble periods become approximately 5.395311 m each; the shared atlas covers 32.371866 m in that approved artistic presentation. This is intentional texture magnification, not a claim that the native texture scan physically spans that width. Colour, roughness/ORM and source normals remain aligned. UV1 geometric normals retain repeat [1,1].

Material differences remain: the original finite mixing-mask code and exact original atlas pixels did not survive; Phase 2 reconstructs the documented inclined weathering/source-height preference. Tile phase, local warmth and weathering placement are therefore not certified identical. This phase preserves Phase 2 rather than silently rewriting its approved comparison.

Geometry-host differences are substantial and separate: historical C8 used the lost 35.557 m C6.2 study, including its known stretched captured surfaces and bake. Current C8 uses one surviving 21.950486 m C5.1 sector. Its upper wall is smoother, bedding differs and the material boundary has another silhouette. Those differences cannot be repaired by changing 3× sampling, inventing old coordinates or recreating the rejected 4.8×/7× fitting.

## 4. Source selection, licence and actual scale

Selected genuine scanned geometry: [Poly Haven Coastal Cliff 01](https://polyhaven.com/a/coastal_cliff_01), **CC0 1.0 Universal**; photography/processing Rob Tuytel, cleanup Rico Cilliers. Official API metadata, provider MD5, SHA-256 and licence evidence accompany the unchanged 2K Blender download and its linked source maps. No preview thumbnail is used as production geometry or texture. This is composition of an existing scan, not a newly captured photogrammetry scan.

Measured native Blender dimensions: **91.979954 × 10.966709 × 10.325531 m** (X/Y/Z); source LOD0 has **461,824 triangles**. The API dimensions are millimetres; actual mesh bounds are measured independently. The source is an open captured surface, not an assumed watertight solid.

| Authentic original | Bytes | SHA-256 |
| --- | ---: | --- |
{originals}

Only one formation near source X≈−30 m is used. Reconstructed crop: **10.588781 × 5.141219 × 8.727990 m**, 51,337 high-detail triangles. Historical report: approximately 10.390 × 4.992 × 8.419 m. Four mildly oblique trim planes and the exact source transform are recorded in `composition-contract.json`. Their original historical values were lost; this crop is deliberately not claimed identical.

All transform singular values equal **0.9**. No horizontal widening, depth flattening, source-normalized fitting, random cliff displacement, C7 folded loft, Boolean solid union or decorative boulder ring is used. The original scan file remains byte-identical. Sub-millimetre cut-boundary slivers and a 9.16 mm capture hole are repaired in the authored copy; original downloads are retained. Interior LOD needles are welded into exact cut landmarks, not accepted as invalid tangent corners.

Reconstructed native formation bounds, world Y-up: X **−47.419728…−40.475482**, Y **0.384085…8.239275**, Z **−70.798254…−60.474297 m**. Compare historical bounds X −47.987…−40.899, Y 0.55…8.627, Z −70.363…−60.809. These are documented reconstruction differences, not a proportional stretch.

## 5. Composition and protected interfaces

The original report's lower `Wall_14` belonged to the missing C6.2 partition. In the surviving C5.1 export, arc327 m lies in **Wall_15**, arc315.076709…337.027196. Blindly replacing current Wall_14 would put the scan in the wrong place. The implementation reads the actual current GLB and uses the real Wall_15 interfaces.

Only covered interior host triangles are removed. A minimum-cost oriented 3D annulus connects the native cut boundary to the actual local hole. A pinched coarse-LOD crop fan is repaired locally; no rectangular collar or complete-world replacement is introduced. Outer rim/side/foot landmarks remain exact. Host parts around and above the local scan remain the surviving geometry. The local formation occupies approximately 9.53 m along the study orientation; the transferred part also includes retained host geometry.

Protected host coordinates are supplied in `assets-source/gullyverse/quarry-scanned-composition/protected-host-boundaries.json`, in world metres/Y-up. There are 393 / 341 / 319 original external vertices per LOD. Exported maximum positional error is **0 m** at all three levels, against the unchanged **2e−5 m** gate. Maximum protected normal angle is **{max_normal:.6f}°** after preserving original glTF corner normals rather than recomputing Blender vertex averages.

The visual surface stays outside the protected quarry polygon at relevant wall heights: zero clearance violations at every LOD. Collision/navigation ownership is unchanged. Native cut boundaries are protected across reductions, and the entire part has one intentional outer interface loop, zero new internal holes and zero non-manifold interior edges. This does not claim a closed solid or an exhaustive self-intersection proof.

## 6. Blender, UVs, baking and runtime assets

Editable master: `assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend` (**{master['bytes']:,} bytes**, SHA-256 `{master['masterSHA256']}`). It retains the original licensed meshes, native high crop, retained host/high-bake surfaces, optimized LODs, packed C8 maps and geometry-normal atlas. Read-only reopen succeeds with all required file images packed and no missing linked image. It is not an offline beauty render substituted for website evidence.

Reproduction, after restoring Phase 1+2 dependencies:

```sh
python3 scripts/blender/recover_c9_source.py
blender -b -t 2 --python-exit-code 1 --python scripts/blender/author_recovered_c9.py
blender -b -t 2 --python-exit-code 1 --python scripts/blender/bake_recovered_c9.py
```

The shipped source/runtime assets permit restoration without re-downloading the scan or re-running Blender. The commands reproduce the method, not cross-version byte-identical decimation/baking. Blender 4.3.2 was used. Authoring caches are regenerated by the pipeline and are not required checkpoint payloads.

| LOD | Retained host | Native runtime | Join | Total region triangles |
| --- | ---: | ---: | ---: | ---: |
{tri}

UV0 follows the surviving metre-scale chart and physical source projections. Ten whole approved atlas periods are subtracted horizontally to reduce float cancellation without changing phase, scale or orientation. Side-face projections and explicit hard fracture corners repair local frame failures. Blender→glTF V-origin conversion is performed once. Source albedo remains sRGB; normal/ORM remain linear/non-colour. New geometry does not require COLOR_0 because its borrowed C8 material uses vertexColors=false; the public C5.1 vertex-colour contract is untouched.

Middle/far geometry receives fresh UV1 charts and **one shared 1024² geometry-only high-to-low normal atlas**. Fine C8 normal detail is not baked twice. The missing C6.2 bake's old pixels are not fabricated or claimed recovered. Near tangents use UV0; middle/far tangents use UV1, verified before geometry-only packing and after actual GLB import. Float32 round-trip testing identified two additional fracture corners; their physical normals were split before baking, with positions/UV0 unchanged. All final UV/tangent regeneration checks pass, with zero bad corners at all LODs.

| Runtime file | Bytes | SHA-256 |
| --- | ---: | --- |
| composition-region.glb | {manifest['runtimeBytes']:,} | `{manifest['runtimeSHA256']}` |
| composition-bake.glb | {manifest['normalBake']['bytes']:,} | `{manifest['normalBake']['sha256']}` |

Combined local payload: **{manifest['runtimeBytes']+manifest['normalBake']['bytes']:,} bytes**; historical C9 was 3,781,532 bytes. The geometry GLB contains no PBR images; the tiny bake holder owns only one normal image and is never rendered. No new albedo/ORM family, 4K set, loader dependency, global triplanar shader, displacement shader or dynamic light is introduced.

## 7. Runtime integration and reversibility

Private selector: `/?arrival=hub&diagnostics&quarryReview=scanned-composition`, under the existing development gate or `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`. The gate is review configuration, not authentication. Existing C8 selector `scanned-material-multi` and C5.1 `foundation-refined` remain available. Lost C6.2/C7 runtime assets have not been invented; their historical evidence remains preserved.

`ScannedCompositionSession` reuses the foundation/C8 owners and owns only the local geometry and normal proxy. Rendered clones borrow those resources. Only the three Wall_15 visual geometries change; other cloned BufferGeometry references remain the original owner's references. C8/C9 comparison uses a covered swap, not another complete quarry download. The existing screen-space thresholds/hysteresis and frustum culling remain authoritative.

Normal UV1 stays fixed while colour/roughness UV0 remain 3×. C9 starts and stays at 3× even if another scale is present in a URL. The selector survives map travel, stage/playback, return, history and direct reload. Persistent Canvas operation, original stage cache, covered texture/shader preparation, failure fallback, retry and context recovery remain in the existing architecture.

Geometry/bake failures retain an explicitly labelled C8 fallback; rejected/unpublished payloads are disposed. Shared albedo/ORM images are never disposed by a borrowed C9 material. Inactive retirement and complete unmount separately free the three local geometries, the bake holder and its one image. The original stage is not evicted.

## 8. Actual-browser gallery and historical comparison

**{review['images']} final full-resolution browser PNGs / {review['matchedViewpoints']} matched poses per mode**, build `{review['build']}`, Chromium154 software renderer. Desktop1366×900 and portrait390×844, effective DPR1/Q0, FOV58 for visitor inspections; aerial camera uses its original adaptive framing. Matching audit verifies actual camera, FOV, viewport, DPR, quality and light arrays across all three modes, not merely requested settings.

Views include all three validated public positions, medium/close/along-wall inspections, both source joins and sector edges, upper rim, foot, behind-stall context, hub/scaffold, tunnel exit, aerial and portrait. Temporary neutral material and geometry-only images are separately labelled. Wireframe/forced-LOD diagnostics are separate from the visitor gallery. No image generation, offline Blender beauty render, colour grading or relighting is used as acceptance evidence. PDFs use compressed embedded screenshots for phone size; original PNGs remain in the gallery.

Historical C8 approved pages record rounded poses, enabling the public1/close/tunnel/behind-stall orientations to be closely aligned. The C9 PDF lacks full original raw camera metadata; its comparisons are **reference-aligned, not certified pixel-identical**. Historical PDF image bytes are extracted without colour edits and identified by page and source package. Current C51/C8/C9 comparisons are precisely matched to each other.

The native lower formation is visible from the first public viewpoint. Public positions2/3 remain substantially stall-occluded; they do not independently demonstrate unoccluded visitor-distance quality. Close/medium cameras are clearly non-public. The apparent body is genuinely three-dimensional with fine maps disabled, but its coastal scalloped recesses and annulus facets are still visible limitations, not proof of finished quarry art.

## 9. Photographic reference assessment

Inspected project references: `design/references/03-open-roof-quarry/quarry-open-sky-geometry.jpeg` and `quarry-warm-dappled-light.jpeg`. Broad charcoal/grey-brown masses, selective lighter fresh faces, muted weathering, related vertical/diagonal joints and thick broken beds guide the comparison. Warm highlights and dark joints partly arise from illumination/occlusion; arbitrary material percentages or painted shadow stripes are not justified. No reference pixels are runtime maps.

The recovered C9 provides real protrusions, recesses and broken thickness at native proportions. Differences remain: the source has coastal erosion pockets rather than the references' predominantly angular excavated beds; adjacent C5.1 remains comparatively smooth; bedding/texture orientation changes at joins; the native scan is local rather than a composed tall quarry cliff; the ground has far less geological dressing; and approved dusk gives less directional relief than the reference lighting. Global lighting has not been changed to manufacture similarity.

Compared with historical C9, the smoother C5.1 upper host and reconstructed crop/annulus are the principal geometric differences. Compared with reconstructed C8, C9 adds meaningful physical relief without depending on extra diffuse detail. The existing material-treatment edge and some manufactured-looking neighbouring legacy fractures remain. This is an honest restoration candidate, not a claim of photorealism or final production approval.

## 10. Geometry and visibility verification

Actual GLB import validates finite UVs, authored and regenerated tangent frames, normals, zero-area faces, geometric topology and protected borders. Source dimensions/MD5/SHA, uniform singular values and material channels pass. Khronos validation reports zero errors/warnings for C8 holder and both new C9 GLBs. The current 10,920-ray survey checks seven documented visitor positions, thirteen pitches and120 azimuths across all LODs against actual surviving C5.1. There are **zero new inverted scan hits, zero added horizontal gaps and zero new cross-LOD skyline disagreements**. No threshold is loosened.

Full-scene status remains **FAIL_INHERITED**, with these seven unchanged-surface hits (one is an original coincident wall/terrain BVH tie, independently verified against that exact baseline surface):

| LOD | Eye | Pitch / yaw degrees | Unchanged mesh | Normal·ray |
| --- | --- | --- | --- | ---: |
{inherited}

The historical C9 report recorded nine expanded upper/terrain defects on its lost C6.2 host. Those original defects are not represented as solved: the restored host and documented survey differ, and the original raw expanded ray set is not supplied by the historical ZIP. Candidate pass and whole-scene failure are reported separately. Sampling is not exhaustive visibility/self-intersection proof.

## 11. Build, navigation, playback and lifecycle results

TypeScript, lint under the established warning policy, production build and **88 immersive unit tests pass**. Existing unrelated lint warnings remain; no major dependency upgrade or lockfile change was made. Build verification uses clearly non-secret local backend placeholders; it does not certify remote forms/payments/backend connectivity. Their source remains unchanged.

| Browser cohort | Result | Duration |
| --- | --- | ---: |
{tests}

Composition-specific ownership/recovery: **{owner_pass}/{len(ownership['checks'])} groups pass**. Raw assertions include exact non-target geometry sharing, 3×/UV1 separation, shader links, repeated covered comparisons, actual WebGL context loss/recovery, inactive retirement/reload, full unmount, local geometry/bake failure and retry, malformed payload rejection, delayed loading, interrupted-load disposal and ordinary public-default isolation. Resource plateaus are sampled checks, not a long-session leak-free VRAM guarantee.

Preview persistence records **{len(persistence['states'])} states**, including map, original movie playback, repeated hub/stage journeys, browser history, hard reload, direct stage URL and critical original-stage native video fallback. The full browser journey records {len(journey['states'])} selected-C9 states. Separate directional tests use real keys and public menu controls. Desktop/portrait tests are emulation, not a physical phone measurement.

Early authoring/tangent failures, the normal-preservation correction, initial export survey and browser harness trials are retained under `raw/trials/`; they are not silently relabelled as successful final evidence. Final assertions apply to the recorded final build and assets.

An initial default-tier persistence run reached ten successful states, then its90-second harness wait expired on the direct-stage URL. It did not retain the live application error, so a specific underlying failure cause is **unconfirmed**. The original failed cohort remains in `raw/trials/initial-preview-persistence.json`. No application, timeout or default quality setting was changed. An isolated stage comparison and a complete same-default persistence rerun then passed, including three additional stage/playback/hub cycles. This does not prove the intermittent cold-load risk resolved.

| Isolated cold-stage mode / initial quality | Ready ms | Result |
| --- | ---: | --- |
{cold_rows}

These software tests use1366×900/DPR0.25; default loads are close to the45-second production preparation deadline. The Q3 row is a separately labelled diagnostic, not a production default change. Retain that margin concern for real-device testing rather than extending the timeout or attributing it conclusively to C9.


## 12. Performance, transfer and memory

Matched current-build diagnostics use1366×900, DPR0.5/Q3, eight-second settled windows, an explicitly cleared cold HTTP cache and same-context warm revisit. API/analytics are blocked through CDP rather than Playwright routing disabling the measured cache. The profile runs alone after authoring/capture/regression jobs. Software frame counts are small; p99 is coarse, no confidence interval or internet-latency simulation is claimed. The public C5.1 retains its original preparation path; C8/C9 use the already established private scoped warm-render path, so load differences cannot all be attributed to the scan.

| Mode / view | Software FPS | p50 ms | p95 ms | p99 ms | Calls | Visible triangles | Textures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{frames}

| Mode / cache | Ready ms | Total measured localhost transfer bytes |
| --- | ---: | ---: |
{loads}

The final wall consumer image set is **10 unique images, approximately85.33MiB RGBA8+mips**: retained C5.1 approximately48MiB, C8 approximately32MiB and one C9 geometric normal approximately5.33MiB. Wrapper counts differ from unique source images; no duplicate complete PBR family is added by C9. This is estimated decoded image payload, not measured GPU memory. Raw profile includes texture/geometry allocations, transfer resources, nested shader/texture preparation timings, frame samples and LOD choices.

The 3.42MB local GLBs include retained host geometry and should not be multiplied blindly per future10m patch. A naive ten-copy extension would add about34.24MB GLB files and53.33MiB of normal images on top of the retained families, before other assets; that is not an approved production plan. Future regions should share the material owner, partition genuinely local geometry, pack compatible geometric bakes and deliberately retire obsolete material consumers. No streaming rewrite or additional rollout is implemented here.

## 13. Physical-device acceptance — pending

No physical laptop GPU/phone is attached; Chromium uses ANGLE SwiftShader. These measurements are **not hardware FPS**, mobile GPU certification or a60FPS guarantee. Native background-tab scheduling, thermal behaviour, real VRAM and long playback remain pending.

Reproduce on an actual device using the restored project and existing lockfile. Build with the private preview gate, run the local server, enable browser hardware acceleration, record OS/browser/GPU from the renderer diagnostics and `chrome://gpu`, viewport/actual DPR and selected tier. Compare public C5.1, C8 and C9 under identical poses/settings. Collect cold/warm loads, p50/p95/p99, hub walking, map open/close, original playback/return and repeated allocations. Use headed local browser tooling or remote debugging on a real phone; do not substitute portrait emulation for a physical result. `GULLYVERSE_HEADED=1` and `CHROME_PATH` are supported by the evidence helpers.

## 14. Checkpoint and next step

The new Phase3 checkpoint is incremental on the protected Phase1 **and Phase2** payloads. It contains all Phase3 changed/new source, original licensed Blender/maps, final packed master, runtime GLBs/normal source, manifests/interfaces, authoring/test scripts, technical report, full-resolution review, PDFs, recordings, restoration README and SHA-256 manifests. Required baseline hashes and exact prior checkpoint identities are supplied. A Git bundle alone is not treated as sufficient; the earlier protected Phase1 archive supplies the actual original LFS/stage/media payloads.

Restore into a new directory using Phase1 then Phase2 instructions, extract every Phase3 archive into a separate overlay, and run `apply-phase3.py --base /path/to/restored-phase2/project`. It preflights the whole overlay and baseline, rejects unrelated edits/symlinks, writes atomic replacements and verifies every restored file. The checkpoint is separately extracted and tested for hashes, idempotency, conflicting-user-work rejection and Blender-master readability before upload. Download-back verification and archive SHA-256 are in the accompanying Drive receipt/index. Credentials, live.env files, dependencies, build output, caches and redundant archives are excluded.

**Stop here for visual approval of the reconstructed C9 candidate.** Keep the private C8 comparison and ordinary C5.1 unchanged. The next authorized phase must explicitly connect any recovered entrance/tunnel to this selected C9 owner; no Stage3A assets have been reconstructed in Phase3. Wider quarry production, joining refinement and unrelated inherited visibility repairs remain separate decisions. This phase does not restore the rejected C7 method, promote failed C8 Boolean geometry or reverse the user's C9 choice.
'''
(ROOT/'docs/gullyverse-recovery-phase3-c9-composition.md').write_text(md)
print('WROTE_PHASE3_REPORT',len(md))
