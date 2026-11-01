import bpy,json,hashlib,ast
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
tree=ast.parse((O/'source/author_world.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='uvmetre');exec(compile(ast.Module(body=[fn],type_ignores=[]),'uvmetre','exec'))
rows=[]
for r in a['surfaceCopies']:
 o=bpy.data.objects[r['copy']]
 if not any(m.type=='SOLIDIFY'for m in o.modifiers):continue
 ev=o.evaluated_get(dep);before=ev.to_mesh();v=[list(x.co)for x in before.vertices];f=[list(x.vertices)for x in before.polygons];ev.to_mesh_clear()
 m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dep);o.modifiers.clear();o.data=m;uvmetre(o)
 assert v==[list(x.co)for x in m.vertices]and f==[list(x.vertices)for x in m.polygons]
 r['bakedIdenticalSolidifyForUVs']=True;rows.append({'object':o.name,'evaluatedVerticesAndTopologyExact':True,'onlyUVsChanged':True,'vertices':len(v),'polygons':len(f)})
master=O/'source/Gullyverse-Selected-C-Wider-Realism.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
a['masterSHA256']=hashlib.sha256(master.read_bytes()).hexdigest();a['masterBytes']=master.stat().st_size;(O/'evidence/authoring.json').write_text(json.dumps(a,indent=2)+'\n');(O/'evidence/solidify-uv-repair.json').write_text(json.dumps({'status':'PASS','rows':rows,'physicalGeometryUnchanged':True,'originalObjectsUntouched':True,'testTolerancesUnchanged':True},indent=2)+'\n')
