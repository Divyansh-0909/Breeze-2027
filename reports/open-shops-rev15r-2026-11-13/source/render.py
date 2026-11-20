import bpy,json,time,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'evidence/build-verification.json').read_text());P=Path(proof['editedMaster']);assert hashlib.sha256(P.read_bytes()).hexdigest()==proof['editedSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P));before=bpy.data.scenes['REV15P / Isolated Night Atmosphere Pilot'];after=bpy.data.scenes[proof['newScene']]
world=bpy.data.worlds.new('REVIEW ONLY / shop inspection ambient');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.32,.36,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
def inspect(source,key):
 s=bpy.data.scenes.new('REVIEW ONLY / '+key);s.world=world
 for o in source.objects:
  if o.type!='CAMERA':s.collection.objects.link(o)
 s.view_settings.view_transform=source.view_settings.view_transform;s.view_settings.look=source.view_settings.look;s.view_settings.exposure=source.view_settings.exposure
 for name,energy,c,rotation in [('key',1.6,(1,.91,.78),(math.radians(28),math.radians(-25),math.radians(-30))),('fill',.7,(.76,.85,1),(math.radians(20),math.radians(55),math.radians(150)))]:
  d=bpy.data.lights.new('REVIEW ONLY / '+key+' '+name,'SUN');d.energy=energy;d.color=c;d.angle=.35;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=rotation
 return s
bi=inspect(before,'before');ai=inspect(after,'after');results=[]
def capture(scene,key,cameraSource=None,pos=None,target=None,lens=24):
 bpy.context.window.scene=scene;scene.frame_set(1)
 d=bpy.data.cameras.new('REVIEW / '+key);d.sensor_width=36;d.lens=lens;d.clip_start=.06;d.clip_end=200;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o)
 if cameraSource:
  assert cameraSource.parent is None;o.location=cameraSource.location.copy();o.rotation_euler=cameraSource.rotation_euler.copy();d.lens=cameraSource.data.lens
 else:o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 scene.camera=o;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=12;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'renders'/f'{key}.png');t=time.monotonic();print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True);results.append({'key':key,'seconds':time.monotonic()-t,'lighting':'Native approved night plus local shelf practicals' if scene==after else 'Identical temporary inspection world/key/fill; native shop practicals retained','position':list(o.location),'lens':d.lens,'sha256':hashlib.sha256((R/'renders'/f'{key}.png').read_bytes()).hexdigest()});(R/'evidence/captures.json').write_text(json.dumps(results,indent=2));scene.collection.objects.unlink(o)
for i,shop in enumerate(proof['shops']):
 key=shop['id'];cam=next(o for o in before.objects if o.type=='CAMERA' and o.name.endswith(['/ 21-shop-left-25','/ 22-shop-left-7','/ 23-shop-left2','/ 24-shop-right-16','/ 25-shop-right-7'][i]))
 capture(bi,key+'-before',cameraSource=cam);capture(ai,key+'-after',cameraSource=cam)
capture(after,'night-chai',pos=(.6,-8.8,7.87),target=(-5.4,-7,7.65),lens=25)
capture(after,'night-kirana',pos=(.6,-26.8,7.72),target=(-5.4,-25,7.55),lens=25)
capture(after,'night-lane',pos=(0,-13,8.2),target=(0,6,10),lens=22)
print('RENDER_DONE',len(results),flush=True)
