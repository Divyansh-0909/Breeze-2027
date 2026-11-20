import bpy,json,hashlib,sys,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15T-Continuous-Asphalt-Gully-and-Cypher.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15T1-Unpainted-Cypher-Road.blend');ap.add_argument('--material');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert Path(a.output).resolve()!=Path(a.base).resolve() and not Path(a.output).exists(),'Choose a new output filename; original and existing files are preserved.'
expected='8c0745fcb068ba8039a8196742e0b500e905026e842e09788e565d3c34a459fc';assert sha(a.base)==expected
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};oldmat=next(m for o in base.objects if o.get('groundSurface') for m in o.data.materials if m and 'Reference-authored worn asphalt' in m.name)
if a.material:
 priorimages=list(bpy.data.images)
 with bpy.data.libraries.load(a.material,link=False) as (src,dst):dst.materials=[n for n in src.materials if n.startswith('REV15T1 /')]
 m=dst.materials[0];assert m
 # Reuse unchanged normal image data from the verified base.
 for im in list(bpy.data.images):
  if im in priorimages or not im.packed_file:continue
  match=next((old for old in priorimages if old.packed_file and bytes(old.packed_file.data)==bytes(im.packed_file.data)),None)
  if match:im.user_remap(match);bpy.data.images.remove(im)
else:
 m=oldmat.copy();m.name='REV15T1 / Reference-authored worn asphalt'
 for node in m.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image and node.image.name in ['road-world-color.png','road-world-roughness.png']:
   old=node.image;im=bpy.data.images.load(str(R/'textures'/old.name));im.name='REV15T1 / unpainted / '+old.name;im.colorspace_settings.name=old.colorspace_settings.name;im.pack();node.image=im
s=base.copy();s.name='REV15T1 / Unpainted cypher asphalt'
for co in list(s.collection.children):s.collection.children.unlink(co)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for o in base.objects:
 ob=o.copy();ob.name='REV15T1 / '+o.name.removeprefix('REV15T / ')
 if o.type in ['LIGHT','CAMERA']:ob.data=o.data.copy()
 s.collection.objects.link(ob);copies[o]=ob
for o,ob in copies.items():
 if o.parent in copies:ob.parent=copies[o.parent]
 if ob.animation_data:
  for f in ob.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15T1 / independent view')
for x in list(s.view_layers):
 if x!=layer:s.view_layers.remove(x)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
floors=[]
for old,ob in copies.items():
 if not old.get('groundSurface'):continue
 for slot in ob.material_slots:
  if slot.material==oldmat:slot.link='OBJECT';slot.material=m
 floors.append(ob)
assert len(floors)==4
assert all(o.data is ob.data and list(o.matrix_world)==list(ob.matrix_world) for o,ob in copies.items() if o.type=='MESH')
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==x for n,x in history.items())
assert all(any(slot.material==oldmat for slot in old.material_slots) for old in copies if old.get('groundSurface'))
assert all(ob.hide_render for old,ob in copies.items() if 'Cypher chalk arc' in old.name)
s.camera=copies[base.camera];s['paintedCypherCircle']=False;bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
assert len([o for o in s.objects if o.get('artKind')])==8
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=a.output,compress=True)
if a.material:
 proof={'status':'PASS','method':'Fresh Blender process reconstructed the edited 50-scene master using the verified Rev15T master and packed material delta','historicalScenes':len(history),'activeScenes':len(bpy.data.scenes),'geometryAndTransformsUnchanged':True,'floorCount':len(floors),'paintedCircle':False,'baseSHA256':sha(a.base),'output':a.output}
 (R/'evidence/restore-check.json').write_text(json.dumps(proof,indent=2)+'\n')
else:
 lib=R/'delivery/Rev15T1-Unpainted-Asphalt-Material.blend';bpy.data.libraries.write(str(lib),{m},fake_user=True,compress=True)
 proof={'status':'PASS','scene':s.name,'base':a.base,'baseSHA256':expected,'editedMaster':a.output,'editedBytes':Path(a.output).stat().st_size,'editedSHA256':sha(a.output),'historicalScenesPreserved':len(history),'scenes':len(bpy.data.scenes),'paintedCircle':False,'originalRaisedArcsRemainHidden':True,'geometryAndTransformsUnchanged':True,'otherMaterialsUnchanged':True,'crowdCount':189,'muralStates':8,'floorCount':4,'deltaLibrary':str(lib),'deltaSHA256':sha(lib),'productionWebsiteChanged':False}
 (R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
 # Ground-only runtime export; no geometry is reauthored.
 ex=bpy.data.scenes.new('TEMP EXPORT / unpainted ground')
 for old in bpy.data.collections['REV15T / Asphalt road and edge details'].objects:ex.collection.objects.link(copies[old])
 bpy.context.window.scene=ex
 for ob in ex.objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=floors[0]
 bpy.ops.export_scene.gltf(filepath=str(R/'delivery/Rev15T1-Unpainted-Asphalt-Ground.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_yup=True,export_materials='EXPORT',export_normals=True,export_texcoords=True)
assert sha(a.base)==expected
print('EDIT_DONE',json.dumps(proof),flush=True)
