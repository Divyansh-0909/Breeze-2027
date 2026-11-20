import bpy,json,hashlib,time,sys,math
from pathlib import Path
from mathutils import Vector

O=Path(__file__).resolve().parents[1]
plan=json.loads((O/'evidence/capture-plan.json').read_text())
P=O.parent/'team-wall-rev15j1-full-heading-2026-11-10/delivery/Gullyverse-Rev15J1-Full-Heading.blend'
assert hashlib.sha256(P.read_bytes()).hexdigest()==plan['masterSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P))
base=next(s for s in bpy.data.scenes if s.get('variant')=='REV15J1')
bpy.context.window.scene=base;base.frame_set(1)
original_scenes={s.name:tuple(s.objects) for s in bpy.data.scenes}
original_lights={o.name:o.data.energy for o in base.objects if o.type=='LIGHT'}
inspection_world=bpy.data.worlds.new('REVIEW ONLY / neutral inspection world');inspection_world.use_nodes=True
bg=inspection_world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.32,.37,.43,1);bg.inputs['Strength'].default_value=.6
def architecture(o):
 return o.type=='MESH' and (o.name.startswith(('REV15 / REV12 /','REV15 / REV14B /','REV15F / continuous house shell')) or 'continuous house shell' in o.name)
def make_scene(name,architecture_only=False):
 s=bpy.data.scenes.new(name);s.world=inspection_world
 for o in base.objects:
  if architecture_only:
   if architecture(o):s.collection.objects.link(o)
  elif o.type!='CAMERA':s.collection.objects.link(o)
 for p in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,p,getattr(base.view_settings,p))
 for key,energy,color in [('key',2.1,(1,.95,.88)),('fill',.65,(.78,.87,1))]:
  data=bpy.data.lights.new(name+' / '+key,'SUN');data.energy=energy;data.color=color;data.angle=math.radians(15)
  ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob)
 return s
inspection=make_scene('REVIEW ONLY / full environment inspection')
architectural=make_scene('REVIEW ONLY / isolated architecture',True)
for s in [base,inspection,architectural]:
 s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=8;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
 if hasattr(s.render,'film_transparent'):s.render.film_transparent=False
camera_data=bpy.data.cameras.new('REVIEW ONLY / capture camera');camera_data.sensor_width=36;camera_data.clip_start=.06;camera_data.clip_end=500
camera=bpy.data.objects.new(camera_data.name,camera_data)
for s in [base,inspection,architectural]:s.collection.objects.link(camera)
results_path=O/'evidence/captures.json';rows=json.loads(results_path.read_text()) if results_path.exists() else []
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
wanted=set(args)
for pose in plan['poses']:
 if wanted and pose['id'] not in wanted:continue
 file=O/pose['file']
 if any(r['id']==pose['id'] and r['masterSHA256']==plan['masterSHA256'] and file.exists() for r in rows):continue
 if pose.get('reuse'):
  result=dict(pose,masterSHA256=plan['masterSHA256'],sha256=hashlib.sha256(file.read_bytes()).hexdigest(),renderer='Actual Blender EEVEE master scene; unchanged existing capture',seconds=0)
  rows=[r for r in rows if r['id']!=pose['id']]+[result];results_path.write_text(json.dumps(rows,indent=2));continue
 s=base if pose['lighting']=='original' else architectural if pose['scene']=='architecture' else inspection
 bpy.context.window.scene=s;s.frame_set(1)
 if 'camera' in pose:
  c=pose['camera'];camera.location=c['position'];camera.rotation_euler=c['rotation'];camera_data.type=c['type'];camera_data.lens=c['lens'];camera_data.ortho_scale=c['orthoScale']
 else:
  camera.location=pose['position'];camera.rotation_euler=(Vector(pose['target'])-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO' if pose.get('ortho') else 'PERSP';camera_data.ortho_scale=pose.get('ortho') or 6;camera_data.lens=pose['lens']
 if pose.get('roll'):camera.rotation_euler.rotate_axis('Z',pose['roll'])
 s.camera=camera;s.render.resolution_x,s.render.resolution_y=pose['viewport']
 camera_data.clip_start=pose.get('nearClip',.06)
 forward=camera.rotation_euler.to_quaternion()@Vector((0,0,-1))
 target=Vector(pose['target']) if pose.get('target') else camera.location+forward*10
 if s!=base:
  key=next(o for o in s.objects if o.type=='LIGHT' and o.name.endswith('/ key'))
  fill=next(o for o in s.objects if o.type=='LIGHT' and o.name.endswith('/ fill'))
  from_subject=(camera.location-target);from_subject.z=0
  if from_subject.length<.01:from_subject=Vector((12,-20,0))
  from_subject.normalize();key.rotation_euler=(-from_subject+Vector((0,0,-.9))).to_track_quat('-Z','Y').to_euler()
  side=Vector((-from_subject.y,from_subject.x,-.6));fill.rotation_euler=side.to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(file);start=time.monotonic();bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
 result=dict(pose,masterSHA256=plan['masterSHA256'],sha256=hashlib.sha256(file.read_bytes()).hexdigest(),renderer='Actual Blender EEVEE; original lighting' if s==base else 'Actual Blender EEVEE; clearly labelled temporary inspection lighting',cameraPosition=list(camera.location),cameraRotation=list(camera.rotation_euler),seconds=time.monotonic()-start)
 rows=[r for r in rows if r['id']!=pose['id']]+[result];results_path.write_text(json.dumps(rows,indent=2))
 print('CAPTURED',pose['id'],round(result['seconds'],2),flush=True)

for s in [base,inspection,architectural]:s.collection.objects.unlink(camera)
checks={'masterFileUnchanged':hashlib.sha256(P.read_bytes()).hexdigest()==plan['masterSHA256'],'all40OriginalSceneMembershipsExact':all(tuple(bpy.data.scenes[n].objects)==members for n,members in original_scenes.items()),'allOriginalLightEnergiesExact':all(bpy.data.objects[n].data.energy==energy for n,energy in original_lights.items())}
assert all(checks.values()),checks
(O/'evidence/preservation.json').write_text(json.dumps({'status':'PASS','checks':checks,'capturesComplete':len(rows),'capturesPlanned':len(plan['poses'])},indent=2))
print('DONE',len(rows),'of',len(plan['poses']),flush=True)
