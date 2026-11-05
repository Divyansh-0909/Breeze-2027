import bpy,json,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(O/'delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend'));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15I1');bpy.context.window.scene=s;s.frame_set(1);c=s.objects['REV15I1 / Team Carousel Controller'];c['team_index']=1;c.update_tag();bpy.context.view_layer.update();records=[]
poses=[('oc-wall',(9.4,31.445,9.25),(15.13,31.445,9.25),22,(1920,1080)),('oc-left-close',(12.0,33.31,8.95),(15.13,33.31,8.95),24,(1600,1100)),('oc-right-close',(12.0,29.58,8.95),(15.13,29.58,8.95),24,(1600,1100)),('oc-context',(5.5,29,8.92),(15.13,31.445,9.25),24,(1600,900)),('oc-mobile',(8.7,31.445,9.25),(15.13,31.445,9.25),12,(720,1280))]
for name,pos,target,lens,size in poses:
 if name not in ['oc-wall','oc-mobile']:continue
 d=bpy.data.cameras.new('REV15I review '+name);d.lens=lens;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=8;s.render.resolution_x,s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.filepath=str(O/'renders'/f'{name}.png');t=time.monotonic();bpy.ops.render.render(write_still=True);records.append({'pose':name,'position':pos,'target':target,'lensMm':lens,'viewport':size,'DPR':1,'renderer':'Actual Blender EEVEE master scene','world':s.world.name,'exposure':s.view_settings.exposure,'look':s.view_settings.look,'seconds':time.monotonic()-t,'file':f'renders/{name}.png'});print('RENDERED',name,flush=True)
(O/'evidence/captures.json').write_text(json.dumps(records,indent=2))
