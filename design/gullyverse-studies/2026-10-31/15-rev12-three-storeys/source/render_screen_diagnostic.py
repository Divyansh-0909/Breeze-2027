import bpy,sys,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from rooftop_cameras import add
s=next(s for s in bpy.data.scenes if s.get('variant')=='REV12');bpy.context.window.scene=s;s.frame_set(1);add(s);s.camera=bpy.data.objects['REV10 CAMERA / 04-front'];hidden=[]
for o in s.objects:
 if o.name.startswith('Existing Aftermovie /'):o.hide_render=True;hidden.append(o.name)
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';f=O/'review/DIAGNOSTIC-screen-media-hidden.png';s.render.filepath=str(f);bpy.ops.render.render(write_still=True)
(O/'evidence/screen-obscuration.json').write_text(json.dumps({'diagnosticOnly':True,'selectedScreenUnchanged':True,'masterNotSaved':True,'temporarilyHidden':hidden,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'cameraAndLightingMatch04Front':True},indent=2))
