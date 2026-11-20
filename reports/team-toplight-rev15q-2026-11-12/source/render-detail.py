import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15Q-Team-Toplight-Detail-Review.blend')
base=bpy.data.scenes['REV15P / Isolated Night Atmosphere Pilot'];s=bpy.data.scenes['REV15Q / Team top light and full-detail crowd review']
def render(scene,key,pos,target,lens):
 bpy.context.window.scene=scene
 d=bpy.data.cameras.new('REVIEW / '+key);d.lens=lens;d.sensor_width=36;o=bpy.data.objects.new('REVIEW / '+key,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();scene.camera=o
 scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=16;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'renders'/f'{key}.png');print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True)
render(base,'crowd-detail-before',(7.45,39.5,8.8),(7.45,36.7,8.5),40)
render(s,'crowd-detail-after',(7.45,39.5,8.8),(7.45,36.7,8.5),40)
