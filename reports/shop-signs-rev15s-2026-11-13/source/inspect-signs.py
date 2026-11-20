import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=Path('/dev/shm/Gullyverse-Rev15R-Indian-Market-Open-Shops-Final.blend');assert P.exists();bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 if o.type=='FONT' or (o.type=='MESH' and any(k in o.name.lower() for k in ['sign','fascia','board','painted chai','painted general'])):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];row={'name':o.name,'type':o.type,'location':list(o.location),'lo':[min(p[i] for p in pts) for i in range(3)],'hi':[max(p[i] for p in pts) for i in range(3)]}
  if o.type=='FONT':row['body']=o.data.body
  if o.type=='MESH':row['materials']=[m.name if m else None for m in o.data.materials];row['images']=[n.image.name for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
  rows.append(row)
(R/'evidence/sign-inventory.json').write_text(json.dumps(rows,indent=2));print('SIGN_INVENTORY',len(rows))
