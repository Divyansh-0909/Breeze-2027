import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15X-Accommodation-Coming-Soon.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 if 'Entry parapet return'not in o.name or o.type!='MESH':continue
 row={'name':o.name,'materials':[],'faces':len(o.data.polygons),'matrix':[list(x)for x in o.matrix_world]}
 for slot in o.material_slots:
  m=slot.material;r={'name':m.name,'link':slot.link,'principled':[]}
  for n in m.node_tree.nodes:
   if n.type!='BSDF_PRINCIPLED':continue
   for key in ['Base Color','Roughness','Metallic']:
    v=n.inputs[key];r['principled'].append({'input':key,'links':[(l.from_node.name,l.from_node.type,l.from_socket.identifier)for l in v.links]})
  row['materials'].append(r)
 rows.append(row)
(R/'evidence/survey.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
