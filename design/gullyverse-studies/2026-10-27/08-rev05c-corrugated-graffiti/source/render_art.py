import bpy,json,sys,hashlib,time,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from art_cameras import add_cameras
new=add_cameras();args=sys.argv[sys.argv.index('--')+1:];edition=args[0];variant=args[1]if len(args)>1 else'C'
assert edition in ['before','after','preview','profile-before','profile-after']
names=[f'ART-{k}-{kind}'for k in ['chaar-diwari','ritviz','neha-kakkar']for kind in ['front','grazing','context']]+['01-landing','12-mobile-landing','04-hub','ART-rooftop-back-context']
if variant=='C':names += [f'ART-{k}-{kind}'for k in ['chaar-diwari','ritviz','neha-kakkar']for kind in ['detail','mobile']]+['ART-wall-pier-left','ART-wall-pier-right','ART-wall-return-left','ART-wall-return-right','05-team','06-events','ART-lane-left-context','ART-lane-right-context']
if edition=='preview':names=['ART-chaar-diwari-front','ART-ritviz-grazing','ART-neha-kakkar-front','ART-wall-pier-left','ART-wall-return-right','01-landing']
if edition.startswith('profile-'):
 names=[f'ART-{k}-grazing'for k in ['chaar-diwari','ritviz','neha-kakkar']]
 m=bpy.data.materials.new('DIAGNOSTIC_SAME_NEUTRAL_METAL');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.28,.28,.28,1);bs.inputs['Roughness'].default_value=.60;bs.inputs['Metallic'].default_value=.30
 for o in bpy.data.objects:
  if o.name.startswith(('Closed rolling shutter','Shutter slat')):
   o.material_slots[0].link='OBJECT';o.material_slots[0].material=m
scene=next(s for s in bpy.data.scenes if s['variant']==variant);bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
manifest=O/f'evidence/render-{edition}-{variant}.json';rows=json.loads(manifest.read_text())if manifest.exists()else[]
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
for name in names:
 target=O/f'renders/{edition}/{variant}/{name}.png';target.parent.mkdir(parents=True,exist_ok=True)
 if any(r['camera']==name for r in rows)and target.exists():continue
 cam=bpy.data.objects[name];scene.camera=cam;mobile='mobile'in name
 scene.render.resolution_x=540 if mobile else 1200;scene.render.resolution_y=960 if mobile else 750;scene.render.resolution_percentage=100;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16;scene.render.filepath=str(target)
 if edition=='before'and name in ['01-landing','12-mobile-landing']and Path('/workspace/gullyverse-world-concept/2026-10-26/07-rev05c-support-off-artist-graffiti/evidence/render-manifest.json').exists():
  old=Path('/workspace/gullyverse-world-concept/2026-10-26/07-rev05c-support-off-artist-graffiti');meta=json.loads((old/'evidence/render-manifest.json').read_text());prior=next(r for r in meta if r['edition']=='off'and r['variant']==variant and r['camera']==name)
  source=old/prior['file'];assert prior['masterSHA256']==sha and hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256'];shutil.copyfile(source,target)
  prior.update(edition=edition,file=str(target.relative_to(O)),optionalSupportW=0,diagnostic=False,renderType='Exact existing0W baseline render reused after source master/hash verification')
  rows.append(prior);manifest.write_text(json.dumps(rows,indent=2)+'\n');print('ART_CACHED_BASELINE',variant,name,flush=True);continue
 start=time.monotonic();bpy.ops.render.render(write_still=True)
 row={'edition':edition,'variant':variant,'camera':name,'file':str(target.relative_to(O)),'position':list(cam.location),'rotationEuler':list(cam.rotation_euler),'lens':cam.data.lens,'sensorWidthMM':cam.data.sensor_width,'cameraType':cam.data.type,'orthoScale':cam.data.ortho_scale,'clipStart':cam.data.clip_start,'clipEnd':cam.data.clip_end,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'engine':scene.render.engine,'samples':16,'exposure':scene.view_settings.exposure,'viewTransform':scene.view_settings.view_transform,'look':scene.view_settings.look,'optionalSupportW':0,'seconds':time.monotonic()-start,'masterSHA256':sha,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'diagnostic':edition.startswith('profile-'),'renderType':'Actual Blender EEVEE software renderer, no physical-device FPS claim'}
 rows.append(row);manifest.write_text(json.dumps(rows,indent=2)+'\n');print('ART_CAPTURE',edition,variant,name,round(row['seconds'],2),flush=True)
print('ART_CAPTURES_COMPLETE',edition,variant,len(names),flush=True)
