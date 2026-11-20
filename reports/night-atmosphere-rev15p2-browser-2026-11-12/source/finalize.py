from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];B=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11';d=json.loads((R/'evidence/browser-comparison.json').read_text());assert d['status']=='PASS';cases={(x['profile'],x['version']):x for x in d['results']};compiled=json.loads((R/'evidence/compile.json').read_text());movement=json.loads((R/'evidence/movement-preservation.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend')=='f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682'
assert sha(B/'viewer/pilot.glb')==compiled['baselineGLBSHA256'];assert sha(R/'viewer/pilot.glb')==compiled['compiledGLBSHA256'];assert compiled['clippedComponents']==0
for row in movement['files']:assert sha(Path(row['path']))==row['sha256'],row['path']
assert not subprocess.check_output(['git','diff','--name-only','--','app','components/immersive','lib'],text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='0e1e23dd2f5181df202d862d147067249bc55a41'
def summary(a):
 s=sorted(a);return {'samples':len(s),'p50Ms':s[min(len(s)-1,int(len(s)*.5))] if s else None,'p95Ms':s[min(len(s)-1,int(len(s)*.95))] if s else None,'p99Ms':s[min(len(s)-1,int(len(s)*.99))] if s else None}
def metric(s):return ' / '.join(f'{s.get(k):.1f}' if s and s.get(k) is not None else 'unmeasured' for k in ['p50Ms','p95Ms','p99Ms'])
rows=[];reductions=[]
for profile in ['desktop','mobile-emulated']:
 for old,new in zip(cases[profile,'baseline']['measures'],cases[profile,'updated']['measures']):
  a=old['completedRenderReadback']['meanMs'];b=new['completedRenderReadback']['meanMs'];reduction=(1-b/a)*100;reductions.append({'profile':profile,'view':new['view'],'beforeMs':a,'afterMs':b,'reductionPercent':reduction})
  gpu=summary(new.get('gpu',[])) if isinstance(new.get('gpu'),list) else new.get('gpuSummary');rows.append(f"| {profile} / {new['view']} | {a:.1f} | {b:.1f} | {reduction:.1f}% | {metric(new['completedRenderReadback'])} | {metric(new['cpuSubmission'])} | {metric(gpu)} |")
(R/'evidence/final-validation.json').write_text(json.dumps({'status':'PASS_WITH_DECLARED_PILOT_LIMITS','sourceMasterUnchanged':True,'baselineGLBUnchanged':True,'sourceGeometryIndicesUV0AndArtworkUnchanged':True,'groundUV1Corrected':True,'movementAndTransitionFilesUnchanged':True,'productionAppDiffEmpty':True,'gitHEAD':head,'browserFunctionalTests':d['status'],'performanceComparison':reductions,'GPUResults':'See raw completed-query samples; unavailable timings are not inferred','productionIntegration':False,'physicalDeviceCertification':False},indent=2)+'\n')
folders=json.loads((R/'evidence/drive-folders.json').read_text());sourceURL=folders['source']['url'];checkpointURL=folders['checkpoint']['url'];visual=json.loads((R/'evidence/visual-comparison.json').read_text())
text='''# Rev15P2 — browser night lighting and performance

12 November 2026, Asia/Kolkata. The user authorized continuing the isolated pilot and asked that the original website quarry movement flow be preserved. This update changes the private browser asset/viewer only. It restores static shadows, fixes the floor lightmap and damp roughness mapping, removes most runtime lighting work and leaves the live website, movement controller and entrance/exit transitions unchanged.

The updated asset is 16,701,980 bytes, down from 23,776,228 bytes (29.8%). All 447,269 source triangles, node transforms, positions, indices, UV0 artwork coordinates and retained base image bytes remain unchanged. The UV1 floor atlas is deliberately corrected. Original Rev15O and the packed 46-scene Rev15P source master are untouched.

## Lighting changes

Cycles baked diffuse direct/indirect illumination onto the compiled mesh, using the native lamp transforms, shapes, powers, colours and world. Four samples and up to three bounces were used. Metals were neutralized for a reusable diffuse illuminance field; original base artwork remains a separate unchanged map. The per-corner result is averaged to the existing export points and encoded as normalized 16-bit linear RGB. The material's explicit `nativeLightfieldScale=32` restores its range in Three.js; matching original emissive image contributions are preserved. No component clips at that scale.

The static scene uses lightweight unlit materials. Live normal/roughness maps and multiple lamps are removed from those surfaces. Four ground meshes retain a standard material with a single specular-only point light, preserving camera-dependent damp highlights while the main diffuse/shadow response remains baked. It is an approximation of the native area-light reflection and has no runtime shadow map. Native roughness noise is baked separately into the same atlas.

The previous test checked that a second UV existed, but two ground meshes contained metre-scale coordinates there. The new pass gives all four floors explicit non-overlapping, bounded tiles in a 1024 × 2048 atlas and explicitly requests that UV layer during baking. The viewer binds it on channel 1. This fixes actual sampling, beyond merely checking the attribute's presence.

Fog density remains 0.024. Its displayed target colour is calibrated to the fully fogged native reference sky (RGB8 19, 28, 37). Exposure follows the native 0.25-stop setting. The sponsor shader retains its two exact 5338 × 64 atlas tiles, 10,676-cell period, logo spacing, pause and reduced-motion behaviour. No thick particle layers, SSR or duplicate canvas is introduced.

## Preservation and movement

The original quarry runtime, navigation, input, rendering shell, hub, cave entrance and world files have recorded SHA-256 values and are unchanged. The production `app`, `components/immersive` and `lib` tracked diff is empty; HEAD remains `0e1e23dd2f5181df202d862d147067249bc55a41` on `work-in-progress-2027`. The existing README modification predates this task and is retained. No commit, push, PR, deployment or production integration occurred.

This is source preservation, not a claim that the new model has already been integrated or exercised through the production movement flow. Future integration must bind these materials/assets into the existing one-canvas runtime and keep its movement controller and transitions. The pilot's three fixed review cameras do not replace the website controls.

Packed native source SHA-256: `f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682`.

## Same-harness measurements

Chromium uses ANGLE SwiftShader in this cloud environment. Desktop is 1440 × 900 at render DPR 1. Emulated mobile is 390 × 844, device DPR 2 capped to render DPR 0.85, with 4× CPU throttling. Each view has two warm-up renders and five measured renders. A synchronous one-pixel readback forces completion; its overhead is included. CPU submission is measured separately. These are render-cost diagnostics, not display FPS, network delivery estimates or physical-device certification. Tail percentiles from five samples are descriptive only.

| Profile / view | Before mean ms | Updated mean ms | Reduction | Updated render p50 / p95 / p99 ms | CPU submission p50 / p95 / p99 ms | Valid GPU p50 / p95 / p99 ms |
| --- | ---: | ---: | ---: | --- | --- | --- |
'''+ '\n'.join(rows)+'''

In these conditions, desktop render cost falls by roughly 61–71% and emulated-mobile cost by 47–56%. Draw calls stay at 95–128 depending on the view; this pass improves material/lighting cost, not mesh count. No geometry compression or LOD change is used to obtain the result.

The fair texture-source estimate rises slightly, from 145,513,472 to 149,707,776 bytes (about 2.9%), because the floor maps are higher resolution. Both versions use the same source/sRGB-variant/mip estimate. It does not measure driver VRAM or allocation padding. Geometry attribute bytes fall because unused normals/tangents are removed from static materials. Ground normals are derived at runtime for the four specular surfaces. Shader programs, load/compile times, bytes and raw samples are in `evidence/browser-comparison.json`.

Valid GPU query times are reported only when completed and non-disjoint; extension availability alone is not a result. Physical GPU performance, physical-phone FPS, input latency, battery/thermal behaviour and full-world production movement remain unmeasured. The desktop ~60 FPS and mobile >=30 FPS goals are not certified and remain unmet on this software renderer.

## Visual and functional checks

Matching far/middle/near captures compare the native reference, the previous browser and the updated browser. Whole-frame RGB error against the native reference falls in all three views; this is a descriptive check, not a perceptual-fidelity guarantee. Static shadows and shop interiors now follow the baked lighting. View-dependent metal response and very large sparsely sampled faces remain approximations.

Both versions/profile sets pass one-canvas, HTML directions, reduced-motion pause, LED count, second-UV presence and GL-error checks. The updated compile separately verifies valid ground atlas coordinates, original geometry/UV0/image hashes and movement-file preservation. There are no console or page errors in the comparison run. The review PDF is the user-facing visual deliverable.

## Recovery and delivery

All new files are under `reports/night-atmosphere-rev15p2-browser-2026-11-12`. `viewer/` is standalone with its bundled Three.js runtime. `source/` contains the bake, compile, server, comparison and review scripts. `evidence/` records hashes, raw lightfields, atlas metadata and test results. The packed native master and exact baseline GLB remain in the verified local Rev15P base checkpoint; they are not overwritten.

The user permitted PDF delivery to Breeze Drive. The source checkpoint remains local under the pilot source-upload restriction; PDF permission is not treated as permission to upload the entire editable source. The incremental local archive contains the new implementation, screenshots, PDF, restore instructions and checksums, with an explicit dependency on the already verified complete Rev15P base checkpoint. The Drive review PDF is separately verified by parent, size and authenticated download-back SHA-256. Earlier folders and sharing settings remain unchanged.

Existing local base: reports/night-atmosphere-rev15p-pilot-2026-11-11/checkpoint/Rev15P-Night-Pilot-Local-Checkpoint-20261111.zip; SHA256 df53edfb1d95dde30c3e3dfe140a730daec7a8b50d4dd79e575df7f8ba5340ac. Review phase: '''+sourceURL+'''

PDF review folder: '''+checkpointURL+'''

The night look is retained as an isolated candidate. Full-environment rollout and production movement integration are not started by this handoff. Next work should validate representative physical hardware and address texture compression/streaming and culling/LODs before making a production performance claim.
'''
(R/'REPORT.md').write_text(text);print('FINAL VALIDATION AND REPORT WRITTEN')
