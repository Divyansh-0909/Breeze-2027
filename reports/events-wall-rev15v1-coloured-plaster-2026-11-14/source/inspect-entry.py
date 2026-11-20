import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15V1-Events-Coloured-Plaster.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 if not any(k.lower() in o.name.lower() for k in ['gate','GULLYVERSE','Past Sponsors plaque','main post','sign post','F1 / mineral','F2 / mineral','ground surface','ramp','lane road','events house shell']):continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type not in ['EMPTY'] else [o.matrix_world.translation];rows.append({'name':o.name,'type':o.type,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
(R/'evidence/entry-layout.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
