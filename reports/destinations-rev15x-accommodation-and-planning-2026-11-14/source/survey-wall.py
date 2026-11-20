import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15W-Streetlights-and-Overhead-Cables.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[];samples=[];deps=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if o.type!='MESH' or not any(k in o.name for k in ['/ F1 /','Existing Events house shell']):continue
 for f in o.data.polygons:
  ps=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];n=(o.matrix_world.to_3x3().inverted().transposed()@f.normal).normalized()
  if n.y<.9 or max(p.z for p in ps)<7.15 or min(p.z for p in ps)>10.7 or min(p.x for p in ps)>-8 or max(p.y for p in ps)<12.8 or min(p.y for p in ps)>14.6:continue
  rows.append({'object':o.name,'face':f.index,'material':o.material_slots[f.material_index].material.name,'points':[list(p)for p in ps]})
for z in [7.4,7.9,8.4,8.9,9.4,9.9]:
 line=[]
 for i in range(39):
  x=-27.5+i*.5;hit=s.ray_cast(deps,Vector((x,16,z)),Vector((0,-1,0)),distance=6)
  line.append({'x':x,'z':z,'hit':hit[4].name if hit[0] else None,'point':list(hit[1])if hit[0]else None,'face':hit[3]if hit[0]else None})
 samples.append(line)
(R/'evidence/accommodation-wall-survey.json').write_text(json.dumps({'faces':rows,'samples':samples},indent=2)+'\n');print("WALL_SURVEY_PASS",len(rows))
