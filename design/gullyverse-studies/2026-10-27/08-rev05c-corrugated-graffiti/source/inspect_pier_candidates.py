import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s['variant']=='C');bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
v=[];f=[];names=[]
for ob in scene.objects:
 if ob.type!='MESH'or ob.name.startswith('Bounded lane haze'):continue
 ev=ob.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();base=len(v);v.extend(ev.matrix_world@p.co for p in m.vertices);f.extend(tuple(base+i for i in t.vertices)for t in m.loop_triangles);names.extend([ob.name]*len(m.loop_triangles));ev.to_mesh_clear()
tree=BVHTree.FromPolygons(v,f,all_triangles=True)
results=[]
for side,cy,index in [(-1,-25,0),(-1,-16,1),(-1,2,3),(1,-25,0),(1,-16,1),(1,-7,2),(1,2,3)]:
 host=bpy.data.objects[f'Building / {side} / {index}'];g=6+1.2*min(1,max(0,(cy+10)/24))
 for direction in [-1,1]:
  centerY=cy+direction*3.85;centerZ=g+1.5;clear=True;hits=[]
  for dy in [-.26,0,.26]:
   for dz in [-.8,0,.8]:
    h=tree.ray_cast(Vector((0,centerY+dy,centerZ+dz)),Vector((side,0,0)),5)
    hit=names[h[2]]if h[0]is not None else 'none';hits.append(hit);clear&=hit==host.name
  results.append({'host':host.name,'side':side,'centerY':centerY,'centerZ':centerZ,'widthM':.52,'heightM':1.56,'clear':clear,'hits':hits})
(O/'evidence/pier-candidate-survey.json').write_text(json.dumps(results,indent=2)+'\n');print('PIER_SURVEY',results)
