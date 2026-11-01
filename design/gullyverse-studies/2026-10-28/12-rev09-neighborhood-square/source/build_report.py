from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parents[1]
def read(n):return json.loads((O/'evidence'/n).read_text())
a=read('authoring.json');p=read('preservation-audit.json');g=read('house-geometry-and-coverage.json');b=read('budget.json');floor=read('open-floor-comparison.json');layout=read('layout-validation.json');web=read('website-preservation.json');budget={r['variant']:r for r in b['rows']};m=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend';sha=hashlib.sha256(m.read_bytes()).hexdigest();photos=len(list((O/'renders/after').glob('*.png')));walk=len(list((O/'renders/walk').glob('*.png')))
text=f'''# Rev09 — Multi-storey neighborhood square with the previous C180 crowd

Handoff: WORLD-REV09-SQUARE-C180-20261028-3f637b22

Private Blender implementation. User visual approval is pending. USER-SELECTED CROWD = EXACT PRIOR BLENDER C180. Real steel rack/table identity remains PENDING. No website integration or production acceptance is implied.

## Exact baseline and approved direction

The latest green manual prompt was read from the shared Google Doc after the user explicitly approved implementation. It is archived in source/APPROVED-PROMPT.txt. Its review heading is dated 29 October; execution timestamps and folder dates use the workspace's observed UTC date, 28 October 2026.

Authentic Rev08 master: SHA-256 f130611ac54090baf6e25052c222b53a5a243414e1e49686bc1882dc3d6f7f50, 14,829,066 bytes. It was downloaded again through authenticated Drive access and verified against that full hash before further work. New scenes clone REV08 I / TERRACE ARCH, which contains the exact earlier Blender crowd. Rev08 II and its exact website Man/Woman import remain historical; they are not the selected design.

Protected website branch {web['branch']}, HEAD {web['HEAD']}. All 1,213 protected hashes and exact starting staged/unstaged/untracked state remain unchanged, as does the other navigation checkout. No website edit, dependency install, server, build, git mutation, commit, push, merge or deployment occurred.

## Architecture: a square defined by inhabited housing

The main gathering slab is still the original 32 × 34 m rectangle at Z7.2 m (aspect ratio .941), with the same screen, board, Team RIGHT, Events LEFT, media/DJ point, audience and lane route. It is now bordered by {len(a['houses'])} individually composed houses: four on each side, five across the far edge and two entrance wings. The wings frame, rather than close, the original 16.6 m entrance opening; the new house bodies leave 17.2 m clear between themselves. The central floor remains open to sky. No central building, stage, ceiling, banner, truss, reveal column or detour was added.

Courtyard-facing houses have 2–5 apparent residential storeys at 3.1 m floor spacing, with main roof slabs ranging from Z{g['mainRoofZRange'][0]:.2f} to Z{g['mainRoofZRange'][1]:.2f} m. Two lower podium/storey levels below the courtyard datum explain their support from the exterior. Apparent courtyard storeys and total exterior height are distinct; this is a visual architectural model, not a structural engineering approval.

The inward frontages are real thick walls partitioned around doors/windows, with physical jambs, lintels, sills and recessed glazing. Floor slabs, return/party walls, balconies with rails/balusters, projecting chhajjas, opening timber shutters, door hardware, plinths and roof parapets provide human-scale depth. Roof access rooms, tanks/plinths/ribs, compressors/brackets, rainwater pipes/clamps and facade service wires give the perimeter residential purpose. Heights, frontage widths, setbacks, door/window bay counts, balcony positions and plaster families vary deliberately; no uniform superblock grid was substituted for the old blocks.

The previous five large venue-side/back neighbor blocks and their associated window/frame detail are unlinked ONLY from the selected new scene, along with small Rev08 service-room/headhouse groups and long side parapet/coping groups replaced by housing. Their original objects, meshes, materials and all eleven Rev08 scene memberships remain intact. The upgraded lane, structural roof/decks below the unchanged main floor, entry art returns and all protected destinations stay. The exact replacement list is in evidence/authoring.json.

{len(a['parts']):,} authored architectural components are grouped into {len(a['newConstruction'])} spatial/material meshes. New podium bodies reach the first-floor slab continuously; an initial support-joint clearance was corrected before final source sealing. All final captures and the final archive use master hash {sha}. The initial unapproved safety master remains an explicitly superseded Drive snapshot, not a final restore input.

## Perimeter coverage and open floor

House frontage covers {g['houseCoveredPerimeterM']:.2f} m of {g['eligiblePerimeterExcludingEntranceM']:.2f} m eligible perimeter, or {g['perimeterCoveragePercentExcludingEntrance']:.2f}%, excluding the original 16.6 m entry. This is the union of actual authored inward-frontage intervals projected onto the original rectangle. It does not count thin parapets, service sheds or distant blocks as residential enclosure. It is not a claim that every facade is visible from every viewpoint or that the remaining seam/gap length is solidly enclosed.

The original reference floor is 1,088 m². No part of its geometry, UVs, datum or authoritative route was changed; no new ground-level house solid enters it. Projecting balconies are above visitor head clearance. The separate .5 m grid survey includes original crowd/props and uses .35 m horizontal clearances at .8/1.72 m height: zero previously clear cells become blocked. Baseline {floor['rows'][0]['clearCells']} clear cells versus new {floor['rows'][1]['clearCells']} is a diagnostic occupancy estimate over {floor['sampledCenterGridAreaM2']:.2f} m², not newly authorized walking space or regulatory access certification. The authoritative movement registry remains untouched.

## Previous crowd restored exactly — aesthetic decision first

All 180 original Blender spectators and their 1,440 body-part objects are the same source objects used in the C/wider C+A/Rev08 architecture-only variants. Source object/mesh/UV/material/action hashes, feet, width/height scale, yaw, filled center, asymmetric wings and sparse board observers match exactly. No alternate 8/12-sided prototype, new population generation, new density or website baked actor enters the selected scene. Separate non-audience sparse figures remain unchanged.

The original crowd is 54,000 triangles; the historical imported website crowd is 639,792. The user's style preference, rather than that cost difference alone, determines selection. CONTROL 1 is Rev08 architecture + previous crowd; CONTROL 2 is the same Rev08 architecture + website crowd, labelled HISTORICAL/NOT SELECTED. The NEW scene is the square + original crowd. These controls keep architecture and crowd changes separate.

## Materials, colour, lighting and provenance

The reviewed mineral concrete, worn lime/plaster, muted sage/ochre, roof concrete, zinc, timber/frame and dusty glass materials are reused. All 33 existing image owners are shared/packed; no additional atlas, texture download, AI mural, branding or invented artist artwork is introduced. Existing Poly Haven scuffed_cement/worn_plaster_wall provenance is retained under source/material-provenance and in the original packed master.

Two small material variants provide non-emissive amber-tinted window glass and muted green timber window shutters. No new emissive window response or physical support light is adopted. All 17 original light owners, 12 active and five optional interior supports at exactly 0 W, plus world, exposure, fog and view transform remain exact. Upper windows are intentionally subdued. Greater occupied-window glow would be a separate lighting comparison requiring later approval, not a hidden fill here.

The three exact supplied artist paintings retain their 54 physical shutter slats, approximately .03 m groove relief, .001 m seams, source colours, alpha and projection at Chaar Diwari RIGHT Y-25, Ritviz LEFT Y-16 and Neha Kakkar RIGHT Y+2. All four supporting wall motifs and their original lane-pier/return hosts remain exact. Matched return and named-shutter renders are supplied to expose any physical shading change from the new neighborhood, rather than moving or repainting art.

## Real steel rack/table source: pending, no guessed adoption

The bounded read-only recheck still finds active Trusses.tsx box-truss frames, Barricades.tsx crowd barriers and steel-trimmed stage road cases, plus the dormant timber/cloth festival-stall table. None is declared the user's intended standalone steel rack/table. The archival cloth table and old invented counter are not adopted. All five original shop counters and current media props stay unchanged. A concise screenshot/source inventory and an exact page/section/object clarification request are provided in FURNITURE-SOURCE-STATUS.md. That question does not block this square/crowd implementation.

## Geometry, route and preservation validation

- {p['originalObjectSignaturesExact']:,} prior object signatures and all eleven source scene memberships/settings remain exact. Thirteen total scenes: eleven archives plus isolated comparison copy and selected new scene. Old files are not overwritten.
- {len(a['newConstruction'])} new architectural meshes: closed manifold components, positive signed volume, face area >1e-9 m², finite UV/normal/tangent data, normal/tangent dot <1e-4, tangent length >.999 and valid handedness. Tolerances unchanged.
- Original actor body/body and body/architecture intersections pass. Exact crowd identity and placement is separately recorded; no crowd movement masks collisions.
- 960 original straight camera-action frames per applicable scene, floor tolerance .002 m and .35 m capsule checks are run without altered thresholds. The saved 40 s X=0 action remains exact. The source-audit-only display scene remains outside walking-survey scope.
- All three 18-slat shutters and four supporting paint hosts pass geometry, mapping and ray tests. Five open shop cavities/shelves/cartons/counter bases remain exact; positive-Y shop approaches pass.
- The same two inherited negative-Y scooter approaches remain BLOCKED (left Y+2, right Y-7). No scooter or counter was moved to conceal them.
- Screen, board, Team and Events first-hit ray comparisons show no new sampled occlusion. Early screen reading is maintained through the same direct route.
- Master reopen verifies the selected old C180, zero website actors in the selected scene, all 13 scenes, 33 packed images and no external-font dependency.
- Website typecheck/build/browser/FPS testing is NOT RUN because no website work, build or server is authorized. No real-device result is inferred from offline rendering.

An overly concurrent offline render/test attempt hit the cloud's 8 GiB process memory budget and interrupted one final route recheck. Captures were serialized and the unchanged route test rerun. Initial interruption logs and final results are retained; this is an authoring-resource limit, not a measured website-memory or physical-device performance result.

## Measured budget

Counts include evaluated font geometry consistently, and are Blender counts, not measured browser draws.

| Variant | Triangles | Mesh/curve owners | Materials | Shared images | RGBA8+mips estimate |
|---|---:|---:|---:|---:|---:|
'''
for key in['TERRACE ARCH','TERRACE WEB CROWD','SQUARE C180']:
 r=budget[key];text+=f"| {key} | {r['triangles']:,} | {r['meshCurveOwners']:,} | {r['materials']} | {r['imageOwners']} | {r['RGBA8PlusMipsMiBEstimate']:.2f} MiB |\n"
text+=f'''
Architecture impact against the correct old-crowd control is {budget['SQUARE C180']['triangles']-budget['TERRACE ARCH']['triangles']:,} triangles net, not the crowd-style saving against Rev08 II. Image residency estimate remains unchanged at 138.53 MiB conservative RGBA8+mips; actual GPU residency is unmeasured. Static house grouping, repeated geometry families and shared materials provide bounded future batching/LOD opportunities. No glTF export, loader compatibility, runtime draws/FPS/VRAM, laptop or phone acceptance is claimed. Future runtime work must export the selected scene only, not ship all thirteen archival/editorial scenes.

Final master: {m.stat().st_size:,} bytes, SHA-256 {sha}. All required editable sources, exact original baseline masters and packed maps are checkpointed. No new complete-world runtime GLB exists.

## Real-render evidence and honest art assessment

Nineteen matched before/after viewpoints include the top plan, aerial, front entry/screen, reverse, both lateral diagonals, two facade close-ups, Team/Events, exterior elevation, both return artworks, two portrait compositions and all three artist shutters. The paired top plan uses 91 m horizontal orthographic framing to include the full house envelope; its render-time camera override is recorded explicitly without resaving the sealed master. Same camera pose/lens/viewport, EEVEE 16 samples, exposure/world and support OFF. Historical website-crowd controls are separate. These are actual OFFLINE BLENDER images, not generated concept art or fresh website screenshots. Final captured evidence: {photos}/19 selected stills; {walk}/80 final route frames. Final capture completeness and per-image SHA-256 are verified separately before handoff.

The full original 40 s route is an actual sampled offline inspection over source frames 1–960: 80 frames, 480×270 / two samples, encoded at 2 fps. The sampling is deliberately coarse and is not gameplay FPS. Full-resolution stills remain available separately.

The built mass now reads as a neighborhood square: close multi-storey faces define the left/right/back and entrance wings, while the familiar crowd and central gathering floor remain intact. Recesses, balcony thickness, shutters and services are recognisable at normal review distances. Final visual acceptance belongs to the user. Remaining limits include simplified/unfurnished house interiors, some surface-mounted lane-facing end-window details, repeated construction grammar, muted occupied-window cues, broad outer/podium surfaces and low-sample walk grain. No photorealism or final production claim is made.

Main question for review: does this now read as the open rooftop CHOWK/community courtyard, ringed by inhabited multi-storey houses, with the same preferred crowd gathering around the existing Aftermovie screen?

## Delivery / stop

The phone PDF, full-resolution gallery, technical evidence, offline clip and all editable source are in the new Rev09 Drive hierarchy. Final authenticated download-back SHA-256/parent/size checks and a fresh extraction/reopen are recorded in the final receipt, after uploads complete. The protected Rev08 master and original website remain unchanged. Use RESTORE.md and the numbered archive index; an interim safety snapshot is not a final restore input.

Stop for user visual approval of this square and the restored C180. Steel furniture identity remains pending. No automatic next phase or website integration; check the shared document only when the user messages.
'''
(O/'REPORT.md').write_text(text);print('REPORT_WRITTEN',sha,photos,walk)
