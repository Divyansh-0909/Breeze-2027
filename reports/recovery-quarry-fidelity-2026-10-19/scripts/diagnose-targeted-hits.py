from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path('reports/recovery-quarry-fidelity-2026-10-19');issues=json.loads((r/'raw/targeted-ray-cones.json').read_text())['newInvertedHits']
bpy.ops.wm.open_mainfile(filepath=str(Path('assets-source/gullyverse/quarry-fidelity-correction/.authoring-cache/fidelity-unbaked.blend').resolve()));tags=json.loads(bpy.data.texts['ALL_LOD_FACE_SOURCE_TAGS'].as_string());lookup=[]
for level in range(3):
 near=bpy.data.objects['Fidelity_Wall_15_LOD'+str(level)];lookup.append({tuple(sorted(tuple(near.data.vertices[i].co)for i in p.vertices)):tags[level][p.index]for p in near.data.polygons})
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path('public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb').resolve()));obs=sorted([o for o in bpy.data.objects if o not in old and o.type=='MESH'],key=lambda o:o.name);trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],all_triangles=True,epsilon=1e-6)for o in obs]
def B(p):return Vector((p[0],-p[2],p[1]))
def G(p):return [p[0],p[2],-p[1]]
rows=[]
for q in issues:
 level=q['LOD'];o=obs[level];a,b=math.radians(q['pitch']),math.radians(q['yaw']);d=B([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)]);hit=trees[level].ray_cast(B(q['eye']),d,650);p=o.data.polygons[hit[2]];key=tuple(sorted(tuple(o.data.vertices[i].co)for i in p.vertices));xyz=np.array([G(o.data.vertices[i].co)for i in p.vertices]);row={'LOD':level,'eye':q['eye'],'pitch':q['pitch'],'yaw':q['yaw'],'point':G(hit[0]),'normal':G(hit[1]),'faceIndex':p.index,'sourceTag':lookup[level].get(key),'area':p.area,'vertices':xyz.tolist(),'maximumEdgeM':float(np.linalg.norm(xyz[:,None,:]-xyz[None,:,:],axis=-1).max())};rows.append(row);print(json.dumps(row),flush=True)
(r/'raw/targeted-inverted-face-diagnosis.json').write_text(json.dumps(rows,indent=2)+'\n')
