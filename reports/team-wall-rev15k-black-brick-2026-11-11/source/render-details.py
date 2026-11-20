import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
expected=json.loads((O/'evidence/blender-validation.json').read_text())['masterSHA256']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15K');bpy.context.window.scene=s;s.frame_set(1)
c=s.objects['REV15K / Team Carousel Controller'];c['team_index']=1;c.update_tag();bpy.context.view_layer.update()
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
rows=[]
for name,title,pos,target,lens in [('09-brick-paint-close','Black paint, worn brick and mural detail',(12.7,29.4,9.9),(15.13,29.4,9.9),35),('10-content-oblique','Content mural / oblique wall view',(10.8,27.0,9.4),(15.13,31.445,9.4),25)]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.filepath=str(O/'renders'/f'{name}.png');t=time.monotonic();bpy.ops.render.render(write_still=True)
 rows.append({'title':title,'file':f'renders/{name}.png','viewport':[1600,900],'masterSHA256':expected,'sha256':sha(O/'renders'/f'{name}.png'),'seconds':time.monotonic()-t,'camera':{'position':pos,'target':target,'lens':lens}})
assert sha(P)==expected
(O/'evidence/detail-captures.json').write_text(json.dumps(rows,indent=2));print('DETAILS COMPLETE',flush=True)
