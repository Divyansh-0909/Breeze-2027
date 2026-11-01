import json,hashlib,statistics,html,re
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
O=Path(__file__).resolve().parents[1];get=lambda n:json.loads((O/'evidence'/n).read_text());a=get('authoring.json');s=get('before-survey.json');b=get('budget.json');p=get('preservation-geometry-height.json');head=get('head-top-stature.json');j=get('adjacency-after.json');tests=get('tests.json');floor=get('open-floor-attribution.json');web=get('website-preservation.json');review=get('review-build.json')
joins='\n'.join(f'| {x["from"]}–{x["to"]} | {x["beforePodiumXYGapM"]:.3f} | {x["afterPodiumXYGapM"]:.3f} | {x["sharedLengthM"]:.2f} | {x["roofStepM"]:.2f} |'for x in j['joins'])
heights='\n'.join(f'| {x["factor"]:.2f} | {x["minHeightM"]:.3f} | {x["medianHeightM"]:.3f} | {x["maxHeightM"]:.3f} |'for x in sorted(b['heightVariants'],key=lambda x:x['factor']))
cost='\n'.join(f'| {x["variant"]} | {x["triangles"]:,} | {x["meshCurveOwners"]:,} | {x["materialOwners"]} | {x["imageOwners"]} | {x["RGBA8PlusMipsMiBEstimate"]:.2f} |'for x in b['rows'])
checks='\n'.join(f'| {x["test"]} | {"PASS"if x["exitCode"]==0 else"FAIL"} |'for x in tests)
text=f'''# Gullyverse Rev11 — Connected Neighborhood + Human-Scale Study

**READY FOR USER VISUAL REVIEW.** The connected hybrid and +7% stature are proposals, not a final A/B selection. Website unchanged; no integration, install, build, server, commit, push, merge or deployment. Steel rack/table identity remains unresolved; no substitute was adopted.

## Baseline and preservation

Authentic Rev10 input: 16,715,517 bytes, SHA-256 d530f164318ac4f736d43159b7eac705ca4233ac78d69fb545c2b71b950da850. Source: https://drive.google.com/file/d/1vewUBittPgybS7q0qjqT49hI7BFWto_x/view . All 15 old editable scenes, all {p['allOriginalObjectSignaturesExact']:,} original object signatures and original image/material/world signatures are exact. There are now 19 scenes: original 15 plus hybrid H07 and H00/H06/H09 controls.

Sealed master: source/Gullyverse-Rev11-Connected-Neighborhood.blend, 20,471,503 bytes, SHA-256 b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd. Authenticated upload/download-back preceded the restart. It was restored byte-exact on 31 October, never regenerated or resaved for delivery.

Protected WIP branch/HEAD: work-in-progress-2027 / e638140b37045a805b23b4d406d387a8870f8486. Navigation branch/HEAD: codex/navigation-board / 14f36da1a9b79a3b4926f7445bf0cde6c6c8f767. All 1,213 protected website SHA-256 values and exact starting dirty/untracked states pass. C9, C8 3×, cave, navigation, map, stage and media code/assets remain untouched.

## Measured diagnosis

Original total actor envelopes span 1.498–2.094m, median 1.780m; raised arms may determine those bounds. Head-top stature separately measures {head['original']['minM']:.3f}–{head['original']['maxM']:.3f}m, median {head['original']['medianM']:.3f}m, rising to median {head['proposed7Percent']['medianM']:.3f}m at +7%. This is a geometric head-top proxy, not a biological measurement. The protected 32×34m roof is 1,088m² at Z7.2m. The main screen is 8.84×5.98m, and the three media panels span 14.56m. Screen center is about 9.60m from the unchanged walk endpoint; the board raster is 4.80×1.152m, with its original stack/supports intact. Screen dominance and the large floor therefore contribute to perceived stature.

Original house bodies had ten intended attachment gaps despite connected floor/service terraces. Upper floor pitch was 2.85m, nominal main door aperture about 2.27m before trim. Existing frontage widths were 8.0–13.2m with relatively sparse openings. Reference values—1.7m avatar, 2.1m door, 2.8–3.3m storey and 1.0–1.2m guard—are illustrative guidance, not measured original dimensions or code certification.

## Connected architecture and proportion changes

A is the starting visual identity, with selected B-style 1.5m deep galleries at L2, R1, R3 and B2. Lower L1/R2 working roofs, staggered levels and setbacks retain informal roof character. The six preserved real photographs guide inhabited roof rooms, attached party walls, galleries, tank supports, plumbing and weathering; see REFERENCE-ANALYSIS.md and original provenance. No reference pixels entered textures/backplates. R2/R4 remain private-only references with unverified public redistribution rights.

All 11 parcels now form ONE closed, vertex-connected structural shell. Exact orthogonal exposed-surface composition removes duplicate internal wall/slab planes; no Boolean modifier is used. Construction is drafted on a 1cm grid outside the protected floor/registry. Two adjoining 0.30m masonry leaves form a 0.60m party junction. Shared structure runs from foundation through adjoining storeys; stepped roofs receive real terrace slabs and seated guards. Doors/windows buried by corner attachments are omitted and useful entries reassigned to exposed frontage. The 16.6m entry opening at X±8.3m remains clear. No unexplained gaps remain at the ten registered house-to-house interfaces. This is not a claim that every setback outside the protected central floor is a new walkable terrace.

| Join | Before gap m | After gap m | Shared length m | Roof step m |
|---|---:|---:|---:|---:|
{joins}

The measured adjacency graph, CSV, plan and elevation trace every join. Intentional open sky above a lower attached roof is not a gap in its bearing structure. One manifold core with {p['structuralShellVertexComponents'][0]:,} connected vertices is verified separately from subjective visual acceptance.

New upper storeys are 3.0m; lower support storeys 3.3m above a 0.6m base. Main apertures are nominally 2.10m, approximately 2.06m clear below trim/above threshold. Domestic sub-bays replace isolated tiny openings. Galleries are 1.50m deep; roof parapets 1.05m and gallery guard about 1.05m above deck. Water tanks are about 1.16m diameter/1.14m body height, with actual plinths/downpipes. Roof service-hatch clearance remains ~1.92m outside visitor circulation; it is not presented as an accessible public doorway. Floor, screen, board, destinations and camera were not scaled to fake proportions.

## Original C180, modest height only

All 180 original identities / 1,440 parts retain foot positions, yaw, XY vertex footprints, topology, UVs, colours and materials. No Man/Woman GLB, alternate crowd, animation or redistribution was introduced. Double-precision world-Z vertex changes are anchored at original feet while object transforms remain exact. Maximum error against the permitted height-only transform is {max(x['maxXYErrorM']for x in p['crowdHeightOnly']):.9f}m, below the unchanged 1e-5 check. Source and H00 remain reversible.

| Factor | Envelope min m | Envelope median m | Envelope max m |
|---|---:|---:|---:|
{heights}

H07 is the proposed +7%; H06/H09 are controls. Shortest original actor: Organic audience 071; tallest: Organic audience 092. No individual collision reduction was required. The familiar figures read slightly longer; their posed envelopes are not uniformly comparable to standing head-top stature. The 1.7m ruler sheet uses an unraised-arm source figure so the reference has an actual 1.7m head top. This is aesthetic calibration, not demographic realism certification. Front/angle/mobile/aerial controls use the same hybrid architecture and cameras.

## Lighting, protected screen and optional floor

Original 17 light owners remain exact: twelve active and five optional shop supports at 0W. World, fog, exposure, materials and seven approved paintings remain exact. No new selected image/material/light owners or emissive windows. Upper domestic details are still subdued under locked night lighting; geometry helps silhouette but does not solve all readability limits.

The screen remains dominant and masks rear houses. A separate actual Blender hidden-media diagnostic shows the obscured housing. The 80% screen outline is analysis only (7.07×4.78m); it is NOT applied or selected. Resizing would need fresh permission. Selected floor mesh/material/UV is exact. A process-only patina proposal uses one temporary cloned material and no new images/geometry/lights, at most 6.6% darkening. It is not saved into the master or adopted.

## Actual render evidence

Forty original A/B PNGs are byte-exact authenticated controls. Twenty-five new context/inspection PNGs and twelve isolated height-control PNGs use identical defined camera/FOV/quality/lighting. Desktop 1280×720, portrait 576×1024, pixel ratio 1, sixteen EEVEE samples. Position/rotation/lens/projection/world/exposure/support power are recorded per capture. Close side-gallery/roof views are inspection cameras, not newly approved travel routes. Scale rulers use an explicitly separate Workbench studio diagnostic.

Phone review: {review['phonePages']} pages; full comparison: {review['fullComparisonPages']} pages. GALLERY.html links every full-resolution image. The 40-second offline walk contains 80 real Blender samples from the original 960-frame X=0 action, 480×270/two EEVEE samples, played at 2fps and encoded with repeated frames at 24fps. This is not website footage, interactive FPS or hardware certification.

The restart removed unuploaded transient Rev11 media. R1 recaptures use the SAME b149a04a model/settings; no pixel-identical restoration claim is made for lost temporary raster files. Original A/B controls remain byte-exact. See DELIVERY-COMPLETION-R1.md.

## Geometry/resource budget

| Scene | Evaluated triangles | Mesh/curve owners | Materials | Images | RGBA8+mips MiB |
|---|---:|---:|---:|---:|---:|
{cost}

Totals include evaluated font/curve geometry, consistent with Rev10. Rev11 adds 62,410 triangles versus A (~39.3%); this is a measurable cost of continuous structure, supported galleries and domestic articulation. Master size rises 16.72→20.47MB including all four new scenes and controls; it is not a runtime GLB transfer figure. All 33 packed image owners and ~138.53MiB conservative decoded estimate are inherited, with zero added texture download.

Mesh-owner count is not a draw-call measurement. Browser draws, visible runtime triangles, shader/texture preparation, interactive p50/p95/p99, laptop/mobile FPS and runtime lifecycle are not measured for this offline candidate. Software/offline render timings cannot certify physical GPUs. A future web phase should partition the large core along the verified party ownership planes, batch/instance repeated elements, use actor-root height transforms/shared source geometry and author screen-space LODs. None is implemented in the website here.

## Validation and explicit exceptions

| Final check | Result |
|---|---|
{checks}

All 18 applicable scenes pass the original 960-frame straight action, 0.35m capsule and 0.002m floor tolerance. Four new crowd variants pass actual body/body and body/prop/house triangle checks. Destination first-hit rays find no new screen/board/Team/Events obstruction. Three grooved artist shutters / 54 slats and four wall pieces preserve their profiles, UVs and visibility. Five shops/stock/counters remain correct. Two inherited negative-Y scooter approaches remain blocked, with original positive-Y alternatives passing; they are not marked repaired.

The old exact unchanged-population floor-grid equality diagnostic is intentionally retained as FAIL after the authorized height change. At +7%, 29 previously clear sampled centers gain a people hit (26 at +6%, 36 at +9%). This is not 7.25m² of actual removed floor. H00 proves ZERO new architecture obstructions; all added hits are attributed to height clones, with identical numerical ray thresholds. Protected routes and world XY footprints remain clear. No claim of identical whole-grid occupancy is made. A separate nonpublic setback survey confirms the retained side ledges around Z7.18m, but finds six rear samples beyond the protected Y48 floor edge with no downward hit. Those inherited rear service/lightwell openings are outside the visitor route and remain an explicit architectural-continuity limitation; the ten house-body joins are not a claim of a fully sealed rear service roof.

Development evidence retains the initial memory-heavy construction attempt, metadata serialization error, tuple/list/inactive-scene comparison mistakes, thin-face tangent failures and an unsupported intermediate terrace guard. Topology/retopology and the harness were corrected before sealing; no tolerances were relaxed. Current source signatures, normals/tangents/UV/manifold and collision gates pass.

Website regression builds/browser tests were not run: the prompt explicitly prohibits website work/install/build/server. The 1,213 source hashes and both full Git states are verified unchanged instead. Unintegrated Blender art is not represented as a web runtime certification.

## Artistic verdict and handoff

READY FOR VISUAL REVIEW, not final art approval. The hybrid shows actual house attachments, coherent lower support, joined stepped roofs, deeper lived-in frontage and slightly taller familiar people. Remaining weaknesses: repetitive aperture/slab grammar, subdued upper materials, large fixed floor, dominant screen, simplified interiors and intentionally low-poly crowd. Some compositions still read as a courtyard. Verified connectivity does not make the model photorealistic.

Review the proposed connected architecture and +7% stature against preserved A/B and +0/+6/+9 controls. Do not infer a final A/B selection. If intimacy still feels wrong, reassess the protected floor/screen relationship with explicit user direction instead of repeatedly enlarging people. Steel rack/table identity remains pending. No next phase or website integration starts automatically.

## Independently restorable delivery

FINAL-REVIEW-AND-RESTORE-INDEX.md identifies every required complementary ZIP, SHA-256 and authenticated download-back. FILE-MANIFEST.json covers payload hashes. The final fresh-restore receipt proves reopening from actual Drive-downloaded archives. Index/receipt/handoff are external sidecars to avoid circular hashing. Older checkpoints remain untouched. See RESTORE.md; keep a downloaded copy outside Codex as well as the verified Drive backup.
'''
(O/'REPORT.md').write_text(text)
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));styles=getSampleStyleSheet();
for name in ['BodyText','Heading2','Title']:styles[name].fontName='DejaVu'
styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;styles['BodyText'].spaceAfter=5;story=[];table=[]
def flush():
 global table
 if not table:return
 t=Table([[Paragraph(html.escape(c),styles['BodyText'])for c in row]for row in table],repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#dde5e4')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,HexColor('#b7c7cc'))]));story.extend([t,Spacer(1,8)]);table=[]
for line in text.splitlines():
 if line.startswith('|'):
  row=[c.strip()for c in line.strip('|').split('|')]
  if not all(re.fullmatch(r'[-:]+',c)for c in row):table.append(row)
  continue
 flush()
 if not line:continue
 if line.startswith('# '):story.append(Paragraph(html.escape(line[2:]),styles['Title']))
 elif line.startswith('## '):story.append(Paragraph(html.escape(line[3:]),styles['Heading2']))
 else:story.append(Paragraph(html.escape(line.replace('**','')).replace('SHA-256 ','SHA-256<br/>'),styles['BodyText']))
flush();SimpleDocTemplate(str(O/'review/Rev11-Technical-Report.pdf'),pagesize=(540,850),rightMargin=30,leftMargin=30,topMargin=30,bottomMargin=30).build(story);print('TECHNICAL_REPORT_COMPLETE',len(text))
