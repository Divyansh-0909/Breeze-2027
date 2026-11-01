import bpy,json,math
from pathlib import Path
p=Path('/workspace/gullyverse-world-concept/2026-10-25/04-straight-walk-semicircular-crowd')
people=json.loads((p/'evidence/crowd-composition.json').read_text())['people'];bad=[]
for s in bpy.data.scenes:
 bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
 for person in people:
  obj=bpy.data.objects[person['label']+' shirt']
  if obj.name not in s.objects:continue
  x,y,_=person['foot'];delta=math.hypot(obj.location.x-x,obj.location.y-y)
  if delta>1e-4:bad.append({'scene':s.name,'label':person['label'],'expected':person['foot'],'location':list(obj.location),'matrixLocation':list(obj.matrix_world.translation),'delta':delta})
(p/'evidence/crowd-probe.json').write_text(json.dumps(bad,indent=2));print('BAD',json.dumps(bad))
