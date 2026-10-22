"""Replay historical component rays with their ORIGINAL Blender/BVH convention."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw';base=ROOT/'reports/recovery-quarry-fidelity-2026-10-19/raw'
def B(p):return Vector((p[0],-p[2],p[1]))
def imported(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));return[o for o in bpy.data.objects if o not in before and o.type=='MESH']
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],all_triangles=False,epsilon=1e-6)
entry=json.loads((ROOT/'public/models/gullyverse/c9-cave-recovery/entry-clearance.json').read_text());local=imported(ROOT/'public/models/gullyverse/c9-cave-recovery/entry-clearance.glb');mapping={target:next(o for o in local if o.name==runtime)for target,runtime in zip(entry['targetNodes'],entry['runtimeNodes'])}
original={}
for level in range(3):
 for o in imported(ROOT/f'public/models/gullyverse/quarry-foundation-refined/foundation-lod{level}.glb'):original[o.name.split('.')[0]]=o
j=json.loads((base/'fidelity-geometry-validation.json').read_text());seventh=json.loads((base/'known-seventh-legacy-hit.json').read_text());cases=[]
for q in j['inheritedInvertedHits']:
 h=q['verifiedUnchangedSurface'];cases.append({'eye':q['eye'],'pitch':q['pitch'],'yaw':q['yaw'],'mesh':h['mesh'],'distance':h['distance'],'dot':h['normalDotRay']})
cases.append({'eye':seventh['eye'],'pitch':seventh['pitch'],'yaw':seventh['yaw'],'mesh':seventh['mesh'],'distance':seventh['componentDistanceM'],'dot':seventh['componentNormalDotRay']})
result=[]
for c in cases:
 p=math.radians(c['pitch']);y=math.radians(c['yaw']);d=B([math.cos(p)*math.sin(y),math.sin(p),-math.cos(p)*math.cos(y)]);origin=B(c['eye']);old=tree(original[c['mesh']]).ray_cast(origin,d,650);new=tree(mapping.get(c['mesh'],original[c['mesh']])).ray_cast(origin,d,650)
 row={**c,'originalHit':{'distance':old[3],'dot':old[1].dot(d)if old[1]is not None else None},'currentHit':{'distance':new[3],'dot':new[1].dot(d)if new[1]is not None else None}};result.append(row)
 assert old[0]is not None and new[0]is not None,row
 assert abs(new[3]-c['distance'])<=2e-5,row;assert abs(new[1].dot(d)-c['dot'])<=2e-5,row
assert len(result)==7
(R/'inherited-quarry-visibility-replay.json').write_text(json.dumps({'status':'FAIL_INHERITED_UNCHANGED','knownComponentsReplayed':len(result),'sameHistoricalBVHEpsilonM':1e-6,'distanceNormalTolerance':2e-5,'allSevenRemain':True,'newLocalCaveVisibility':'separate full-cave-geometry-validation.json','cases':result},indent=2)+'\n');print('ALL_SEVEN_INHERITED_COMPONENT_DEFECTS_UNCHANGED')
