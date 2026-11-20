import bpy,json,re
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'crowd-rev15m-aftermovie-models-2026-11-11/delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if re.search('event|poster|cypher|Team wall black',ob.name,re.I):
  bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];rows.append({'name':ob.name,'type':ob.type,'data':ob.data.name if ob.data else None,'location':list(ob.location),'dimensions':list(ob.dimensions),'bounds':[[min(p[i] for p in bb),max(p[i] for p in bb)] for i in range(3)],'materialNames':[m.name if m else '' for m in ob.data.materials] if ob.type=='MESH' else [],'materialFaceCounts':{str(i):sum(p.material_index==i for p in ob.data.polygons) for i in set(p.material_index for p in ob.data.polygons)} if ob.type=='MESH' else {},'props':dict(ob.items()),'body':ob.data.body if ob.type=='FONT' else None})
(O/'evidence/wall-baseline.json').write_text(json.dumps(rows,indent=2,default=str));print(json.dumps(rows,default=str),flush=True)
