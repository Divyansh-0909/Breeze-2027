import bpy,json,hashlib,math,argparse,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15T1-Unpainted-Cypher-Road.blend');ap.add_argument('--expected-sha256',default='5f32cb917b1f2d8037e1445b8bfad69462be28dde7e1194a230c8a65fd720a09');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);P=Path(a.base);expected=a.expected_sha256;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15T2 / Coarse wet asphalt and muddy water edges'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for o in base.objects:
 ob=o.copy();ob.name='REV15T2 / '+o.name.removeprefix('REV15T1 / ')
 if o.type in ['LIGHT','CAMERA']:ob.data=o.data.copy()
 s.collection.objects.link(ob);copies[o]=ob
for o,ob in copies.items():
 if o.parent in copies:ob.parent=copies[o.parent]
 if ob.animation_data:
  for f in ob.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15T2 / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
assets=bpy.data.collections.new('REV15T2 / Runtime road and edge water');s.collection.children.link(assets)
art=json.loads((R/'evidence/material-art.json').read_text());tile=art['tileMetres'];mean=np.array(art['tileMeanLinearRGB'])
def image(file,noncolor=False):
 im=bpy.data.images.load(str(R/'textures'/file));im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';im.pack();return im
grain=image('aggregate-1p2m-color.jpg');norm=image('aggregate-1p2m-normal.png',True);rough=image('wet-road-world-roughness.png',True);waternormal=image('edge-water-normal.png',True)
macro=bpy.data.images.load(str(R/'textures/wet-road-world-color.png'));macro.colorspace_settings.name='Non-Color';W,H=macro.size;pixels=np.empty(W*H*4,dtype=np.float32);macro.pixels.foreach_get(pixels);pixels=pixels.reshape(H,W,4);rgb=pixels[:,:,:3];linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
def material(name,normalStrength=1):
 m=bpy.data.materials.new('REV15T2 / '+name);m.use_nodes=True;nd=m.node_tree.nodes;lk=m.node_tree.links;b=nd['Principled BSDF'];b.inputs['Metallic'].default_value=0;b.inputs['Coat Weight'].default_value=.15;b.inputs['Coat Roughness'].default_value=.23
 u=nd.new('ShaderNodeUVMap');u.uv_map='RoadDetailUV';tex=nd.new('ShaderNodeTexImage');tex.image=grain;lk.new(u.outputs['UV'],tex.inputs['Vector'])
 vc=nd.new('ShaderNodeVertexColor');vc.layer_name='RoadTint';mix=nd.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;lk.new(tex.outputs['Color'],mix.inputs[1]);lk.new(vc.outputs['Color'],mix.inputs[2]);lk.new(mix.outputs[0],b.inputs['Base Color'])
 nt=nd.new('ShaderNodeTexImage');nt.image=norm;lk.new(u.outputs['UV'],nt.inputs['Vector']);nm=nd.new('ShaderNodeNormalMap');nm.uv_map='RoadDetailUV';nm.inputs['Strength'].default_value=normalStrength;lk.new(nt.outputs['Color'],nm.inputs['Color']);lk.new(nm.outputs['Normal'],b.inputs['Normal'])
 uw=nd.new('ShaderNodeUVMap');uw.uv_map='RoadWorldUV';rt=nd.new('ShaderNodeTexImage');rt.image=rough;lk.new(uw.outputs['UV'],rt.inputs['Vector']);lk.new(rt.outputs['Color'],b.inputs['Roughness']);return m
road=material('Wet coarse-grain asphalt',.82);mud=material('Silt-coated wet shoulder',.20)
# The smoother mud uses the same original grain colour at reduced contrast.
mudgrain=image('mud-mean-color.png')
for n in mud.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image==grain:n.image=mudgrain
water=bpy.data.materials.new('REV15T2 / Muddy settled edge water');water.use_nodes=True;wb=water.node_tree.nodes['Principled BSDF'];wb.inputs['Base Color'].default_value=(.028,.023,.015,1);wb.inputs['Roughness'].default_value=.095;wb.inputs['IOR'].default_value=1.333;wb.inputs['Coat Weight'].default_value=1;wb.inputs['Coat Roughness'].default_value=.07
nd=water.node_tree.nodes;lk=water.node_tree.links;nt=nd.new('ShaderNodeTexImage');nt.image=waternormal;uv=nd.new('ShaderNodeUVMap');uv.uv_map='WaterUV';lk.new(uv.outputs[0],nt.inputs['Vector']);nm=nd.new('ShaderNodeNormalMap');nm.uv_map='WaterUV';nm.inputs['Strength'].default_value=.35;lk.new(nt.outputs['Color'],nm.inputs['Color']);lk.new(nm.outputs['Normal'],wb.inputs['Normal'])
floors=[];floorproof=[]
def halfwidth(y):return 3.6 if y<5 else 4.25 if y<14 else 16-(y-14)*.3 if y<22 else 13.6
for old,ob in copies.items():
 if not old.get('groundSurface'):continue
 ob.data=old.data.copy();me=ob.data;arr=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',arr);co=arr.reshape(-1,3);world=np.c_[co,np.ones(len(co))]@np.array(ob.matrix_world).T;x,y=world[:,0],world[:,1]
 ix=np.clip(np.rint((x+16)/32*(W-1)).astype(int),0,W-1);iy=np.clip(np.rint((y+30)/78*(H-1)).astype(int),0,H-1);tint=np.clip(linear[iy,ix]/mean,.005,1)
 attr=me.color_attributes.new(name='RoadTint',type='FLOAT_COLOR',domain='POINT');attr.data.foreach_set('color',np.c_[tint,np.ones(len(tint))].astype(np.float32).ravel());me.color_attributes.active_color_name='RoadTint'
 loops=np.array([l.vertex_index for l in me.loops]);me.uv_layers['RoadDetailUV'].data.foreach_set('uv',(world[loops,:2]/tile).astype(np.float32).ravel())
 slot=ob.material_slots[0];slot.link='OBJECT';slot.material=None;me.materials[0]=road;slot.link='DATA'
 me.materials.append(mud);mi=len(me.materials)-1;mudfaces=0
 for f in me.polygons:
  if f.material_index!=0:continue
  q=ob.matrix_world@f.center
  if halfwidth(q.y)-abs(q.x)<.84:f.material_index=mi;mudfaces+=1
 # New data adds colours and finer detail UVs; shape and topology remain identical.
 assert np.array_equal(co,np.array([list(v.co) for v in old.data.vertices],dtype=np.float32));assert [tuple(f.vertices) for f in me.polygons]==[tuple(f.vertices) for f in old.data.polygons]
 assets.objects.link(ob);floors.append(ob);floorproof.append({'name':ob.name,'vertices':len(me.vertices),'mudShoulderFaces':mudfaces,'positionsAndIndicesUnchanged':True})
bpy.data.images.remove(macro)
runtime=[]
for old,ob in copies.items():
 if old.get('groundSurface') or any(k in old.name for k in ['nearly flush drain','batched loose aggregate','shallow damp pocket']):
  runtime.append(ob)
  if ob.name not in assets.objects:assets.objects.link(ob)
 if 'shallow damp pocket' in old.name:
  ob.data=old.data.copy()
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=water
  uv=ob.data.uv_layers.new(name='WaterUV')
  for loop in ob.data.loops:
   p=ob.matrix_world@ob.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/2,p.y/2)
pools=json.loads((R/'source/edge-pools.json').read_text());added=[]
for p in pools:
 z=6.0 if p['y']<-10 else 7.2;vs=[(p['x'],p['y'],z+.002)]
 for i in range(64):
  a=i*math.tau/64;r=1+.08*math.sin(a*5+p['phase'])+.035*math.cos(a*9-p['phase']);u=math.cos(a)*p['width']/2*r;v=math.sin(a)*p['length']/2*r;x=p['x']+u*math.cos(p['angle'])-v*math.sin(p['angle']);y=p['y']+u*math.sin(p['angle'])+v*math.cos(p['angle']);assert abs(x)>1.4
  vs.append((x,y,z+.002))
 me=bpy.data.meshes.new('REV15T2 / edge pool '+p['id']);me.from_pydata(vs,[],[(0,i+1,(i+1)%64+1) for i in range(64)]);me.update();me.materials.append(water);uv=me.uv_layers.new(name='WaterUV')
 for loop in me.loops:
  q=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(q.x/2,q.y/2)
 ob=bpy.data.objects.new(me.name,me);assets.objects.link(ob);runtime.append(ob);added.append(ob)
s.eevee.use_raytracing=True;s.eevee.ray_tracing_options.resolution_scale='4'
s.camera=copies[base.camera];s['paintedCypherCircle']=False;bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert len(floors)==4 and len(runtime)==29;assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items());assert all(ob.hide_render for old,ob in copies.items() if 'Cypher chalk arc' in old.name)
assert all(list(old.matrix_world)==list(ob.matrix_world) for old,ob in copies.items())
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189;assert len([o for o in s.objects if o.get('artKind')])==8
assert all(o.data.energy==ob.data.energy and list(o.data.color)==list(ob.data.color) for o,ob in copies.items() if o.type=='LIGHT');assert s.world==base.world and s.view_settings.exposure==base.view_settings.exposure
out=Path('/dev/shm/Gullyverse-Rev15T2-Wet-Grain-Asphalt-and-Muddy-Edges.blend');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.data.libraries.write(str(R/'delivery/Rev15T2-Wet-Road-Additions.blend'),{assets},fake_user=True,compress=True)
proof={'status':'PASS','scene':s.name,'source':str(P),'sourceSHA256':expected,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'historicalScenesPreserved':len(history),'scenes':len(bpy.data.scenes),'floors':floorproof,'groundShapeAndTopologyUnchanged':True,'lightingAndExposureUnchanged':True,'nativeScreenRayReflectionsEnabled':True,'grainTileMetres':tile,'newEdgePools':len(added),'totalDampPockets':len(added)+5,'crowdCount':189,'muralStates':8,'paintedCircle':False,'runtimeObjects':len(runtime),'productionWebsiteChanged':False};(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');assert sha(P)==expected
ex=bpy.data.scenes.new('TEMP EXPORT / wet road');bpy.context.window.scene=ex
for o in runtime:ex.collection.objects.link(o);o.select_set(True)
bpy.context.view_layer.objects.active=floors[0]
bpy.ops.export_scene.gltf(filepath=str(R/'delivery/Rev15T2-Wet-Grain-Asphalt-Ground.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_yup=True,export_materials='EXPORT',export_normals=True,export_texcoords=True)
import runpy
runpy.run_path(str(R/'source/fix-export.py'))
print('BUILD_DONE',json.dumps(proof),flush=True)
