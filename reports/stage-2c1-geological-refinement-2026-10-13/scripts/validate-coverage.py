"""Retained perimeter survey PLUS Stage2C comparison, upward rays and mixed LODs."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c1-geological-refinement-2026-10-13/raw'
source=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
def B(p):return Vector((p[0],-p[2],p[1]))
def tree(objects):
 vertices=[];polys=[]
 for o in objects:
  if o.type!='MESH':continue
  offset=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices);polys.extend([[offset+i for i in p.vertices]for p in o.data.polygons])
 return BVHTree.FromPolygons(vertices,polys,all_triangles=False,epsilon=1e-5)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend'))
base=[[o for o in bpy.data.collections[f'RUNTIME_LOD{i}'].objects if o.type=='MESH']for i in range(3)]
before=[tree(objects)for objects in base];unaffected=[[o for o in objects if not o.name.startswith(('Quarry_Rock_22_','Quarry_Rock_23_'))]for objects in base]
with bpy.data.libraries.load(str(ROOT/'assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend'),link=False)as(data,to):to.objects=[f'Refined_Pair_LOD{i}'for i in range(3)]
ref={o.name:o for o in to.objects};refLevels=[[ref[f'Refined_Pair_LOD{i}']]for i in range(3)];after=[tree(unaffected[i]+refLevels[i])for i in range(3)]
p=[];f=[]
for rock in source['rocks']:
 offset=len(p);p.extend(B(v)for v in rock['vertices']);f.extend([[offset+i for i in face]for face in rock['faces']])
original=BVHTree.FromPolygons(p,f,all_triangles=False,epsilon=1e-5)
eyes=[[0,1.72,-51],[0,1.72,-96],[-10.5,1.72,-110.8]];rows=[];gaps=[];up=[];baselineChanges=[];disagree=[]
for eye in eyes:
 for pitch in [0,10,20,30]:
  for yaw in range(0,360,3):
   pp=math.radians(pitch);yy=math.radians(yaw);d=B([math.cos(pp)*math.sin(yy),math.sin(pp),-math.cos(pp)*math.cos(yy)])
   old=original.ray_cast(B(eye),d,300)[3];bb=[t.ray_cast(B(eye),d,300)[3]for t in before];aa=[t.ray_cast(B(eye),d,300)[3]for t in after]
   row={'eye':eye,'pitch':pitch,'yaw':yaw,'originalEnvelopeHitM':old,'stage2CLODHitM':bb,'refinedLODHitM':aa};rows.append(row)
   if old is not None and any(a is None for a in aa):
    (gaps if pitch==0 else up).append(row)
   if any((a is None)!=(b is None)for a,b in zip(aa,bb)):baselineChanges.append(row)
   if any(a is None for a in aa)and any(a is not None for a in aa):disagree.append(row)
# More demanding local angular coverage and skyline survey. Mixed LOD seams
# are tested independently, not just the whole-world same-LOD alternatives.
mixed=[[tree([ref[f'Refined_Pair_LOD{a}']])for a in range(3)]]
localEyes=[[-20,1.72,-57],[-39,4,-65],[-10.5,1.72,-110.8]];mixedDisagree=[];maskedDisagree=[];fineChanges=[];tested=0;neighborTrees=[tree(objs)for objs in unaffected]
for eye in localEyes:
 for pitch in range(0,51,2):
  for yaw in range(216,305):
   pp=math.radians(pitch);yy=math.radians(yaw);d=B([math.cos(pp)*math.sin(yy),math.sin(pp),-math.cos(pp)*math.cos(yy)])
   hits=[t.ray_cast(B(eye),d,300)[3]for row in mixed for t in row];tested+=1
   if any(h is None for h in hits)and any(h is not None for h in hits):
    neighborHits=[t.ray_cast(B(eye),d,300)[3]for t in neighborTrees];near=min(h for h in hits if h is not None);row={'eye':eye,'pitch':pitch,'yaw':yaw,'pairHitsM':hits,'unchangedNeighborHitsM':neighborHits}
    # An isolated-volume tangent is not an exposed perimeter gap if every
    # unchanged neighbor LOD occludes it BEFORE the refined section. Retain
    # and publish those samples; never waive an exposed disagreement.
    (maskedDisagree if all(h is not None and h<near-.05 for h in neighborHits)else mixedDisagree).append(row)
   a=after[0].ray_cast(B(eye),d,300)[3];b=before[0].ray_cast(B(eye),d,300)[3]
   if (a is None)!=(b is None):fineChanges.append({'eye':eye,'pitch':pitch,'yaw':yaw,'stage2CHitM':b,'refinedHitM':a})
result={'status':'PASS'if not gaps and not mixedDisagree else'FAIL','method':'Retained 360-degree 3-degree-step original-envelope ray survey at 0/10/20/30deg incl upward. Fresh Stage2C-to-refined hits compared at all LODs. Additional local 1deg yaw x2deg elevation tests all coordinated pair LODs (mixed states are prevented by a welded single volume) at three actual review/visitor origins. Skyline edits are authorized and explicitly enumerated; zero horizontal gaps required, zero added pair/mixed-LOD hit disagreements required. Sampled coverage, not a universal silhouette proof.','sourceHitRays':sum(r['originalEnvelopeHitM']is not None for r in rows),'visitorHeightSourceHitRays':sum(r['pitch']==0 and r['originalEnvelopeHitM']is not None for r in rows),'newVisitorHeightGaps':gaps,'changedUpwardSkylineSamples':up,'stage2CVisibilityChanges':baselineChanges,'fullWorldLODHitDisagreements':disagree,'mixedLODLocalRays':tested,'mixedLODHitDisagreements':mixedDisagree,'isolatedPairDifferencesOccludedByUnchangedNeighbors':maskedDisagree,'localSkylineChanges':fineChanges,'samples':rows}
(OUT/'perimeter-coverage.json').write_text(json.dumps(result,indent=2));print(result['status'],'horizontal gaps',len(gaps),'mixed disagreements',len(mixedDisagree),'upward samples',len(up),'baseline changes',len(baselineChanges),'local changes',len(fineChanges),flush=True)
assert not gaps and not mixedDisagree
