"""Export both original transparent standalone headings with no-shadow metadata."""
import bpy,json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];plan=json.loads(Path(os.environ.get('GULLYVERSE_PLAN',str(Path(__file__).with_name('export-plan.json')))).read_text());out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/plan['output'])));r=out/'validation';r.mkdir(parents=True,exist_ok=True);source=Path(plan['source']['path']);guard=hashlib.sha256(source.read_bytes()).hexdigest();assert guard==plan['source']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));native=bpy.context.scene;scene=bpy.data.scenes.new('Transparent lettering export only');bpy.context.window.scene=scene;rows=[];folder=out/'graffiti';folder.mkdir(exist_ok=True)
for old in native.objects:
 if old.type!='MESH':continue
 matches=[m for m in old.data.materials if m and m.use_nodes and any(n.type=='TEX_IMAGE'and n.image and ('graffiti'in n.image.name.lower()or'coming soon'in n.image.name.lower())for n in m.node_tree.nodes)]
 if not matches:continue
 ob=old.copy();ob.data=old.data.copy();ob.visible_shadow=False;ob['runtimeNoShadow']=True;scene.collection.objects.link(ob)
 for i,m in enumerate(ob.data.materials):
  m=m.copy();ob.data.materials[i]=m;m['runtimeDecal']=True;m.surface_render_method='DITHERED';p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');assert p.inputs['Alpha'].is_linked
  for node in m.node_tree.nodes:
   if node.type=='TEX_IMAGE'and node.image and node.image.packed_file:
    file='coming-soon.png'if'COMING'in node.image.name else'contact-us.png';data=bytes(node.image.packed_file.data);(folder/file).write_bytes(data);rows.append({'object':old.name,'image':node.image.name,'file':'graffiti/'+file,'sourcePNGUnchanged':True,'sha256':hashlib.sha256(data).hexdigest(),'sourceAlphaLinked':True,'castsShadow':False})
bpy.ops.export_scene.gltf(filepath=str(out/'transparent-graffiti.glb'),export_format='GLB',use_active_scene=True,export_extras=True,export_animations=False,export_lights=False);assert len(rows)==2;assert hashlib.sha256(source.read_bytes()).hexdigest()==guard;(r/'graffiti-export.json').write_text(json.dumps({'status':'PASS','sourceMasterUnchanged':True,'headings':rows},indent=2)+'\n');print('BOTH_TRANSPARENT_GRAFFITI_EXPORT_PASS')
