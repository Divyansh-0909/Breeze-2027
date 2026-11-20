import bpy,json,time,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1]
P=O/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((O/'evidence/blender-validation.json').read_text())['masterSHA256'];assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15K');bpy.context.window.scene=s;s.frame_set(1)
controller=s.objects['REV15K / Team Carousel Controller'];manifest=json.loads((O/'evidence/carousel-manifest.json').read_text())
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.image_settings.file_format='PNG';s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
f=O/'evidence/captures.json';rows=json.loads(f.read_text()) if f.exists() else []
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for i,slide in enumerate(manifest['slides']):
 if args and str(i) not in args:continue
 if any(r['index']==i and r['masterSHA256']==expected for r in rows):continue
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();name=f'{i+1:02d}-'+slide['team'].lower().replace(' ','-')+'-laptop.png';s.render.filepath=str(O/'renders'/name);t=time.monotonic();bpy.ops.render.render(write_still=True)
 row={'index':i,'team':slide['team'],'file':'renders/'+name,'viewport':[1600,900],'renderer':'Actual Blender EEVEE, original scene lighting','seconds':time.monotonic()-t,'masterSHA256':expected,'sha256':sha(O/'renders'/name),'layout':slide['layout'],'people':slide['people']};rows=[r for r in rows if r['index']!=i]+[row];f.write_text(json.dumps(sorted(rows,key=lambda r:r['index']),indent=2));print('CAPTURED',i,slide['team'],round(row['seconds'],1),flush=True)
assert sha(P)==expected
print('DONE',len(rows),'of 8')
