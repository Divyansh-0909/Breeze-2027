import bpy,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
config=json.loads((R/'viewer/cameras.json').read_text());args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
rows=[]
for mode in ['baseline','pilot']:
 if args and mode not in args:continue
 p=R/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend' if mode=='pilot' else R.parent/'house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend'
 bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.frame_set(1)
 # Temporary camera only; neither source nor pilot file is saved by rendering.
 data=bpy.data.cameras.new('CAPTURE / matching camera');data.sensor_width=36;cam=bpy.data.objects.new('CAPTURE / matching camera',data);s.collection.objects.link(cam);s.camera=cam
 s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.eevee.taa_render_samples=16;s.render.image_settings.file_format='PNG'
 for c in config['cameras']:
  cam.location=c['position'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=c['lens'];t=time.monotonic();p=R/'renders'/f'blender-{mode}-{c["key"]}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  rows.append({'mode':mode,'camera':c['key'],'path':str(p.relative_to(R)),'seconds':time.monotonic()-t,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});print('CAPTURE',mode,c['key'],flush=True)
 (R/f'evidence/captures-{mode}.json').write_text(json.dumps([x for x in rows if x['mode']==mode],indent=2))
