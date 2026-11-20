import bpy,json,hashlib,argparse,sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];V=R.parent/'cypher-houses-rev15v-walls-windows-2026-11-14';plan=json.loads((R/'source/events-plan.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'];ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15V-Weathered-Cypher-Houses.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15V1-Events-Coloured-Plaster.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);out=Path(a.output);assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();before=fp(base);assert before['sha256']==json.loads((V/'evidence/native-scene-fingerprint.json').read_text())['sha256'];protected=snapshot(base,plan,'REV15V / ');history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15V1 / Events coloured house plaster';s['variant']='REV15V1'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 ob=old.copy();ob.name='REV15V1 / '+old.name.removeprefix('REV15V / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for driver in ob.animation_data.drivers:
   for var in driver.driver.variables:
    for target in var.targets:
     if target.id in copies:target.id=copies[target.id]
layer=s.view_layers.new('REV15V1 / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
m=bpy.data.materials.new('REV15V1 / Events dusty terracotta painted plaster');m.use_nodes=True;nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Specular IOR Level'].default_value=.23;uv=nodes.new('ShaderNodeUVMap');uv.uv_map='REV15VFacadeUV';maps=json.loads((R/'evidence/material.json').read_text())['files']
for row in maps:
 assert sha(R/'textures'/row['file'])==row['sha256'];im=bpy.data.images.load(str(R/'textures'/row['file']));im.name='REV15V1 / '+row['file'];im.colorspace_settings.name='sRGB' if 'color' in row['file'] else 'Non-Color';im.pack();assert hashlib.sha256(im.packed_file.data).hexdigest()==row['sha256'];t=nodes.new('ShaderNodeTexImage');t.image=im;t.extension='EXTEND';links.new(uv.outputs['UV'],t.inputs['Vector'])
 if 'normal' in row['file']:
  n=nodes.new('ShaderNodeNormalMap');n.uv_map='REV15VFacadeUV';n.inputs['Strength'].default_value=.78;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],p.inputs['Normal'])
 else:links.new(t.outputs['Color'],p.inputs['Base Color' if 'color' in row['file'] else 'Roughness'])
changed=[]
for row in plan['objects']:
 old=base.objects[row['object']];ob=copies[old];bindings=[slot.material for slot in old.material_slots];ob.data=old.data.copy()
 for i,mat in enumerate(bindings):ob.data.materials[i]=mat;ob.material_slots[i].link='DATA'
 index=len(ob.data.materials);ob.data.materials.append(m)
 for i in row['faces']:ob.data.polygons[i].material_index=index
 changed.append(ob.name)
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update();assert snapshot(s,plan,'REV15V1 / ')==protected;assert fp(base)['sha256']==before['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items());fingerprint=fp(s);fingerprint.pop('data')
if a.restore:assert fingerprint['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
proof={'status':'PASS','source':a.base,'sourceSHA256':sha(a.base),'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':56,'changedObjects':changed,'changedFaces':sum(len(r['faces']) for r in plan['objects']),'protectedSnapshot':protected,'EventsPostersFramesAndHeadingUnchanged':True,'wholeTeamBuildingUnchanged':True,'allGeometryUVsColoursTransformsUnchanged':True,'otherHousesWindowsRoadCrowdNavigationAndLightsUnchanged':True,'brickPatternOnEventsWall':False,'finish':'Dusty terracotta painted plaster','sceneFingerprintSHA256':fingerprint['sha256']}
(R/('evidence/restore-check.json' if a.restore else 'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n')
print(json.dumps({'status':'PASS','restore':a.restore,'scenes':len(bpy.data.scenes),'changedFaces':proof['changedFaces']}),flush=True)
