import bpy,sys,json,time,os
from pathlib import Path
O=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];mode=args[0]if args else'preview';jobs=[]
if mode=='preview':jobs=[('C',n)for n in ['01-landing','03-opening','04-hub']]
elif mode=='revision':jobs=[(v,n)for v in ['A','B','C']for n in ['01-landing','02-lane-walk','03-opening','04-hub','11-overhead','12-mobile-landing']]
elif mode=='final':jobs=[(v,n)for v in ['A','B','C']for n in ['01-landing','02-lane-walk','03-opening','04-hub','05-team','06-events','07-cutscene-begin','08-cutscene-mid','09-screen-reveal','10-screen-watch','11-overhead','12-mobile-landing']]
elif mode=='composition-fix':jobs=[(v,n)for v in ['A','B','C']for n in ['04-hub','05-team','06-events','11-overhead']]
elif mode=='animatic':jobs=[('C','13-CROWD-MOVE-20s',f)for f in [1,44,88,132,175,219,263,306,350,394,437,480]]
manifest=O/'evidence/render-manifest.json';records=json.loads(manifest.read_text())if manifest.exists()else[]
for job in jobs:
 v,name=job[:2];frame=job[2]if len(job)>2 else 1;scene=next(s for s in bpy.data.scenes if s.name.startswith(v+' /'));bpy.context.window.scene=scene;scene.camera=bpy.data.objects[name];scene.frame_set(frame)
 target=O/('renders'if mode!='preview'else'evidence/preview')/v/(name+(f'-{frame:03}'if len(job)>2 else'')+'.png');target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():print('EXISTS',target,flush=True);continue
 mobile='mobile'in name
 scene.render.resolution_x=540 if mobile else 720 if mode=='preview'else 640 if mode=='animatic'else 1200;scene.render.resolution_y=960 if mobile else 450 if mode=='preview'else 400 if mode=='animatic'else 750
 scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=8 if mode in ['preview','animatic']else 16;scene.cycles.use_denoising=False;scene.cycles.samples=12;scene.render.filepath=str(target);start=time.time();print('RENDER_START',v,name,frame,flush=True);bpy.ops.render.render(write_still=True,scene=scene.name);elapsed=time.time()-start
 records.append({'variant':v,'camera':name,'frame':frame,'file':str(target.relative_to(O)),'mode':mode,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':scene.eevee.taa_render_samples,'engine':scene.render.engine,'device':'Blender offscreen OpenGL software driver; not physical GPU certification','seconds':elapsed,'position':list(scene.camera.location),'rotationEuler':list(scene.camera.rotation_euler),'lens':scene.camera.data.lens,'sensor':scene.camera.data.sensor_width,'cameraType':scene.camera.data.type,'exposure':scene.view_settings.exposure});manifest.write_text(json.dumps(records,indent=2));print('RENDER_SAVED',target,round(elapsed,2),flush=True)
print('RENDER_JOBS_COMPLETE',len(jobs),flush=True)
