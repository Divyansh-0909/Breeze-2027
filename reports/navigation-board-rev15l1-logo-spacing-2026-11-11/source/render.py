import bpy,json,time,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend';v=json.loads((O/'evidence/blender-validation.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(P)==v['masterSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15L1');bpy.context.window.scene=s
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
logos=json.loads((O/'evidence/sponsors.json').read_text());f=O/'evidence/captures.json';rows=json.loads(f.read_text()) if f.exists() else []
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
poses=[('01-navigation-board','Whole updated board',(0,0,11),(0,11,11),40,[1600,1400],1),('02-led-close','Close-hung Past Sponsors LED',(0,6.3,9.95),(0,11,9.95),38,[1600,900],1),('03-board-oblique','Board and short screen hangers',(-5.3,1.4,11.1),(0,11,11),32,[1600,1200],1),('04-led-next-logos','Another point in the sponsor loop',(0,6.3,9.95),(0,11,9.95),38,[1600,900],logos['logos'][2]['startCell']+1)]
for name,title,pos,target,lens,size,frame in poses:
 if args and name not in args:continue
 rows=[r for r in rows if r['file']!='renders/'+name+'.png']
 s.frame_set(frame);bpy.context.view_layer.update();s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.resolution_x,s.render.resolution_y=size;file=O/'renders'/f'{name}.png';s.render.filepath=str(file);start=time.monotonic();bpy.ops.render.render(write_still=True);rows.append({'file':'renders/'+file.name,'title':title,'viewport':size,'frame':frame,'masterSHA256':v['masterSHA256'],'sha256':sha(file),'seconds':time.monotonic()-start});(O/'evidence/captures.json').write_text(json.dumps(rows,indent=2));print('CAPTURED',name,flush=True)
f.write_text(json.dumps(sorted(rows,key=lambda r:r['file']),indent=2));assert sha(P)==v['masterSHA256'];print('ALL CAPTURES COMPLETE',flush=True)
