import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'crowd-rev15m-aftermovie-models-2026-11-11/delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];bounds=[[min(p[i] for p in bb),max(p[i] for p in bb)] for i in range(3)]
 if bounds[0][0]<-14.7 and bounds[0][1]>-16 and bounds[1][0]<32 and bounds[1][1]>22 and bounds[2][0]<10.8 and bounds[2][1]>7.3:
  rows.append({'name':ob.name,'data':ob.data.name,'bounds':bounds,'materials':[m.name if m else '' for m in ob.data.materials],'faces':len(ob.data.polygons),'location':list(ob.location),'props':dict(ob.items())})
(O/'evidence/house-baseline.json').write_text(json.dumps(rows,indent=2,default=str));print('Nearby house objects',len(rows),flush=True)
