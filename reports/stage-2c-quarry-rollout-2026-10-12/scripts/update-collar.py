"""Finish the generated collar without reauthoring the already fitted perimeter."""
import bpy,bmesh,sys,json,math,ast,numpy as np
from pathlib import Path
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts/blender'))
from quarry_rollout_geometry import SOURCE,gate,reflect
SRC=ROOT/'assets-source/gullyverse/quarry-rollout';OUT=ROOT/'public/models/gullyverse/quarry-rollout'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'quarry-limestone.blend'));mat=bpy.data.materials['Approved_Cool_Grey_Limestone_Family'];rows=[]
module=ast.parse((ROOT/'scripts/blender/author_quarry_rollout.py').read_text());wanted={'B','G','create','stats','decimate','surface_geometry'}
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)and n.name in wanted],type_ignores=[]),'selected_author_functions','exec'))
for name in ['Quarry_Exit_Master',*[f'Quarry_Exit_LOD{i}'for i in range(3)]]:
 o=bpy.data.objects[name];mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
 if mesh.users==0:bpy.data.meshes.remove(mesh)
points,faces,a,b,distance,count,boundary=surface_geometry(SOURCE['exitAttributes'],[(0,len(SOURCE['exitAttributes']['position'])//3)],True,n=10);master=create('Quarry_Exit_Master',points,faces,a,b,bpy.data.collections['EDITABLE_QUARRY_GEOLOGY']);stats(master);group=master.vertex_groups.new(name='SIMPLIFIABLE');group.add([i for i in range(len(points))if distance[i%count]>1e-5],1,'REPLACE')
for i,t in enumerate([12000,4000,1400]):
 o=decimate(master,f'Quarry_Exit_LOD{i}',t,bpy.data.collections[f'RUNTIME_LOD{i}']);o.parent=bpy.data.objects[f'Quarry_LOD{i}'];stats(o)
m=json.loads((OUT/'manifest.json').read_text());lo=points.min(axis=0);hi=points.max(axis=0)
for p in m['parts']:
 if p['name']=='Quarry_Exit':p.update(center=((lo+hi)/2).tolist(),radius=float(np.linalg.norm((hi-lo)/2)))
m['nodes']=[x for x in m['nodes']if not x['name'].startswith('Quarry_Exit')]+rows;m['collarReturn']='Swept along the existing bent tunnel centerline, expanded into existing rock mass; original front opening and roof seams retained.'
def export(path,selected):
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)
objects=[[bpy.data.objects[p['nodes'][i]]for p in m['parts']]for i in range(3)];levels=[bpy.data.objects[f'Quarry_LOD{i}']for i in range(3)];proxy=bpy.data.objects['Wall_Collision']
export(OUT/'quarry-limestone.glb',[o for level in objects for o in level]+levels+[proxy])
for i in range(3):export(OUT/f'quarry-lod{i}.glb',objects[i]+[levels[i]])
export(OUT/'quarry-collision.glb',[proxy]);master.hide_set(True);proxy.hide_set(True)
for i in range(2):levels[i].hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'quarry-limestone.blend'))
for p in[SRC/'manifest.json',OUT/'manifest.json']:p.write_text(json.dumps(m,indent=2))
print('COLLAR_FINAL',rows)
