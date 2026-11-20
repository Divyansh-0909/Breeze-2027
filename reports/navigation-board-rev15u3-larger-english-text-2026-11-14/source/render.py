import bpy,json,hashlib,time,sys,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());ap=argparse.ArgumentParser();ap.add_argument('--before',action='store_true');ap.add_argument('--keys');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
P=Path(b['source'] if a.before else b['editedMaster']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();expected=b['sourceSHA256'] if a.before else b['editedSHA256'];assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def lighting():return {'world':s.world.name,'exposure':s.view_settings.exposure,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'lights':[(o.name,o.data.energy,list(o.data.color),[list(r) for r in o.matrix_world]) for o in s.objects if o.type=='LIGHT']}
saved=lighting();records=json.loads((R/'evidence/captures.json').read_text()) if (R/'evidence/captures.json').exists() else []
shots=[('01-whole-board',(0,5.5,12.0),(0,11,12.0),23,[1280,1100]),('02-sign-close',(0,5.0,12.8),(0,11,12.8),30,[1440,1100]),('03-oblique',(-4.5,2.6,12.0),(0,11,12.0),35,[1440,1100])]
if a.before:shots=[shots[0]]
if a.keys:shots=[x for x in shots if x[0] in a.keys.split(',')]
for key,pos,target,lens,res in shots:
    key=('before-' if a.before else '')+key;cam=bpy.data.cameras.new('REVIEW / '+key);ob=bpy.data.objects.new(cam.name,cam);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_start=.05;cam.clip_end=180;s.camera=ob
    s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.filepath=str(R/'renders'/(key+'.jpg'));start=time.monotonic();print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True)
    assert lighting()==saved;row={'key':key,'file':'renders/'+key+'.jpg','sourceSHA256':expected,'sha256':sha(R/'renders'/(key+'.jpg')),'savedNightLighting':True,'inspectionLightsAdded':False,'postCaptureBrightening':False,'seconds':time.monotonic()-start};records=[x for x in records if x['key']!=key];records.append(row);(R/'evidence/captures.json').write_text(json.dumps(records,indent=2)+'\n');s.collection.objects.unlink(ob)
assert sha(P)==expected
(R/('evidence/before-lighting-verification.json' if a.before else 'evidence/lighting-verification.json')).write_text(json.dumps({'status':'PASS','sourceSHA256':expected,'savedNightLighting':True,'worldAndLightsAndExposureUnchanged':True,'sourceFileUnchanged':True,'settings':saved},indent=2)+'\n');print('NAV_CAPTURES_DONE',flush=True)
