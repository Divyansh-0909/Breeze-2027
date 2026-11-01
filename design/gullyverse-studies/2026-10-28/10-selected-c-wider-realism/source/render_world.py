import bpy,sys,json,time,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from world_cameras import SPECS,add
args=sys.argv[sys.argv.index('--')+1:];edition=args[0];wanted=args[1:]
s=next(s for s in bpy.data.scenes if s.get('variant')==('C+A PILOT'if edition=='before'else'C+A WORLD'))
bpy.context.window.scene=s;s.frame_set(1);add(s);bpy.context.view_layer.update()
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();manifest=O/f'evidence/render-{edition}.json';rows=json.loads(manifest.read_text())if manifest.exists()else[]
names=wanted or [x[0]for x in SPECS]
for name in names:
 path=O/f'renders/{edition}/{name}.png';path.parent.mkdir(parents=True,exist_ok=True)
 if any(x['pose']==name and x['masterSHA256']==sha for x in rows)and path.exists():continue
 s.camera=bpy.data.objects['WORLD REVIEW / '+name];portrait='mobile'in name
 s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_percentage=100;s.render.resolution_x=576 if portrait else 1280;s.render.resolution_y=1024 if portrait else 720;s.render.image_settings.file_format='PNG';s.render.filepath=str(path)
 supports=[o for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')];assert len(supports)==5 and all(o.data.energy==0 for o in supports)
 t=time.monotonic();bpy.ops.render.render(write_still=True);cam=s.camera
 rows=[r for r in rows if r['pose']!=name]
 rows.append({'edition':edition,'pose':name,'scene':s.name,'file':str(path.relative_to(O)),'position':list(cam.location),'rotationEuler':list(cam.rotation_euler),'lens':cam.data.lens,'sensorWidth':cam.data.sensor_width,'clipStart':cam.data.clip_start,'clipEnd':cam.data.clip_end,'resolution':[s.render.resolution_x,s.render.resolution_y],'engine':s.render.engine,'samples':16,'look':s.view_settings.look,'viewTransform':s.view_settings.view_transform,'exposure':s.view_settings.exposure,'world':s.world.name,'supportW':[o.data.energy for o in supports],'seconds':time.monotonic()-t,'masterSHA256':sha,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'evidenceType':'Actual offline Blender EEVEE; no browser DPR or physical-device FPS claim'})
 manifest.write_text(json.dumps(rows,indent=2)+'\n');print('LOOKDEV_CAPTURE',edition,name,rows[-1]['seconds'],flush=True)
