"""Locked native -> bounded representative runtime chunk. Never saves the source.

Source artwork/PBR image channels keep their original bytes and UVs. Unsupported
procedural channels are baked; static diffuse direct+indirect lighting receives a
separate, explicitly bound UV atlas. Full native visibility is used for shadows.
"""
import bpy,bmesh,json,hashlib,math,argparse,sys,time
from pathlib import Path
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[2];ap=argparse.ArgumentParser();ap.add_argument('--plan',default=str(Path(__file__).with_name('export-plan.json')));ap.add_argument('--out');ap.add_argument('--samples',type=int);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);plan=json.loads(Path(a.plan).read_text());out=Path(a.out or ROOT/plan['output']);out.mkdir(parents=True,exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=Path(plan['source']['path']);assert sha(source)==plan['source']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));native=bpy.context.scene;assert native.name==plan['source']['scene'];native.frame_set(1);bpy.context.view_layer.update();sourceMembers={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes};m=plan['contact'];n=Vector(m['normal']);t=Vector(m['tangent']);up=Vector((0,0,1));uvName=plan['bake']['uvName'];size=plan['bake']['resolution'];P=lambda u,d,z:t*u+n*d+up*z
formOnly={'native form label','native form illustration'};omissions=[];targets=[];contexts=[];faceSelection=[];sourceRows=[];materialRows=[];timings=[]
selection=plan.get('selection',{})
explicit=set(selection.get('sourceObjects',[]))
whole=set(selection.get('wholeObjects',[]))
mesh_overrides=selection.get('meshOverrides',{})
evaluated_parts={}
if explicit:
 deps=bpy.context.evaluated_depsgraph_get()
 for old in native.objects:
  if old.name not in explicit:continue
  needs_evaluation=old.type in ('FONT','CURVE') or (
   old.type=='MESH' and old.name in whole and old.modifiers and selection.get('evaluateWholeMeshes')
  )
  if not needs_evaluation:continue
  assert old.name in whole, f'Keep the whole evaluated sign or cable: {old.name}'
  evaluated=old.evaluated_get(deps)
  mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
  evaluated_parts[old.name]=(mesh,evaluated.matrix_world.copy())
scene=native.copy();scene.name='RUNTIME BUILD ONLY / contact-frontage';scene.world=native.world.copy()
for c in list(scene.collection.children):scene.collection.children.unlink(c)
for o in list(scene.collection.objects):scene.collection.objects.unlink(o)
bpy.context.window.scene=scene;collection=bpy.data.collections.new('Runtime / contact-frontage');scene.collection.children.link(collection)
def intersects(o):
 bb=[o.matrix_world@Vector(p)for p in o.bound_box];us=[p.dot(t)for p in bb];ds=[p.dot(n)for p in bb];zs=[p.z for p in bb]
 return min(us)<m['frameBoundsU'][1]+1.2 and max(us)>m['frameBoundsU'][0]-1.2 and min(ds)<-19.5 and max(ds)>-23.1 and min(zs)<13.5 and max(zs)>7.15
def in_bounds(p):
 if bounds := plan.get('selection', {}).get('worldFaceBounds'):
  return all(lo <= p[i] <= hi for i, (lo, hi) in enumerate(bounds))
 depth=plan.get('selection',{}).get('depthBounds',[-23.1,-19.5])
 height=plan.get('selection',{}).get('heightBounds',[7.15,13.5])
 return m['frameBoundsU'][0]-1.2<=p.dot(t)<=m['frameBoundsU'][1]+1.2 and depth[0]<=p.dot(n)<=depth[1] and height[0]<=p.z<=height[1]
def copy_mesh(old,indices=None):
 if old.name in evaluated_parts:
  mesh,matrix=evaluated_parts[old.name]
  ob=bpy.data.objects.new('Runtime / '+old.name,mesh)
  ob.matrix_world=matrix
  for key in old.keys():ob[key]=old[key]
 else:
  ob=old.copy();ob.name='Runtime / '+old.name
  mesh=bpy.data.meshes[mesh_overrides[old.name]] if old.name in mesh_overrides else old.data
  ob.data=mesh.copy();ob.parent=None;ob.matrix_world=old.matrix_world
 collection.objects.link(ob)
 original_uvs=[uv.name for uv in ob.data.uv_layers]
 original_materials=[mat.name if mat else None for mat in ob.data.materials]
 if indices is not None:
  original=[v.co.copy()for v in old.data.vertices];lo=Vector(tuple(min(v[i]for v in original)for i in range(3)));hi=Vector(tuple(max(v[i]for v in original)for i in range(3)));attr=ob.data.attributes.new('RuntimeOriginalGenerated','FLOAT_VECTOR','POINT')
  for v,dst in zip(original,attr.data):dst.vector=tuple((v[i]-lo[i])/max(hi[i]-lo[i],1e-8)for i in range(3))
  keep=set(indices);bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in keep],context='FACES');bm.to_mesh(ob.data);bm.free();ob.data.update()
 row={'node':ob.name,'sourceObject':old.name,'sourceFaces':indices if indices is not None else 'ALL','originalUVLayers':original_uvs,'originalMaterials':original_materials}
 if old.name in mesh_overrides:row.update(sourceMesh=old.data.name,runtimeMesh=mesh_overrides[old.name])
 targets.append(ob);sourceRows.append(row);return ob
for old in sorted(native.objects,key=lambda o:o.name):
 part=old.get('contactPart')
 if old.type=='VOLUME' or (old.type=='MESH'and any(mat and mat.use_nodes and any(n.type in ['PRINCIPLED_VOLUME','VOLUME_ABSORPTION','VOLUME_SCATTER']for n in mat.node_tree.nodes)for mat in old.data.materials)):
  omissions.append({'object':old.name,'reason':'Atmosphere volume excluded from textures; browser fog is a separate runtime effect'});continue
 if old.hide_render:omissions.append({'object':old.name,'reason':'Hidden source variant; retained in whole-world inventory'});continue
 if part in formOnly:omissions.append({'object':old.name,'reason':'Authoring form illustration; replaced by accessible HTML form'});continue
 if part=='local house light':omissions.append({'object':old.name,'reason':'Static light contribution baked; no runtime diffuse lamp'});scene.collection.objects.link(old);continue
 if (old.type=='MESH' or old.name in evaluated_parts) and ((old.name in explicit) if explicit else (part or intersects(old))):
  indices=None
  if not part and old.name not in whole:
   excluded_faces=selection.get('excludedFaces',{}).get(old.name)
   if excluded_faces is not None:
    excluded=set(excluded_faces)
    assert excluded <= set(range(len(old.data.polygons))), old.name
    indices=[p.index for p in old.data.polygons if p.index not in excluded]
   else:
    indices=[p.index for p in old.data.polygons if in_bounds(old.matrix_world@p.center)]
   if not indices:scene.collection.objects.link(old);contexts.append(old.name);continue
  ob=copy_mesh(old,indices)
  if indices is not None:
   # Preserve remaining source faces as bake-only shadow/bounce context.
   rest=old.copy();rest.name='Bake context / '+old.name;rest.data=old.data.copy();scene.collection.objects.link(rest);bm=bmesh.new();bm.from_mesh(rest.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i]for i in indices],context='FACES');bm.to_mesh(rest.data);bm.free();contexts.append(old.name);faceSelection.append({'object':old.name,'exportedFaces':len(indices),'sourceFaces':len(old.data.polygons)})
  continue
 scene.collection.objects.link(old);contexts.append(old.name)
assert targets and (not plan.get('selection',{}).get('sourceObjects')or len(targets)==len(plan['selection']['sourceObjects']))
if not plan.get('selection',{}).get('sourceObjects'):assert any(o.get('contactPart')=='contact heading'for o in targets)
prunedMaterialBindings=0
for ob in targets:
 me=ob.data;allMaterials=list(me.materials);used=sorted({p.material_index for p in me.polygons});mapping={old:i for i,old in enumerate(used)};oldIndices=[p.material_index for p in me.polygons]
 me.materials.clear()
 for i in used:me.materials.append(allMaterials[i])
 for face,oldIndex in zip(me.polygons,oldIndices):face.material_index=mapping[oldIndex]
 prunedMaterialBindings+=len(allMaterials)-len(used)
 if ob.get('contactPart')=='contact heading':
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bm.to_mesh(me);bm.free();me.update()
assert not any(o.get('contactPart')=='attendant'for o in targets)
if selection.get('batchStaticProps'):
 from collections import defaultdict
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from market_batches import batch_key
 batches=defaultdict(list)
 rows_by_object=dict(zip(targets,sourceRows))
 for ob in targets:
  key=batch_key(ob,rows_by_object[ob])
  if key is not None:batches[key].append(ob)
 for selected in bpy.context.selected_objects:selected.select_set(False)
 removed=set()
 for members in batches.values():
  if len(members)<2:continue
  lead,*rest=members
  expected_faces=sum(len(ob.data.polygons) for ob in members)
  rows_by_object[lead]['batchedSourceObjects']=[rows_by_object[ob]['sourceObject'] for ob in rest]
  removed.update(ob.name for ob in rest)
  for ob in members:ob.select_set(True)
  bpy.context.view_layer.objects.active=lead
  bpy.ops.object.join()
  assert len(lead.data.polygons)==expected_faces,lead.name
  lead.select_set(False)
 remaining=[(ob,row) for ob,row in zip(targets,sourceRows) if row['node'] not in removed]
 targets,sourceRows=map(list,zip(*remaining))
 print('BATCHED_STATIC_PROPS',len(removed), 'remaining meshes',len(targets),flush=True)
# Independent materials retain source references. Default UV reads are pinned
# before the bake UV is added, preserving existing image sampling.
unsupported={};maps={'color':'Base Color','roughness':'Roughness','metallic':'Metallic','normal':'Normal'}
def upstream(socket,seen=None):
 seen=set()if seen is None else seen
 for link in socket.links:
  node=link.from_node
  if node.as_pointer()in seen:continue
  seen.add(node.as_pointer());yield node
  for inp in node.inputs:yield from upstream(inp,seen)
for ob in targets:
 me=ob.data;srcUV=me.uv_layers.active_render.name if hasattr(me.uv_layers,'active_render')and me.uv_layers.active_render else next((u.name for u in me.uv_layers if u.active_render),me.uv_layers[0].name if len(me.uv_layers)else None)
 ob['runtimeOriginalSource']=sourceRows[targets.index(ob)]['sourceObject'];ob['runtimeChunk']=plan.get('chunk','contact-frontage')
 for i,mat in enumerate(list(me.materials)):
  if not mat:continue
  mat=mat.copy();mat.name='Runtime / '+ob.name.removeprefix('Runtime / ')+' / material '+str(i);me.materials[i]=mat;nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
  if not p:p=next((x for x in nodes if x.type=='BSDF_PRINCIPLED'),None)
  assert p,('Unsupported surface graph',mat.name)
  if plan.get('chunk')=='cypher-approach' and (
   ob.get('navigationLabel') and ob.name in {f'Runtime / {name}' for name in evaluated_parts}
   or ob.get('direction') or 'White inset border' in ob.name
  ):
   mat['runtimeSignInk']=True
  if ob.get('ledScreen'):
   # The browser shader reproduces the source dot matrix and scroll clock.
   # Preserve mesh/UVs, and carry the actual packed grayscale strip separately.
   strip=next(x.image for x in nodes if x.type=='TEX_IMAGE' and x.image and x.image.packed_file)
   (out/'sponsor-strip.png').write_bytes(bytes(strip.packed_file.data))
   for link in list(p.inputs['Emission Strength'].links):links.remove(link)
   p.inputs['Emission Strength'].default_value=0
  if srcUV:
   for node in list(nodes):
    if node.type=='TEX_IMAGE'and not node.inputs['Vector'].is_linked:
     uv=nodes.new('ShaderNodeUVMap');uv.uv_map=srcUV;links.new(uv.outputs['UV'],node.inputs['Vector'])
  if me.attributes.get('RuntimeOriginalGenerated'):
   generated=nodes.new('ShaderNodeAttribute');generated.attribute_name='RuntimeOriginalGenerated'
   for node in list(nodes):
    if node.type=='TEX_COORD':
     for link in list(node.outputs['Generated'].links):links.new(generated.outputs['Vector'],link.to_socket)
    elif node.type.startswith('TEX_')and node.type!='TEX_IMAGE'and node.inputs.get('Vector')and not node.inputs['Vector'].is_linked:links.new(generated.outputs['Vector'],node.inputs['Vector'])
  needed=[]
  for key,socket in maps.items():
   graph=list(upstream(p.inputs[socket]));types={x.type for x in graph}
   if p.inputs[socket].is_linked and (types-{'TEX_IMAGE','UVMAP','NORMAL_MAP','SEPRGB','SEPARATE_COLOR','COMBRGB','COMBINE_COLOR','RGB','VALUE','TEX_COORD'}):needed.append(key)
  unsupported[mat.name]=needed;materialRows.append({'name':mat.name,'sourceImages':[{'name':x.image.name,'sha256':hashlib.sha256(x.image.packed_file.data).hexdigest()}for x in nodes if x.type=='TEX_IMAGE'and x.image and x.image.packed_file],'bakedChannels':needed})
 if not plan.get('quality',{}).get('proceduralUVOnly') or any(unsupported.get(m.name) for m in me.materials if m):
  me.uv_layers.new(name=uvName);me.uv_layers.active=me.uv_layers[uvName]
# Explicit disjoint object tiles avoid cross-object UV packing ambiguity.
uv_targets=[ob for ob in targets if ob.data.uv_layers.get(uvName)]
tiles=[];columns=max(1,math.ceil(math.sqrt(len(uv_targets))));pad=8/size
for index,ob in enumerate(uv_targets):
 for o in scene.objects:o.select_set(o==ob)
 bpy.context.view_layer.objects.active=ob;ob.data.uv_layers.active=ob.data.uv_layers[uvName]
 for uv in ob.data.uv_layers:uv.active_render=(uv.name==uvName)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02,area_weight=.2,correct_aspect=False);bpy.ops.object.mode_set(mode='OBJECT')
 left=(index%columns)/columns+pad;bottom=(index//columns)/columns+pad;span=1/columns-2*pad
 for v in ob.data.uv_layers[uvName].data:v.uv=(left+v.uv.x*span,bottom+v.uv.y*span)
 tiles.append({'node':ob.name,'rect':[left,bottom,left+span,bottom+span]});ob['runtimeLightmapChannel']=list(ob.data.uv_layers).index(ob.data.uv_layers[uvName])
for ob in targets:
 if not ob.data.uv_layers.get(uvName):ob['runtimeLightmapChannel']=0
for o in scene.objects:o.select_set(o in targets)
bpy.context.view_layer.objects.active=targets[0]
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples or plan['bake']['samples'];scene.cycles.seed=plan['bake']['seed'];scene.cycles.use_denoising=False;scene.cycles.max_bounces=plan['bake']['bounces'];scene.cycles.diffuse_bounces=3;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.bake.target='IMAGE_TEXTURES';scene.render.bake.use_selected_to_active=False;scene.render.bake.use_clear=False;scene.render.bake.margin=plan['bake']['margin'];scene.render.bake.normal_space='TANGENT'
materials=list({mat.as_pointer():mat for ob in targets for mat in ob.data.materials if mat}.values());images={};sourceImageNodes={}
def target_image(key,isdata=True):
 im=bpy.data.images.new('Runtime / contact / '+key,width=size,height=size,alpha=(key=='lightmap'),float_buffer=True,is_data=isdata);im.colorspace_settings.name='Non-Color'if isdata else'sRGB';images[key]=im
 for mat in materials:
  node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='Runtime bake target';node.image=im;mat.node_tree.nodes.active=node
 return im
def bake(key,kind):
 use_scene=scene
 if plan.get('quality',{}).get('isolateMaterialBake') and key!='lightmap':
  # Colour and tangent-normal transfer need only selected surfaces. Do not
  # rebuild the complete Cycles world before evaluating every sign/object.
  use_scene=bpy.data.scenes.new('Runtime procedural channels only')
  use_scene.render.engine='CYCLES'
  use_scene.cycles.device='CPU'
  use_scene.cycles.samples=scene.cycles.samples
  use_scene.render.bake.use_clear=False
  use_scene.render.bake.margin=scene.render.bake.margin
  active=[ob for ob in targets if any(key in unsupported.get(m.name,[]) for m in ob.data.materials if m)]
  for ob in active:use_scene.collection.objects.link(ob)
  bpy.context.window.scene=use_scene
  for ob in active:ob.select_set(True)
  bpy.context.view_layer.objects.active=active[0]
 start=time.monotonic()
 print('BAKE',key,flush=True)
 try:bpy.ops.object.bake(type=kind,uv_layer=uvName)
 finally:
  if use_scene!=scene:
   bpy.context.window.scene=scene
   bpy.data.scenes.remove(use_scene)
 timings.append({'channel':key,'seconds':time.monotonic()-start})
needed=set(x for v in unsupported.values()for x in v)
for key in sorted(needed):
 im=target_image(key,key!='color');restore=[]
 if key in ['color','roughness','metallic']:
  for mat in materials:
   nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=next(x for x in nodes if x.type=='BSDF_PRINCIPLED');output=next(x for x in nodes if x.type=='OUTPUT_MATERIAL'and x.is_active_output);old=[(l.from_socket,l.to_socket)for l in output.inputs['Surface'].links];em=nodes.new('ShaderNodeEmission');socket=p.inputs[maps[key]]
   if socket.is_linked:links.new(socket.links[0].from_socket,em.inputs['Color'])
   else:
    value=socket.default_value;em.inputs['Color'].default_value=tuple(value)if hasattr(value,'__len__')else(value,value,value,1)
   links.new(em.outputs[0],output.inputs['Surface']);restore.append((mat,em,old))
  bake(key,'EMIT')
  for mat,node,old in restore:
   mat.node_tree.nodes.remove(node)
   for f,tg in old:mat.node_tree.links.new(f,tg)
 else:bake(key,'NORMAL')
light=target_image('lightmap');neutral=[]
for mat in materials:
 p=next(x for x in mat.node_tree.nodes if x.type=='BSDF_PRINCIPLED')
 for key,value in [('Metallic',0),('Roughness',1),('Alpha',1)]:
  socket=p.inputs[key];old=[(l.from_socket,l.to_socket)for l in socket.links];neutral.append((mat,socket,socket.default_value,old))
  for l in list(socket.links):mat.node_tree.links.remove(l)
  socket.default_value=value
scene.render.bake.use_pass_color=False;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True
if not plan.get('quality',{}).get('skipLegacyIrradiance',False):bake('lightmap','DIFFUSE')
for mat,socket,value,old in neutral:
 socket.default_value=value
 for f,tg in old:mat.node_tree.links.new(f,tg)
light.filepath_raw=str(out/'lightmap.hdr');light.file_format='HDR';light.save()
pixels=np.empty(size*size*4,dtype=np.float32);light.pixels.foreach_get(pixels);assert np.isfinite(pixels).all();scale=max(1.0,float(pixels.reshape(-1,4)[:,:3].max()));rgb=pixels.reshape(-1,4)[:,:3].copy();rgbmRange=2**math.ceil(math.log2(scale));multiplier=np.ceil(np.clip(rgb.max(axis=1)/rgbmRange,1/255,1)*255)/255;pixels.reshape(-1,4)[:,:3]=rgb/(multiplier[:,None]*rgbmRange);pixels.reshape(-1,4)[:,3]=multiplier;light.pixels.foreach_set(pixels)
for key,im in images.items():
 im.filepath_raw=str(out/(key+'.png'));im.file_format='PNG';im.save();im.pack()
# Bake nodes become runtime PBR maps only where the source graph requires them.
for ob in targets:
 for mat in ob.data.materials:
  if not mat:continue
  nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=next(x for x in nodes if x.type=='BSDF_PRINCIPLED')
  for node in list(nodes):
   if node.name.startswith('Runtime bake target'):nodes.remove(node)
  for key in unsupported[mat.name]:
   uv=nodes.new('ShaderNodeUVMap');uv.uv_map=uvName;tex=nodes.new('ShaderNodeTexImage');tex.image=images[key];links.new(uv.outputs['UV'],tex.inputs['Vector']);socket=p.inputs[maps[key]]
   if key=='normal':
    norm=nodes.new('ShaderNodeNormalMap');norm.uv_map=uvName;links.new(tex.outputs['Color'],norm.inputs['Color']);links.new(norm.outputs['Normal'],socket)
   else:links.new(tex.outputs['Color'],socket)
  mat['runtimeLightmap']='lightmap.png';mat['runtimeLightmapChannel']=ob['runtimeLightmapChannel'];mat['runtimeLightmapIntensity']=math.pi;mat['runtimeLightmapRGBMRange']=rgbmRange
 ob['runtimeLightmap']='lightmap.png'
nativeComponent=out/'contact-frontage-baked.blend';bpy.data.libraries.write(str(nativeComponent),{collection,scene.world},fake_user=True,compress=True)
ex=bpy.data.scenes.new('Runtime export / contact-frontage');bpy.context.window.scene=ex
for ob in targets:ex.collection.objects.link(ob)
glb=out/'contact-frontage.png.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_active_scene=True,export_apply=True,export_animations=False,export_extras=True,export_lights=False,export_normals=True,export_tangents=False)
assert sha(source)==plan['source']['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in sourceMembers.items())
for ob in targets:ob.data.calc_loop_triangles()
manifest={'schemaVersion':1,'version':plan['version'],'chunk':plan.get('chunk','contact-frontage'),'source':plan['source'],'bake':{'engine':'Cycles CPU','samples':scene.cycles.samples,'seed':scene.cycles.seed,'bounces':scene.cycles.max_bounces,'resolution':[size,size],'fogBaked':False,'method':'Diffuse direct+indirect irradiance, colour excluded; neutral receiving response','encoding':'RGBM-linear','range':rgbmRange,'nativeMaxIrradiance':scale,'lightmapIntensity':math.pi,'uri':'lightmap.png','timings':timings,'atlasTiles':tiles,'explicitNonOverlappingObjectTiles':True},'objects':sourceRows,'materials':materialRows,'bakeOnlyContextObjects':contexts,'intentionalSourceExclusions':omissions,'partialSourceMeshes':faceSelection,'counts':{'objects':len(targets),'triangles':sum(len(o.data.loop_triangles)for o in targets),'materialBindings':len(materials),'runtimeDynamicLights':0},'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.iterdir())if p.is_file()],'chunks':plan['chunks'],'unusedMaterialBindingsPruned':prunedMaterialBindings,'masterUnchanged':True,'artworkUnmodified':True,'fullWorldIntegration':'PENDING'};(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('EXPORT_PASS',json.dumps({'objects':len(targets),'triangles':manifest['counts']['triangles'],'bakedChannels':sorted(needed),'lightmapScale':scale,'sourceUnchanged':True}),flush=True)
