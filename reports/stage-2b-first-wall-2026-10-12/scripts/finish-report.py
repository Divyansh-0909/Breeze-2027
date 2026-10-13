from pathlib import Path
import json,html,hashlib
root=Path.cwd();r=root/'reports/stage-2b-first-wall-2026-10-12';p='../reports/stage-2b-first-wall-2026-10-12/'
def load(name):return json.loads((r/'raw'/name).read_text())
perf=load('performance-lifecycle.json');detail=load('detail-view-performance.json');meta=load('capture-metadata.json');high=load('high-resolution-capture-metadata.json');walk=load('walkthrough.json');inventory=load('asset-inventory.json');master=load('master-inspection.json');pres=load('preservation-results.json');commands=load('verification-commands.json');start=load('starting-state.json');manifest=json.loads((root/'public/models/gullyverse/first-wall-section/manifest.json').read_text());hardware=load('hardware-profile.json')
filebytes={Path(x['file']).name:x['bytes'] for x in inventory['GLBs']};near=manifest['nodes'][1];middle=manifest['nodes'][2];far=manifest['nodes'][3]
tests=[]
for name,rows in [('default-runtime','default-regressions/results.json'),('opt-in','opt-in-regressions.json'),('default-smoke','production-smoke.json'),('interruption','interruption.json'),('opt-in-touch','touch-optin.json'),('video-with-wall','video-with-wall.json')]:
 data=load(rows);data=data if isinstance(data,list) else data['checks']
 for t in data:tests.append({'suite':name,**t})
summary={'unitTests':61,'browserChecks':tests,'assetValidation':[(Path(t['file']).name,t['issues'])for t in load('glTF-validator.json')],'resourceLifecycle':perf['checks'],'preservation':pres,'physicalPerformance':'PENDING','commands':commands,'currentFailures':[t for t in tests if t['status']!='PASS']};(r/'raw/test-summary.json').write_text(json.dumps(summary,indent=2))
for data in [meta,high]:
 for c in data['captures']:
  if c['file'].endswith('20-medium-lod1.png'):
   old=r/c['file'];new=r/'acceptance/20-medium-auto-lod.png'
   if old.exists():old.rename(new)
   c['file']='acceptance/20-medium-auto-lod.png'
(r/'raw/high-resolution-capture-metadata.json').write_text(json.dumps(high,indent=2))
frames='| Window | Actual seconds / frames | Mean FPS | p50 / p95 / p99 ms | >100 ms stalls | Settled calls / triangles | LOD |\n|---|---:|---:|---|---:|---|---:|\n'
for w in perf['windows']:
 s=w['settled']['stats'];frames+=f"| {w['name']} | {w['elapsedMs']/1000:.2f} / {len(w['frames'])} | {w['FPS']:.2f} | {w['p50']:.1f} / {w['p95']:.1f} / {w['p99']:.1f} | {w['significantStalls100ms']} | {s['calls']} / {s['triangles']:,} | {w['settled']['wall']['activeLOD']} |\n"
detailtable='| Inspection view / surface | Actual seconds / frames | Mean FPS | p50 / p95 / p99 ms | Calls / triangles | LOD |\n|---|---:|---:|---|---|---:|\n'
for w in detail['windows']:
 s=w['after']['stats'];detailtable+=f"| {w['name']} / {w['mode']} | {w['elapsedMs']/1000:.2f} / {len(w['frames'])} | {w['FPS']:.2f} | {w['p50']:.1f} / {w['p95']:.1f} / {w['p99']:.1f} | {s['calls']} / {s['triangles']:,} | {w['after']['wall']['activeLOD'] if w['mode']=='authored' else '— (original face)'} |\n"
trace=perf['trace'];firstparse=next(t for t in trace if t['event']=='parse-ready');firstload=next(t for t in trace if t['event']=='load-ready');tex=next(t for t in trace if t['event']=='texture-init' and t['count']==3);comp=next(t for t in trace if t['event']=='shader-compile' and t['at']>tex['at']);authored=next(t for t in trace if t['event']=='covered-ready' and t['revision']==3);network=[t for t in perf['resources']if 'first-wall-section.glb' in t['url']][0]
video=Path(walk['recording']).name
touch=load('touch-optin.json')
if 'boundary' in touch and not any(c['file'].endswith('22-optin-touch-boundary.png') for c in meta['captures']):
 meta['captures'].append({'file':'acceptance/22-optin-touch-boundary.png','method':'Public touch-emulated portrait movement/map/Aftermovie boundary capture; no inspection pose','before':touch['boundary']});(r/'raw/capture-metadata.json').write_text(json.dumps(meta,indent=2))
counterparts=load('counterpart-metadata.json')
for row in counterparts['captures']:
 if not any(c['file']==row['file'] for c in meta['captures']):meta['captures'].append(row)
(r/'raw/capture-metadata.json').write_text(json.dumps(meta,indent=2))
sourceRows=[('components/immersive/HubScene.tsx','Optional single-face batch substitution; default generator unchanged.'),('components/immersive/AftermovieScene.tsx','Connect optional wall to the existing world and readiness gate; stage JSX/settings retained.'),('components/immersive/ImmersiveShell.tsx','Explicit local opt-in, private owner, authoring controls/cover and input release while preparing.'),('components/immersive/rendering.tsx','Avoid ordinary reveal/draw while optional section is covered.'),('components/immersive/wallSection.ts','Face cut/rigid anchor, screen-space LOD policy and private asset ownership/disposal.'),('components/immersive/QuarryWallSection.tsx','Single visible LOD, shared material, texture/shader/warm-render preparation and recovery.'),('tests/immersive/wall-section.test.ts','Four substantive geometry/anchor/hysteresis/projection regressions.'),('scripts/blender/author_first_wall_section.py','Deterministic metric master/LOD/proxy export.'),('scripts/blender/wall_section_surface.py','Original geological morphology and compatible material fields.'),('scripts/blender/wall_section_materials.py','Original source/runtime PBR map generation.')]
sourceTable='| File | Reason |\n|---|---|\n'+''.join(f'| [{f}](../{f}) | {why} |\n' for f,why in sourceRows)
checkTable='| Browser suite | Checks | Result |\n|---|---:|---|\n'
for name in ['default-runtime','opt-in','default-smoke','interruption','opt-in-touch','video-with-wall']:
 rows=[t for t in tests if t['suite']==name];checkTable+=f"| {name} | {len(rows)} | {'PASS' if all(t['status']=='PASS' for t in rows) else 'FAIL'} |\n"
text=f'''# Gullyverse Stage 2B — first reversible limestone wall integration

Review date: **2026-10-12**. One existing quarry face is replaced only in an explicit local preview. **The default public website retains its approved appearance. No commit, push or deployment occurred.** This is a reviewable first section, not approval to replace the quarry or a claim of finished photorealism.

[Actual browser gallery]({p}gallery.html) · [Screenshot metadata]({p}raw/capture-metadata.json) · [DPR1 metadata]({p}raw/high-resolution-capture-metadata.json) · [Recorded walkthrough]({p}recordings/{video}) · [Test summary]({p}raw/test-summary.json)

## 1. Exact baseline and preservation

Branch **{start['branch']}**, HEAD **{start['HEAD']}**. Starting tracked staged/unstaged diffs were empty; prior untracked pilots, Blender sources, exports, reports and ZIPs existed. Their origin is not inferred. [Starting state]({p}raw/starting-state.json) records the actual status before edits.

A recoverable relevant source/config/asset snapshot exists locally at `reports/stage-2b-first-wall-2026-10-12/backup/current-source-assets.tar.gz` (excluded from the review ZIP because it contains unrelated existing production assets). Credentials/environment files were excluded. [Original hashes]({p}raw/source-hashes-before.json) and [preservation results]({p}raw/preservation-results.json): **726/730 original relevant files unchanged; only the four explicitly listed immersive source files changed; all 478 pre-existing untracked files unchanged; no missing files; unchanged branch/HEAD and empty staged diff.** Historical reports/captures were not overwritten.

The actual registry footprint remains **97.8 × 123.5 m** (boundary x -49.8..48, z -165.5..-42; not a measurement of every protruding rock vertex). Stage origin **[-12,0,-134.3]**, scaffold **[0,0,-70]**, scaffold dimensions **24×14.5×3.4 m**, eye height1.72 m, current movement polygons/gates, stalls, tunnel bend/end and camera/map configuration are unchanged. Original stage/crowd GLBs, trusses, LED/video code/media and restored Aftermovie surroundings match their original hashes. No payment/admin/forms/routes were edited.

## 2. Approved cool-grey limestone: actual repository finding

The latest approved appearance is the **grey limestone pilot**, `assets-source/gullyverse/limestone-grey-pilot/` and `public/models/gullyverse/pilot-limestone-grey/`. Its original maps/scripts/hashes are preserved. [Previous approved grey screenshot]({p}references/previous-user-approved-grey-pilot.png) is historical reference evidence, with a different object/camera; it is not a matched new capture.

**The default quarry in the actual checkout still uses vertex-coloured procedural rock**, roughness0.98/flat shading, without those limestone maps. The grey material was not globally applied in this checkout. This discrepancy was identified before implementation. The new section follows the latest approved grey family; the rest of the quarry was not silently recoloured. Three comparisons therefore distinguish actual default rock, the original three-triangle face with the compatible grey material, and the refined mesh with exactly that same compatible material.

New mapping preserves source body palette **sRGB184/188/193**, normal strength **0.58**, metallic0, roughness **0.82..0.99** and metre-scale mineral frequencies. Original pilot UVs do not fit this larger pentagonal wall face, so **compatible original maps were re-authored**, rather than claiming byte-identical texture reuse. Only a **0.62 m perimeter** blends toward the actual untouched neighbor colour; local AO reflects the new cavities. These local differences are explicit. Global lighting/exposure/fog/sky remain unchanged. Body hue responds to the approved warm Hub light and the distinct stage atmosphere; no warm/brown material replacement was introduced.

## 3. Selected face and fit

Existing **rock4, inward pentagonal face3**, anchor **[42.1893349,6.4880474,-63.6718422]**, width/height **15.5741×19.8942 m**. Normal **[-0.9821211,0.0192810,-0.1872603]**; full rigid basis, corners and author orientation are in [anchor metadata](../assets-source/gullyverse/first-wall-section/anchor.json).

Opt-in removes **exactly 9 vertices/3 triangles** from the existing merged quarry batch. All other position/normal/colour attributes are byte-for-byte preserved by regression test. Relief is recessed into the existing convex solid, with the original pentagonal corners and rim fixed. The two-metre back skin stays inside that solid. The original generator remains available immediately through Original quarry; failed/stale anchor loading retains it. No exposed duplicate face or z-fighting overlay is used.

This low east-side face is away from the entrance, tunnel occlusion, stage/scaffold and active travel thresholds. [Export fit check]({p}raw/asset-fit.json) confirms each LOD stays inside the original rock within floating-point tolerance and retains the corners. A source-corner maximum error is below2 micrometres. Outer silhouette and collision boundaries do not expand.

The wall is beyond ordinary Hub walking bounds. Public walkthrough reaches x≈19.13 m without crossing a gate; close-up cameras are **explicit diagnostic inspection fixtures**, not newly accessible player space. No walking area was enlarged to obtain close-ups.

## 4. Blender construction and validation

[Editable master](../assets-source/gullyverse/first-wall-section/first-wall-section.blend): **{inventory['master']['bytes']:,} bytes**, Blender **4.3.2**. [Author/export README](../assets-source/gullyverse/first-wall-section/README.md) and three dedicated scripts provide reproducible output. Only new first-wall-section paths are written; no site/stage generators ran.

The custom closed mesh combines11 unequal oblique geological planes, finite jagged joints, interrupted bedding,27 small erosion recesses, localized chipped regions and bounded fine relief. It is not a stock noisy primitive or evenly stacked slabs. Geometry handles larger fractures; the normal map handles small mineral texture. Simple back/caps remain embedded in the existing rock rather than exposed as finished outside surfaces. Strata/fractures are original mathematical modelling; [quarry photograph]({p}references/quarry-morphology-reference.jpeg) informed shape only, with no photo texels pasted into maps.

An initial soft trial and a subsequent sharp sawtooth trial were rejected during inspection. A first aggressive middle decimation distorted the sampled front surface (**0.301 m RMS**); it was replaced by sampling the same geological field, reducing error to **0.0193 m RMS**. Draft logs/images remain under `exploratory/` and are not final evidence.

| Source/export | Triangles | Runtime GLB bytes | Role |
|---|---:|---:|---|
| Editable master |243,110|—|Author-only source|
| LOD0 |21,500|{filebytes['wall-lod0.glb']:,}|Near, feature-weighted quadric collapse|
| LOD1 |5,290|{filebytes['wall-lod1.glb']:,}|Middle, same continuous morphology sampled less densely|
| LOD2 |1,720|{filebytes['wall-lod2.glb']:,}|Distant|
| Collision proxy |16|{filebytes['wall-collision.glb']:,}|Separate conservative prism|
| [Combined GLB](../public/models/gullyverse/first-wall-section/first-wall-section.glb) |28,526 incl.proxy|**{filebytes['first-wall-section.glb']:,}**|One shared map set; only one visual LOD renders|

Blender source objects use identity rotation/scale and metres. Front -Y/Z-up exports to glTF front+Z/Y-up. Stable nodes: `Wall_LOD0/1/2`, `Wall_Collision`, `wall_anchor`. All source meshes are closed, zero non-manifold edges, positive signed volume. [Fresh master inspection]({p}raw/master-inspection.json) measures front-ray RMS error **1.84 mm /19.32 mm /39.33 mm** and max **24.9/109.7/193.5 mm**, respectively. This is a2,209-hit front sample, not Hausdorff distance or a visual certification.

Khronos glTF Validator **2.0.0-dev.3.10**: all five GLBs **zero errors/warnings**. Exported normals/tangents/UVs are finite, normal lengths approximately1 and tangents nearly perpendicular. [Validator]({p}raw/glTF-validator.json), [inventory/hashes]({p}raw/asset-inventory.json). Single-sided closed visual meshes; no metallic or wet/glossy response. No Draco, Meshopt or KTX2 was assumed or introduced.

## 5. PBR maps and size tradeoffs

One visible material (the hidden decoded proxy also has a loader-default untextured material) with **1024² JPEG sRGB basecolour**, **1024² PNG linear tangent normal**, **512² packed linear ORM**. Roughness/AO sources are exported into one ORM image. The editable runtime maps are packed in the master;2048 author maps are supplied separately. UV0 uniquely covers the complete face for colour/AO/roughness. UV1 uses a12×10 m mineral normal tile, matching the approved grain scale; it repeats approximately1.3×2 across this face and must be reviewed for visible repetition at high resolution. This avoids smearing fine normal detail over a20 m face without a second downloaded map set.

Conservative decoded RGBA8+mipmap estimate **12 MiB**, reduced from Stage2A's16 MiB; **not measured driver VRAM**. Combined GLB is about**31.8% smaller** than Stage2A's4,127,092-byte prototype, and near triangles drop about34.1% from32,616. Those are data-size comparisons, not cross-scene FPS claims. Lower512 ORM preserves low-frequency roughness/AO; close albedo grain can still look soft. Separate LOD exports each embed maps and are alternatives: loading all of them would duplicate payloads.

## 6. Runtime integration, LOD and ownership

The existing persistent R3F Canvas, coordinator, scene, lights and camera controller remain. A private session loads the combined GLB once and clones objects with shared geometry/material/textures. Only one named visual LOD is visible; proxy/master do not render. Original face, material-reference face and authored wall are mutually exclusive.

Projected diameter in **actual drawing-buffer pixels** uses bounding sphere, camera depth/FOV, viewport and effective DPR. LOD0 enters at720 px, exits below78%; LOD1 enters at220 px, exits below72%. Existing quality tier1 multiplies thresholds by1.15; tiers2/3 by1.5. Invalid/behind-camera measurements select low detail; frustum culling remains enabled. Hysteresis avoids threshold oscillation. Actual walkthrough shows **LOD2→LOD1→LOD2** at roughly331.6/236.9px in tier3. Close/mid/far captured nodes and actual rendering counters are recorded, rather than inferred from glTF node names.

Collision proxy raycast hits its front correctly. It is hidden and **not installed into the approved movement polygons**; the original walking/camera collision strategy remains unchanged.

Mode switches release movement and remain covered through texture initialization, `compileAsync` and real warm renders (each LOD uploaded sequentially, never all visible together). Hub/stage lighting preparation is tracked separately; context restoration clears preparation state and rewarms beneath cover. Critical destination readiness still uses the existing gate. This protects against incomplete reveal, but synchronous API spans do not certify GPU completion or perceived smoothness on physical devices.

Cache ownership is explicit: shell-owner and mounted-consumer leases, revision/generation tokens for interrupted load/preparation, and microtask collection after the last consumer/owner. Off mode intentionally retains **one bounded private cache**, permitting quick re-enable; it does not prove zero residency. `retire()` requires off/not busy/zero consumers, then disposes only owned geometries/materials/textures/ImageBitmaps. Pending abandoned assets dispose after resolution. Shared stage/useLoader caches are never indiscriminately cleared.

## 7. Measured performance and transfer

[Hardware/software profile]({p}raw/hardware-profile.json): Debian13 cloud VM, three AMD EPYC9V74 KVM vCPUs, Chromium151.0.7922.173, ANGLE/Vulkan **SwiftShader software GPU**. No physical laptop/iPhone/Android device tested. Physical60/30 FPS acceptance is **PENDING**, not a blocker to this bounded authoring milestone. [Physical-device procedure]({p}PHYSICAL-DEVICE-PROCEDURE.md) records the required local evidence.

Production-mode localhost measurement:1366×900, effectiveDPR0.5, tier3; no explicit CPU/network throttle, no recording/screenshots during FPS windows, one browser job at a time. Identical valid starting eye pose **[12,1.72,-52]**, same target and alternating actual W/S controls. Requested8s input windows ran longer under software scheduling; actual intervals and bounded frame samples are reported. Quantiles use sorted samples at floor((n−1)q). Snapshots are settled end states, not whole-window draw-count averages. Later Original quarry rows retain the warmed optional cache.

{frames}

The overlapping software results **do not establish an FPS improvement**. Every measured frame was a significant software-rendering stall; temporal correctness is not smooth perception. These short windows do not establish thermal stability, representative desktop/mobile performance or full-quarry scaling. Initial frame-window instrumentation included possible post-end samples; it was corrected and rerun, with the first raw trial retained separately.

[Full movement/lifecycle JSON]({p}raw/performance-lifecycle.json) retains individual frames, renderer counters, heap/resource snapshots and navigation/LOD traces. Main movement windows select distantLOD2. Matched near/mid **inspection** views additionally isolate old-face/same-PBR versus authored geometry atDPR0.5/tier0; these are not normal visitor positions:

{detailtable}

[Inspection raw data]({p}raw/detail-view-performance.json). Current snapshots may differ by a few calls/triangles from animated existing lights/effects; they do not mean the wall has multiple material draws. One visual wall mesh/material is active.

Optional GLB: **{network['transferSize']:,} bytes transfer incl.reported overhead**, **{network['encodedBodySize']:,} encoded**, **{network['decodedBodySize']:,} decoded**, response duration**{network['duration']:.1f}ms** on loopback. First parse-to-ready**{firstparse['ms']:.1f}ms** (includes asynchronous image decode/scheduling), load-to-ready**{firstload['ms']:.1f}ms** (not additive). First three-texture initialization API span**{tex['ms']:.1f}ms**, subsequent compile API span**{comp['ms']:.1f}ms**, first authored covered warm preparation**{authored['ms']:.1f}ms**. These JavaScript spans are not isolated GPU upload/driver timings.

Repeated toggles issue **no additional GLB request**; explicit cache retirement/reload issues the second measured request. Public default smoke test finds **zero pilot/new-wall requests and no preview UI**. No full-quarry preload was added. Cold-resource data in the benchmark is direct Hub/off-preview entry, **not cold fresh landing**, and is not compared with October11 landing transfer totals. Initial public landing visuals were not tuned for SwiftShader.

## 8. Ten-cycle resource lifecycle

Ten completed off/authored cycles plateau in both states. Warmed asset cache: Three.js **28 textures/146 geometries**, tracked GL **32 textures/546 buffers/24 programs** in every cycle. Off detaches the wall/zero consumers but intentionally retains that bounded allocation. Exactly one visual LOD appears when enabled. The three high/mid/low buffers are warmed and remain resident in this one pilot; generalizing that eager policy across the quarry is not recommended.

After deterministic retirement, Three.js returns to **25 textures/143 geometries**, tracked GL **29 textures/528 buffers/22 programs**, matching the initial context baseline; re-enable loads and renders correctly. Active-geometry bytes, estimated texture bytes and heap samples are in rawJSON. Heap remains GC-sensitive, not monotonically increasing evidence or a driver-memory measurement. Context-loss allocation counters are excluded from leak comparisons. A further ten actual movie/exit/camera-restoration cycles with the wall present passed; cycles3/6/9 toggle the preview during playback. Settled Three/GL textures remain28/32 after every cycle, geometry counts plateau and diagnostics report no disposed texture still sampled after rendering. [Video lifecycle raw evidence]({p}raw/video-with-wall.json). These are completed exits, not ten full-length movie viewings. No claim of driver VRAM leak freedom is made.

## 9. Visitor and failure verification

{checkTable}

Existing unit suite **61/61 PASS** (57 preserved plus4 new tests). `npx tsc --noEmit`, `npm run lint`, and production `npm run build` pass; lint retains pre-existing warnings outside the new wall code. Build used inert local Supabase placeholders, not copied credentials; no environment files were edited, APIs/form submissions were not performed. [Build log]({p}raw/build-complete-assets.log), [lint]({p}raw/lint-final.log), [typecheck]({p}raw/typecheck-final.log), [unit results]({p}raw/unit-final.log), [command journal]({p}raw/verification-commands.json).

Actual existing-browser suite verifies intentional fresh entry/≈7.2s entrance pacing, held-key editable focus and blur/freeze recovery, map resize/projection/saved camera, actual movie-activation restoration/rapid restart, boundary Stay/hysteresis/return, navbarHome/reload/directURL/Back/Forward, touch entry/movement/map and reduced motion. These fixes were already present; they were **verified, not rewritten**. Public forward movement beneath the scaffold reachesAftermovie in the sameCanvas.

Opt-in browser tests additionally verify valid proxy raycast, wall persistence through directional travel, movie playback/Esc camera restore, boundary/map/history, real WebGL loss/recovery, failed optional GLB→original/retry, delayed optional load interrupted by native fallback→deterministic unpublished-resource disposal. A separate opt-in portrait test uses actual touch pad/release, saved-pose map open/close, touch map destination selection and boundary Stay in the same Canvas. Default critical stage-asset failure reaches native video fallback. Delayed crowd preparation can be interrupted by public return without stale reveal; context loss during playback preserves the original walking pose.

No current tested functional failure remains in these scoped checks. Real hidden-tab/device suspension and physical mobile/GPU performance remain unverified. Full all-eight-edge boundary coverage was not rerun as a new exhaustive browser matrix; existing boundary unit coverage and representative public browser paths passed. Initial own typecheck defects and capture/decimation trials are retained in raw logs, corrected rather than silently hidden. High-resolution capture metadata explicitly checks actualDPR1; the first failed DPR-override experiment is archived as a trial.

## 10. Actual visual evidence and assessment

Desktop/matched PNGs, mobile/touch-emulated390×844 frames, actual map and stage-look-back captures, camera position/yaw/pitch/quaternion/FOV, viewport/effectiveDPR/tier and visibleLOD are linked from the [gallery]({p}gallery.html). PNGs retain browser output resolution. Original-wall counterparts for close/medium/long/seam/portrait/map use the exact authored-camera metadata and assert matched pose/FOV/DPR; [counterpart metadata]({p}raw/counterpart-metadata.json). Close-ups/diagonal wall angles are inspection fixtures; ordinary Hub/tunnel-exit eye coordinates and public map captures are identified separately. The tunnel-exit camera is turned toward the east wall for inspection, not a change to the authored tunnel composition.

[Walkthrough]({p}recordings/{video}) is actual uninterrupted Playwright screen recording from a controlled valid Hub start followed by realW/A/S approach/pass/retreat. It remains inside current walking bounds and records automaticLOD2→1→2. Software rendering visibly stutters; the recording is excluded from FPS tests. It does not pretend the player can walk right up to this wall or that the cloud renderer is smooth.

| Visual criterion | Result | Evidence/remaining limitation |
|---|---|---|
| Approved default preservation |PASS|Original hashes/config; no public preview/asset requests|
| Single fitted face/no duplicate overlay |PASS|Three original triangles removed; fixed rim/inside-solid validation|
| Cool-grey body under unchanged Hub/stage lighting |PARTIAL for visual coherence|Approved family preserved; untouched actual blockout neighbors are a different treatment|
| Irregular geometry versus Stage2A |Improved; human review required|Unequal oblique joints/chips/recesses; fewer regular horizontal slabs|
| Finished geological realism |PARTIAL|Some smooth/sculpted regions, angular chip facets and crease highlights remain visible in the DPR1 close-up; reference rock has richer irregular fragmentation/mineral detail|
| Seam/terrain connection |PARTIAL|No measured gaps/outer silhouette change, but old straight pentagonal facet seams and material contrast can remain perceptible|
| LOD mechanics |PASS technically|One visible node, screen/DPR/FOV/tier policy+hysteresis, measured transitions; subtle popping needs physical high-DPR review|
| Fine maps/UVs |PASS technically/PARTIAL visually|Valid twoUVs; limited1024 maps can soften grain, repeating mineral normal tile needs high-DPR scrutiny|
| Stage/video identity |PASS|Original assets/code hashes and actual playback/recovery tests; no stage remodeling|
| Physical performance |PENDING|SwiftShader cannot certify laptop/phone budgets|

No global visual changes were made to hide these limitations. Neighboring procedural wall faces still expose blockout angularity and the selected pentagon's silhouette; solving every join by reshaping them would violate this milestone. Source/back surfaces inside the existing solid are technically closed, not claimed as separately finished production rock.

## 11. Files changed

{sourceTable}

New source/runtime assets live exclusively in `assets-source/gullyverse/first-wall-section/` and `public/models/gullyverse/first-wall-section/`. New evidence/scripts/docs live under this Stage2B report directory and this document. [Exact original-source patch]({p}raw/source-changes.patch) and [ending Git status]({p}raw/ending-git-status.txt) separate our changes from pre-existing untracked work. No dependency/library upgrade or production-data change occurred.

## 12. Preview and reversal

Development mode automatically permits the opt-in; local production review build requires **`NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`** at build time. Existing diagnostic inspection capture uses its separate **`NEXT_PUBLIC_GULLYVERSE_INSPECTION=1`** flag. No controls or asset appear without the query.

Open **`http://localhost:3000/?arrival=hub&wallPreview=limestone&diagnostics`** on the running local review server. Query values`authored`, `reference`, `off` are also supported. Original quarry restores the face immediately after covered preparation; Material baseline applies the same new map set to the original face for comparison. Remove the query/reload to restore the ordinary default. The existing coordinator may drop the authoring query while traveling; the current shell retains its preview, but reloading a URL without the query returns to default. No separate production route/destination is added.

## 13. Measured scaling plan and next decision

**Stop at this face for human geometry/material review.** Production-scale readiness is not established by one section. Physical profiles remain pending but do not require reopening Stage1 design approval.

1. Review the new fracture morphology, native-DPR detail and grey/body-to-blockout rim. Clarify the actual checkout's default-material discrepancy before any future approved public substitution; do not silently recolour or redesign the world.
2. Reproduce matched wall/Hub/stage/map tests on real integrated GPU/iPhone/Android using the supplied procedure; collect large enough windows/thermal sessions and trace stalls. Measure alongside original stage/crowd, not in an empty rock-only renderer.
3. Before expanding beyond a second small milestone, split reusable limestone normal/roughness families from per-section albedo/AO. Loading10 copies of today's combined file would cost roughly**28.1MB unencoded files /24.7MB measured loopback wire /120MiB estimated maps** plus geometry and the existing stage; such duplication is not an approved budget.
4. Provisional per-section targets from this pilot: **near20–25k/mid4–6k/far1–2k triangles; one material/visible draw; shared material family**. Treat these as experimental ceilings, not hardware-certified limits. Ten near sections would be215k visible triangles; ten distant sections17.2k. The current eager threeLOD residency is suitable for one reversible pilot, not future landing residency.
5. Add further unique sections gradually at existing non-critical anchors. Keep approved registry/outer silhouette/collision/tunnel/stage fixed; assess join quality and shared-family repetition before authoring the whole ring. Introduce camera-distance residency/preload only when measured and covered; don't preload a future high-poly quarry on landing.
6. Test compression separately only after loader configuration exists. Compare actual decode/upload/visual artifacts and target browsers; do not assumeDraco/Meshopt/KTX2 support or trade visible quality for the old2MB guess.

Remaining production-art work includes richer localized limestone breakup, high-resolution mineral/weathering refinement, consistent approved-family treatment at future joins and reviewed LOD fracture continuity. Final entrance/tunnel/graffiti/stall/population/stage-surroundings production has **not** begun. Whole-quarry replacement, permanent/default activation and deployment require later explicit approval.
'''
(root/'docs/gullyverse-stage-2b-first-wall-integration.md').write_text(text)
# Browsable evidence, all individual PNGs also retained in their original resolution.
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse Stage2B first wall review</title><style>body{background:#111818;color:#e5ebed;font:16px system-ui;max-width:1450px;margin:auto;padding:22px}a{color:#9dd1ed}img,video{max-width:100%;height:auto}figure{margin:20px 0}figcaption{padding:14px;background:#223035}.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,450px),1fr));gap:16px}details{margin:12px}pre{overflow:auto;font-size:12px}</style><h1>Stage2B — one opt-in limestone wall</h1><p>Actual browser captures. Approved production default retained. Geometry/material is for human review; physical-device performance pending. Some joins and sculpted detail remain provisional.</p><nav><a href="../../docs/gullyverse-stage-2b-first-wall-integration.md">Main report</a> · <a href="raw/test-summary.json">Tests</a> · <a href="raw/performance-lifecycle.json">Frames/resources</a> · <a href="raw/asset-inventory.json">Asset inventory</a> · <a href="raw/capture-metadata.json">Capture metadata</a> · <a href="raw/high-resolution-capture-metadata.json">DPR1 metadata</a> · <a href="PHYSICAL-DEVICE-PROCEDURE.md">Physical procedure</a></nav>']
for title,data in [('Matched/DPR0.5 and world context captures',meta),('Checked DPR1 detail / portrait aspect',high)]:
 parts.append('<h2>'+title+'</h2><div class="pair">')
 for row in data['captures']:
  d=row.get('before',row);f=row['file'];pose=d.get('camera',{});stats=d.get('stats',{});wall=d.get('wall',{});vp=d.get('viewport',{});caption=f"{Path(f).name} · {vp.get('width')}×{vp.get('height')} · effectiveDPR {stats.get('dpr')} · quality{d.get('snapshot',{}).get('quality')} · {('LOD'+str(wall.get('activeLOD'))) if wall.get('state',{}).get('mode')=='authored' else 'No visual LOD ('+str(wall.get('state',{}).get('mode'))+')'}"
  parts.append(f'<figure><a href="{f}"><img loading="lazy" src="{f}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}<details><summary>Camera/capture details</summary><pre>{html.escape(json.dumps({"camera":pose,"visibleLOD":wall.get("visible"),"viewport":vp,"method":row.get("method",title)},indent=2))}</pre></details></figcaption></figure>')
 parts.append('</div>')
parts.append(f'<h2>Actual browser approach / pass / retreat</h2><p>Controlled valid Hub start, then actual W/A/S. AutomaticLOD2→1→2. SwiftShader stutters. Near diagnostic images do not imply enlarged walking space.</p><video controls preload="metadata" src="recordings/{video}"></video><p><a href="recordings/{video}">Download recording</a> · <a href="raw/walkthrough.json">Pose/LOD trace</a></p><h2>Untouched starting baseline</h2><div class="pair">')
for f in sorted((r/'baseline').glob('*.png')):parts.append(f'<figure><a href="baseline/{f.name}"><img loading="lazy" src="baseline/{f.name}"></a><figcaption>{f.name}; captured before production edits. Camera/quality may differ from later matched fixtures; see baseline metadata.</figcaption></figure>')
parts.append('</div><h2>References, not matched captures</h2><p>Historical user-approved grey pilot and supplied morphology inspiration. No reference pixels are used in production maps.</p><div class="pair">')
for f in sorted((r/'references').iterdir()):parts.append(f'<figure><a href="references/{f.name}"><img loading="lazy" src="references/{f.name}"></a><figcaption>{f.name}</figcaption></figure>')
parts.append('<h2>Direct counterpart comparisons</h2><div class="pair">')
for c in counterparts['captures']:
 for f in [c['file'],c['matchedTo']]:parts.append(f'<figure><a href="{f}"><img loading="lazy" src="{f}"></a><figcaption>{html.escape(f)}; same recorded camera/FOV/DPR as paired frame.</figcaption></figure>')
parts.append('</div><p>Rejected soft/sharp/DPR trials remain under exploratory/ and raw trial metadata. They are not current acceptance captures.</p></html>');(r/'gallery.html').write_text('\n'.join(parts))
print('Report/gallery/test summary written',len(tests),'browser checks')
