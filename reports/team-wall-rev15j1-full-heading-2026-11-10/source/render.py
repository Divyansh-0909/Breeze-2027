import bpy
import json
import time
from pathlib import Path
from mathutils import Vector

O = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(O/'delivery/Gullyverse-Rev15J1-Full-Heading.blend'))
s = next(s for s in bpy.data.scenes if s.get('variant') == 'REV15J1')
bpy.context.window.scene = s
s.frame_set(1)
controller = s.objects['REV15J1 / Team Carousel Controller']
manifest = json.loads((O/'evidence/carousel-manifest.json').read_text())
data = bpy.data.cameras.new('REV15J1 / matched mural review camera')
data.lens = 22
camera = bpy.data.objects.new(data.name, data)
s.collection.objects.link(camera)
camera.location = (9.4, 31.445, 9.25)
camera.rotation_euler = (Vector((15.13,31.445,9.25))-camera.location).to_track_quat('-Z','Y').to_euler()
s.camera = camera
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.eevee.taa_render_samples = 8
s.render.resolution_x, s.render.resolution_y = 1600, 900
s.render.resolution_percentage = 100
records=json.loads((O/'evidence/captures.json').read_text())
for index, slide in enumerate(manifest['slides']):
    if index != 0:
        continue
    controller['team_index'] = index
    controller.update_tag()
    bpy.context.view_layer.update()
    filename = f'{index+1:02d}-' + slide['team'].lower().replace(' ', '-') + '-laptop.png'
    s.render.filepath = str(O/'renders'/filename)
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    records[index] = {'sourceVersion':'REV15J1','team':slide['team'],'index':index,'file':'renders/'+filename,'viewport':[1600,900],'renderer':'Actual Blender EEVEE master scene','world':s.world.name,'exposure':s.view_settings.exposure,'look':s.view_settings.look,'viewTransform':s.view_settings.view_transform,'seconds':time.monotonic()-start}
    (O/'evidence/captures.json').write_text(json.dumps(records,indent=2))
    print('RENDERED',index+1,slide['team'],flush=True)
