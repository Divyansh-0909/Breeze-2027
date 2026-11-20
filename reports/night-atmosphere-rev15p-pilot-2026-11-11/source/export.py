"""Disposable evaluated export scene; never saves either Blender master."""
import bpy,bmesh,json,math,hashlib,time
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=R/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(P);bpy.ops.wm.open_mainfile(filepath=str(P));pilot=bpy.context.scene;pilot.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
materials={};converted=[];bakes=[]
texture_dir=R/'viewer/textures';texture_dir.mkdir(exist_ok=True)

def png(image,path):image.filepath_raw=str(path);image.file_format='PNG';image.save();return image
def basic(name,color=(.3,.3,.3,1),rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=rough;return m,bs

# Bake unsupported spatial shader graphs to texture in a tiny isolated scene.
bake_scene=bpy.data.scenes.new('REV15P TEMP / material bake');bake_scene.render.engine='CYCLES';bake_scene.cycles.samples=1;bake_scene.render.bake.margin=4
def bake_color(original,source=None,size=1024,warm=False):
 bpy.context.window.scene=bake_scene
 if source:
  ob=source.copy();ob.data=source.data.copy();ob.matrix_world=source.matrix_world.copy()
 else:
  x,y,z=(-15.895,26,7.24) if warm else (0,0,0)
  me=bpy.data.meshes.new('Tile');me.from_pydata([(x,y,z),(x,y+2.48,z),(x,y+2.48,z+2.48),(x,y,z+2.48)],[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new(name='UVMap')
  for loop,value in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=value
  ob=bpy.data.objects.new('Tile',me)
 bake_scene.collection.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False;ob.animation_data_clear()
 m=original.copy();ob.data.materials.clear();ob.data.materials.append(m);nodes=m.node_tree.nodes;links=m.node_tree.links
 # Choose the brick branch for spatially selected Events material.
 bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED' and (not warm or 'brick' in n.name.lower())),None) or next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');em=nodes.new('ShaderNodeEmission')
 if bs.inputs['Base Color'].is_linked:links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color'])
 else:em.inputs['Color'].default_value=bs.inputs['Base Color'].default_value
 links.new(em.outputs[0],output.inputs['Surface'])
 image=bpy.data.images.new('BAKED / '+original.name,width=size,height=size,alpha=False);target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
 for a in bake_scene.objects:a.select_set(False)
 ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.bake(type='EMIT')
 path=texture_dir/('material-'+str(len(bakes))+'.png');png(image,path);bakes.append({'sourceMaterial':original.name,'method':'Cycles EMIT bake of original Base Color graph','size':size,'file':str(path.relative_to(R)),'sourceObject':source.name if source else None})
 bake_scene.collection.objects.unlink(ob);bpy.data.objects.remove(ob,do_unlink=True)
 return image

black_orig=next(m for m in bpy.data.materials if m.name=='REV15K / matte black-painted brick');black_image=bake_color(black_orig)
warm_orig=next(m for m in bpy.data.materials if m.name.startswith('REV15N / warm house brick over'));warm_image=bake_color(warm_orig,warm=True)
brick_black,bs=basic('WEB / black painted brick',rough=.91);t=brick_black.node_tree.nodes.new('ShaderNodeTexImage');t.image=black_image;brick_black.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
brick_warm,bs=basic('WEB / warm Events brick',rough=.87);t=brick_warm.node_tree.nodes.new('ShaderNodeTexImage');t.image=warm_image;brick_warm.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])

def convert(m,source=None):
 if m in materials:return materials[m]
 if m==black_orig:materials[m]=brick_black;return brick_black
 if any(n.type=='GROUP' for n in m.node_tree.nodes) and source and source.get('artKind'):
  image=bake_color(m,source=source,size=2048);new,bs=basic('WEB / baked '+m.name);tex=new.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;new.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);materials[m]=new;return new
 nodes=m.node_tree.nodes if m.use_nodes else []
 bs=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
 color=tuple(bs.inputs['Base Color'].default_value) if bs else tuple(m.diffuse_color)
 new,b=basic('WEB / '+m.name,color,bs.inputs['Roughness'].default_value if bs else .8)
 if bs:
  for key in ['Metallic','Emission Color','Emission Strength','Alpha']:
   b.inputs[key].default_value=bs.inputs[key].default_value
 new.diffuse_color=color
 mix=next((n for n in nodes if n.type=='MIX_RGB' and n.inputs[2].is_linked),None)
 images=[n for n in nodes if n.type=='TEX_IMAGE' and n.image]
 base=next((n for n in images if any(k in n.image.name.lower() for k in ['basecolor','albedo','diffuse'])),None)
 if not base and bs and bs.inputs['Base Color'].is_linked and bs.inputs['Base Color'].links[0].from_node.type=='TEX_IMAGE':base=bs.inputs['Base Color'].links[0].from_node
 if not base:base=next((n for n in images if not any(k in n.image.name.lower() for k in ['normal','rough','height','mask'])),None)
 if base:
  image=base.image
  # Bake the source texture/paint tint mix to pixels in linear colour space.
  if mix and mix.blend_type=='MIX':
   w,h=image.size;arr=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(arr);arr=arr.reshape((-1,4));fac=float(mix.inputs[0].default_value);tint=np.array(mix.inputs[1].default_value[:3]);arr[:,:3]=arr[:,:3]*fac+tint*(1-fac)
   baked=bpy.data.images.new('Tint baked / '+m.name,width=w,height=h,alpha=False);baked.pixels.foreach_set(arr.ravel());baked.update();image=baked
  tex=new.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;new.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color'])
  if bs and bs.inputs['Emission Strength'].default_value>0:new.node_tree.links.new(tex.outputs['Color'],b.inputs['Emission Color'])
  if bs and bs.inputs['Alpha'].is_linked:new.node_tree.links.new(tex.outputs['Alpha'],b.inputs['Alpha']);new.surface_render_method='DITHERED'
 for n in images:
  if 'normal' in n.image.name.lower():
   tex=new.node_tree.nodes.new('ShaderNodeTexImage');tex.image=n.image;normal=new.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.24;new.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);new.node_tree.links.new(normal.outputs[0],b.inputs['Normal']);break
 if 'Damp patches' in m.name:
  new['dampFloor']=True;b.inputs['Roughness'].default_value=.68
 converted.append({'source':m.name,'export':new.name,'texture':base.image.name if base else None,'method':'PBR inputs, explicit linear tint bake, evaluated UV conversion','approximation':'damp procedural roughness replaced by baked roughness texture in viewer' if 'Damp patches' in m.name else None})
 materials[m]=new;return new

export_scene=bpy.data.scenes.new('REV15P TEMP / representative lane cypher');export_scene.world=pilot.world.copy();export_scene.render.engine='CYCLES';export_scene.cycles.samples=4
records=[];floors=[];lights=[]
for original in pilot.objects:
 if original.hide_render or original.type not in ['MESH','FONT','CURVE','LIGHT']:continue
 if original.type=='LIGHT':
  a=original.copy();a.data=original.data.copy();export_scene.collection.objects.link(a);lights.append(a);continue
 if original.get('artKind') and original.get('carouselSlide')!=0:continue
 if 'Bounded lane haze' in original.name:continue
 pts=[original.matrix_world@Vector(v) for v in original.bound_box]
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if hi[1]<-34 or lo[1]>34 or hi[0]<-24 or lo[0]>24:continue
 evaluated=original.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);mesh.transform(evaluated.matrix_world);mesh.update()
 ob=bpy.data.objects.new('WEB / '+original.name,mesh);ob['sourceObject']=original.name;ob['ledScreen']=bool(original.get('ledScreen'));export_scene.collection.objects.link(ob)
 source_mats=[slot.material for slot in original.material_slots];mesh.materials.clear()
 for m in source_mats:mesh.materials.append(convert(m,source=original) if m else basic('WEB / default')[0])
 uv=mesh.uv_layers.new(name='WEB_METERS');mesh.uv_layers.active=uv;uv.active_render=True
 warm_index=None
 for p in mesh.polygons:
  m=source_mats[p.material_index] if p.material_index<len(source_mats) else None
  if not m:continue
  world_center=p.center;is_warm=m.name.startswith('REV15N / warm house brick') and -16.4<=world_center.x<=-14.8 and 25.2<=world_center.y<=37 and 7.19<=world_center.z<=9.83
  is_black=m==black_orig
  if is_warm:
   if warm_index is None:warm_index=len(mesh.materials);mesh.materials.append(brick_warm)
   p.material_index=warm_index
  nd=m.node_tree.nodes if m.use_nodes else []
  un=next((n for n in nd if n.type=='UVMAP'),None)
  scale=next((float(n.inputs['Scale'].default_value) for n in nd if n.type=='VECT_MATH' and n.operation=='SCALE'),1)
  src_uv=mesh.uv_layers.get(un.uv_map) if un else next((x for x in mesh.uv_layers if x!=uv),None)
  for li in p.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(co.y/2.48,co.z/2.48) if is_warm or is_black else tuple(v*scale for v in src_uv.data[li].uv) if src_uv else (co.x,co.y)
 # Export UV0 only plus a deliberate second UV for floor lighting.
 for layer in list(mesh.uv_layers):
  if layer.name!='WEB_METERS':mesh.uv_layers.remove(layer)
 mesh.uv_layers[0].name='UVMap'
 if any('Damp patches' in m.name for m in source_mats if m):
  ob['bakedGround']=True;uv2=mesh.uv_layers.new(name='PilotLightUV')
  for p in mesh.polygons:
   for li in p.loop_indices:
    co=mesh.vertices[mesh.loops[li].vertex_index].co
    uv2.data[li].uv=((co.x+4.5)/9*.97+.015,(co.y+35)/90*.97+.015) if p.normal.z>.5 else (.002,.002)
  floors.append(ob)
 records.append({'source':original.name,'object':ob.name,'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),'sourceBounds':[lo,hi],'materials':[m.name for m in mesh.materials]})

# Bake actual static direct/indirect diffuse illumination and occlusion to UV1.
bpy.context.window.scene=export_scene
image=bpy.data.images.new('REV15P / static ground lighting',width=512,height=2048,alpha=False);image.colorspace_settings.name='Non-Color'
for ob in floors:
 ob.data.uv_layers.active=ob.data.uv_layers['PilotLightUV']
 for m in ob.data.materials:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.nodes.active=node
for ob in export_scene.objects:ob.select_set(False)
export_scene.render.bake.use_clear=False;export_scene.render.bake.margin=2;export_scene.render.bake.use_pass_color=False;export_scene.render.bake.use_pass_direct=True;export_scene.render.bake.use_pass_indirect=True
for ob in floors:ob.select_set(True)
bpy.context.view_layer.objects.active=floors[0];bpy.ops.object.bake(type='DIFFUSE');png(image,texture_dir/'ground-lightmap.png')
group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree');group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
for ob in floors:
 ob.data.uv_layers.active=ob.data.uv_layers['UVMap'];ob.data.uv_layers['UVMap'].active_render=True
 for m in ob.data.materials:
  m['groundLightmap']='textures/ground-lightmap.png';nd=m.node_tree.nodes;tex=nd.new('ShaderNodeTexImage');tex.image=image;uv=nd.new('ShaderNodeUVMap');uv.uv_map='PilotLightUV';m.node_tree.links.new(uv.outputs[0],tex.inputs[0]);g=nd.new('ShaderNodeGroup');g.node_tree=group;m.node_tree.links.new(tex.outputs['Color'],g.inputs['Occlusion'])
for a in lights:export_scene.collection.objects.unlink(a)

# Merge compatible static props by exact material, preserving world positions.
# This is export data only; baked ground, transparent and artwork remain separate.
for ob in export_scene.objects:ob.select_set(False)
groups={}
for ob in list(export_scene.objects):
 if ob.type=='MESH' and not ob.get('bakedGround') and len(ob.data.materials)==1 and not any(k in ob.name for k in ['painted mural','animated sponsor LED']):groups.setdefault(ob.data.materials[0].name,[]).append(ob)
for names,objects in groups.items():
 if len(objects)<2:continue
 for ob in export_scene.objects:ob.select_set(False)
 for ob in objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
for ob in export_scene.objects:ob.select_set(True)
options=dict(export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_extras=True,export_cameras=False,export_lights=False,export_image_format='AUTO')
t=time.monotonic();bpy.ops.export_scene.gltf(filepath=str(R/'viewer/pilot.glb'),**options)
compression={'baselineBytes':(R/'viewer/pilot.glb').stat().st_size}
try:
 bpy.ops.export_scene.gltf(filepath=str(R/'viewer/pilot-draco.glb'),export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,**options)
 compression.update(dracoBytes=(R/'viewer/pilot-draco.glb').stat().st_size,dracoStatus='EXPORTED; browser decode verification pending')
except Exception as e:compression['dracoError']=str(e)
assert sha(P)==before
(R/'evidence/export.json').write_text(json.dumps({'status':'PASS','pilotMasterUnchanged':True,'pilotSHA256':before,'sourceObjects':len(records),'exportMergedObjects':len(export_scene.objects),'evaluatedTriangles':sum(r['triangles'] for r in records),'objects':records,'materialConversions':converted,'bakes':bakes,'lightmap':{'file':'viewer/textures/ground-lightmap.png','size':[512,2048],'channel':1,'UVName':'PilotLightUV','method':'Cycles DIFFUSE, direct+indirect, no albedo, four samples; UV1 bound explicitly in viewer; no runtime lightmap guarantee assumed','groundMeshes':len(floors)},'compression':compression,'seconds':time.monotonic()-t,'limits':['Single representative export; current OC slide only. All 8 slides remain in Blender pilot.','No crowd rigs; static pose meshes.','Damp procedural roughness needs viewer texture conversion.','KTX2 encoding not claimed without encoder and browser check.']},indent=2));print('EXPORT COMPLETE',compression,flush=True)
