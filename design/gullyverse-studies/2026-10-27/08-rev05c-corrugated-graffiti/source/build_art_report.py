from pathlib import Path
import json,hashlib,statistics,datetime
O=Path(__file__).resolve().parents[1];read=lambda n:json.loads((O/n).read_text())
a=read('evidence/art-authoring.json');p=read('evidence/preservation-audit.json');g=read('evidence/shutter-geometry-validation.json');w=read('evidence/wall-placement-validation.json');b=read('evidence/scene-budget-final.json');body=read('evidence/body-overlap-validation.json');shop=read('evidence/shop-geometry-stock-validation.json');route=read('evidence/layout-validation.json');web=read('evidence/website-preservation.json');review=read('evidence/review-build.json');match=read('evidence/matched-render-validation.json');rgb=read('evidence/original-rgb-preservation.json');matte=read('evidence/exact-source-matte-bake.json');folders=read('checkpoint/drive-folders.json');renders=read('evidence/final-render-manifest.json');sources=read('source/provenance/artist-sources.json')
assert all(x['status']=='PASS'for x in [p,g,w,body,shop,route,web,review,match,rgb])
costs=[]
def percentile(values,q):
 position=(len(values)-1)*q;low=int(position);high=min(len(values)-1,low+1);return values[low]+(values[high]-values[low])*(position-low)
for variant in ['A','B']:
 pairs=[]
 for r in renders:
  if r['variant']!=variant or r['edition']!='before'or str(r.get('renderType','')).startswith('Exact existing'):continue
  after=next(x for x in renders if x['variant']==variant and x['edition']=='after'and x['camera']==r['camera']);pairs.append((r,after))
 for edition,index in [('before',0),('after',1)]:
  t=sorted(pair[index]['seconds']for pair in pairs);costs.append({'variant':variant,'edition':edition,'sameFreshPoses':len(t),'medianSoftwareStillSeconds':statistics.median(t),'p95SoftwareStillSeconds':percentile(t,.95)})
(O/'evidence/offline-render-costs.json').write_text(json.dumps({'scope':'Serial A/B matched fresh EEVEE still wall times; no physical GPU, browser frame-time or FPS acceptance. C was partly concurrent and is excluded from this comparison. Cold cache/shader compilation can still vary.','records':costs},indent=2)+'\n')
source_rows='\n'.join(f"|{s['artist']}|{s['metadata']['title']}|{s['bytes']:,}|`{s['sha256']}`|"for s in sources)
shape_rows='\n'.join(f"|{r['artist']}|{r['physicalSlatCount']}|{r['grooveDepthMeasuredM']:.6f}|{r['maximumOuterAssemblyBoundsErrorM']:.9f}|"for r in g['checks'])
base_tri={'A':83564,'B':86698,'C':84768}
budget_rows='\n'.join(f"|{s['variant']}|{base_tri[s['variant']]:,}|{s['evaluatedMeshAndCurveTriangles']:,}|{s['meshAndConvertedCurveObjects']:,}|"for s in b['scenes'])
timing_rows='\n'.join(f"|{r['variant']}|{r['edition']}|{r['sameFreshPoses']}|{r['medianSoftwareStillSeconds']:.2f}s|{r['p95SoftwareStillSeconds']:.2f}s|"for r in costs)
rgb_rows='\n'.join(f"|{r['key']}|{r['fullyOpaqueCorePixels']:,}|{r['maximumSourceRGBErrorFullyOpaqueCore']}|{r['semiTransparentEdgePixels']:,}|"for r in rgb['images'])
master=O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend'
text=f'''# Gullyverse Rev05C — exact artist graffiti on physical rolling shutters

27 October 2026. Built {datetime.datetime.now(datetime.timezone.utc).isoformat()}.

Handoff: **WORLD-REV05C-CORRUGATED-ART-20261027-{a['masterSHA256'][:8]}**.

**Private implementation complete; READY FOR USER VISUAL REVIEW.** All three supplied artist designs are applied to actual profiled steel shutters. Four newly image-generated supporting compositions are applied to existing lane/transition surfaces as proposals. Support OFF remains locked. No A/B/C selection, website implementation or final production acceptance is implied.

## Baseline and preserved work

The manually approved current shared-Doc prompt supersedes the earlier source-only discovery task: all three exact images are now supplied. This pass starts from packed `source/baseline/Rev05C-Support-Off.blend`,SHA256 `{a['baselineSHA256']}`, retaining the user's approved0W state rather than Rev05B's45W supports. The original input is included unchanged. Final packed master: `source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend`,{master.stat().st_size:,}bytes,SHA256 `{a['masterSHA256']}`.

Protected website remains `{web['branch']}` at `{web['HEAD']}`. All{web['protectedFiles']} protected file hashes and exact pre-existing Git status match. Existing modified source/traces and untracked canal-study work remain intact; the other navigation checkout was untouched. No reset,clean,commit,push,merge,branch switch,live/WIP/public asset change or deployment. C8's approved3× sampling, C9 and cave/stage/media/navigation source remain protected by this unchanged website state.

In Blender, all original object transforms/actions, five open cavities,45shelf boards/180cartons, exact counters/DJ furniture, crowd countsA176/B184/C180, full center/wings/board foreground, original straight40second X=0 action, TeamRIGHT/EventsLEFT, signboard/screen and no-banner fix remain unchanged. All original17light objects (five at0W),39cameras, source material nodes,24original image payloads, world,sky,fog,exposure and emission are preserved.22new review cameras are the only new scene objects; there are **zero new mesh/decal objects**.

## Exact source verification and provenance

Authenticated downloads from the new user folder were verified BEFORE use:1536×512JPEG each. Original files are retained byte-for-byte under `source/originals`. Their availability blocker is resolved; the historical partial report remains preserved as an accurate earlier state.

|Artist|Exact Drive filename|Bytes|SHA256|
|---|---|---:|---|
{source_rows}

Source folder:https://drive.google.com/drive/folders/1uRxVGQcUvCQuQGxIPHcLvP9yVlekHwGL . Individual observed URLs/IDs and original hashes are in `source/provenance/artist-sources.json`. Origin is user-supplied artwork, authorized for this private study; ownership/commercial redistribution rights were not independently audited. No public promotion occurs. Existing background CC0 source provenance is retained separately.

Exact assignments, shared across A/B/C:

|Artist|Existing closed shutter|Location|
|---|---|---|
|CHAAR DIWARI|Closed rolling shutter.001|RIGHTY-25|
|RITVIZ|Closed rolling shutter|LEFTY-16|
|NEHA KAKKAR|Closed rolling shutter.002|RIGHTY+2|

Exactly one artist per closed shutter. No optional extra-name shutter, new name art or conversion of an open store.

## Alpha extraction and retained source colours

Actual `image_gen.imagegen` background-extraction trials were performed using each original reference, with transparent output requested. The tool did not expose a model version. Those trials altered some edge pixels; their RGB was **not** substituted as the artist designs. Raw trial outputs/prompts are retained as source-stage evidence.

Final author-time matte refinement/baking uses the original JPEG pixels in Blender. Connected exterior near-white paper is excluded while enclosed silver/white letter highlights remain protected. Trial alpha serves only as a guide for genuine enclosed negative-paper regions. Two pixels around the exterior edge receive white-matte decontamination to remove the thin JPEG halo seen in the first draft. Transparent hidden RGB is cleared; original canvas/aspect and opaque interior colour remain exact. This is not a global 'all white is transparent' threshold and not a lettering redraw.

|Source|Fully opaque original core pixels|Maximum8-bit RGB error in core|Corrected semi-transparent edge pixels|
|---|---:|---:|---:|
{rgb_rows}

The three final RGBA maps and separate grayscale matte PNGs are1536×512. Core RGB error is zero; edge decontamination is intentionally documented rather than claiming every JPEG/background pixel is unchanged. Enclosed white/silver highlight counts are retained in `exact-source-matte-bake.json`. Front/dark-surface and grazing renders were inspected. The first white-fringe draft remains labelled as a draft, outside final comparison pages.

## True corrugated rolling steel

Only the three existing backing meshes and their54existing slat meshes change geometry. The18slats per door become thin, closed rolled-steel sections with14front-profile samples,3mmmetal thickness,15cmpitch, nominal3cmfront-to-valley depth and1mminter-slat mechanical gap. The backing front recesses locally to stop its formerly flat plane from occluding the valleys. The backing remains closed behind the joints; no new building opening is made.

All existing host/slat object transforms, names, shop frames,lintels,signs,original latch geometry and exterior assembly bounds remain preserved. There are no hovering image planes, independently extruded letters or a white JPEG poster. The source graphic's illustrated3D lettering is pigment; the physically modelled relief is the steel itself.

|Artist|Physical slats|Measured groove depth(m)|Maximum assembly bound error(m)|
|---|---:|---:|---:|
{shape_rows}

Caps are triangulated for valid tangent computation; the initial n-gon-cap tangent error was repaired in the authoring topology, not by relaxing checks. The final57controlled meshes pass closed-manifold/positive-volume/nonzero-area checks, finiteUV and unit tangent checks, correct bitangent signs and outward front/valley ray hits. Same-camera neutral-metal before/after renders isolate the actual profile change under unchanged environment lighting.

Paint uses one continuous world-metreY/Z projection and one shared artist image/material per backing-plus18slat assembly, with mirrored coordinate orientation for the opposing side. The6.3m×2.1mpaint rectangle preserves the3:1source aspect and fits inside shutter bounds. The same coordinate field reaches ridge faces and valleys; the actual normals/shadows affect the letters. World projection avoids UV resets on each slat, while a separate valid local UV layer supplies tangent data. No per-frame projection operation or global triplanar shader is introduced.

Paint is nonmetallic with matte roughness near0.82; local worn enamel/steel has restrained roughness/grain. Geometry provides the3cmrelief; submillimetre enamel bump is secondary. All new paint emission strengths are0. No extra light or exposure compensation. Existing latch/boxes/scooters can naturally occlude small parts from some oblique views, rather than moving them to improve screenshots.

## Actual generated wall art and inspected placements

`image_gen.imagegen` was actually invoked with all three original images as style references. The generated output is a four-piece non-name abstract spray-paint atlas, preserving cyan/magenta/violet, lime/orange, dark dimensional outlines, drips and spray density. No new artist name, brand or readable slogan was requested or selected. Model/version beyond the exposed tool name is unknown and not invented. Raw output, complete prompt, reference IDs and hashes are retained in `source/generated` and `source/provenance/supporting-wall-generation.json`.

The output is one2172×724RGBAatlas shared by four UV regions. Existing surfaces were surveyed and rendered before selecting the proposals. Broad unoccluded upper-storey bands existed only nearZ13.6; these were rejected for poor pedestrian relevance. Two narrow, lower lane wall/piers and two existing entry-parapet returns offered better-scale supporting locations. They use six existing objects because each lane piece crosses a pier/its adjacent wall surface, with a coherent projection. No new flat panel was added.

|Proposed piece|Existing physical surface|Paint size|
|---|---|---|
|Cyan/magenta lane fragment|Building/-1/0 + Shop pier.001, nearY-21.15|0.52mwide×1.56mhigh; motif rotated90°, aspect preserved|
|Lime/orange lane fragment|Building/1/1 + Shop pier.011, nearY-12.15|0.52mwide×1.56mhigh; motif rotated90°, aspect preserved|
|Violet/cyan roof fragment|Left Entry parapet return, centerX-11.5,Y14.3,Z7.75|2.6m×0.867m|
|Warm pink/orange roof fragment|Right Entry parapet return.001, centerX+11.5,Y14.3,Z7.75|2.6m×0.867m|

Each9-point patch survey hits only the assigned physical hosts. Team/Events posters,nav board,screen,doors/signs remain outside the paint rectangles and their materials remain exact. Supporting paint retains original plaster/concrete normals and roughness with subtle grain wear; source textures/images are borrowed without mutation. The three artist shutters remain the hero works. Four placements are **PROPOSED, NOT LOCKED**; their balance and visibility remain user art decisions. Parapet pieces read best when looking back into the transition, rather than being forced onto the forward screen composition.

## Actual review evidence

Phone review:{review['phonePDFPages']}pages. Full comparison:{review['fullPDFPages']}pages. `GALLERY.html` links all53main matched pairs and3neutral-profile diagnostic pairs:112final scene PNGs. Every artist has front,grazing and in-lane context in A/B/C. C adds detail,mobile artist views,wall-paint applications,Team/Events preservation and wider lane context. SourceJPEG→derivedRGBA→real shutter contact sheets and raw-generated-atlas→actual-wall views clearly distinguish assets from scene evidence.

All pairs match actual camera position/orientation,FOV/lens,sensor,projection type,clip planes,resolution,16sampleEEVEEquality,exposure,look and approved0Wlighting. Desktop1200×750,portrait540×960. Offline Blender has no browserDPR. A small set of baseline landing PNGs is reused only after verifying the exact0Wmaster and image hashes. Final preview frames promoted into final evidence also retain exact candidate/hash provenance. No generated mockup or beauty render substitutes for the required actual Blender scene comparisons.

## Regression and preservation results

- Full original object/material/image/action/environment audit PASS, with only57controlled shutter meshes and63controlled paint material overrides. All non-target geometry/UV/transform state stays identical; original39cameras and17lights remain exact.22review cameras are additive only. Zero new mesh objects and zero banner reintroduction.
- Shutter topology/UV/tangent/normals/outer-bounds/real-depth checks PASS; all19surface objects per artist share the same continuous paint image/material. No floating decal,repeat-per-slat texture or source-scale distortion.
- All960straight-walk frames in each A/B/C pass the original0.35mcamera-radius and0.002mfloor checks. Straight entry/screen,Team-right and Events-left routes pass. Original navigation/animation data is unchanged.
- Actual audience counts176/184/180.188unionactors/1,504parts,17,578actor pairs,zero crowd body/prop triangle overlaps. Shelf stock remains225objects inside five cavities, and exact counters/DJ geometry/transforms unchanged.
- Two inherited negative-Y approaches remain blocked by Scooter steering.002 atLEFTY+2and Scooter steering.001 atRIGHTY-7; tested positive-Y alternatives pass. Fail samples remain in evidence. No scooter/counter was moved or tolerance loosened.
- All1,213protected website hashes and exact dirtyGit state pass. No changed runtime or glTF export was introduced. Consequently no new website TypeScript/build/browser/map/playback/context-recovery success is claimed for this Blender-only phase; existing runtime/cache systems were preserved rather than reimplemented.

These are concept/art-authoring geometry surveys, not public-accessibility certification or physical laptop/phone performance acceptance. No strict test tolerance was relaxed.

## Geometry, materials and measured costs

|Variant|Before triangles|After triangles|Mesh/converted-curve objects after|
|---|---:|---:|---:|
{budget_rows}

Each variant gains5,184triangles from the physical profiles; no mesh-object/draw-object count is added. The full three-shutter assemblies contain5,868triangles including backing. Nine new authoring material datablocks use four shared new images, rather than independent full-resolution sets per slat/wall. Original24images remain shared/packed. New PNGs total{b['newImageBytesPNG']:,}bytes. Estimated unique RGBA8+mip payload rises95.86→{b['estimatedUniqueImageRGBA8MipMiB']:.2f}MiB, about20MiB. This is an image-format estimate, not measuredGPUVRAM. Packed authoring master grows4,037,755→{master.stat().st_size:,}bytes; it is not runtimeGLB transfer.

All17authoring lights remain stored with the same original12active and five optional0W. No new shadow-light cost. Material/node and texture-reference counts are in `scene-budget-final.json`. No liveR3F draw-call/FPS query is fabricated.

Serial A/B fresh matched-pose software still timings:

|Variant|Edition|Fresh matched poses|Median|p95|
|---|---|---:|---:|---:|
{timing_rows}

These are software EEVEE still wall times, not interactive frame times. C included concurrent jobs and is excluded from the timing comparison; cached/reused frames are excluded too. Shader/cold-cache/load differences still prevent hardware acceptance or a strong isolated performance verdict. Physical laptop/mobile verification remains pending.

For a separately approved futureR3Fconversion, merge static slat parts by each shutter/material; preserve the same paint UV/projection across joins. A6sample/profile middle mesh would be about2,412triangles for the three units and a3sampledistant profile about1,116, before bake/culling decisions; these are proposed targets, not delivered/tested runtimeLODs. Bake or retain the bounded2Dprojection with validated tangent/alpha handling, share the four images and measure actual web draw calls/loading/device cost. No full-worldGLBduplicate or texture rollout is needed for this local art. Do not claim the Blender shader graph is already a validated glTF material export.

## Remaining art limitations and next decision

The paint now has the supplied identity, real metal profiles and physical shading instead of a floating image. The broader city remains a spatial/art blockout: simplified stock,building masses and proxy crowds are unchanged. Some graffiti microdetail softens at pedestrian distance; the6.3mhero words remain the main read. Oblique mechanical grooves deliberately deform the apparent lettering through depth. Supporting pier fragments are secondary small non-name accents, and roof pieces depend on viewing direction. These are review choices, not automatic final-art success.

No A/B/C aesthetic is selected. User review should judge the three exact shutter paintings,the3cmgroove appearance,retained night mood and four supporting placement proposals. Do not begin a wider world overhaul or website implementation automatically.

## Independently recoverable checkpoint

New phase:{folders['phase']['url']}

Review:{folders['review']['url']}

Checkpoint:{folders['checkpoint']['url']}

The final complementary ZIPs contain exact0Winput and new packed master,all three originalJPEGs,RGBA/mask derivatives,raw image-generation trials/atlas,prompts/source hashes/provenance,authoring/validation scripts,all rendered PNGs,PDFs,gallery,report and restoration instructions. Per-file/archive SHA256manifests and authenticated download-back/independent extraction/reopen receipts are separate final delivery records. The earlier source snapshot is an independently verified working snapshot, superseded by the complete final package. Earlier checkpoints/approval records are preserved in place.

**Stop for user visual review.** No commit,push,merge,deploy,website promotion or next phase.
'''
(O/'REPORT.md').write_text(text)
print('ART_TECHNICAL_REPORT_BUILT',len(text))
