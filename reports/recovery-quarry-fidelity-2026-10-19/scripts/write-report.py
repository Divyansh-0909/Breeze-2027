"""Generate the technical record from frozen asset and browser evidence."""
from pathlib import Path
import json, hashlib, csv

ROOT = Path.cwd()
R = ROOT / 'reports/recovery-quarry-fidelity-2026-10-19'
raw = R / 'raw'
load = lambda name: json.loads((raw / name).read_text())
asset = json.loads((ROOT / 'public/models/gullyverse/quarry-fidelity-correction/manifest.json').read_text())
perf = load('matched-performance.json')
master = load('editable-master-validation.json')
preserve = load('final-preservation.json')
source = load('source-contribution-audit.json')
geometry = load('fidelity-geometry-validation.json')
stage = load('cold-stage-diagnostic.json')

def table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |'] +
                     ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows])

authority = list(csv.DictReader((R / 'stage-fidelity-matrix.csv').open()))
authority_table = table(['Stage / historical page', 'Authority', 'Survival and comparison limit'], [
    ['C5.1 / C6 p1 BEFORE', 'Approved public foundation', 'Original masters and runtime survive; public assets unchanged'],
    ['C6 / C6 p1 AFTER', 'Private experiment', 'Images/reports only; nearest current host is explicitly non-equivalent'],
    ['C6.1 / p1 third panel', 'Engineering foundation, not final art', '35.557 m extent documented; old expanded geometry not restored'],
    ['C6.2 / p2 fourth panel', 'Preferred earlier character; failed final-art gate', 'Historical visual reference; severe source stretching not reproduced'],
    ['C7 / rejected p2', 'Rejected', 'Historical failure reference only'],
    ['C8 / approved 3x PDF pp6–12', 'User-approved material and scale', 'Recovered maps preserved; original C6.2 host/mask not identical'],
    ['C8.1 / p2 second panel', 'Optional continuity study', 'Reference only; not silently promoted as a product stage'],
    ['C9 / original 54-page PDF, D panels', 'User-selected rock appearance', 'Authoritative target; B panels show C8, not C9']])
lod_table = table(['LOD', 'Total runtime triangles', 'Composed front triangles', 'Original 0.9x hero triangles', 'Protected outer vertices'], [
    [r['LOD'], r['triangles'], r['composedSurfaceTriangles'], r['heroTriangles'], r['protectedBoundaryVertices']] for r in asset['LODs']])
frame_table = table(['Mode / view', 'Frames', 'FPS', 'p50 ms', 'p95 ms', 'p99 ms', 'Calls', 'Visible triangles'], [
    [r['mode'] + ' / ' + r['name'], r['count'], f"{r['fps']:.2f}", f"{r['p50']:.1f}", f"{r['p95']:.1f}", f"{r['p99']:.1f}", r['after']['stats']['calls'], r['after']['stats']['triangles']] for r in perf['windows']])
loads_table = table(['Mode / cache', 'Navigation-to-ready ms', 'HTTP transfer bytes'], [
    [r['mode'] + ' / ' + r['cache'], r['readyMs'], r['totalTransferBytes']] for r in perf['loads']])
cold_table = table(['Direct stage / initial quality', 'Navigation-to-ready ms', 'Boot-to-local ms', '45s minus observed boot interval', 'Result'], [
    [r['mode'] + ' / ' + ('default' if r['initialQualityOverride'] is None else 'Q' + str(r['initialQualityOverride'])), r['milliseconds'],
     round(r['preparationWallMs'], 1) if r['preparationWallMs'] is not None else 'not local',
     round(r['conservativeDeadlineMarginMs'], 1) if r['conservativeDeadlineMarginMs'] is not None else 'unavailable', r['data'].get('state', {}).get('phase')] for r in stage['runs']])
counts_table = table(['Mode', 'Renderer textures', 'Geometries', 'Linked programs', 'Scene texture estimate MiB'], [
    [r['mode'], r['data']['stats']['textures'], r['data']['stats']['geometries'], r['data']['contexts'][0]['stats']['Program']['active'],
     f"{r['data']['memory']['activeTextureBytesEstimate']/1048576:.2f}"] for r in perf['loads'] if r['cache'] == 'cold'])
source_table = table(['Authoring crop', 'Native cropped dimensions m', 'Uniform scale', 'Sparse front correspondence samples'], [
    [s['name'], ' x '.join(f'{v:.3f}' for v in s['cropDimensionsM']), s['uniformScale'], source['nearestNativeCropWithin024m'][s['name']]] for s in asset['sourceModels']])
validation_table = table(['Check', 'Result / scope'], [
    ['Blender master open/read', 'PASS; all four file images packed; original hero positions verified'],
    ['glTF validation', 'PASS; zero errors and zero warnings for the three tested holders'],
    ['Topology / normals / UV / tangent corners', 'PASS; no non-manifold interior edges, zero-area faces, invalid normals or bad tangent corners'],
    ['Protected borders', 'PASS; zero positional drift at unchanged 2e-5 m tolerance; normal dot >= 0.999999821'],
    ['Sightline survey', 'No new failures in 32,760 casts per scene, plus 1,875 targeted LOD-specific casts'],
    ['Whole-scene visibility', 'FAIL_INHERITED; seven known component defects remain, not repaired'],
    ['Walking clearance', 'PASS; zero candidate vertices inside protected quarry floor polygon; registry unchanged'],
    ['TypeScript / lint / production build', 'PASS; lint retains inherited warnings; invalid local backend placeholders are not a backend certification'],
    ['Immersive unit tests', 'PASS; 90 tests'],
    ['Public browser stabilization', 'PASS; all eight original groups on final build'],
    ['Private desktop regression', 'Seven groups PASS; combined fresh mobile landing timed out at 90s'],
    ['Isolated same touch/reduced-motion assertions', 'PASS; no application or timeout changes; combined failure retained'],
    ['Directional travel / map / playback / history', 'PASS; actual controls, same persistent Canvas'],
    ['Composition ownership / fallback / retry', 'PASS; 11 groups, including actual WebGL loss/recovery'],
    ['Repeated preview/navigation', 'PASS for sampled cycles; not a long-session leak-free VRAM guarantee'],
    ['Physical laptop / phone', 'PENDING; no physical device available']])

text = f'''# Gullyverse recovery — pre-C9 and C9 quarry fidelity correction

20 October 2026 UTC. Private comparison candidate; visual approval PENDING. This is the merged fidelity correction requested in the shared handoff, not a duplicate Recovery Phase 3 and not Stage 3A.

## Decision and practical result

The material treatment now covers the documented **35.557 m** study extent rather than only the recovered **21.950 m** sector. It uses the unchanged approved C8 scanned maps at **threefold apparent feature size**. A separate physical candidate preserves every original native **0.9x Coastal Cliff 01 hero triangle** and adds correctly scaled source-derived middle/upper relief. Public C5.1, original recovered C8/C9 and all protected checkpoints remain available.

**Fidelity is only partially recovered. Do not treat this as final art acceptance or a pixel-identical restoration.** In the final browser images the brown-grey surface coverage is closer to original C9 than the narrow rejected recovery, but abrupt outer material changes, smooth protected boundary strips, fluted coastal pockets, and triangular/faceted connecting surfaces remain visible. The neutral geometry-only view makes the weak joins particularly clear. The candidate is more expensive at middle/far distances and is not ready for quarry-wide replication. The strongest defensible improvement is corrected material scope; the geological composition still requires the user's comparison against the original D panels.

Recommendation: **READY FOR USER COMPARISON, FIDELITY NOT YET ESTABLISHED; NO ROLLOUT.** Review the material-only and physical candidates separately. Keep C9 as the selected artistic reference; do not replace it with C7 or call the missing C6.2 geometry restored. Stop for acceptance of both pre-C9 material fidelity and C9 fidelity. Stage 3A remains on hold.

## Exact starting baseline and preservation

Repository: `/workspace/Breeze-2027-navigation`; branch `codex/navigation-board`; HEAD `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`. The starting tree already included uncommitted recovered Phase 2/3 work. The read-only inventory contains **3,761 files / 2,849,797,618 bytes**, SHA-256 `dac0e3c8f3105c9f592102b94cfbb834027ea764cea5ba4659f8f048d5b22a0e`.

The final preservation check finds **3,758 unchanged files**, no missing files, and only these three authorized existing-file integration edits: `ImmersiveShell.tsx`, `QuarryPerimeter.tsx`, `scannedRockSampling.ts`. New classes, tests, scripts, sources, runtime assets and evidence are additive. All original LFS Blender masters, C5.1 runtime geometry/material, C8 holder and old recovered C9 assets retain their starting hashes. `raw/final-preservation.json` records the evidence. No reset, clean, branch switch, commit, push, merge, deployment or public promotion occurred.

The quarry layout, ground, original stage/crowd/video, scaffold and signs, stalls, destination coordinates, collision registry, map, navigation choreography, global sky/fog/exposure/lights and persistent Canvas are unchanged. The stage and old tunnel shown in this package are preserved context, not reconstructed Stage 3A artwork.

## Historical authority and drift inventory

{authority_table}

The 13-row `stage-fidelity-matrix.csv` identifies exact source PDF/page/panel, approval classification, recovered/corrected file, drift, correction and non-equivalence. C6/C6.1/C6.2 do not have surviving standalone runtimes in this checkout. Their genuine historical images are compared to the nearest surviving host with that limitation explicit. Original project photography is geological reference; it is not labelled a screenshot of an implemented stage.

Authenticated historical downloads were hash-verified before separate extraction:

- Pre-C9 review archive: Drive `1M7Np5ywCzOvIdMgCn95MQVij7O4I3TS8`, 5,855,286 bytes, SHA-256 `e7edb115190a2fa1050541b1c7cc064871d69e7e116e352364d0aedb4451e2bb`.
- Original visual pack: Drive `1rkl9Np7SatwA24sKjnFavO2nTAAJQJAL`, 17,442,826 bytes, SHA-256 `a82e6336490858d1d68f387f298e0060c68a0d6c9f07a97b033183d4b0a91274`.
- Original approved C8 package: Drive `1YJplmjx7cBGrRg-8D4Sz1_bLz5AeVmOu`, SHA-256 `e9b67adf3ab5656fdec7599ab56e33218d3202c36feec07cbc051faf812a5815`.
- Original selected C9 package: Drive `12xi4iOo887gOc5yUembJN9r5RE3P0Dim`, SHA-256 `24d37c280844e7f5a30fef700f205955255d5323ddb564286dfefd370af664eb`.

The approved C8 162-page comparison, C9 54-page comparison and authentic earlier progression are represented in `references/historical-image-index.json`. C9's **D** panel is the selected geometry; **B** is the material preview. Historical camera metadata is incomplete. Historical views are **reference-aligned**, while the five current modes are exactly matched in actual camera/FOV, canvas size, DPR, quality and light state. No pixel-identical historical claim is made.

## Diagnosed causes of recovery drift

1. The lost lower/upper C6.2 visual partition IDs were mistaken for surviving C5.1 sector IDs. Old C8/C9 used the broad arc **311.02719558677654–346.5843803697403 m**, length **35.55718478296376 m**. The recovery selected only current Wall_15, arc315.07670942703663–337.02719558677654 m, length21.95048615973991 m. Current Wall_14 and Wall_16 cover the missing adjoining portions. This narrowed the brown scanned treatment and exaggerated the isolated insert.
2. The original broad C6.2 physical host and exact blend-mask pixels are missing. They cannot be reconstructed merely by matching a shader repeat number. C5.1 has smoother slopes, different surface orientations and different UV exposure. This changes both material appearance and silhouette.
3. Original C6/C6.1/C6.2 expanded small scans approximately 4.8x/7x across width while depth stayed much smaller. That method is deliberately not reproduced. Its broad appearance is a visual reference, not permission to restore the distortion.
4. The surviving native Coastal Cliff01 hero has genuine depth but coastal fluting, unlike the quarry's broad broken beds. Widening materials helps scope without making these geological shapes equivalent to the originals.
5. A real export problem affected normal frames: geometry-only normals use UV1 at middle/far LODs, but the exporter initially supplied UV0 tangents. The new asset now has tangents regenerated from the actual normal-map UV channel, with genuine seam splits and correct handedness. The preserved recovered C9 medium/far audit differs from regenerated UV1 frames (mean direction dot0.643/0.413); that old asset remains unchanged for comparison.

## Material-only correction

New private selector: `/?arrival=hub&diagnostics&quarryReview=material-fidelity`. `ScannedMaterialFidelitySession.ts` borrows the existing C8 family on unchanged C5.1 geometry for all nine Wall14/15/16 LOD nodes. There is no new texture, new physical mesh, full-world copy, global colour adjustment or shader blend layer for this pass.

The approved threefold apparent size is maintained by dividing the original repeat0.18534612740581588 by3: **0.061782042468605296** (float export differs only by precision). It does not triple repeats. Albedo, tangent normal and ORM transforms remain aligned; the geometry UV1 bake is independent. Existing whole-atlas UV rebasing preserves integer periods rather than altering the selected texture size.

The immutable C8 holder is `public/models/gullyverse/recovered-c8-material/scanned-materials.glb`, 5,412,804 bytes, SHA-256 `ff330dcfe418436d324535675472b7e10ca34e8f4cb924faf40e7748bea5feee`. It retains genuine Poly Haven Marble Rock03 / Rock Face03 maps, CC0 provenance, non-metallic rough stone, sRGB albedo and linear non-colour maps. Normal strength remains0.7/0.7. COLOR_0 is present; shared vertex-colour behavior is unchanged. No extra dark AO or fake shadow streak was added.

This corrects **coverage**, not the lost authoring mask. Broad brown fractured grain is much less confined to one sector, but the ends still meet very different legacy wall surfaces. No camouflage, random per-face colours, or blurry rectangular gradient was used to pretend the boundary disappeared. The full five-mode comparison deliberately shows these remaining colour/grain changes.

## New physical composition and actual source scale

New private selector: `/?arrival=hub&diagnostics&quarryReview=geology-fidelity`. It keeps the original native Coastal Cliff01 hero at **uniform 0.9x**. All **21,991 / 6,493 / 2,093** hero triangle positions remain exact float32 matches; side-face UV projection and shading/tangent data may change. Do not claim every attribute is untouched.

Additional source: [Poly Haven Coastal Cliff04](https://polyhaven.com/a/coastal_cliff_04), CC0, authentic provider Blender model. Original raw-axis dimensions are **86.771980 x24.247431 x10.999709 m**; the coordinate remap is explicit in the composition contract. The original full model has1,537,429 triangles. Authoring uses its native LOD1,768,962 triangles, to fit the8GiB workspace. Provider1K images are authoring-only; no new source PBR collection is sent to visitors.

{source_table}

The source blend is101,278,315 bytes, SHA-256 `9b956257d3c8605b142fe270908dbc082f4f4ffcced5b2f9ca85501db769d21b`, provider MD5 `62857db7edca7b69e4f4b80d3cacca7d`. Original diffuse JPG, OpenGL normal EXR and roughness EXR, official URLs and per-file provider MD5/SHA are retained under `licensed-source/coastal_cliff_04/`. Commercial use and redistribution follow Poly Haven CC0; reference photographs are not copied into runtime maps.

**Important composition limitation:** four disjoint scan crops are retained as authoring inputs, but only **Middle_North and Upper_South** have measured close correspondence on the final front surface. Middle_South and Upper_North were buried or moved outward while protecting clearance and do not establish visible front coverage. The sparse audit samples every20th composed triangle (7,044 samples,0.24m nearest-source threshold);5904 samples are host/backing/beyond that threshold. These counts are not exact area or provenance percentages. Do not claim four visible scan formations or scan coverage across the whole35.557m wall.

The material covers the full old study extent. The local composed partition spans roughly25.6m within it, with much of the original host retained/remeshed around two effective additional formations. No small source is stretched to fill the whole wall. Exact matrices, native crop bounds, outward placement corrections and scale singular values are in `composition-contract.json` and runtime manifest. The source is genuinely scanned; the resulting assembled wall is not claimed to be a site photogrammetry capture.

## Modelling, joining and failed trials

The final entry is `scripts/blender/compose_quarry_fidelity_volume.py`, not the earlier direct-entry trial. It closes authoring backs, composes source and an8m outward host backing through **OpenVDB0.12m volumetric solid remeshing**, and extracts/retopologizes the front skin. This is a voxel solid-composition workflow; it is not represented as avoiding all union concepts. It differs from C8's rejected exact-triangle Boolean subtraction/join attempt. The protected original hero and outer C5.1 ring are excluded from the remesh. No random-displacement cliff, C7 folded-plane generator or repeated scan tiling was used.

Shared external borders are established first from actual host vertices. The top protected strip, buried foot and unchanged collision envelope are retained. Interior annuli are triangulated using perspective-facing checks from seven public eyes. One measured far-LOD join uses a manifold diagonal rotation without changing positions. A local sub-metre fin cleanup affects 373 vertices, maximum0.0636m adjustment, rather than applying noise to the whole surface. Two genuinely ill-conditioned shading faces use explicit local hard breaks.

Several direct joining, collapse-decimation, blanket crease-protection and alternative rim/LOD trials failed stricter ray or tangent checks. Their logs and diagnostic evidence are retained under `raw/` and `trials/`; none are relabelled passing. **Decimation that broke sightlines was rejected**, not excused by changing test tolerances or double-sided materials. The final conservative simplification uses 6-degree limited planar dissolve for middle/far source fronts. It protects visible shapes but leaves too many triangles for uncritical rollout.

The final neutral view still exposes long smooth connecting regions and fan-like triangular shading/facets. Correct topology and passing sampled rays do not make those artistic transitions convincing. Their remaining appearance is a fidelity limitation, not a solved seam.

## Editable source, runtime and tangents

Editable packed master: `assets-source/gullyverse/quarry-fidelity-correction/quarry-fidelity-correction.blend`, **{master['masterBytes']:,} bytes**, SHA-256 `{master['masterSHA256']}`. Blender4.3.2 opens it read-only; all four file images are packed. High authoring objects and optimized runtime objects remain separate, with the source contract embedded.

Runtime geometry: `public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb`, **{asset['runtimeBytes']:,} bytes**, SHA-256 `{asset['runtimeSHA256']}`. Geometry-normal holder: `fidelity-bake.glb`, **553,448 bytes**. Combined new local transfer is **8,803,764 bytes**, not a duplicate complete-world quarry.

{lod_table}

The composed front is36,000 triangles near and29,946 middle/far. Total region triangles include the original hero, unchanged host parts and joins. Manifest labels such as retainedHostTriangles describe input accounting and are not additive with every overlapping category. Use the final GLB triangle total as authoritative. The middle/far representation is materially more expensive than the rejected recovery and **fails a sensible future rollout budget**; no claim of production optimization acceptance is made.

UV0 retains physical host scale and selected3x sampling. Near-singular side/undercut UVs use offline dominant-plane projection; exact protected outer position/normal/UV contracts are retained. A single1024px geometry-only normal atlas uses independent UV1 halves for middle/far. Fine C8 grain is not baked twice into that atlas. No real-time displacement, global triplanar shader, new decoder or runtime loader dependency was added.

Offline MikkTSpace regeneration uses Three's already-installed bundled implementation. The final read-only audit of actual exported normal channels produces mean tangent-direction agreement approximately1.0 for all three LODs. Production uses UV0 near and UV1 middle/far. UV/tangent seam vertex splits are real; the final audit does not merely project arbitrary tangents onto normals. Protected raw float32 normals are restored in the **new** GLB only, followed by strict validation.

Reproduction uses Blender4.3.2: first `compose_quarry_fidelity_volume.py`, then `bake_quarry_fidelity.py`. Do not use `--resume` on a clean restore; it requires a regenerated cache. Original packed files and exports can be restored without any regeneration or source re-download. Cross-version remesh/bake bytes are not promised identical.

## Runtime ownership and preservation of the website

`GeologyFidelitySession.ts` reuses the material-fidelity owner and adds one local3LOD geometry owner plus one geometry-normal image. Rendering clones remove current Wall14/16 and replace Wall15 with the combined local partition; unaffected world geometry and C8 image resources are borrowed. A region-level bound is used by the existing screen-space LOD selector/hysteresis and frustum culling. The authoritative movement registry is untouched.

Covered preparation waits for the material and local geometry/bake owners. Load failure shows the explicit material-only candidate with retry. Disposed or superseded load generations close only their own unpublished resources. Ten comparison cycles, deliberate retirement/reload, delayed loading, partial holder failures, malformed embedded-PBR rejection, unmount, context loss/recovery and native-video fallback are included in actual-browser checks. These sampled plateaus do not prove infinite-session leak freedom.

All selectors remain private behind the existing development/preview build gate. Old `scanned-material-multi` and `scanned-composition` comparisons are intact. Ordinary URLs remain C5.1 with no scanned candidates or review controls. The preview gate is not an authentication system. Map, stage, return, browser history, hard reload and direct URLs preserve the selected new review mode.

## Geometry validation and seven inherited defects

{validation_table}

The standard survey uses **10,920 directions per scene x3LODs =32,760 actual casts per scene**, baseline and corrected. Additional targeted cones contribute **1,875 LOD-specific casts per scene**. `raysPerVersion` in the older JSON name counts directions, not the multiplied casts. Tolerances remain2e-5m for shared positions and normal dot at least1−1e-6. All protected positions have zero drift; all three LODs have zero non-manifold interior edges and zero new floor-polygon intrusion. The exported local wall remains a visual open surface at its intentional protected perimeter, not a supposedly watertight full world.

Whole-scene status remains **FAIL_INHERITED**. Six current first-hit samples are the unchanged Terrain2_2 surfaces in three LODs (hub,pitch35,yaw90) and Terrain1_2 surfaces in three LODs (visitor3,pitch40,yaw183). The seventh known component defect is unchanged Terrain2_1_LOD1 from eye[0,1.72,−96],pitch30,yaw48: distance70.451118m, normalDotRay+0.2413709. The current combined BVH chooses a coincident front-facing Wall06 at the same distance. A separate component BVH proves the original back face still exists. It is **not repaired**. `known-seventh-legacy-hit.json` retains the evidence and original hit, so a first-hit count of six is not misreported as improvement from seven.

These are finite ray/clearance surveys, not an exhaustive absence-of-defects proof. No unrelated C9 terrain or cave-mouth repair was attempted in this correction.

## Browser tests, retained failure and cold-stage margin

Final production build: **{perf['build']}**. Typecheck, lint, build and90 immersive unit tests pass. The build uses non-secret invalid Supabase placeholders solely to compile/run locally; payment, backend APIs and external services are not certified. Existing lockfile/dependencies are retained.

The final serial browser queue completed all captures, diagnostics, videos and matched performance. Public stabilization passed8/8 groups. Private desktop entry, input-focus handling, suspension, map, playback/rapid replay, boundary menus/history and direct routes passed. The final combined private cohort's fresh mobile context then timed out waiting 90s for landing while the desktop Aftermovie Canvas remained active. It did not retain enough live failure state to establish the cause. The original failed JSON/log remain intact. An isolated rerun of **the same mobile and reduced-motion assertions and timeouts** passed: actual touch movement2.233m, map open/close and reduced-motion Enter. No application code, default tier or timeout was changed. Do not call the original combined cohort all-green or assert that resource contention is proven as its cause.

Composition ownership/recovery passes11/11 groups. Preview persistence passes21 recorded states; the real journey records10 states. Actual keys and public map/menu controls exercise directional travel and stage return. The initial concurrent public-browser trial also timed out on its boundary menu; the subsequent unchanged serial public cohort passed. Both trial and final records are retained.

Fresh isolated direct-stage checks on the final build use1366x900/DPR0.25:

{cold_table}

The application retains its45-second active preparation deadline. The table's margin uses observed boot-to-local wall time, not an instrumented internal deadline clock; hidden/suspended time would differ. These local software checks are single samples and do not certify network or device margins. Earlier protected Phase 3 default-stage loads were40.57–42.64s, already close to45s. The separately labelled Q3 run is diagnostic only and does not change the production default. Retain any narrow or failed margins for hardware testing rather than extending the deadline to hide them.

## Matched transfer, memory and rendering cost

All following measurements are **Chromium154 / ANGLE SwiftShader software rendering**, not hardware GPU acceptance. The five modes use1366x900, actual DPR0.5, quality3, approved unchanged dusk lighting and eight-second settled windows. The profile ran alone, with cold HTTP cache explicitly cleared, warm cache enabled and APIs/analytics blocked through CDP. Windows contain only 9–30 frames; p99 is coarse and often equals p95. No confidence interval or physical-device FPS inference is appropriate.

{loads_table}

Warm low transfer does not remove image decoding, uploads and shader preparation. Corrected cold transfer is23.38MB versus18.97MB for rejected recovered C9 and16.54MB for material-only coverage. These are measured localhost HTTP transfers including application assets, not just GLB file sums or a WAN benchmark. Existing C5.1 preparation and the established private C8/C9 scoped preparation path differ, so load-time differences are not attributable solely to geometry.

Shared rock **unique decoded image** estimate remains48MiB C5.1 +32MiB C8 +5.33MiB geometry normal =**85.33MiB** for either recovered or corrected C9. Material-only correction adds **zero** images or bytes over recovered C8. The corrected geometry substitutes a same-size1K bake, not another large PBR family. The three C8 unique images expose five texture wrappers due to ORM channel use. Renderer allocation/scene estimates include other website assets and wrapper counting and must not be confused with unique source-image residency:

{counts_table}

There are24 active linked programs in recovered and corrected C9 versus23 C8 and22 C5.1 at this sampled point. Geometry objects decrease because three host sectors become one local owner, while visible triangle cost increases. Counts are renderer snapshots, not exact driver VRAM.

{frame_table}

At the visitor wall, corrected visible geometry is143,647 triangles/34calls versus117,083/36calls for recovered C9. Corrected p50 is376.4ms versus328.5ms; hardware performance remains pending. Aerial map triangles rise to154,794. Original stage geometry remains1,040,175 visible triangles in all five modes; its software frame rate is dominated by that preserved stage. The same stage draw/geometry counts and functioning playback are preservation evidence, not a claim that stage performance is acceptable on phones.

Future scaling: PBR images can remain shared. Repeating this unoptimized local package ten times would add approximately88.0MB local GLB bytes and, if each region kept a unique1K bake,53.3MiB decoded geometry normals before any baseline assets; it would also multiply far-triangle cost. This is an illustrative budget warning, not permission or a rollout plan. A viable future budget requires genuine middle/far retopology or silhouette-impostor evaluation without relaxing the interface/visibility checks. No such expansion was implemented.

For real-device verification: restore this checkpoint, run the preserved lockfile/build with the private gates, use actual hardware acceleration, record OS/browser/GPU and viewport/actual DPR/tier, then repeat the five mode comparisons, walking/map/stage playback/return and allocation cycles. Record cold/warm loads and p50/p95/p99 on integrated-GPU laptop and physical phone. Portrait emulation and SwiftShader are not substitutes. No 60 FPS guarantee is made.

## Visual evidence and photographic comparison

The package contains **125 current full-resolution browser PNGs** (25 poses x5 modes), **73 authentic historical browser images**, six separate diagnostics,21 original→recovered→corrected contact sheets, a phone review PDF, full screenshot PDF, technical PDF and two actual-browser recordings. `matched-pose-verification.json` checks every current pose's actual camera/FOV/canvas/light label/quality. Desktop is1366x900/DPR1/Q0 and portrait390x844/DPR1/Q0. No screenshot is colour-graded; PDF JPEG derivatives are compressed reading copies, with original PNGs retained. A final metadata check found a Q0/Q1 mismatch only in portrait map stills because adaptive quality changed during ascent. All five portrait map stills were recaptured with browser-only Q0 pinning after opening; the original mismatched stills and JSON remain in trials/10-mobile-map-quality-mismatch. Production adaptive quality and automatic LOD video were not changed.

Three public eye positions[−18,1.72,−55],[−18,1.72,−62],[−17,1.72,−69] are included. The first clearly exposes the material/rock region; the second and third remain substantially stall-occluded. Stalls were not moved or cropped away. Close/medium/along-wall/rim/foot inspection cameras outside normal walking bounds are labelled. Their appearance does not independently establish visitor-distance acceptance.

The original D panels and corrected candidate are presented without hiding blank surrounding surfaces. At visitor1, broader scanned colour/grain reads more like the original than the narrow grey-surrounded recovery. Medium/upper views add actual relief in two effective areas, but coastal folds, smooth host, boundary bands and orientation-dependent mapping still differ. Along-wall and neutral views reveal thin/faceted transitions that are less evident under textured dusk. Rim strips are intentionally original and remain smoother. The lower foot remains grounded but still lacks the naturally distributed rubble/sediment of the photographic reference. None of these limitations is concealed by a lighting change.

The project quarry photographs show broad, coherent excavated planes, thick broken beds, irregular joint intersections, real shadow depth and restrained naturally varying stone shades. Current material grain helps surface character, but dense diagonal crack/grain patterns and fluted source shapes do not reproduce that full hierarchy. Some light-dark variation in the photos comes from sunlight/shadow, not separate albedo. No attempt was made to paint those shadows or globally brighten the quarry. The remaining problem is medium-scale form/composition and transitions, not simply missing4K maps or polygons.

Temporary neutral lighting and texture-free geometry are development/browser diagnostics only. Approved dusk, sky, fog, exposure and stage lights remain unchanged. No old local-fill proxy was activated by default. The actual-browser visitor journey includes original entrance/tunnel, public walking, map, stage video and return; the separate non-public inspection recording retains automatic screen-space LOD selection and original timestamps, without speed-up.

## Review and restoration files

Open `reports/recovery-quarry-fidelity-2026-10-19/gallery.html` after extracting all review ZIP parts. The phone PDF presents genuine original C9 D / rejected recovery / corrected candidate. The full screenshot PDF includes every current mode and historical progression; individual full-resolution PNGs and exact metadata remain linked. `stage-fidelity-matrix.csv` is the concise pre-C9 handoff. Videos are `videos/visitor-journey.mp4` and `videos/automatic-lod-inspection.mp4`.

The new dated Drive folder is [2026-10-19 Recovery Phase 3 Fidelity Correction](https://drive.google.com/drive/folders/1doGUar6hMGWhFuqn0jlkcG4sl2nE2MXw), with distinct visual-review, source/assets and verification subfolders. The19October date denotes phase start; final delivery is20October. Earlier protected backups are immutable:

- Phase1 foundation: https://drive.google.com/drive/folders/1OdGXZvpfHCdYpWesgya3x_lTupKsB_HI
- Phase2 C8: https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-
- Phase 3 original recovery: https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A

The correction checkpoint is an **incremental overlay on all three protected checkpoints**, not a standalone source tree pretending to contain their LFS assets. `DEPENDENCIES.json` identifies exact prior archive hashes and real required payloads, including original Blender masters/stage/media, shared C8 maps and original C9 scan/master. New archives contain changed/additional code, editable packed master, authentic CC04 source/maps, local exports, reports, gallery, video, scripts, tests and failure evidence. Starting user files missing from the older protected checkpoint are included too. Source, licensed-source, review-gallery and technical-evidence archives are independently extractable below100MiB; merge their `project/` trees. No binary concatenation is required.

`RESTORE-FIDELITY.md`, `apply-fidelity.py`, `fidelity-file-manifest.json`, `checkpoint-index.json` and `SHA256SUMS.txt` accompany the archives. The restorer checks all baseline/payload hashes before atomic edits, rejects unrelated source changes, preserves unrelated files and is idempotent. Independent restoration proof checks archive CRC/SHA, every new member, all 3,761 audited starting files and read-only opening of the restored packed master. Credentials, .env contents, node_modules, .next, authoring caches, redundant ZIPs and raw video intermediates are excluded.

**External verification is recorded in the late-generated `DRIVE-BACKUP-RECEIPT.json`, not inferred from this report or upload success.** After the archive freeze, each uploaded payload is downloaded in full through authenticated Drive access and its name/ID/parent/size/SHA checked. The receipt and start index are companion files with their own subsequent download-back verification; no circular self-checksum is claimed. Consult the final receipt and shared Doc for actual verification counts, hashes, links and the unique new handoff ID. The small interim authoring snapshot is expressly not a complete restoration checkpoint.

## Stop and approval gate

Both corrected private candidates, original recovered comparisons, source history and all prior backups remain reversible. User visual approval is PENDING. Material coverage is corrected; full historical geological fidelity is not proven and visible weaknesses remain. Do not advance to Stage 3A, promote public rendering or roll this cost around additional sectors. The next action is the user's side-by-side review of material scope and geological composition, with the original C9 D panels as the reference and the limitations above visible.
'''
(ROOT / 'docs/gullyverse-recovery-quarry-fidelity-correction.md').write_text(text)
print('REPORT_WRITTEN', len(text.encode()), 'bytes')
