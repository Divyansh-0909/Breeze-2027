import bpy,sys,json,time,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from rooftop_cameras import SPECS,add
args=sys.argv[sys.argv.index('--')+1:];edition=args[0];variants={'A':'PHOTO A','B':'PHOTO B','new':'REV12','before':'REV11','H00':'REV11 H00','H06':'REV11 H06','H09':'REV11 H09'};s=next(s for s in bpy.data.scenes if s.get('variant')==variants[edition]);bpy.context.window.scene=s;s.frame_set(1);add(s)
extra=[('24-right-elevation',(70,32,15),(0,32,11),30,'ORTHO',68),('25-back-junction',(-16,44,13),(-24,50,13),24,'PERSP',0),('26-left-junction',(-15.7,28,8.92),(-20,25.2,10),24,'PERSP',0),('27-right-junction',(15.7,34,8.92),(22,38.1,10.8),24,'PERSP',0),('28-roof-joins',(-38,22,25),(-21,35,12),30,'PERSP',0)]
for n,p,t,l,k,ortho in extra:
 key='REV11 CAMERA / '+n;d=bpy.data.cameras.get(key)or bpy.data.cameras.new(key);d.type=k;d.lens=l;d.sensor_width=36;d.clip_start=.06;d.clip_end=300;d.ortho_scale=ortho or 6;o=bpy.data.objects.get(key)or bpy.data.objects.new(key,d)
 if o.name not in s.objects:s.collection.objects.link(o)
 o.location=p;o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();out=O/'evidence'/('render-'+edition+'.json');rows=json.loads(out.read_text())if out.exists()else[]
for pose in args[1:]:
 f=O/'renders'/edition/(pose+'.png');f.parent.mkdir(exist_ok=True,parents=True)
 if f.exists()and any(r['pose']==pose and r['masterSHA256']==sha for r in rows):continue
 s.camera=bpy.data.objects[('REV11 CAMERA / 'if pose.startswith(('24','25','26','27','28'))else'REV10 CAMERA / ')+pose];c=s.camera;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=576 if 'mobile'in pose else 1280;s.render.resolution_y=1024 if 'mobile'in pose else 720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(f);start=time.monotonic();bpy.ops.render.render(write_still=True)
 rows=[r for r in rows if r['pose']!=pose];rows.append({'edition':edition,'pose':pose,'file':str(f.relative_to(O)),'cameraPosition':list(c.location),'rotationEuler':list(c.rotation_euler),'lens':c.data.lens,'sensorWidth':c.data.sensor_width,'type':c.data.type,'orthoScale':c.data.ortho_scale,'viewport':[s.render.resolution_x,s.render.resolution_y],'pixelRatio':1,'samples':16,'engine':s.render.engine,'world':s.world.name,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'optionalSupportW':[o.data.energy for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')],'seconds':time.monotonic()-start,'masterSHA256':sha,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'evidence':'Actual offline Blender; no website/gameplay/device FPS claim'})
 out.write_text(json.dumps(rows,indent=2));print('CAPTURE',edition,pose,round(time.monotonic()-start,2),flush=True)
