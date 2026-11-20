import bpy,json,time,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'evidence/build-verification.json').read_text());P=Path(proof['editedMaster']);assert hashlib.sha256(P.read_bytes()).hexdigest()==proof['editedSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P));after=bpy.context.scene;before=bpy.data.scenes['REV15S / Reference-led realistic shop name boards']
w=bpy.data.worlds.new('REVIEW ONLY / neutral ground inspection');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.26,.29,.32,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
def inspection(src,name):
 s=bpy.data.scenes.new('REVIEW ONLY / '+name);s.world=w
 for o in src.objects:
  if o.type!='CAMERA':s.collection.objects.link(o)
 for k in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,k,getattr(src.view_settings,k))
 for name,e,col,rot in [('key',1.8,(1,.92,.80),(28,-25,-30)),('fill',.65,(.76,.85,1),(20,55,150))]:
  d=bpy.data.lights.new('REVIEW ONLY / '+name,'SUN');d.energy=e;d.color=col;d.angle=.35;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
 return s
bi=inspection(before,'before');ai=inspection(after,'after');rows=[]
def capture(sc,key,pos,target,lens=23):
 bpy.context.window.scene=sc;sc.frame_set(1);d=bpy.data.cameras.new('REVIEW / '+key);d.lens=lens;d.sensor_width=36;d.clip_start=.055;d.clip_end=180;o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();sc.camera=o;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=1280;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94;path=R/'renders'/f'{key}.jpg';sc.render.filepath=str(path);t=time.monotonic();print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True);rows.append({'key':key,'file':str(path.relative_to(R)),'position':pos,'target':target,'lens':lens,'lighting':'Unchanged native night lighting' if sc==after else 'Matched temporary inspection ambient and sun lights','masterSHA256':proof['editedSHA256'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.monotonic()-t});(R/'evidence/captures.json').write_text(json.dumps(rows,indent=2)+'\n');sc.collection.objects.unlink(o)
shots=[
 ('01-lane',(0,-28.8,7.72),(.15,-13.5,6.2),23),
 ('02-approach',(.2,1.6,8.3),(-2,20.5,7.35),22),
 ('03-cypher',(2.7,17.5,8.92),(-5.1,25,7.2),22)]
preview='--preview' in sys.argv
if preview:
 for key,p,t,l in [shots[0],shots[2]]:capture(ai,key+'-after',p,t,l)
 capture(ai,'04-pothole-after',(.35,-25.55,7.34),(2.43,-23.6,5.97),36)
else:
 for key,p,t,l in shots:
  capture(bi,key+'-before',p,t,l);capture(ai,key+'-after',p,t,l)
 capture(ai,'04-pothole-after',(.35,-25.55,7.34),(2.43,-23.6,5.97),36)
 capture(ai,'05-overview-after',(0,12,24),(-1,24,7.2),23)
 for key,p,t,l in [shots[0],shots[2]]:capture(after,key+'-night',p,t,l)
print('CAPTURES_DONE',len(rows),flush=True)
