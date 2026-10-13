"""Blender BVH check for newly opened sightline gaps in the quarry perimeter."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'reports/stage-2c-quarry-rollout-2026-10-12'
source=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend'))
def B(p):return Vector((p[0],-p[2],p[1]))
points=[];faces=[]
for rock in source['rocks']:
 offset=len(points);points.extend(B(p)for p in rock['vertices']);faces.extend([[offset+i for i in f]for f in rock['faces']])
original=BVHTree.FromPolygons(points,faces,all_triangles=False,epsilon=1e-5)
trees=[]
for level in range(3):
 vertices=[];polygons=[]
 for ob in bpy.data.collections[f'RUNTIME_LOD{level}'].objects:
  if ob.type!='MESH':continue
  offset=len(vertices);vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices);polygons.extend([[offset+i for i in p.vertices]for p in ob.data.polygons])
 trees.append(BVHTree.FromPolygons(vertices,polygons,all_triangles=False,epsilon=1e-5))
eyes=[[0,1.72,-51],[0,1.72,-96],[-10.5,1.72,-110.8]]
rows=[];newGaps=[]
for eye in eyes:
 for pitch in [0,10,20,30]:
  for yaw in range(0,360,3):
   p=math.radians(pitch);y=math.radians(yaw);direction=B([math.cos(p)*math.sin(y),math.sin(p),-math.cos(p)*math.cos(y)])
   before=original.ray_cast(B(eye),direction,300)[3]
   if before is None:continue
   hits=[tree.ray_cast(B(eye),direction,300)[3]for tree in trees]
   row={'eye':eye,'pitch':pitch,'yaw':yaw,'originalHitM':before,'authoredLODHitsM':hits};rows.append(row)
   if any(hit is None for hit in hits):newGaps.append(row)
visitorGaps=[row for row in newGaps if row['pitch']==0]
skylineChanges=[row for row in newGaps if row['pitch']>0]
lodDisagreements=[row for row in rows if any(hit is None for hit in row['authoredLODHitsM'])and any(hit is not None for hit in row['authoredLODHitsM'])]
result={'status':'PASS' if not visitorGaps else 'FAIL','method':'Original 25 rock envelopes vs closed authored LOD geometry (plus collar/crown). Three visitor-height origins, full 360 degrees in 3 degree increments. Every previously blocked horizontal visitor-height ray must still hit authored geology at every LOD. Upward rays are also recorded: individual skyline rays can change with inward crest chips, while macro corners/hulls are separately locked. This is sampled coverage, not universal seam/z-fighting proof.','sourceHitRays':len(rows),'visitorHeightSourceHitRays':sum(row['pitch']==0 for row in rows),'newVisitorHeightGaps':visitorGaps,'changedUpwardSkylineSamples':skylineChanges,'LODHitDisagreements':lodDisagreements,'samples':rows}
(R/'raw/perimeter-coverage.json').write_text(json.dumps(result,indent=2));print(result['status'],len(rows),'rays',len(newGaps),'gaps',flush=True)
assert not visitorGaps
