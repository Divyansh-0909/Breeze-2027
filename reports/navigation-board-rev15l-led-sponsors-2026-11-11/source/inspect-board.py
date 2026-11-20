import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1]
P=O.parent/'team-wall-rev15k-black-brick-2026-11-11/delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15K');bpy.context.window.scene=s;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.type=='FONT' or any(t in o.name for t in ['Navigation','Reused sign','GULLYVERSE hero','Signboard practical','board foot']):
  rows.append({'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'body':o.data.body if o.type=='FONT' else None,'parent':o.parent.name if o.parent else None,'rotation':list(o.rotation_euler),'scale':list(o.scale),'props':dict(o.items())})
(O/'evidence/board-baseline.json').write_text(json.dumps(rows,indent=2,default=str));print(json.dumps(rows,indent=2,default=str))
