import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1]
P=O.parent/'team-wall-rev15k-black-brick-2026-11-11/delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((O.parent/'team-wall-rev15k-black-brick-2026-11-11/evidence/blender-validation.json').read_text())['masterSHA256'];assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15K');bpy.context.window.scene=s;s.frame_set(1)
data=bpy.data.cameras.new('REVIEW ONLY / navigation board camera');data.lens=31.5;data.clip_start=.1;data.clip_end=250
camera=bpy.data.objects.new(data.name,data);s.collection.objects.link(camera);camera.location=(0,2.5,10.14);target=Vector((0,11,10.14));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
file=O/'renders/navigation-board-current.png';s.render.filepath=str(file);t=time.monotonic();bpy.ops.render.render(write_still=True)
assert sha(P)==expected
record={'sourceVersion':'REV15K','masterSHA256':expected,'masterUnchanged':True,'file':'renders/'+file.name,'sha256':sha(file),'bytes':file.stat().st_size,'viewport':[1600,1100],'lighting':'Original saved Blender scene lighting','camera':{'position':list(camera.location),'target':list(target),'lens':data.lens},'seconds':time.monotonic()-t,'labels':['GULLYVERSE','EVENTS <','TEAM >','PAST SPONSORS','CONTACT US','AFTERMOVIE ^'],'masterCheckpoint':'https://drive.google.com/drive/folders/1tlYCgRpcWRswyMbvCfCxjhCdEmwy3JuP'}
(O/'evidence/capture.json').write_text(json.dumps(record,indent=2));print('CAPTURE COMPLETE',round(record['seconds'],1),flush=True)
