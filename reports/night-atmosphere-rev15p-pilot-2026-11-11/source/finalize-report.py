from pathlib import Path
import json,hashlib,struct
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
proof=json.loads((R/'evidence/preservation.json').read_text());perf=json.loads((R/'evidence/browser-performance.json').read_text());export=json.loads((R/'evidence/export.json').read_text());comp=json.loads((R/'evidence/compression.json').read_text());fresh=json.loads((R/'evidence/fresh-open.json').read_text())
source=R.parent/'house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==proof['sourceSHA256']
assert hashlib.sha256((R/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend').read_bytes()).hexdigest()==proof['pilotSHA256']
followup=json.loads((R/'evidence/final-functional-check.json').read_text());assert followup['status']=='PASS'
assert all(not p['errors'] and all(v for k,v in p['checks'].items() if k!='reducedMotionPaused') for p in perf['profiles'])
assert all(fresh['checks'].values())
rows=[]
def metrics(s):return ' / '.join(f'{s[k]:.1f}' if s and s[k] is not None else 'unmeasured' for k in ['p50Ms','p95Ms','p99Ms'])
for p in perf['profiles']:
 for m in p['measures']:rows.append(f"| {p['profile']} / {m['view']} | {m['frames']['sustainedFPS']:.2f} | {metrics(m['frames'])} | {metrics(m['cpuRenderSubmission'])} | {metrics(m['gpu'])} | {m['stats']['drawCalls']} |")

fog=[]
for key,box in [('far',(640,335,810,487)),('middle',(510,130,930,650)),('near',(220,240,1220,680))]:
 clear=np.asarray(Image.open(R/'renders'/f'browser-clear-{key}.png').convert('RGB'))[box[1]:box[3],box[0]:box[2]].mean(axis=2)
 mist=np.asarray(Image.open(R/'renders'/f'browser-desktop-{key}.png').convert('RGB'))[box[1]:box[3],box[0]:box[2]].mean(axis=2)
 fog.append({'camera':key,'region':box,'clearStd':float(clear.std()),'fogStd':float(mist.std()),'contrastRatio':float(mist.std()/clear.std())})
image_checks={}
for key in ['far','middle','near']:
 for prefix in ['blender-baseline','blender-pilot','browser-desktop','browser-clear']:
  p=R/'renders'/f'{prefix}-{key}.png';image_checks[p.name]=Image.open(p).size== (1440,900)
assert all(image_checks.values())
(R/'evidence/final-validation.json').write_text(json.dumps({'status':'PASS_WITH_REPORTED_PILOT_LIMITS','sourceAndPilotHashUnchanged':True,'freshBlenderOpen':fresh['status'],'browserFunctionalChecks':'Final targeted desktop/mobile checks PASS after reduced-motion listener/check timing correction; original performance-run failure remains recorded','comparisonImageDimensions':image_checks,'signFogContrastMeasurements':fog,'visualInspection':'Native far/near and corrected browser far/near inspected. Browser is visibly flatter/brighter than Blender; no pixel-match claim. Original world graffiti projection corrected. Near navigation labels remain legible.','performanceGoals':'NOT MET in cloud software rendering','draco':'Experimental: decoded triangle count differs; plain GLB is default','ktx2':'NOT ENCODED: no local encoder; runtime format capabilities recorded'},indent=2))

text=f'''# Rev15P — isolated night-atmosphere pilot

The authorized next prompt has been implemented as a local pilot. The native Blender look uses a darker cool ambient fill, three principal warm shop-light pools, occasional damp concrete and distance fog. The browser prototype shows the same camera compositions and inexpensive distance fog, with a persistent HTML directions alternative and a pausable LED. The original Rev15O master remains unchanged and authoritative.

The browser prototype is not ready for a full rollout. It misses the requested performance goals on this cloud software renderer, and its material/lighting response is visibly flatter and brighter than Blender. Draco decodes but changes the triangle count, so the plain GLB is the default. KTX2/Basis encoding is not delivered. These are recorded limits, not production approval.

## Files and scope

- Native pilot: `delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend` — {proof['pilotBytes']:,} bytes, 46 packed scenes.
- Browser viewer: `viewer/index.html`, served locally by `source/serve.py` on 127.0.0.1:8765. The viewer and bundled vendor files can be restored independently of the website.
- Review: `review/Gullyverse-Rev15P-Night-Pilot-Review.pdf` and `review/GALLERY.html`.
- Measurement data: `evidence/browser-performance.json`; source/preservation/export/conversion records are beside it.
- Handoff: `WORLD-REV15P-NIGHT-PILOT-20261111-{proof['pilotSHA256'][:8]}-R1` — pilot complete with the limits below, awaiting visual review and further direction.

All new implementation files are under this report directory. Only prior verified duplicate download staging was cleaned to make room, with receipts in `evidence/staging-cleanup.json`; original masters remain. No app route, package, production asset, current-pointer document, commit, push, PR, deployment or Drive file was changed. The latest prompt's explicit prohibition on Drive writes overrides routine backup uploading for this phase: the checkpoint is local only.

## Verified source inventory

The actual source .blend opened in Blender 4.3.2 before visual edits. Current branch is `work-in-progress-2027`; HEAD remains `0e1e23dd2f5181df202d862d147067249bc55a41`. The source has 45 scenes, 1,601 current-scene objects, 1,412 mesh objects, 1,344 unique meshes, 690,617 raw triangles, 189 native crowd meshes, 18 lights and 124 materials including object-level overrides. The initial mesh-data-only material pass counted 102; the completed inventory includes those overrides. There are no armature objects or linked libraries. The 69 images across all historical scenes have 95,446,183 packed bytes; no file image is missing. 1,404 meshes have UVs, but a second UV alone is not proof of a non-overlapping lightmap atlas.

`evidence/inventory.json` records object hierarchy/collections, camera transforms, mesh sizes, materials and node graphs, lights/shadows, UV names, image sizes/packing, actions and rigging findings. World-coordinate paint, layered brick/Events shaders, haze and LED animation require conversion for glTF. The crowd is static shared pose geometry; this pilot adds no skeletal animation.

The website audit confirmed React 19.0.8, R3F 9.6.1 and Three.js 0.169.0. Its older hub/blockout is separate from Rev15O. The existing one-Canvas shell, quality/DPR adaptation, compile/warm-up and diagnostics were inspected. This private Three.js viewer reuses the existing quantile, CPU-submission, GPU-query and texture-estimate conventions rather than loading production routes.

## Native look and preservation

Every pilot object has its own object datablock. Lights, cameras, world and edited floor materials are independent; geometry stays shared with the unchanged source data. Broad cool light is reduced, existing shop pools are selectively weighted and sign/wall lighting is restrained. Four existing floor materials receive a 0.31–0.91 roughness variation. Optional five interior support lights remain locked off. No geometry, walking route, artwork, portrait identity, text, logo, board position or upper balcony was edited.

The source has 18 shop fronts: 13 closed and five physically open. Those fronts remain geometrically unchanged; three principal warm pools identify the active storefronts. This does not claim that the other two authored open fronts were rebuilt as shut shops.

The native pilot retains all 45 historic scene memberships, all 11 houses and 189 people, eight exclusive Team mural states, Events façade, sponsor LED, cypher and upper balconies. The active scene is `REV15P / Isolated Night Atmosphere Pilot`. Fresh-open checks pass. The pilot controller ends in `REV15O / Team Carousel Controller`; index 0 remains Organising Committee, with indices 0–7 verified independently. The original source hash still matches after every export/render phase.

Source SHA-256: `{proof['sourceSHA256']}`

Pilot SHA-256: `{proof['pilotSHA256']}`

## Browser conversion and fog

The representative lane/nearby-cypher subset includes {export['sourceObjects']:,} evaluated source objects merged into {export['exportMergedObjects']} export mesh objects. The plain viewer has {perf['profiles'][0]['measures'][0]['stats']['totalTriangles']:,} triangles and 84 materials. The full packed native world remains in the pilot .blend; the browser is a subset with the current OC slide, not a new full-world production asset.

Three unsupported paint/brick colour graphs were baked with Cycles. Nine world-projected graffiti materials retain their original affine world-coordinate projection, source alpha and normal-side mask; a repeating-UV conversion error was found and corrected before final captures. Fine enamel wear/noise is approximated, and brick relief is not a complete reproduction of the native shader. Spatial Events shader selection uses an export-only face-region approximation. These conversions are disposable web data and do not alter the native artwork.

Actual static direct/indirect ground illumination and occlusion were baked with Cycles at four samples to a 512 × 2048 image for four ground meshes. `PilotLightUV` is exported as TEXCOORD_1 / Three.js `uv1`, with lightMap channel 1 explicitly bound; both browser profiles verify zero missing second-UV bindings. A portable glTF lightmap workflow is not assumed. The rest of the scene is not fully light-baked: it uses a small set of PBR lights without runtime shadow maps. Roughness is a baked tile; no runtime volume fog, SSR or mist-card overdraw is added.

Both native and browser fog use density 0.024 and the equivalent `1-exp(-density² × distance²)` falloff. Native depth compositing and Three.js view-depth fog are equivalent approximations, not pixel-identical at off-axis rays or through tone mapping. Standard, emissive and custom LED materials receive fog. Fixed far/middle/near positions, targets, lens/FOV and aspect are recorded in `viewer/cameras.json`; all desktop comparison frames are 1440 × 900. Browser clear controls remove fog only; native baseline captures are actual Rev15O.

The 10,676-cell sponsor strip exceeds this renderer's 8,192-pixel texture limit. The final viewer splits it into two exact 5,338 × 64 textures, preserving all pixels and gaps without automatic downsampling. The custom shader samples across the split and includes fog. Reduced motion pauses the scroll; the HTML directions remain accessible independently of sign visibility. No navigation destination was renamed or chosen.

## Compression and browser cost

The initial Blender GLB was 115,379,540 bytes. Current plain GLB: {(R/'viewer/pilot.glb').stat().st_size:,} bytes; experimental Draco: {(R/'viewer/pilot-draco.glb').stat().st_size:,} bytes. PBR colour images use JPEG 86 where opaque, while alpha/normal/lighting maps remain PNG; most maps are capped at 1,024 pixels and selected artwork at 2,048. Original native images remain packed and unchanged.

The installed Blender Draco library is missing; the exporter returned success while writing uncompressed geometry. This was detected by inspecting the actual GLB extension list and byte counts. The repository's official Draco JS encoder produced a real compressed extension with second UV retained. Browser decode succeeds but reports {perf['geometryCompression']['dracoTriangles']:,} triangles versus {perf['geometryCompression']['plainTriangles']:,} for plain geometry, so the compressed file is experimental. The source plain export contains zero-area triangles; the count difference has not been accepted as complete visual/topology equivalence.

KTX2/Basis has no installed encoder. ASTC/S3TC/ETC runtime capabilities were probed and are recorded, but no KTX2 encoding/transcoding result is claimed. Existing crowd LOD meshes are retained and export meshes are merged/cullable; runtime LOD switching and a full-world streaming/instancing rollout remain future work. Large merged façades limit culling granularity.

## Measured performance

Conditions: Chromium with ANGLE SwiftShader software rendering in this managed cloud environment. Desktop viewport 1440 × 900 at render DPR 1; emulated mobile 390 × 844, device DPR 2 capped to render DPR 0.85, with 4× CPU throttling. Local uncached loopback delivery. The controlled benchmark completes three renders per view with gl.finish; the two frame intervals are a small-sample serialized-throughput diagnostic, not display-FPS or hardware certification. GPU-query polling includes a 25 ms settling delay; CPU render-submission timing excludes that delay. p95/p99 values from this small set are not stable population estimates. GPU timings are unmeasured when the extension returns no valid completed query, even if the capability is exposed.

| Profile / camera | Serialized FPS | Frame p50 / p95 / p99 ms | CPU submission p50 / p95 / p99 ms | GPU p50 / p95 / p99 ms | Draw calls |
| --- | ---: | --- | --- | --- | ---: |
'''+ '\n'.join(rows)+f'''

Each profile downloaded {perf['profiles'][0]['totalEncodedResponseBytes']:,} encoded response bytes for the viewer, asset and dependencies. The estimate for sampled texture payload residency is {perf['profiles'][0]['measures'][0]['stats']['textureBytesEstimate']:,} bytes; this counts material texture objects and mip assumptions and may overcount shared image sources. Driver allocations/physical VRAM are not exposed by WebGL. Exact per-view calls, triangles, shader programs, compile time, resource bytes and timing samples are in `evidence/browser-performance.json`.

The desktop ~60 FPS and mobile stable >=30 FPS goals are **not met** in this software-rendered environment. Hardware GPU results, physical phone FPS, mobile battery/thermal behaviour, full-world delivery and production-route integration are unmeasured. Do not infer real-device performance from viewport/CPU emulation.

## Review result and next step

The isolated native atmosphere study and representative browser workflow are implemented and reversible. Near navigation is legible in inspected captures; distant fog reduces sign contrast. Source preservation, packed fresh-open, one canvas, explicit second-UV binding, custom LED fog and reduced-motion checks pass with no console/page errors in the final targeted checks. The dynamic reduced-motion check initially failed; the media-query object is now retained and the check awaits its change event. The final targeted desktop/mobile functional check passes. Performance measurements precede that event-handling-only fix; timing samples were not silently altered.

Before scaling, choose the preferred native mood from the review PDF, complete the remaining static lighting/material bakes, reduce texture residency and material/draw counts, resolve the Draco fidelity difference, establish an actual KTX2 encoder/transcoder pipeline and measure representative physical hardware. This report does not start that larger phase. Rev15O remains authoritative and the shared document is intentionally untouched under the prompt's no-Drive-edits instruction.
'''
(R/'REPORT.md').write_text(text)
print('REPORT WRITTEN',len(text))
