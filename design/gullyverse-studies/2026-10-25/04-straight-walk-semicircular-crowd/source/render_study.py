import bpy,sys,json,time,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];mode=sys.argv[sys.argv.index('--')+1]if'--'in sys.argv else'stills'
poses=['01-landing','03-opening','04-hub','08-crowd-middle','09-screen-front','11-overhead']
if mode=='stills':
    jobs=[('C','15-semicircle-high',1),('C','16-rooftop-plan',1)]
    jobs += [(v,n,1)for v in ['C','A','B']for n in poses]
    jobs += [('C','02-lane-walk',1),('C','12-mobile-landing',1),('C','14-board-arrival',1)]
elif mode=='walk':jobs=[('C','13-CONTINUOUS-STRAIGHT-WALK',f)for f in range(300,780,4)]
else:raise ValueError(mode)
manifest=O/'evidence/render-manifest.json';rows=json.loads(manifest.read_text())if manifest.exists()else[]
for variant,name,frame in jobs:
    scene=next(s for s in bpy.data.scenes if s.name.startswith(variant+' /'));bpy.context.window.scene=scene;scene.camera=bpy.data.objects[name];scene.frame_set(frame)
    target=O/('walk-frames'if mode=='walk'else'renders')/variant/(f'{frame:04}.png'if mode=='walk'else name+'.png');target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():continue
    mobile='mobile'in name
    scene.render.resolution_x=384 if mode=='walk'else 540 if mobile else 1200
    scene.render.resolution_y=240 if mode=='walk'else 960 if mobile else 750
    scene.render.resolution_percentage=100;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=2 if mode=='walk'else 16
    scene.render.filepath=str(target);start=time.time();bpy.ops.render.render(write_still=True,scene=scene.name)
    rows.append({'variant':variant,'camera':name,'frame':frame,'mode':mode,'file':str(target.relative_to(O)),'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':scene.eevee.taa_render_samples,'engine':scene.render.engine,'seconds':time.time()-start,'position':list(scene.camera.location),'rotationEuler':list(scene.camera.rotation_euler),'lens':scene.camera.data.lens,'sensorWidthMM':scene.camera.data.sensor_width,'exposure':scene.view_settings.exposure,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    manifest.write_text(json.dumps(rows,indent=2)+'\n');print('SAVED',mode,variant,name,frame,flush=True)
print('RENDER_COMPLETE',mode,len(jobs),flush=True)
