import bpy,json,re
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15X1-Accommodation-Clean-Wall.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[];actors=[]
for o in s.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(p)for p in o.bound_box];bounds=[[min(p[i]for p in pts),max(p[i]for p in pts)]for i in range(3)]
 if any(k in o.name for k in ['/ R1 /','R1 window detail batch','Entry parapet return','jointed parapet coping'])or(bounds[0][0]<-8.2and bounds[0][1]>-15.8and bounds[1][0]>13.7and bounds[1][1]<14.7and bounds[2][0]>6.9and bounds[2][1]<8.6):rows.append({'name':o.name,'bounds':bounds,'faces':len(o.data.polygons),'vertices':len(o.data.vertices),'materials':[m.material.name if m.material else None for m in o.material_slots],'props':dict(o.items())})
 if o.data.name.startswith('REV13A shared')or o.get('crowdStyle'):
  if len(actors)<12:actors.append({'name':o.name,'mesh':o.data.name,'boundsLocal':[[min(v.co[i]for v in o.data.vertices),max(v.co[i]for v in o.data.vertices)]for i in range(3)],'props':dict(o.items()),'materials':[m.material.name for m in o.material_slots if m.material]})
deps=bpy.context.evaluated_depsgraph_get();rays=[]
for z in [8.4,8.9,9.4,9.8,10.0,10.5]:
 for i in range(25):
  y=14.5+i*.5;hit=s.ray_cast(deps,Vector((14,y,z)),Vector((1,0,0)),distance=7);rays.append({'y':y,'z':z,'name':hit[4].name if hit[0]else None,'point':list(hit[1])if hit[0]else None})
out={'objects':rows,'actors':actors,'R1Rays':rays};(R/'evidence/survey.json').write_text(json.dumps(out,indent=2,default=str)+'\n');print(json.dumps({'objects':len(rows),'actors':actors[:2]}))
