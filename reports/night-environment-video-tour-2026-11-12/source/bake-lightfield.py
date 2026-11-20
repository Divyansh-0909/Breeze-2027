"""Bake native static diffuse lighting; read-only source, disposable scene."""
import bpy,json,time,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R;MASTER=Path('/workspace/Breeze-2027/reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(MASTER)=='f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682'
for d in ['evidence','viewer','renders','review']:(R/d).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(MASTER));native=bpy.context.scene;scene=bpy.data.scenes.new('REV15P2 TEMP / lightfield bake');scene.world=native.world.copy();scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.max_bounces=3;scene.cycles.diffuse_bounces=2
bpy.context.window.scene=scene
for o in native.objects:
 if o.type=='LIGHT' and o.data.energy>0 and not o.hide_render:
  a=o.copy();a.data=o.data.copy();scene.collection.objects.link(a)
bpy.ops.import_scene.gltf(filepath=str(B/'viewer/pilot.glb'),merge_vertices=False)
meshes=[o for o in scene.objects if o.type=='MESH'];mapping=[];offset=0;errors=[]
for o in meshes:
 n=len(o.data.vertices);ids=o.data.attributes.new('source_point_id','INT','POINT');ids.data.foreach_set('value',np.arange(offset,offset+n,dtype=np.int32));mapping.append({'object':o.name,'offset':offset,'count':n});offset+=n
 # A neutral diffuse response exposes illuminance even on source metals.
 # Base colours remain for indirect bounce; diffuse-pass colour is excluded.
 for slot in o.material_slots:
  m=slot.material
  if m and m.use_nodes:
   for node in m.node_tree.nodes:
    if node.type=='BSDF_PRINCIPLED':node.inputs['Metallic'].default_value=0;node.inputs['Roughness'].default_value=1
 if o.name.startswith('WEB / REV15P / REV15L / animated sponsor LED'):
  o.hide_render=True
for o in scene.objects:o.select_set(o in meshes)
active=next(o for o in meshes if not o.hide_render);bpy.context.view_layer.objects.active=active
bpy.ops.object.join();ob=bpy.context.object;mesh=ob.data
ids=np.empty(len(mesh.vertices),dtype=np.int32);mesh.attributes['source_point_id'].data.foreach_get('value',ids)
coords=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coords);coords=coords.reshape(-1,3)
assert len(ids)==offset and len(set(ids.tolist()))==offset
colour=mesh.color_attributes.new(name='NativeDiffuseLight',type='FLOAT_COLOR',domain='CORNER');mesh.color_attributes.active_color=colour
scene.render.bake.target='VERTEX_COLORS';scene.render.bake.use_pass_color=False;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True
scene.render.bake.use_clear=True
(R/'evidence/bake-mapping.json').write_text(json.dumps(mapping,indent=2))
start=time.monotonic();print('BAKE_START',len(mesh.vertices),len(mesh.polygons),len(mesh.loops),flush=True)
bpy.ops.object.bake(type='DIFFUSE')
rgba=np.empty(len(mesh.loops)*4,dtype=np.float32);colour.data.foreach_get('color',rgba);rgba=rgba.reshape(-1,4)
loop_vertex=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loop_vertex)
values=np.zeros((len(mesh.vertices),3),dtype=np.float32);counts=np.zeros(len(mesh.vertices),dtype=np.float32);np.add.at(values,loop_vertex,rgba[:,:3]);np.add.at(counts,loop_vertex,1);values/=np.maximum(counts[:,None],1)
ordered=np.zeros_like(values);ordered[ids]=values;positions=np.zeros_like(coords);positions[ids]=coords
ordered.astype('<f4').tofile(R/'evidence/native-lightfield.f32');positions.astype('<f4').tofile(R/'evidence/native-positions.f32')
report={'status':'PASS','method':'Cycles diffuse direct+indirect, colour excluded; source metal response neutralized for reusable illuminance; loop colour averaged to existing export points','samples':scene.cycles.samples,'bounces':scene.cycles.max_bounces,'seconds':time.monotonic()-start,'points':offset,'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),'mapping':mapping,'range':[float(ordered.min()),float(ordered.max())],'percentiles':{str(p):float(np.percentile(ordered,p)) for p in [1,50,90,99,99.9]},'nativeMasterUnchanged':sha(MASTER)=='f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682','baselineGLBSHA256':sha(B/'viewer/pilot.glb'),'savedNativeFile':False}
(R/'evidence/lightfield.json').write_text(json.dumps(report,indent=2));assert report['nativeMasterUnchanged'];print('BAKE_COMPLETE',json.dumps({k:v for k,v in report.items() if k!='mapping'}),flush=True)
