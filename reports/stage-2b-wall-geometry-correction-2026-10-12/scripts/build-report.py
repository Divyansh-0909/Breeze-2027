from pathlib import Path
import json
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');raw=r/'raw';rel='../'+str(r)+'/'
def read(n):return json.loads((raw/n).read_text())
def link(label,n):return f'[{label}]({rel}{n})'
b=read('starting-state.json');pre=read('before-performance.json');post=read('after-performance.json');life=read('lifecycle.json');master=read('master-inspection.json');seams=read('scene-seam-validation.json');assets=read('asset-inventory.json');validation=read('geometry-material-validation.json');commands=read('browser-command-results.json');finalcommands=read('final-validation-commands.json');finalbrowser=read('final-candidate-browser-commands.json')
assert all(c['exitCode']==0 for c in commands+finalcommands+finalbrowser)
assert validation['status']=='PASS'
perf=[]
for old,new in zip(pre['windows'],post['windows']):
 stats=new['after']['stats'];oldstats=old['after']['stats'];perf.append(f"| {old['name']} | {old['FPS']:.2f} → {new['FPS']:.2f} | {old['p50']:.1f} → {new['p50']:.1f} | {old['p95']:.1f} → {new['p95']:.1f} | {old['p99']:.1f} → {new['p99']:.1f} | {oldstats['calls']} → {stats['calls']} | {oldstats['triangles']:,} → {stats['triangles']:,} |")
size={Path(g['file']).name:g['bytes']for g in assets['GLBs']};nearnew=post['windows'][0]['before']['wall']['trace'];nearold=pre['windows'][0]['before']['wall']['trace'];timings=[]
for label,trace in [('Previous',nearold),('Corrected',nearnew)]:
 timing={v['event']:v.get('ms')for v in trace};timings.append(f"| {label} | {timing['load-ready']:.1f} | {timing['parse-ready']:.1f} | {timing['texture-init']:.1f} | {timing['shader-compile']:.1f} | {timing['covered-ready']:.1f} |")
video=read('video-with-wall.json');vcounts=[(v['settled']['stats']['textures'],v['settled']['contexts'][0]['stats']['Texture']['active'])for v in video['cycles']];assert len(vcounts)==10
on=life['cycles'][0]['on'];retired=life['afterRetire'];baseline=life['baseline'];counter=lambda s:tuple(s['contexts'][0]['stats'][k]['active']for k in ['Texture','Buffer','Program']);walk=read('walkthrough.json');inspection=read('inspection-walkthrough.json');videos=[link('Public keyboard approach/retreat', 'recordings/'+Path(walk['recording']).name),link('Eye-height side inspection dolly','recordings/'+Path(inspection['recording']).name)]
tri={o['name']:o['triangles']for o in master['objects']};edges={o['name']:o['protectedOuterEdgeMaxSurfaceDeviationM']for o in master['objects']};texbytes=on['wall']['decodedTextureEstimate'];mapbefore=read('before-captures.json')['captures'][-1]['data'];mapafter=read('after-captures.json')['captures'][-1]['data'];preserved=read('preservation-check.json')
text=f'''# Gullyverse Stage 2B — one wall geometry correction

Date: 2026-10-12. **Material preserved; geometry candidate awaits visual approval.** The normal/default website retains its approved procedural quarry. No commit, push or deployment occurred. No other wall section, entrance, tunnel, stage, stall or population asset was replaced.

## Starting state and preservation

Branch **`{b['branch']}`**, HEAD **`{b['HEAD']}`**. The starting worktree already modified `AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx` and `rendering.tsx`; prior wall helpers, tests, Blender sources, runtime exports and reports were untracked. Nothing was reset, restored or cleaned. The snapshot status was recorded after creating this evidence directory, before production edits. {link('Exact initial status/diffs','raw/starting-state.json')} and {link('recoverable source/asset snapshot','backup/current-wall-candidate.tar.gz')}.

A 100-file hash comparison preserves **{len(preserved['unchanged'])} files exactly**, including the original stage/crowd/media assets, locked maps, old pilot sources/exports, world configuration and lighting sources. Six targeted runtime/test files differ from that starting snapshot. {link('Preservation check','raw/preservation-check.json')}; {link('task-only source patch','raw/task-source-changes.patch')}. This patch distinguishes this task from the existing dirty worktree.

Current dimensions, world anchors, global Hub/Aftermovie lighting, fog, exposure, navigation, movement polygons, camera compositions and map policy remain unchanged. `rendering.tsx` was not edited further. Existing payment/admin/forms/routes were untouched.

## Geometry and actual neighboring surfaces

The prior candidate replaced only the inward pentagonal face with an approximately 2 m deep capped panel. Its ends and join with the occluding procedural neighbors read as a flat applied patch.

The correction authors **one entire existing Rock 4 as a closed volume**. Its inward face wraps onto five original return faces; unequal geological units, finite branching fractures, localized chips and unequal recesses replace the former uniform depth. It carves inward within the original solid rather than expanding the quarry. Original 20 host corners and outer skyline edges are retained. The host's existing bounds are approximately **x 40.670–63.876, y −10.526–22.792, z −76.079–−50.220 m**. Its unchanged anchor is **[42.1893349, 6.4880474, −63.6718422]**.

Actual topology inspection identified the adjacent Rocks 3 and 5. Four local contact faces are replaced with fitted carved skins, retaining their original perimeter and original untextured material colors. Rock 3's visible intersection lies inside its face, beyond the shared corner edge; ray inspection exposed a remaining straight occluder, so its **narrow intersection band** is also carved. This changes the underlying joining surfaces, without adding camouflage boulders. Rear closures stay embedded in their existing original solids. All three closed components intentionally retain the original rocks' internal overlaps.

The preview removes **144 original vertices / 48 triangles**: host range 216–323 and contact ranges 126–134, 135–143, 351–359 and 378–386. Every unrelated source attribute is byte-exact. Removing these surfaces prevents a duplicate exposed procedural wall under the new geometry. There is no separate plane in front of the original face. The wall meets existing terrain by intersection; no ground, route or rubble system was changed.

Source: [author](../scripts/blender/author_corrected_wall_section.py), [geology](../scripts/blender/corrected_wall_geometry.py), [fitted contacts](../scripts/blender/corrected_wall_joins.py). {link('Actual original host topology','raw/host-topology.json')}; {link('visible contact ray investigation','raw/visible-joins.log')}.

## Locked limestone and UV treatment

**All eight original image-file hashes are unchanged. The approved glTF material JSON, three embedded image byte streams and decoded pixels match the prior candidate exactly.** Normal strength remains approximately **0.58**; metallic remains zero; approved roughness/normal/color maps remain intact. No global light, exposure, sky or fog adjustment was made. {link('Material/geometry validation','raw/geometry-material-validation.json')}.

UV changes are confined to fitting new geometry: adjacent faces unfold metrically; boundary UVs reflect into existing interior texels to avoid the old image's edge termination. Central body UVs remain unchanged; the existing **12 × 10 m** fine normal coordinates retain grain scale. The limestone has not been repainted. Original green host/contact material remains on retained exterior surfaces, which still contrasts visibly with the authored limestone.

Runtime maps remain one 1024² JPEG base color, one 1024² PNG normal and one 512² PNG packed AO/roughness/metalness. They share approximately **{texbytes/1048576:.1f} MiB** decoded RGBA-plus-mipmap payload by estimate, not measured driver VRAM. No new texture set or compression/loader requirement was introduced.

## Blender, glTF, LOD and collision validation

Editable [master](../assets-source/gullyverse/first-wall-corrected/first-wall-corrected.blend), packed [material-only library](../assets-source/gullyverse/first-wall-corrected/approved-limestone-material.blend), [reproducible author/export instructions](../assets-source/gullyverse/first-wall-corrected/README.md), [anchor/material manifest](../public/models/gullyverse/first-wall-corrected/manifest.json).

| Asset | Triangles | Export bytes |
|---|---:|---:|
| Editable master | {tri['Wall_Master']:,} | .blend {assets['master']['bytes']:,} |
| Near LOD0 | {tri['Wall_LOD0']:,} | {size['wall-lod0.glb']:,} |
| Middle LOD1 | {tri['Wall_LOD1']:,} | {size['wall-lod1.glb']:,} |
| Far LOD2 | {tri['Wall_LOD2']:,} | {size['wall-lod2.glb']:,} |
| Compound original-solid proxy | {tri['Wall_Collision']:,} | {size['wall-collision.glb']:,} |
| Combined runtime GLB | Three visual alternatives plus hidden proxy | {size['first-wall-corrected.glb']:,} |

Blender **4.3.2**, metre units, identity object transforms, Blender Z-up → glTF Y-up. All source/master/LOD/proxy meshes are closed with **zero non-manifold edges and positive signed volume**. Exported visual meshes also pass exact-position welded topology checks across material/UV seams: no open/non-manifold edges, consistent winding and positive volume for each closed component. Five GLBs pass Khronos Validator **2.0.0-dev.3.10**, **zero errors and warnings**. Informational notices concern unused UV/tangent attributes on untextured retained-color primitives. Textured limestone normals/tangents and both UV sets are validated; unused green tangents do not drive a normal map. {link('Master inspection','raw/master-inspection.json')}, {link('exported topology','raw/exported-topology-validation.json')}, {link('glTF validation','raw/glTF-validator.json')}, {link('inventory','raw/asset-inventory.json')}.

Only one LOD root renders at a time. Each contains three material primitives, not overlapping visible LODs. Existing projected-pixel thresholds, adaptive quality scaling and hysteresis are retained; new bounds cover the visible limestone. All alternatives warm sequentially under cover, share maps, and are frustum culled after preparation. Collision is a separate hidden **108-triangle original-solid proxy**, verified by browser raycast; existing walking polygons remain authoritative.

Outer host-edge deviation after decimation is at most **{max(edges[f'Wall_LOD{i}']for i in range(3))*1000:.2f} mm** in sampled tests. Contact perimeters have measured LOD-dependent deviations up to **{max(x['contactPerimeterMaxDeviationM']for x in seams['contactPerimeters'])*1000:.2f} mm**; this is not a mathematical guarantee of perfectly welded neighbors. Actual assembled scene BVH tests found zero newly uncovered old wall hits in sampled Hub, long and stage views. Two rays at the top border of the close inspection reveal sky after local carving. {link('Seam/ray measurements','raw/scene-seam-validation.json')}. Browser inspection did not show flickering duplicate faces; this does not prove all possible angles free of intersections.

## Browser evidence and visual verdict

{link('Before/after browsable gallery','gallery.html')} contains original-resolution PNGs at identical cameras: front, close, left/right diagonals, top/bottom, adjacent formations, Hub, long quarry view and public aerial map. Desktop viewport **1366 × 900**, near views effective DPR **1**, FOV **58°**, quality **0**. Public map uses its existing camera (about y **165.934 m**, FOV **64°**, DPR **0.6**) in both versions. Additional actual LOD0/1/2 and **390 × 844 portrait** views record their effective DPR, quality and responsive FOV. Metadata: {link('before','raw/before-captures.json')}, {link('after','raw/after-captures.json')}, {link('LOD/mobile','raw/extra-captures.json')}.

Recordings: {'; '.join(videos)}. Public W/A/S movement stays inside unchanged Hub bounds and records automatic LOD changes. The wall is outside the existing close-access walking zone; the second recording is explicitly a **diagnostic eye-height camera dolly**, not normal player walking or changed camera configuration. Recordings use the real browser renderer and are excluded from performance windows.

**Geometry/integration visual verdict: PARTIAL, pending review.** Depth and geological returns improve the rejected panel. Unequal edges and local contact carving reduce its straight termination. Some close-up chips remain triangular/saw-toothed; some broad units still read as block-like. The untouched green blockout neighbors and material transitions remain conspicuous from certain views. This is not photorealism, and the stricter requirement that no artificial patch can be perceived from every ordinary view is not proven. Do not scale this candidate across the quarry before human review.

## Matched software-renderer comparison

Debian 13 cloud VM; **3 AMD EPYC virtual CPUs**, Chromium **151**, ANGLE **SwiftShader Vulkan software rendering**. No accessible physical GPU, iPhone or Android device. Physical desktop/mobile acceptance remains **UNVERIFIED**. {link('Hardware profile','raw/hardware.json')}.

Same localhost production setup, **1366 × 900**, effective DPR **0.5**, quality **0**, three fixed matched camera windows of 10 seconds, no recording or CPU/network throttling. Raw animation-frame samples are bounded by window start/end. FPS is counted frames / observed duration; quantiles use sorted actual frame intervals. These are small software-renderer samples, not sustained hardware or walking benchmarks.

| View | FPS before → after | p50 ms | p95 ms | p99 ms | Draw calls | Visible triangles |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(perf)}

Old combined asset **2,812,828 bytes** versus **{size['first-wall-corrected.glb']:,} bytes** corrected. Texture count remains **28** in matched active views; settled geometry count is **146 → 152**, explained by six additional material primitives across the three LODs. Corrected geometry deliberately costs more triangles and two extra calls in these views. Any observed software FPS improvement is not a certified speedup; scheduling, coverage and warm-up affect these single samples. Raw: {link('before performance','raw/before-performance.json')}, {link('after performance','raw/after-performance.json')}.

| First optional preparation | Load-ready ms | Parse/decode ms | Texture init CPU ms | Compile promise ms | Covered warm ms |
|---|---:|---:|---:|---:|---:|
{chr(10).join(timings)}

Load-ready includes local delivery and parse; compile promise is not GPU execution timing; covered preparation includes multiple hidden renders and software scheduling. No GPU timer/driver VRAM measurement was available. Whole-site cold transfer was not re-benchmarked; the default path is verified to request neither candidate GLB. Full uncompressed optional payload is the combined GLB size above.

## Ownership, tests and preserved interactions

The optional session owns a bounded GLTF cache. Clones borrow its geometries/materials; no shared stage/cache eviction occurs. Ten final preview off/on cycles plateau at **{on['stats']['textures']} textures / {on['stats']['geometries']} geometries** and GL texture/buffer/program proxies **{counter(on)}**. Cache retirement returns to original **{retired['stats']['textures']} textures / {retired['stats']['geometries']} geometries**, GL proxies **{counter(retired)}**, matching original **{counter(baseline)}**. Off alone intentionally retains the reusable cache. Heap samples are included, without forced collection or a leak-free JS-heap claim. {link('Lifecycle results','raw/lifecycle.json')}.

Ten movie/exit cycles with the corrected runtime and preview changes during playback plateau at **{vcounts[0][0]} Three textures / {vcounts[0][1]} tracked GL textures**, with restored activation pose. This suite ran before the final localized contact-band carve; rendering code, material ownership and video code were unchanged by that geometry-only refinement. Final preview cycles, GLB/mesh checks, recordings and matched measurements were rerun afterward. {link('Playback results','raw/video-with-wall.json')}.

* `npx tsc --noEmit`: PASS. `npm run test:immersive`: **62/62 PASS**, including a new test proving the host/contact cut leaves all unrelated quarry attributes exact.
* `npm run lint`: PASS with repository warnings; none reported in the six modified runtime/test files. Production `npm run build`: PASS, rerun against final manifest/assets. Builds use inert local Supabase placeholders and opt-in preview/inspection flags; environment files are not edited and production data is not accessed.
* Existing browser suite: all eight groups PASS: deliberate entrance/tunnel, editable focus release, blur/visibility, map/projection/resize, playback restoration, boundary/hysteresis, Home/direct/history and touch/reduced motion.
* Corrected opt-in checks: seven PASS: proxy raycast, directional stage travel/same Canvas, movie/Escape, boundary/map/history, context recovery, failed optional GLB retry and abandoned load disposal. Additional default critical-asset fallback, delayed stage navigation interruption and context loss during playback PASS. Portrait touch pad/map/boundary PASS.

{link('Browser command journal','raw/browser-command-results.json')}; {link('final candidate reruns','raw/final-candidate-browser-commands.json')}; {link('final validation/build commands','raw/final-validation-commands.json')}; {link('unit log','raw/unit-final.log')}; {link('typecheck','raw/typecheck-final.log')}; {link('lint','raw/lint-final.log')}; {link('build','raw/final-build.log')}; {link('opt-in results','raw/opt-in-regressions.json')}; {link('touch','raw/touch-optin.json')}; {link('loading interruption','raw/interruption.json')}; {link('production default/fallback','raw/production-smoke.json')}.

Early authoring trials and one serialization failure are retained in raw/trials, clearly excluded from final acceptance. The initial right inspection fixture was inside an existing neighboring rock; it was repaired to an outside pose and both candidate captures were repeated. No test assertion was weakened to accept application failures.

## Exact source changes and stop

| File | Purpose |
|---|---|
| `components/immersive/wallSection.ts` | Corrected/previous URLs, full-host/local-contact removal, fit validation; existing cache ownership retained |
| `components/immersive/QuarryWallSection.tsx` | Group-based multi-material LOD roots, approved material discovery and sequential covered warm-up |
| `components/immersive/HubScene.tsx` | Select original/face/volume geometry copy only |
| `components/immersive/AftermovieScene.tsx` | Pass replacement mode; stage JSX/assets unchanged |
| `components/immersive/ImmersiveShell.tsx` | Explicit previous-candidate opt-in for matched comparisons |
| `tests/immersive/wall-section.test.ts` | One additional exact preservation regression test |

New files are the three authoring scripts, corrected source/export directory, this report, and evidence/reproduction scripts under `{r}`. Original candidate, texture files and prior reports are intact.

Preview: `/?diagnostics&wallPreview=limestone`; preserved previous: add `&wallCandidate=previous`. Local production review builds require `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`; ordinary URLs show the original approved quarry. The preview's **Original quarry** button restores it immediately.

**Stop here for visual approval.** Remaining work is review of fracture/chip quality, limestone-to-blockout continuity and LOD seam visibility on a physical GPU. No further section is authorized. Keep shared materials and measured per-section LOD limits when considering scaling; three more primitives per distant segment and high-detail stage/crowd residency must be budgeted together. This pilot does not establish a full-quarry capacity or physical 60 FPS guarantee. The self-contained review ZIP contains the report, PNGs, metadata, recordings, final source/exports and reproducible authoring inputs, without credentials or unrelated application data.
'''
Path('docs/gullyverse-stage-2b-wall-geometry-correction.md').write_text(text)
print('Report words',len(text.split()))
