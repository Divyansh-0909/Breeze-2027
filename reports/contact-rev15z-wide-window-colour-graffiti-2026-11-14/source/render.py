import bpy,json,hashlib,time,sys,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());m=json.loads((R/'delivery/window-manifest.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(b['editedMaster'])==b['editedSHA256'];ap=argparse.ArgumentParser();ap.add_argument('--keys');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();n=Vector(m['normal']);t=Vector(m['tangent']);p=Vector(m['frameCentre']);p.z=8.95;world=s.world;exposure=s.view_settings.exposure;lights={o.name:(o.data.energy,list(o.data.color))for o in s.objects if o.type=='LIGHT'}
shots=[('01-contact-inspection',p+n*6.7,p,35,True),('02-contact-night',p+n*6.7,p,35,False),('03-contact-context',p+n*6.9+t*.8+Vector((0,0,.35)),p,29,True),('04-accommodation-inspection',Vector((-12.015,18.6,8.9)),Vector((-12.015,14,8.8)),29,True),('05-accommodation-night',Vector((-12.015,18.6,8.9)),Vector((-12.015,14,8.8)),29,False)]
if a.keys:shots=[x for x in shots if x[0]in a.keys.split(',')]
rows=json.loads((R/'evidence/captures.json').read_text())['captures']if(R/'evidence/captures.json').exists()else[]
for key,pos,target,lens,inspection in shots:
 temporary=[]
 if inspection:
  w=bpy.data.worlds.new('TEMPORARY REVIEW ONLY / neutral inspection');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.34,.38,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.45;s.world=w
  for suffix,power,color,rot in [('key',1.6,(1,.95,.87),(.5,-.4,-.6)),('fill',.7,(.75,.84,1),(.7,.3,2))]:
   data=bpy.data.lights.new('TEMPORARY REVIEW ONLY / '+suffix,'SUN');data.energy=power;data.color=color;data.angle=.4;ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob);ob.rotation_euler=rot;temporary.append(ob)
 data=bpy.data.cameras.new('REVIEW / '+key);cam=bpy.data.objects.new(data.name,data);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.05;s.camera=cam;s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.eevee.taa_render_samples=12;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94;s.render.filepath=str(R/'renders'/(key+'.jpg'));print('RENDER',key,flush=True);start=time.monotonic();bpy.ops.render.render(write_still=True);rows=[x for x in rows if x['key']!=key]+[{'key':key,'file':'renders/'+key+'.jpg','sha256':sha(R/'renders'/(key+'.jpg')),'masterSHA256':b['editedSHA256'],'lighting':'TEMPORARY NEUTRAL INSPECTION; NOT SAVED'if inspection else'ACTUAL SAVED NIGHT LIGHTING','camera':list(pos),'target':list(target),'seconds':time.monotonic()-start}];s.world=world
 for ob in temporary:bpy.data.objects.remove(ob,do_unlink=True)
 assert s.view_settings.exposure==exposure and all((s.objects[k].data.energy,list(s.objects[k].data.color))==v for k,v in lights.items());(R/'evidence/captures.json').write_text(json.dumps({'status':'PASS','masterUnchanged':True,'captures':rows},indent=2)+'\n')
assert sha(b['editedMaster'])==b['editedSHA256'];print('RENDERS_PASS')
