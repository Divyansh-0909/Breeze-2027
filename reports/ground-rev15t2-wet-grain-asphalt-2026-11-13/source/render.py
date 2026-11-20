import bpy,json,time,hashlib,argparse,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];base=json.loads((R/'evidence/build-verification.json').read_text());base['editedMaster']=base['editedMaster'];base['editedSHA256']=base['editedSHA256'];ap=argparse.ArgumentParser();ap.add_argument('--source',default=base['editedMaster']);ap.add_argument('--expected-sha256',default=base['editedSHA256']);ap.add_argument('--preview',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);P=Path(a.source);base['editedSHA256']=a.expected_sha256;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(P)==base['editedSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
assert s.name=='REV15T2 / Coarse wet asphalt and muddy water edges'
def lighting():
 return {'world':s.world.name,'worldNodes':[(n.name,n.type,[(i.name,str(i.default_value[:]) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in s.world.node_tree.nodes],'lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix':[list(x) for x in o.matrix_world],'hideRender':o.hide_render} for o in s.objects if o.type=='LIGHT'],'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'useNodes':s.use_nodes,'engine':s.render.engine}
settings=lighting();assert not any('REVIEW ONLY' in x['name'] for x in settings['lights']);records=[]
shots=[
 ('01-lane-wide','Wet gully road / actual night lighting',(0,-28.8,7.72),(.15,-13.5,6.2),23),
 ('02-lane-grain-close','Exposed asphalt grain / actual shop lighting',(.4,-10.3,6.95),(-2.35,-7.9,6.12),35),
 ('03-lane-water','Muddy edge water / actual shop lighting',(-.3,-27.6,6.85),(-3.1,-25.8,6.02),30),
 ('04-cypher-wide','Wet cypher road / actual night lighting',(2.7,17.5,8.92),(-5.1,25,7.2),22),
 ('05-cypher-water','Cypher edge water / actual Events light',(-8.5,27.5,8.45),(-12.7,31,7.23),29)]
if '--preview' in sys.argv:shots=[shots[1],shots[2]]
for key,title,pos,target,lens in shots:
 d=bpy.data.cameras.new('ACTUAL NIGHT REVIEW / '+key);d.lens=lens;d.sensor_width=36;d.clip_start=.055;d.clip_end=180;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o
 s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=95;s.render.filepath=str(R/'renders'/(key+'.jpg'))
 t=time.monotonic();print('RENDER',key,'ENGINE',s.render.engine,flush=True);bpy.ops.render.render(write_still=True);assert lighting()==settings
 record={'key':key,'title':title,'file':'renders/'+key+'.jpg','resolution':[1280,800],'position':pos,'target':target,'lens':lens,'sourceMasterSHA256':base['editedSHA256'],'sha256':sha(R/'renders'/(key+'.jpg')),'seconds':time.monotonic()-t};records.append(record);s.collection.objects.unlink(o);(R/'evidence/captures.json').write_text(json.dumps(records,indent=2)+'\n')
assert sha(P)==base['editedSHA256'];(R/'evidence/lighting-verification.json').write_text(json.dumps({'status':'PASS','sourceMaster':str(P),'sourceSHA256':base['editedSHA256'],'scene':s.name,'settings':settings,'lightingWorldAndExposureUnchanged':True,'inspectionLightsAdded':False,'postCaptureBrightening':False,'sourceMasterUnchanged':True,'captures':len(records),'note':'Camera, resolution and JPEG output were changed only in memory. The native file was not saved.'},indent=2)+'\n');print('ACTUAL_NIGHT_CAPTURES_DONE',len(records),flush=True)
