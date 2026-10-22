"""Write the final report from measured evidence, without inventing passes."""
from pathlib import Path
import hashlib
import json

ROOT = Path.cwd()
OUT = ROOT / "reports/recovery-phase2-c8-material-2026-10-19"
RAW = OUT / "raw"


def read(name):
    return json.loads((RAW / name).read_text())


def link(name, title=None):
    return f"[{title or name}](../reports/{OUT.name}/{name})"


perf = read("matched-performance.json")
preservation = read("preservation.json")
material = read("material-validation.json")
geometry = read("excavation-geometry-validation.json")
review = read("review-package.json")
provenance = json.loads((ROOT / "assets-source/gullyverse/recovered-c8-material/source-provenance.json").read_text())
spec = json.loads((ROOT / "assets-source/gullyverse/recovered-c8-material/material-manifest.json").read_text())
runtime = json.loads((ROOT / "public/models/gullyverse/recovered-c8-material/manifest.json").read_text())
public = read("public-stabilization/results.json")
private = read("private-regressions/results.json")
ownership = read("material-browser-checks.json")
persistence = read("preview-persistence.json")
directional = read("directional-travel.json")
cold = read("cold-stage-diagnostic.json")
groups = [("Public navigation/input/playback", public.get("checks", [])),
          ("Private C8 navigation/input/playback", private.get("checks", [])),
          ("Held-key directional travel/boundary return", directional.get("checks", [])),
          ("C8 resource/failure/context checks", ownership.get("checks", []))]
tests = "\n".join(f"|{label}|{sum(row['status']=='PASS' for row in rows)}/{len(rows)} PASS|" for label, rows in groups)
performance_rows = []
for row in perf["windows"]:
    stats = row["after"]["stats"]
    performance_rows.append(f"|{row['mode']} / {row['name']}|{row['fps']:.2f}|{row['p50']:.1f}|{row['p95']:.1f}|{row['p99']:.1f}|{stats['calls']}|{stats['triangles']:,}|{stats['textures']} / {stats['geometries']}|")
load_rows = "\n".join(f"|{row['mode']} / {row['cache']}|{row['readyMs']/1000:.2f}s|{row['totalTransferBytes']:,}|{row['c8EncodedBytes']:,}|" for row in perf["loads"])
cold_rows = "\n".join(f"|{row['mode']} / {'default initial quality' if row['initialQualityOverride'] is None else 'explicit diagnostic Q3'}|{row['milliseconds']/1000:.2f}s|{row['data']['state']['phase']}|{row['data']['state'].get('error') or 'none'}|" for row in cold["runs"])
sources = "\n".join(f"|`{row['id']}`|{' × '.join(f'{v:.6f}' for v in row['scanCoverageMetres'])}m|{', '.join(row['authors'])}|CC0 1.0|" for row in provenance["assets"])
max_border = max(row["maximumSharedBorderErrorM"] for row in geometry["seams"])
build = perf["build"]
report = f"""# Gullyverse — Recovery Phase 2: C8 scanned material at approved 3×

The documented C8 two-source PBR family has been reconstructed as a **private material-only preview on the original C5.1 geometry**. Default sampling is 3×: one-third the original repeat, with colour/normal/ORM aligned. The public C5.1 material, geometry, floor, movement, stage and lighting remain unchanged.

**Historical screenshot matching remains PENDING.** The original C8 report is available, but the companion C8 Evidence ZIP/162-page screenshot PDF was not accessible in the attachments, recovered files or connected Drive. A link was requested during implementation. The lost C6.2 host and original mask script are not recoverable from the available reports. This is an explicitly documented reconstruction, not a byte-identical or pixel-identical restore. No missing historical image is substituted with a new capture.

## Review and preview

- {link('Gullyverse-Recovery-Phase2-C8-Review.pdf', 'Phone-friendly review PDF')} — {review['pdfPages']} pages.
- {link('gallery.html', 'Offline full-resolution screenshot gallery')} — {review['originalBrowserPNGs']} actual-browser PNGs, including {review['matchedPairs']} matched C5.1/C8 pairs.
- [Separate Phase 2 Drive folder](https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-).
- Private URL: `/?arrival=hub&diagnostics&quarryReview=scanned-material-multi`. Uses the existing development or `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` gate. Explicit `rockTextureScale=1`, `2`, `3`, `4` remain controls; missing/invalid values choose 3. No new public destination or authentication mechanism is claimed.

## 1. Exact baseline and preservation

Branch `codex/navigation-board`, HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. Starting status contained only the three untracked Phase 1 report/backup-policy files. The separate starting inventory records 3,281 files and 2,382,351,618 bytes, including the hydrated original LFS masters. **{preservation['byteIdentical']:,} existing files are byte-identical; only ImmersiveShell.tsx and QuarryPerimeter.tsx have authorized application edits; unexpected changes: {len(preservation['unexpectedChanges'])}.** New sources, maps, master, tests and evidence are separate paths.

The C5.1 foundation geometry SHA-256 remains `{runtime['hostGeometrySHA256']}`. `QuarryFoundationSession.ts`, original Blender masters, both existing geometry/material manifests, registry, original stage/crowds/media, scaffold/signs/stalls/destinations, tunnel route, map/cameras, sky/fog/exposure and global lights remain unchanged. No surviving asset was regenerated. No C6.2 stretching, C7 geometry, failed C8 solid-join geometry, C9 or cave reconstruction was introduced. No commit, push, merge or deployment occurred.

Evidence: {link('raw/preservation.json')}, {link('raw/starting-state.json')}, {link('raw/starting-file-hashes.json')}.

## 2. Historical settings and authentic source materials

The {link('historical/Stage2C8_scanned_material_approved_3x.md', 'preserved original C8 report')} identifies Marble Rock 03 and Rock Face 03, a 10.790622m shared atlas, six Marble periods and approximately four Rock Face periods, 2K colour/1K normal/1K ORM, near normal strength 0.7, source roughness, AO=1 and a non-metallic response. It documents linear albedo gains 1.3489028164 / 0.8928655525. These settings were used rather than substituting procedural mineral noise or a new pale family. Historical recommendations about rejected physical C8 geometry do not override the user's later selection of C9 for the following recovery phase.

|Source|Official scan coverage|Provider authors|Rights|
|---|---|---|---|
{sources}

Provider dimensions are millimetres, converted by /1000. This is texture coverage, not a 3D cliff mesh dimension or a certified displacement depth. Eight authentic 2K provider maps (diffuse JPEG, OpenGL normal PNG, roughness PNG and height PNG for both sources) total **78,528,698 bytes**. Every original was verified against provider MD5/size and recorded SHA-256. Height is authoring information for masks, not applied as cliff displacement. Source AO is not multiplied over already dark joint colour. No thumbnails, restricted reference pixels, 4K/8K runtime sets or additional source families are used.

Sources and license: `assets-source/gullyverse/recovered-c8-material/licensed-source/`, `source-provenance.json`; https://polyhaven.com/a/marble_rock_03, https://polyhaven.com/a/rock_face_03, https://polyhaven.com/license and CC0 legal code. Original quarry references remain review-only.

## 3. Material authoring and the locked 3× interpretation

The two scanned colours are converted from sRGB to linear, receive the historical gains, and blend in linear space. Compatible scanned normals blend as vectors and are renormalized. Roughness blends in linear data space. Runtime colour is sRGB; OpenGL normals and ORM are non-colour. ORM is R=1, G=source roughness, B=0; observed roughness range {spec['roughnessRange'][0]:.3f}–{spec['roughnessRange'][1]:.3f}. No emissive contribution, extra baked AO multiplication or global light/exposure gain is introduced.

The missing original mask formula is reconstructed explicitly as interrupted inclined weathered bands with source-height preference. It is deterministic and documented in the script, not random polygon colours. Coefficients are authoring choices, not photograph-derived mineral percentages. This is a known difference from the lost atlas. The photographs guide broad dark/grey-brown surfaces, selective weathering and exposed faces; their warm highlights/shadows are not painted wholesale into albedo.

Surviving C5.1 UV0 spans one repeat per 2m. Authored atlas repeat is `2 / 10.790622 = 0.1853461274`; approved repeat is `2 / 10.790622 / 3 = 0.06178204247`. Actual glTF float32 gives 0.06178204218546549. Both axes and every UV0 surface map use the same transform. Atlas coverage becomes 32.371866m; the Marble source period becomes approximately 5.395311m. Thus features grow threefold; repeat count is not tripled.

This is the user's approved artistic magnification, not a claim that the source scans were physically captured at three times their native coverage. It does not stretch or generate any rock mesh.

Original repeats are cached per texture, so 3→4→1→3 returns exactly without accumulating scale. Texture image identities remain fixed. UV1 channels are excluded from this sampler. **C5.1 has no geometry-derived UV1 normal bake; the lost C6.2 bake was not fabricated, moved to UV0 or silently replaced.** Baseline UVs/tangents remain unchanged. The C8 material keeps its historical vertexColours=false contract locally; C5.1 COLOR_0 and public material behavior are intact.

Reproduce maps: `python3 scripts/blender/recover_c8_scanned_material.py`. Export/master: `blender -b -t 2 --python scripts/blender/export_recovered_c8_material.py`. Editable packed master: `assets-source/gullyverse/recovered-c8-material/recovered-c8-material.blend`. Blender 4.3.2 reads it without saving; all three images are packed, metre units and three original inspection LODs are retained, no linked resources are missing.

Pinned independent authoring/review packages are in {link('scripts/requirements-authoring.txt')}; they are not added to the application's dependencies or lockfile.

## 4. Missing C6.2 host and minimum compatibility layer

Runtime reuses the exact original `quarry-foundation-refined/foundation-geometry.glb`; **no new quarry or local wall geometry GLB is created**. Only the three existing `Foundation_Wall_15_LOD0/1/2` material slots on a borrowed clone use the new family. The original owner and neighbouring materials are untouched.

Wall_15 is the smallest suitable existing whole-mesh host selected here: {runtime['selectedArcMetres']:.6f}m in perimeter arc, bounds X −51.325…−37.822, Y −0.8…35.295, Z −76.302…−54.360. Using one existing sector avoids cutting/re-exporting the protected geometry or adding a per-fragment region shader. This differs from the old 35.557m C6.2 study and its lower/upper partitions. Its source fitting is not recreated. The material-only master imports a read-only inspection copy; the website never loads that round trip.

The C5.1 smooth/folded forms and bright legacy fracture facets remain visible. The new material's outer boundaries are conspicuous against the surrounding smoother material; this phase does not claim C8.1 continuity or natural C9 geometry. Fine scan grain is softer at extreme close range because the documented atlas shares 2K/1K resolution across several periods. Ordinary views and close views are labelled separately. These are material-recovery limitations, not concealed geology repairs.

## 5. Runtime ownership and navigation

`ScannedRockMaterialSession` extends the unchanged foundation owner. A separate hidden GLB owns only one material and three images; its single holder triangle is never attached/rendered. C5.1 geometry is fetched once. Shared borrowed materials are not disposed by scene clones. Explicit retirement/unmount and abandoned-load paths close owned ImageBitmaps once. The sampler keeps no global asset cache.

Independent foundation/material loading is started concurrently; the existing cover remains until both owners are ready. The parent's finite connected-shell/original-baseline fallback chain is drained without swallowing re-entrant load requests. No preparation timeout, quality default, collision envelope or stage asset was changed. `borrowScannedMaterial()` provides the scene-owned family for subsequent C9 geometry, subject to the same leases.

Private C8 covered warm-up draws are limited to the existing quarry clone and the originally active lights, so its four preparation frames do not also redraw the original stage/crowd. An unused render layer is borrowed synchronously and all object, light and camera masks are restored in `finally`, including interrupted renders. No second renderer, Canvas, scene or framebuffer is created. The public C5.1 preparation path remains unchanged. Unit checks cover isolation, restoration after success/failure and the safe full-scene fallback if all layers are already occupied.

The private selection is retained through entry, map, stage travel/return, history and direct reload. Ordinary URLs keep the C5.1 default and make no request for the recovered C8 GLB. The existing persistent Canvas, stage/video ownership, input and fallback architecture remain in use.

## 6. Actual-browser visual evidence

The {review['matchedPairs']} pairs use identical recorded camera pose/FOV, Q0, requested/effective DPR1 and viewports 1366×900 / 390×844. They include all three validated public positions, close and medium inspection, along-wall, both boundaries, upper rim, foot contact, hub/scaffold, original tunnel exit, map and mobile portrait. The three public positions remain inside the same walking envelope; existing stall occlusion is retained. Close/medium/along-wall cameras outside that envelope are explicitly non-public inspections.

Neutral images use browser-only replacement lights with the same geometry, maps, exposure and fog, and restore original lights afterwards. No neutral setup enters application code. Final-build 1×/3×/4×/return-to-3× controls and automatic LOD inspections are separately labelled. No generated image or Blender beauty render substitutes for these PNGs.

Before frames came from the recovered Phase 1 server. The main C8 set used build `q6OdIg668A5Hh6WezvYZT`; subsequent loading-only corrections preserve the same map/geometry bytes. Final controls and current technical/performance cohorts record build `{build}`. Older cohorts are retained with their original results rather than relabelled as current.

The unchanged public stabilization script's eight-group pass belongs to the earlier `YD65XUFAwZ6ZfHNpj_o8x` cohort. The later changes affect private owner loading/preparation. Final-build ordinary-URL checks and controls independently confirm that C5.1 is selected and no C8 GLB is requested. The final private regression, ownership and persistence cohorts are separate from that earlier public run.

Evidence: {link('raw/matched-pose-verification.json')}, {link('raw/final-visual-controls.json')}, {link('raw/c51-captures.json')}, {link('raw/c8-3x-captures.json')}.

## 7. Validation and regression results

|Check|Result|
|---|---|
|TypeScript / production build|PASS; no application dependency or lockfile upgrade|
|Lint|PASS under unchanged warning policy; 21 warnings, no suppression added|
|Immersive unit tests|86 PASS|
|Material GLB validator|0 errors, 0 warnings|
|Provider maps / source dimensions|8 originals verified; official mm→m scale recorded|
|Blender source|Readable, packed images, no missing links; originals unchanged|
|Geometry/tangents/UVs|Existing geometry hash and frames preserved|
|Strict cross-LOD borders|18 joins; maximum {max_border:.9g}m, threshold remains 2e−5m|
|Visibility and clearance|3,000 rays, 0 unexpected gaps, 0 inverted hits, 0 cross-LOD hit differences, 0 clearance violations|
{tests}
|Private selection/history/playback persistence|{persistence['status']}; complete state trace and critical stage fallback retained|

The first serial-loading private cohort recorded one failed cold direct-stage entry; the other seven groups passed. Concurrent owner loading alone still recorded the same one-group failure. Both cohorts are preserved. Focused C5.1/C8 cold-stage controls and independent persistence checks are separate evidence. The final private preparation change removes redundant covered stage/crowd renders from quarry warm-up; final cohort outcomes above are not substituted for the earlier failures. No approved global timeout, geometry threshold or stage quality default was relaxed to force a pass.

Cold direct-stage diagnostics on SwiftShader:

|Mode|Ready time|Final phase|Error|
|---|---:|---|---|
{cold_rows}

The inherited original stage/crowd can approach the 45-second preparation deadline on this software renderer. A successful isolated run is not a guarantee against host contention or hardware/device differences. Explicit Q3 is diagnostic, not a silently adopted production setting. Public baseline tests and original assets remain intact.

Technical evidence: {link('raw/browser-suite-summary.json')}, {link('raw/material-browser-checks.json')}, {link('raw/preview-persistence.json')}, {link('raw/gltf-validation.json')}, {link('raw/material-validation.json')}, {link('raw/excavation-geometry-validation.json')}.

## 8. Texture, loading and rendering cost

The new runtime GLB is **{runtime['runtimeBytes']:,} bytes**; three embedded images, five active texture wrappers around three unique image sources, approximately **32 MiB RGBA8+mips** additional to the retained 48 MiB C5.1 wall family, approximately **80 MiB combined estimated image residency**. This is an image-format estimate, not measured VRAM. All other C5.1 walls still need their original family; it is not evicted from under them. Future regions should reuse this owner rather than allocate independent full families.

The historical atlas's three runtime map files totalled 4,483,782 bytes; this reconstruction's maps total {sum(row['bytes'] for row in spec['textures'] if row['runtime']):,}. Equal documented resolutions do not imply equal compression or identical masks. No 4K atlas, new loader/decoder dependency, triplanar shader or runtime displacement was added. The local material owner adds no visible triangle/draw-call geometry. C5.1 LOD totals remain 178,635 / 52,033 / 25,152 triangles.

Matched localhost loads, HTTP cache enabled and explicitly cleared for each cold run:

|Mode/cache|Covered ready|Total transferred bytes|C8 encoded body bytes|
|---|---:|---:|---:|
{load_rows}

The server compresses the 5,412,804-byte GLB to a measured 5,326,871-byte encoded response body. Warm resource entries retain that cached body-size metadata; the warm total-transfer column records only the actual new request/response overhead, not a second material download.

Single settled eight-second windows, 1366×900, actual DPR0.5, Q3; no concurrent authoring, compression or other browser job:

|Mode/view|FPS|p50 ms|p95 ms|p99 ms|Calls|Visible triangles|Textures/geometries|
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(performance_rows)}

Renderer/browser: {perf['browser']}, actual ANGLE/SwiftShader from the retained context snapshots. These are software diagnostics with sparse/coarse p99, no confidence intervals, no Internet loading model and no physical GPU certification. Physical laptop/mobile acceptance is **PENDING**. {link('raw/matched-performance.json')} records raw windows, allocations, covered preparation, cold/warm resources and automatic near/mid/far LOD selection.

## 9. Independent Phase 2 checkpoint and restoration

The Phase 1 backup folder remains protected and is not modified: https://drive.google.com/drive/folders/1OdGXZvpfHCdYpWesgya3x_lTupKsB_HI . New sibling folder: https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj- (`2026-10-19-Recovery-Phase2-C8`, the requested date label; raw execution clocks are UTC).

The incremental checkpoint contains changed/new application source, authoring and validation scripts, authentic CC0 originals, packed Blender master, final maps/runtime GLB/manifests, tests, report, gallery/PDF/PNG evidence, exact Phase 1 dependency metadata, restoration instructions and per-file/archive SHA-256. It excludes credentials, private env contents, node_modules, .next, caches and redundant whole-world assets.

Archives are grouped below the connector's confirmed 100 MiB limit. Restore the verified Phase 1 checkpoint first. Extract every Phase 2 archive into a separate overlay directory, verify its SHA-256, then run the supplied `apply-phase2.py` against the restored Phase 1 project. It preflights all inputs and destination hashes before atomic replacements, and refuses to overwrite unrelated changes. A separate extraction/restoration verification is supplied.

**External verification is established by the later Drive backup receipt/index, not by this report alone.** Each uploaded file must be fetched back and fully SHA-256 hashed, with parent/name/size verified. The final receipt in the Phase 2 folder records that result and exact archive inventory. This report's packaging precedes its own external upload; no off-cloud certification is inferred from a local ZIP or a successful request alone.

## 10. Readiness and stop state

**Material resource ready for visual review and subsequent reuse; historical C8 pixel matching remains unverified.** The 3× sampling, authentic scanned grain, matte response, safe ownership and unchanged C5.1 host are implemented. The original mask and C6.2 physical form are unavailable, boundaries remain conspicuous, and C5.1's smooth/folded geology is not repaired by this material layer. No photorealistic/final-production claim is made.

For physical-device review, run the documented build with the private preview gate, open baseline and C8 URLs at matched viewport/DPR/quality, record actual OS/browser/GPU, cold/warm entry, valid walking views, map, playback/return and repeated travel; retain p50/p95/p99 and allocation snapshots. Compare on an actual integrated-GPU laptop and physical phone rather than extrapolating SwiftShader.

Next authorized decision is user visual review, including the missing approved C8 screenshot pack if supplied. Only after that approval should Recovery Phase 3 restore the selected C9 native-scale composition while borrowing this family, respecting current UV units/owner leases and protected interfaces. **C9 geometry, Stage 3A cave work and public promotion have not begun.** No commit, push, merge or deployment.
"""
(ROOT / "docs/gullyverse-recovery-phase2-c8-material.md").write_text(report)
print("Wrote docs/gullyverse-recovery-phase2-c8-material.md", len(report.encode()), "bytes")
