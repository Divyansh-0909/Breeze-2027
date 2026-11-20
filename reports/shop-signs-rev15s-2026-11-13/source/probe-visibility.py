import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=json.loads((R/'evidence/build-verification.json').read_text());bpy.ops.wm.open_mainfile(filepath=p['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rows=[]
for dz in [.16,-.15,-.35]:
 origin=Vector((.8,-8.1,8.95));target=Vector((-3.545,-7,9.8+dz));hit,loc,nor,idx,o,mat=s.ray_cast(deps,origin,(target-origin).normalized(),distance=(target-origin).length+.1);rows.append({'dz':dz,'hit':o.name if hit else None,'position':list(loc) if hit else None})
(R/'evidence/sign-raycast.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
