from pathlib import Path
import json,datetime,statistics
O=Path(__file__).resolve().parents[1]
def get(n):return json.loads((O/'evidence'/n).read_text())
a=get('authoring.json');b=get('scene-budget.json');rows={r['variant']:r for r in b['sceneBudgets']};p=rows['C+A PILOT'];w=rows['C+A WORLD'];web=get('website-preservation.json');pres=get('preservation-audit.json');opts=get('options.json');vis=get('visibility-coverage.json');matched=get('matched-render-validation.json');shops=get('shop-geometry-stock-validation.json')
hid='WORLD-C-A-WIDER-REALISM-20261028-'+a['masterSHA256'][:8]
table='\n'.join(f"| {r['variant']} | {r['triangles']:,} | {r['meshAndConvertedCurveObjects']:,} | {r['materialDatablocks']} | {r['shaderNodes']} | {r['uniqueReferencedImages']} | {r['estimatedReferencedRGBA8MipMiB']:.2f} |"for r in b['sceneBudgets']if r['variant']in['C','C+A PILOT','C+A WORLD'])
optiontable='\n'.join(f"| {r['option']} | {r['description']} | {r['trianglesPerActor']} | {r['trianglesFor180']:,} | {r['partOwners']} |"for r in opts['measurements']if r['kind']=='crowd')
countertable='\n'.join(f"| {r['option']} | {r['description']} | {r['triangles']} | {r['owners']} |"for r in opts['measurements']if r['kind']=='counter')
coverage='\n'.join(f"| {r['pose']} | {r['newConstructionPercent']:.2f}% | {r['updatedSurfacePercent']:.2f}% | {r['silhouetteOccupancyPercent']:.2f}% |"for r in vis['rows']if r['variant']=='C+A WORLD')
pixels='\n'.join(f"| {r['pose']} | {100*r['fractionPixelsChangedOver12of255']:.2f}% |"for r in matched['pairs']if r['pose']in['01-lane-entry','02-whole-street','10-lane-roof-transition','11-rooftop-wide','17-rooftop-reverse','18-mobile-lane'])
blocked=[{'shop':r['shop'],'approach':v['side'],'hits':sorted({x['object']for x in v['errors']})}for r in shops['fiveShops']for v in r['doorwayRouteOptions']if v['status']!='PASS']
seconds=[r['seconds']for name in['render-before.json','render-after.json']for r in get(name)]
report=f"""# Gullyverse — selected C+A wider neighborhood realism

Handoff: {hid}

PRIVATE BLENDER CANDIDATE. USER VISUAL APPROVAL REQUIRED. Completed {datetime.datetime.now(datetime.timezone.utc).isoformat()}.

## Decision and scope

Architecture coverage: PASS. Technical preservation: PASS. Locked artwork/lights/crowd: PASS. Visual coherence: PARTIAL, ready for user review. Runtime readiness: NOT ESTABLISHED.

The six remaining shopfronts, upper street window hierarchy, lane finishes, wider rooftop and background construction now receive the selected C+A treatment. Wide renders show additional human-scale frames, shop returns, practical construction and surface hierarchy. The approved pilot remains a separate comparison. This is more developed art, not final photorealism.

Original people, cartons and counter cores remain simplified. Dark interiors with support OFF remain an accepted tradeoff. Crowd/counter alternatives are separate proposals, not replacements. No website or quarry/cave implementation is included.

## Exact baseline and preservation

Authenticated prior checkpoint source ZIP: 35,911,853 bytes, SHA-256 61784b6595d9dd9c9297078bea3c96b6c32c6e702f14c3bbdfbe329f2e507a10. Download and archive CRC verified before extraction. Approved packed pilot inside: 13,720,492 bytes, SHA-256 3ba2b0056a9cd12bc0fefaa9a503df0fe12539467d46a01c7fd0a91fa2124202.

New master: source/Gullyverse-Selected-C-Wider-Realism.blend

Bytes: {a['masterBytes']:,}

SHA-256: {a['masterSHA256']}

All {pres['originalObjectsExact']:,} prior object signatures, materials, images, transforms, UVs, actions and worlds remain exact. A/B/original C/approved pilot retain exact scene membership. A fifth scene, SELECTED C+A / Wider Neighborhood Realism, is added. The earlier corrugated-art master is preserved in the shared inputs.

Website branch work-in-progress-2027, HEAD e638140b37045a805b23b4d406d387a8870f8486; {web['protectedFiles']} protected hashes plus exact full dirty/untracked Git state unchanged. Other navigation-checkout Git state also unchanged. No source modification, install, build, git action, branch switch or deployment occurred.

## Implemented architecture

Additional bays: LEFT Y-7 and Y+2; RIGHT Y-25, Y-16, Y-7 and Y+2. Existing LEFT Y-25 open bay and LEFT Y-16 shutter pilot remain. Five cavities stay open, three artist shops stay closed with physical corrugated slats.

Tailored variants include returned steel opening sections, rolling-head housings, sign trays/stand-offs, 3/4/5 awning folds, drip edges, service enclosures/risers, narrow threshold finishes, curb returns and selected render repairs. No random rubbish scatter, new brand names, new artist art or repeated full cloned shop module.

All 32 street windows gain stepped side/head/sill construction, sash/mullions and selective grilles. Eight building crowns/slab edges gain hierarchy. Existing volumes, glazing positions and balcony footprints remain. Seven original background building masses gain restrained shared plaster treatment, window returns and floor bands. These are surface-built reveals, not newly excavated room cavities.

Roof work continues across remaining visitor-facing edges: shared concrete, jointed side/rear coping, mineral skirting, scuppers and external downpipes. The roof slab and walking floors retain physical shape. Six-millimetre shader joints use a 4.2 m cast interval with signed-safe FLOORED_MODULO sampling. No raised floor seams, route obstacle, reveal column, stage/truss or banner.

Four remaining shops' 144 exact cartons and 36 shelf boards gain shared generic print/wood finishes. All 225 stock objects keep position, bounds and rigid assembly relationships. Five counter cores remain exact; thin finish/worktop/edge overlays add construction. Major counter redesign is not applied.

{len(a['surfaceCopies'])} isolated surface copies; {a['partsBeforeStaticGrouping']} authored components grouped into {a['staticGroups']} spatial/material static meshes. Component dimensions, zones and source identities are recorded in authoring.json.

## Locked art, lighting and navigation

CHAAR DIWARI RIGHT Y-25, RITVIZ LEFT Y-16, NEHA KAKKAR RIGHT Y+2 retain exact source images, material graphs, colour/highlights, alpha projection, 54 slats/three backings and approximately 3 cm groove depth. Four approved supporting wall motifs retain exact source/projection/hosts/materials. No extra copies or covering geometry.

All 17 original C lights remain exact: 12 active and five optional interior supports at 0 W. Same world, fog, exposure, view transform and practical fixtures. No new light, helper fill, emission or sky adjustment.

Audience remains A176/B184/C180/pilot180/world180. No identity, foot coordinate, animation or density change. Team stays RIGHT, Events LEFT, navigation board centered, Aftermovie screen and route retained. Original cameras/actions and straight X=0 960-frame walk remain unchanged.

## Materials and provenance

No new images. Reuse packed CC0 Poly Haven Worn Plaster Wall (1.8 m native scan period) and Scuffed Cement (1.62 m), with the pilot's shared albedo/1K OpenGL normal/roughness maps. Source URLs, hashes, licences, derivation and approved artwork provenance are included in source/prior-pilot/materials and approved-art.

sRGB albedo; Non-Color normal/roughness; aligned world-metre UV sampling. Matte mineral finishes use restrained scan contrast; existing zinc/wood/steel resources are shared. No new displacement, large atlas, AO multiplication, photographic fake-shadow treatment or random polygon colour.

Existing stock print reuses one 512 px unbranded atlas. All 33 image owners remain packed and byte-identical. New texture transfer: 0 bytes. Added decoded image estimate: 0 MiB. New material graphs still add shader variants; R3F compatibility/performance is not claimed.

## Measured asset costs

| Scene | Triangles | Mesh/curve owners | Materials | Nodes | Images | RGBA8+mips MiB |
|---|---:|---:|---:|---:|---:|---:|
{table}

Delta from pilot: {w['triangles']-p['triangles']:,} triangles, {w['meshAndConvertedCurveObjects']-p['meshAndConvertedCurveObjects']} object owners, {w['materialDatablocks']-p['materialDatablocks']} net materials, {w['shaderNodes']-p['shaderNodes']} net shader nodes. Same 17/12 stored/active lights. Counts are evaluated Blender totals, not visible web draw calls, GLB bytes or VRAM. Packed .blend bytes include editorial/archival assets and are not runtime transfer.

## Matched visual evidence

22 matched pairs / 44 scene PNGs: desktop 1280x720 and mobile portrait 576x1024; actual EEVEE 16-sample renders. Pose, rotation, lens/sensor/clip, world, colour management, exposure, atmosphere and light energies match. No browser DPR applies to offline Blender.

Review includes lane entry, multiple new shop groups, open shop and doorway inspection, each artist shutter, straight roof transition, roof/screen/crowd, Team/Events, both painted returns, reverse view and material/stock close inspection. Contact sheet asks whether the whole walk is more like a believable Indian neighborhood while retaining C's night-time cypher energy.

Difference threshold below is max RGB channel >12/255. It measures visible change, not artistic quality.

| View | Pixels changed |
|---|---:|
{pixels}

Coarse 80x45 evaluated first-hit rays separately measure geometry/surface coverage, excluding haze.

| View | New construction | Updated surface | Silhouette occupancy |
|---|---:|---:|---:|
{coverage}

Large silhouettes deliberately remain close because original masses and routes are locked. The new hierarchy concerns construction and material response.

The complete 40-second route uses 120 actual frames sampled from original frames 1–960, encoded at 3 fps, 480x270, 8 samples. All original frames/poses/hashes are supplied. This is frame-linked offline inspection, not real-time gameplay or a 24 fps continuous render.

Still wall-clock render range {min(seconds):.2f}–{max(seconds):.2f} seconds, median {statistics.median(seconds):.2f}. Concurrent jobs and caches differ, so this is not a controlled runtime speed comparison. Browser FPS, physical laptop/mobile acceptance and GPU residency remain unmeasured.

## Separate crowd and counter proposals

source/Crowd-and-Counter-Proposals-Only.blend is separate from the world master. One original actor Audience 00_00 retains exact foot coordinate/yaw/height and source identity in each study.

| Crowd option | Treatment | Tris/actor | Tris for 180 | Current part owners |
|---|---|---:|---:|---:|
{optiontable}

0 is the original control. Three alternatives 1–3 test shading and tapered body silhouettes. They remain stylized, faceless mid-distance proxies, not finished human art. No full-crowd change or animation is applied. Future shared pose/apparel instances or merged actors could reduce owner counts. A hypothetical 12-bone skeleton's matrices alone cost 138,240 bytes for 180 actors, excluding all other runtime/animation cost.

| Counter option | Treatment | Triangles | Current owners |
|---|---|---:|---:|
{countertable}

Counter proposals retain the original 1 x 3.3 x 1.28 m envelope. Current world retains protected cores and only thin finishes. Structural replacements require separate approval.

## Technical validation and repairs

PASS: original four-scene signatures/membership, source hash, packed image hashes, seven art placements/projection, 17 original lights/five 0 W supports, crowd transforms/counts, counter/shelf/carton shape and camera/actions.

PASS: closed positive-volume selected detail; face area >1e-9; finite UV/normal/tangent data; normal dot tangent <1e-4; tangent length >0.999; unit handedness; original shutter profile/seam/depth checks. No numeric tolerance changed.

Two candidate ramp copies initially inherited degenerate UVs on generated Solidify side faces. Their evaluated Solidify output was baked identically and side/underside UVs correctly projected: exact evaluated vertex coordinates and faces remain unchanged. Original authoring objects/modifiers stay intact in archival scenes. Preservation audit evaluates each source in its actual scene; an inactive-scene fixture false failure is retained.

Planar caps on new metal cylinders were explicitly triangulated for tangent generation. No physical boundary or protected geometry changed. Failure logs are retained, not hidden.

PASS: four paint-host ray surveys, crowd body/body and body/prop triangle checks, five shop cavity/stock checks, all positive-Y approaches, strict routes and 960 walk frames per scene. Radius 0.35 m and floor tolerance 0.002 m unchanged. Board/screen/poster comparison is recorded in destination-sightlines.json.

Inherited restricted approaches: {json.dumps(blocked)}. These are the two documented negative-Y scooter-side failures. No scooter/counter moved and no threshold relaxed.

No glTF export, web install/build/typecheck, stage playback, browser context recovery or physical-device benchmark was performed: this task explicitly excludes website work. Website preservation is verified, not represented as newly rerun runtime acceptance.

## Runtime-aware proposals

Already implemented: shared image owners; grouped construction; bounded material families; no new lights. Near/mid/far planning, mobile image reductions and future crowd/stock instancing are in optimization-plan.json and budget-worksheet.csv.

Near: retain meaningful architectural/shutter silhouettes. Mid: bake thin saddles, seams and fixings while keeping window/awning/coping returns. Far: spatial/material chunks with signs/art preserved. None is a validated GLB/LOD implementation.

Reducing four shared 1K normal/roughness images to 512 would save approximately 16 MiB RGBA8+mips, requiring matched phone A/B. Artist maps remain untouched. No invented web budget or hardware FPS target. Existing thousands of owners still require actual runtime batching/preparation measurements in a separately approved phase.

## Honest limitations and next decision

New framing, roof construction and coherent finishes improve multiple-bay views, but crowd placeholders, simple counters/cartons, repeated window rhythms, surface-built reveals and dark interiors remain visible. Fine detail alone is not sufficient; the wide contact sheet and full walk are the acceptance evidence.

READY FOR USER REVIEW, not automatic wider rollout or web promotion. Review architecture and separate proposals before choosing a later bounded runtime-budget task. No new crowd/counter replacement, commit, push, merge, deploy or next phase is authorized by completion.

## Checkpoint and restoration

Started 27 October, resumed 28 October after the environment cleared temporary memory. The approved pilot was recovered from its verified Drive archive. No final new result existed before that restart. New scripts, masters and completed renders are now persistent; two interim source snapshots were uploaded and authenticated download-back verified during work.

Final complementary archives include actual source bytes, prior editable masters/material/art inputs/provenance, new masters, strict tests, reports, PDFs, 55 PNGs, original walk frames and clip. Extract all into one fresh directory; see RESTORE.md, file manifests and ARCHIVE-INDEX.json. Independent archive restore/reopen and complete download-back receipts are final sidecars. Old checkpoints remain untouched. Upload status is established by receipts, not this report alone.
"""
(O/'REPORT.md').write_text(report);(O/'checkpoint/HANDOFF-ID.txt').write_text(hid+'\n');print('REPORT_BUILT',hid,flush=True)
