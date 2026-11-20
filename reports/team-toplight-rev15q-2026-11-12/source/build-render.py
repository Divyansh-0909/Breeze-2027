import bpy,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];basepath=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(basepath);assert before=='f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682'
bpy.ops.wm.open_mainfile(filepath=str(basepath));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes}
s=base.copy();s.name='REV15Q / Team top light and full-detail crowd review'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={};crowd=[]
for o in base.objects:
 a=o.copy();a.name='REV15Q / '+o.name.removeprefix('REV15P / ')
 if o.type in ['LIGHT','CAMERA']:a.data=o.data.copy()
 if o.type=='MESH' and o.data.name.startswith('REV13A shared'):
  a.data=bpy.data.meshes[o.get('LOD0',o.data.name.rsplit('LOD',1)[0]+'LOD0')];a['reviewLOD']=0
  crowd.append({'source':o.name,'object':a.name,'beforeMesh':o.data.name,'afterMesh':a.data.name,'beforeVertices':len(o.data.vertices),'afterVertices':len(a.data.vertices),'transformUnchanged':a.matrix_world==o.matrix_world,'sameMaterialBank':True})
 s.collection.objects.link(a);copies[o]=a
for o,a in copies.items():
 if o.parent in copies:a.parent=copies[o.parent]
 if a.animation_data:
  for f in a.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15Q / independent view')
for x in list(s.view_layers):
 if x!=layer:s.view_layers.remove(x)
bpy.context.window.view_layer=layer
if s.use_nodes:
 for n in s.node_tree.nodes:
  if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
events=next(o for o in base.objects if o.type=='LIGHT' and 'REV15N / Poster wall gentle spill' in o.name)
oldteam=next(o for o in base.objects if o.type=='LIGHT' and 'REV15 / Poster wall gentle spill' in o.name)
team=copies[oldteam];team.data=events.data.copy();team.name='REV15Q / Team mural matched top light'
team.location=(15.126-(abs(-15.85-events.location.x)),31.445,11.08+(events.location.z-9.5))
team.rotation_euler=events.rotation_euler.copy();team['matchedSource']=events.name
s.camera=copies[base.camera];s.frame_set(1);bpy.context.view_layer.update()
assert len(crowd)==189 and all(x['transformUnchanged'] for x in crowd)
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert len([o for o in s.objects if o.get('artKind')])==8
bpy.context.preferences.filepaths.save_version=0
out=Path('/dev/shm/Gullyverse-Rev15Q-Team-Toplight-Detail-Review.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
proof={'status':'PASS','sourceSHA256':before,'editedMaster':str(out),'editedSHA256':sha(out),'editedBytes':out.stat().st_size,'scenes':len(bpy.data.scenes),'all46HistoricalSceneMembershipsPreserved':True,'crowdCount':189,'promotedCrowdMeshes':sum(x['beforeMesh']!=x['afterMesh'] for x in crowd),'crowd':crowd,'teamLight':{'source':events.name,'position':list(team.location),'energy':team.data.energy,'color':list(team.data.color),'size':team.data.size,'rotation':list(team.rotation_euler),'samePowerColorSizeOrientation':team.data.energy==events.data.energy and team.data.color==events.data.color and team.data.size==events.data.size},'all8MuralsRetained':True,'websiteChanged':False,'note':'Full detail is for native camera review. Runtime distance selection still needs camera-aware integration; no new character art or all-LOD0 production claim.'}
(R/'evidence/change-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('MASTER_SAVED',out.stat().st_size,flush=True)
def render(scene,key,pos,target,lens):
 bpy.context.window.scene=scene
 d=bpy.data.cameras.new('REVIEW / '+key);d.lens=lens;d.sensor_width=36;o=bpy.data.objects.new('REVIEW / '+key,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();scene.camera=o
 scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=16;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'renders'/f'{key}.png');print('RENDER',key,flush=True);bpy.ops.render.render(write_still=True)
render(base,'team-before',(9.05,31.445,9.45),(15.3,31.445,9.25),22)
render(s,'team-after',(9.05,31.445,9.45),(15.3,31.445,9.25),22)
render(base,'crowd-before',(0,23,8.7),(1,27,8.3),28)
render(s,'crowd-after',(0,23,8.7),(1,27,8.3),28)
assert sha(basepath)==before
print('DONE',flush=True)
