import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15L-Navigation-LED.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=json.loads((O/'evidence/blender-validation.json').read_text())['masterSHA256'];assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15L');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
manifest=json.loads((O/'evidence/board-manifest.json').read_text());originals=[s.objects[n] for n in manifest['boardObjects']]+[o for o in s.objects if 'board foot' in o.name]
copies=[];records=[]
for original in originals:
 if original.type not in ['MESH','FONT','CURVE']:continue
 evaluated=original.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);mesh.transform(evaluated.matrix_world);mesh.update()
 ob=bpy.data.objects.new('NAV REVIEW / '+original.name,mesh);ob['sourceType']=original.type
 if original.type=='FONT':ob['navigationLabel']=original.data.body
 if 'hero raster' in original.name:ob['navigationLabel']='GULLYVERSE'
 if original.get('ledScreen'):
  mesh.materials.clear();mat=bpy.data.materials.new('LED runtime shader placeholder');mat.diffuse_color=(.003,.003,.003,1);mesh.materials.append(mat);ob['ledScreen']=True
 bounds=[(min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)) for i in range(3)]
 records.append({'name':original.name,'type':original.type,'body':original.data.body if original.type=='FONT' else None,'worldBounds':bounds})
 copies.append(ob)
scene=bpy.data.scenes.new('NAV REVIEW / active board only');bpy.context.window.scene=scene
for ob in copies:scene.collection.objects.link(ob)
bpy.context.view_layer.update()
for ob in scene.objects:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'viewer/board.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_extras=True)
labels={r['body']:r for r in records if r['body']}
assert labels['AFTERMOVIE']['worldBounds'][2][0]>labels['EVENTS  <']['worldBounds'][2][1]
assert labels['PAST SPONSORS']['worldBounds'][2][0]<labels['SCHEDULE']['worldBounds'][2][0]
assert sha(P)==expected
(O/'evidence/viewer-export.json').write_text(json.dumps({'status':'PASS','masterUnchanged':True,'oneActiveSceneOnly':True,'transformsBakedFromFreshMaster':True,'parts':records,'glbSHA256':sha(O/'viewer/board.glb')},indent=2));print('FRESH BOARD EXPORT PASS',len(copies),flush=True)
