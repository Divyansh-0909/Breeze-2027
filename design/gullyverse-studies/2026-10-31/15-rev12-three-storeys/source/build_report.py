import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];q=json.loads((O/'evidence/storey-qa.json').read_text());a=json.loads((O/'evidence/authoring.json').read_text());b=json.loads((O/'evidence/budget.json').read_text());p=json.loads((O/'evidence/preservation-geometry.json').read_text());tests=json.loads((O/'evidence/tests.json').read_text());head=json.loads((O/'evidence/head-top-stature.json').read_text());old,new=b['rows'];order=['F1','L1','L2','L3','B1','B2','B3','R3','R2','R1','F2']
table=['|Parcel|Rev11 upper levels|Rev12 actual / public-visible|Physical floor tops Z (m)|Roof Z (m)|','|---|---:|---:|---|---:|']
for key in order:
 r=next(r for r in q['rows']if r['parcel']==key);table.append(f"|{key}|{r['beforeUpperResidentialCount']}|{r['actualIndependentSlabCount']} / {r['visibleLevelsFromPublicPositions']}|{', '.join(f'{z:.1f}'for z in r['actualSlabTopZs'])}|{r['mainRoofZ']:.2f}|")
text=f'''# Rev12 — three to five real upper storeys on all eleven connected houses

Private Blender proposal, 31 October 2026 UTC. Handoff WORLD-REV12-THREE-PLUS-STOREYS-20261031-{b['masterSHA256'][:8]}-R1. READY FOR USER VISUAL REVIEW; no final architecture or stature approval inferred.

## Result and baseline

All eleven perimeter houses now have at least three actual occupied-looking storeys above the protected Z7.2m courtyard, varying 3/4/5. The independent pre-remodelling audit found eight houses below three; counts rose from 22 to 45 upper residential floors in total. Foundation/podium levels at Z0.6/3.9 and every secondary roof stair headhouse are excluded. Physical upward-facing slab surfaces were independently counted by downward rays through rooms opposite the stair cores. This is not a count inferred from painted bands or object names.

Authentic input is Rev11 20,471,503 bytes, SHA256 b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd, freshly authenticated from Drive before authoring. Packed output is {b['masterBytes']:,} bytes, SHA256 {b['masterSHA256']}. Nineteen historical scenes, including the exact A/B and H00/H06/H07/H09 controls, remain intact; one new scene, REV12 / Three-to-Five Real Upper Storeys, makes twenty. Original 10,086 object signatures and all original memberships/materials/worlds/images are exact. Input master was never resaved.

Protected WIP repository remains work-in-progress-2027 at e638140b37045a805b23b4d406d387a8870f8486. Navigation repository remains codex/navigation-board at 14f36da1a9b79a3b4926f7445bf0cde6c6c8f767. All 1,213 protected hashes and both complete dirty/untracked Git states are unchanged. No website install, server, build, browser run, export integration, Git mutation, public promotion or deployment occurred. This deliberately follows the approved Blender-only scope.

## Eleven-house schedule

{chr(10).join(table)}

All rows PASS >=3. Numeric CSV: evidence/11-parcel-storey-schedule.csv. Complete per-level aperture and stair data: evidence/authoring.json. Public visibility: evidence/storey-qa.json.

Each qualifying level has at least two first-hit facade-band samples visible from validated original public walking positions at Z8.92m. Ray hit must be the structural shell within 0.03m of the authored facade target. Public capsule radius remains 0.35m. This is a union of valid walking views: it does not claim every floor of every house is visible simultaneously from the single front camera. The fixed 8.84×5.98m screen and 14.56m overall media span still mask lower rear floors. The front/night image shows side housing and upper floors above the screen; a separately labelled screen-hidden diagnostic reveals the actual structure behind it.

## Actual construction and junction repair

All upper pitches are 3.0m. Upper walls, 0.20m structural slabs, actual wall openings, 0.30m end returns, thick jambs/sills, projecting chajjas and selective 1.5m supported galleries create inhabited-looking levels. Setbacks vary by parcel and storey; main roof elevations vary 16.42/19.42/22.42m. Main roof slab thickness is 0.22m and guards about 1.05m. Nominal main door apertures are 2.10m (~2.06m below trim). Window sill offsets are 0.90m; nominal opening widths vary 1.28/1.50/1.66m. Intermediate non-gallery upper openings are windows; selected upper doors have supported balconies, avoiding doors onto empty air.

Every house has a genuine 2.2m-wide double-return stair well, 16 rises per storey, upper rise 0.1875m, 0.25m treads, 1.1m flights, 0.75m landings, actual holes through intermediate and roof slabs, and a secondary roof stair headhouse. These are plausible nonpublic circulation features, not building-code/accessibility certification. All roof headhouses are excluded from residential floor counts. Tanks, pipes, drying cloth and weathered roof details remain secondary.

Structural construction is an exact exposed-surface extraction from deliberately dimensioned orthogonal architectural volumes. It is not the rejected procedural quarry-rock generation or Boolean rock-union pipeline. Shared internal planes are removed. One closed manifold primary shell is vertex-connected ({p['coreVertexComponents'][0]:,} vertices in its component). New details are batched by parcel/material; all new meshes have positive signed volume, no zero-area faces, finite UVs and valid tangent frames at unchanged thresholds.

Two specific authoring defects were caught rather than waived: six edge-only contacts from staggered 3.0/3.05/3.1m slabs were repaired by aligned floor datums; an upper L-corner contact then required actual continuous 0.60m registered bearing walls across the original ten joins. All ten joins are now checked at multiple heights through the common house body, not only touching footprint rectangles. All original gaps remain zero. The two shallow entrance wings use smaller upper setbacks to retain at least a 1.0m internal stair-front apron; this is separately asserted in the author and independent storey QA. No shell tolerance was relaxed and no decorative prop hides a joint. Roof height steps retain open sky above the lower house.

The original 16.6m lane entry, 32×34m /1,088m² courtyard at Z7.2, authoritative floor and 40-second X=0 choreography remain exact. No new spectator, prop, balcony or wall is placed into the required center route. Six old rear lightwell floor-edge openings remain separately reported below; structural house connection does not mean a sealed rear service terrace.

## Crowd, lighting and artwork locks

The new scene directly shares the same 180 original C180 actor identities /1,440 object parts with Rev11 H07. Feet, XY footprints, yaw, styling, UVs, material ownership and existing 1.07 world-Z height factor are unchanged. No additional 7% scale was applied. The original height/+6/+9 comparisons remain exact historical scenes. Existing head-top proxy median is 1.696m original /1.815m at +7%; posed full envelopes have medians 1.780/1.905m and may include raised arms. A separately labelled real 1.700m unraised-arm source figure and door/storey ruler demonstrate scale. Stature remains a proposal for user review.

Original seven art compositions, three artist shutters with 54 physical slats plus four non-name wall motifs, keep identical geometry/UVs/materials and host visibility. Five shops, 225 stock items and counters remain unchanged. Team RIGHT, Events LEFT and central navigation board remain fixed. Exact intended steel rack/table identity is unresolved; no guessed replacement is adopted.

All 17 light owners are the originals: 12 active, five optional shop supports exactly 0W. No world, fog, exposure, floor material, screen, signage or camera setting was brightened/moved to manufacture the result. Night views therefore remain subdued; daylight/studio diagnostics are clearly separate and never saved as selected lighting.

## Evidence and reference continuity

renders/before contains 25 byte-exact authenticated Rev11 PNG controls. renders/new contains the same 25 poses at 1280×720 or portrait 576×1024, pixel ratio1, EEVEE16 samples, identical lens/sensor/transform/world/exposure. JSON records every pose and raster SHA. Old close roof cameras are retained even where taller walls change their subject or crop the new roof; no reframing hides that effect. Measured elevation and aerial diagnostics show the complete height extent separately.

The review includes lane arrival, street-to-square, forward screen/crowd, reverse, both diagonals, family housing, left/right elevations, near house joints, roof joins, mobile, plan, actual neutral/clay count views, per-parcel numeric schedule and roofline silhouette comparison. Diagnostic floor bands annotate independently verified slab elevations; they are not production facade stripes or the evidence used to count floors. Screen-hidden inspection is process-only; original screen is retained in every selected view. A 40-second offline walk uses 80 actual Blender frames sampled from the unchanged 960-frame action and played at 2fps; this is not real-time gameplay or a device FPS result.

The original six real references and exact hashes/credits remain in references/ and baseline/source/REFERENCE-PROVENANCE.json. R1 guides tanks/plumbing and roof thickness; R3/R5 guide supported galleries, bays and inhabited openings; R2/R4 guide informal performance/open-sky composition; R6 is a ground-level cypher, used only for crowd spacing. Their low roof heights do not override the new user-directed three-storey minimum. Reference pixels are not used as textures. R2/R4 remain private-reference-only with public redistribution rights unverified; preserve credits for CC BY-SA references. See REFERENCE-ANALYSIS.md and the photo-to-model review board.

## Validation and honest limits

Early failed-authoring and diagnostic path-error logs are retained as history; tests.json and test-* logs identify the final regressions. A missing diagnostic-only baseline path was corrected to the packaged baseline directory, with no model change. Headless EGL fallback warnings occurred during successful PNG rendering; no GPU acceptance is inferred.

All ten targeted regression cohorts pass: preservation/topology/tangents, all-eleven storeys/upper joins, original layout, three grooved shutter art, four wall art placements, crowd/shops, first-hit destinations, exact same-height occupancy grid, rear-setback survey and geometry budget. The unchanged 960-frame X=0 walk and 0.35m capsule /0.002m floor limits pass in all nineteen applicable scenes (SOURCE AUDIT excluded). Body/body and body/architecture intersections remain zero. Texture owners, source scene memberships, camera parameters and light counts are checked independently. Screenshot metadata and restored archives have additional final delivery checks in sidecar evidence.

The full 4,221-center occupancy grid has ZERO boolean differences between Rev11 H07 and Rev12 H07. This does not erase the earlier H00→H07 result: 29 previously clear centers intersect taller people under the same original thresholds. Those samples are not square metres of removed floor. Two inherited negative-Y scooter shop approaches remain blocked; their positive-Y alternatives pass. Six nonpublic rear samples outside Y48 still have no downward floor hit. They remain unresolved, not hidden by tolerances or reported as fixed.

Night rendering remains dark above the performance zone, the screen still dominates and hides rear levels, and facade/slab grammar remains visibly regular. Added galleries, setbacks and roof utilities improve articulation but do not make an artist-finished, photoreal neighborhood. Some old inspection cameras now face nearer upper walls rather than roofs; their original poses are intentionally retained. The architectural minimum is technically demonstrated; final visual quality and +7% stature require user judgment.

## Geometry / asset cost

|Measured selected scene|Rev11|Rev12|
|---|---:|---:|
|Evaluated triangles (includes font/curve mesh)|{old['triangles']:,}|{new['triangles']:,}|
|Mesh/curve object owners|{old['meshCurveOwners']:,}|{new['meshCurveOwners']:,}|
|Geometry datablocks including fonts|{old['geometryDatablocks']:,}|{new['geometryDatablocks']:,}|
|Materials / shader nodes|88 /887|88 /887|
|Image owners / conservative RGBA8+mips estimate|33 /138.53MiB|33 /138.53MiB|
|Active /optional-off lights|12 /5|12 /5|

Increase: {new['triangles']-old['triangles']:,} triangles ({100*(new['triangles']/old['triangles']-1):.1f}%). The master grows 20.47→{b['masterBytes']/1e6:.2f}MB because it retains all old scenes plus new architecture. No new texture download, image, material or light owners. Actual horizontal floor/roof/coping and underside triangles, classified by measured face normal and world-Z, are recorded in evidence/structure-triangle-cost.json; no additive box estimate is presented as an optimized runtime cost. The primary shell contributes {p['newMeshChecks'][0]['triangles']:,} triangles; many remaining increments are railings and actual stair detail. Object counts are NOT browser draw calls; the decoded estimate is NOT measured VRAM. Future runtime work should partition at party ownership, batch/instance casements/pickets, reduce hidden stair detail appropriately and develop tested near/mid/far LODs. No runtime LOD, culling or actor-instancing architecture has been introduced during this private study. Actual laptop/mobile load times, draw calls and FPS remain unmeasured; no hardware certification is inferred from offline/CPU rendering.

## Recovery and next decision

The environment disconnected during an earlier attempt; it returned with source and RAM staging intact. The final model is {b['masterSHA256'][:8]}, superseding the initial cc9d2b0b and intermediate f5053991 attempts. A direct full-byte download-back verified master and interim source safety archive were created before long renders. Final delivery uses a newly dated Rev12 Drive hierarchy, protected old checkpoints untouched. RESTORE.md, FILE-MANIFEST.json and external final archive index/verification receipts enumerate all parts, hashes and independent fresh restore; folders alone are not labelled verified backups.

Recommendation: REVIEW this taller 3/4/5-storey skyline and unchanged +7% original crowd, using matched night views first and neutral/count diagnostics second. No automatic A/B selection, stature acceptance, website integration or next phase follows. Exact rack/table identity and rear service openings remain separate unresolved work.
'''
(O/'REPORT.md').write_text(text)
(O/'REFERENCE-ANALYSIS.md').write_text((O/'baseline/REFERENCE-ANALYSIS.md').read_text().replace('# Rev11 reference translation','# Rev12 reference translation')+'\nRev12 retains the same physical roof/service/gallery cues while increasing all eleven main masses to 3–5 full residential levels above Z7.2m. The newer explicit height rule supersedes the photographs’ low rooflines. Continuous 0.60m bearing junctions and real internal return stairs replace unsupported silhouette counts. Weathered material owners remain unchanged; the result still has repeated bay grammar and darker upper floors.\n')
print('REPORT_COMPLETE',len(text))
