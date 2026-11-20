import bpy,json,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R.parent/'night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'));s=bpy.context.scene;s.frame_set(1)
d=bpy.data.cameras.new('CAPTURE / native team reference');d.lens=22;d.sensor_width=36;o=bpy.data.objects.new('CAPTURE / native team reference',d);s.collection.objects.link(o);o.location=(9.05,31.445,9.45);o.rotation_euler=(Vector((15.3,31.445,9.25))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.eevee.taa_render_samples=8;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'renders/native-team-reference.png');t=time.monotonic();bpy.ops.render.render(write_still=True);print('NATIVE_REFERENCE',time.monotonic()-t,flush=True)
