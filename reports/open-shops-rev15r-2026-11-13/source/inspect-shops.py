import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/workspace/Breeze-2027/reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend');s=bpy.context.scene;rows=[]
for o in s.objects:
 if o.type=='MESH' and any(k in o.name.lower() for k in ['shop','counter','shelf','stock','kettle','jar','sack']):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'lo':[min(p[i] for p in pts) for i in range(3)],'hi':[max(p[i] for p in pts) for i in range(3)],'materials':[m.name if m else None for m in o.data.materials],'hidden':o.hide_render})
(R/'evidence/shop-inventory.json').write_text(json.dumps(rows,indent=2));print('objects',len(rows))
