import bpy,json,hashlib,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];s=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');bpy.context.window.scene=s;s.camera=bpy.data.objects['13-CONTINUOUS-STRAIGHT-WALK'];s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=2;s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
folder=O/'renders/walk';folder.mkdir(exist_ok=True);path=O/'evidence/render-walk.json';rows=json.loads(path.read_text())if path.exists()else[]
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
rows=[r for r in rows if r.get('masterSHA256')==sha]
for i in range(80):
 f=folder/f'{i:04}.png'
 if any(r['index']==i and r['masterSHA256']==sha for r in rows)and f.exists():continue
 frame=round(1+959*i/79);s.frame_set(frame);bpy.context.view_layer.update();assert abs(s.camera.location.x)<1e-5;s.render.filepath=str(f)
 start=time.monotonic();bpy.ops.render.render(write_still=True)
 rows.append({'index':i,'sourceFrame':frame,'position':list(s.camera.location),'rotationEuler':list(s.camera.rotation_euler),'seconds':time.monotonic()-start,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'masterSHA256':sha,'resolution':[480,270],'samples':2,'engine':s.render.engine})
 path.write_text(json.dumps(rows,indent=2)+'\n');print('WALK_FRAME',i,frame,flush=True)
print('ACTUAL_WALK_COMPLETE','80 sampled Blender frames, 40 seconds at 2fps; not interactive FPS',flush=True)
