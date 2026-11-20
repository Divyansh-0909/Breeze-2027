import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O.parent/'crowd-rev15m-aftermovie-models-2026-11-11/delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if ob.type!='MESH' or not ('L2 /' in ob.name and ('glazing' in ob.name or 'shutters' in ob.name)):continue
 for p in ob.data.polygons:
  v=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices];b=[[min(q[i] for q in v),max(q[i] for q in v)] for i in range(3)]
  if b[0][0]<-15 and b[0][1]>-17 and b[1][0]<37 and b[1][1]>25.2 and b[2][0]<10 and b[2][1]>7.2 and b[1][1]-b[1][0]>.2 and b[2][1]-b[2][0]>.2:rows.append({'name':ob.name,'bounds':b})
(O/'evidence/house-openings.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
