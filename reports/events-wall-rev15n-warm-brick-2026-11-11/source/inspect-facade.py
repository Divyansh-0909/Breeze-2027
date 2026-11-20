import bpy,json,re
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'crowd-rev15m-aftermovie-models-2026-11-11/delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();objects=[];faces=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];b=[[min(p[i] for p in bb),max(p[i] for p in bb)] for i in range(3)]
 if b[0][0]<-12.3 and b[0][1]>-13.1 and b[1][0]<34.5 and b[1][1]>23.0 and b[2][0]<11.3 and b[2][1]>7.1 and b[1][1]-b[1][0]>3:objects.append({'name':ob.name,'bounds':b,'materials':[m.name if m else '' for m in ob.data.materials],'faces':len(ob.data.polygons)})
 if ob.name=='REV15F / continuous house shell / flush R2 Team facade':
  for p in ob.data.polygons:
   normal=ob.matrix_world.to_3x3()@p.normal
   if normal.x<.85:continue
   v=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices];b=[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)]
   if -16.3<b[0][0]<-14.8 and b[1][0]<37.01 and b[1][1]>25.19 and b[2][0]<11.3 and b[2][1]>7.1:faces.append({'polygon':p.index,'bounds':b,'material':ob.data.materials[p.material_index].name})
(O/'evidence/facade-analysis.json').write_text(json.dumps({'frontObjects':objects,'houseFaces':faces},indent=2));print('analysed objects',len(objects),'facade polygons',len(faces),flush=True)
