import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=Path(b['editedMaster']);assert sha(P)==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
# Inspection lighting is deliberately temporary and never saved to the master.
w=bpy.data.worlds.new('INSPECTION ONLY / neutral environment');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.48,.52,.58,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.55;s.world=w
d=bpy.data.lights.new('INSPECTION ONLY / sun','SUN');d.energy=2.4;d.angle=.35;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=(Vector((-16,31,13))-Vector((10,20,30))).to_track_quat('-Z','Y').to_euler()
rows=[]
for key,pos,target,lens in [('neutral-house',(-1,24,15.0),(-16.2,31.1,15.0),24),('neutral-window',(-10.8,28.3,11.8),(-16.4,31.1,11.6),34)]:
 d=bpy.data.cameras.new('INSPECTION ONLY / '+key);cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.05;d.clip_end=200;s.camera=cam;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.eevee.taa_render_samples=16;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.filepath=str(R/'renders'/(key+'.jpg'));start=time.monotonic();bpy.ops.render.render(write_still=True);rows.append({'file':'renders/'+key+'.jpg','sha256':sha(R/'renders'/(key+'.jpg')),'camera':pos,'target':target,'seconds':time.monotonic()-start,'lighting':'Temporary neutral inspection world and sun; not the final night appearance'})
assert sha(P)==b['editedSHA256'];(R/'evidence/neutral-captures.json').write_text(json.dumps({'status':'PASS','masterUnchanged':True,'inspectionOnly':True,'captures':rows},indent=2)+'\n');print('NEUTRAL_INSPECTION_DONE',flush=True)
