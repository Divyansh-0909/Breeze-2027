import bpy,json,time,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=json.loads((R/'evidence/build-verification.json').read_text());P=Path(p['editedMaster']);assert hashlib.sha256(P.read_bytes()).hexdigest()==p['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));after=bpy.context.scene;before=bpy.data.scenes['REV15R / Reference-led open market shops']
w=bpy.data.worlds.new('REVIEW ONLY / signage comparison ambient');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.32,.36,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
def inspection(src,name):
 s=bpy.data.scenes.new('REVIEW ONLY / '+name);s.world=w
 for o in src.objects:
  if o.type!='CAMERA':s.collection.objects.link(o)
 for k in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,k,getattr(src.view_settings,k))
 for name,e,col,rot in [('key',1.6,(1,.91,.78),(28,-25,-30)),('fill',.7,(.76,.85,1),(20,55,150))]:
  d=bpy.data.lights.new('REVIEW ONLY / '+name,'SUN');d.energy=e;d.color=col;d.angle=.35;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=tuple(math.radians(v) for v in rot)
 return s
bi=inspection(before,'before');ai=inspection(after,'after');rows=[]
def capture(s,key,pos,target,lens=20):
 bpy.context.window.scene=s;s.frame_set(1);d=bpy.data.cameras.new('REVIEW / '+key);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=160;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=12;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'renders'/f'{key}.png');t=time.monotonic();print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True);rows.append({'key':key,'cameraPosition':pos,'target':target,'lens':lens,'lighting':'Actual native night plus sign lamps' if s==after else 'Same temporary inspection ambient/key/fill','masterSHA256':p['editedSHA256'],'sha256':hashlib.sha256((R/'renders'/f'{key}.png').read_bytes()).hexdigest(),'seconds':time.monotonic()-t});(R/'evidence/captures.json').write_text(json.dumps(rows,indent=2));s.collection.objects.unlink(o)
for shop in p['shops']:
 side,y,z=shop['side'],shop['y'],shop['boardCentreZ'];pos=(-side*1.5,y-.75,z-.6);target=(side*3.39,y,z-.95);key=shop['id'];capture(bi,key+'-before',pos,target,19.5);capture(ai,key+'-after',pos,target,19.5)
for shop in [p['shops'][1],p['shops'][3]]:
 side,y,z=shop['side'],shop['y'],shop['boardCentreZ'];capture(after,shop['id']+'-night',(-side*1.5,y-.75,z-.6),(side*3.39,y,z-.95),19.5)
print('DONE',len(rows),flush=True)
