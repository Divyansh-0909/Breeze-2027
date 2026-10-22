from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path('reports/recovery-quarry-fidelity-2026-10-19');bpy.ops.wm.open_mainfile(filepath=str(Path('assets-source/gullyverse/quarry-fidelity-correction/.authoring-cache/fidelity-unbaked.blend').resolve()))
issues=json.loads((r/'raw/targeted-ray-cones.json').read_text())['newInvertedHits']
obs=[bpy.data.objects['Fidelity_Composed_High']]+[bpy.data.objects['Fidelity_Wall_15_LOD'+str(i)]for i in range(3)];trees=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],all_triangles=True,epsilon=1e-6)for o in obs]
def B(p):return Vector((p[0],-p[2],p[1]))
rows=[]
for q in issues:
 a,b=math.radians(q['pitch']),math.radians(q['yaw']);d=B([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)]);row={'eye':q['eye'],'pitch':q['pitch'],'yaw':q['yaw'],'casts':[]}
 for ob,t in zip(obs,trees):
  p,n,face,distance=t.ray_cast(B(q['eye']),d,650);row['casts'].append({'mesh':ob.name,'distance':distance,'face':face,'normalDotRay':n.dot(d)if n is not None else None})
 rows.append(row);print(json.dumps(row),flush=True)
(r/'raw/targeted-high-versus-runtime.json').write_text(json.dumps(rows,indent=2)+'\n')
