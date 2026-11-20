import bpy,json,re,collections
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'events-wall-rev15n-warm-brick-2026-11-11/delivery/Gullyverse-Rev15N-Events-House-Wall.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 mats=[m.name if m else '' for m in ob.data.materials]
 if re.search('rail|balustr|balcon',ob.name,re.I) or any('blackened zinc' in m for m in mats):
  bb=[ob.matrix_world@Vector(v) for v in ob.bound_box];rows.append({'name':ob.name,'data':ob.data.name,'bounds':[[min(p[i] for p in bb),max(p[i] for p in bb)] for i in range(3)],'materials':mats,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'props':dict(ob.items())})
(O/'evidence/rail-baseline.json').write_text(json.dumps(rows,indent=2,default=str));print('Rail/material candidates',len(rows),flush=True)
