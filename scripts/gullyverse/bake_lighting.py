"""Dense shared light UVs, one invisible bake receiver, original PBR/alpha context.
Transparent paint does not cast opaque rectangular shadows. The master is read-only.
"""
import argparse,bmesh,bpy,hashlib,json,math,os,sys,time
from pathlib import Path
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--manifest');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
plan=json.loads(Path(os.environ.get('GULLYVERSE_PLAN',str(Path(__file__).with_name('export-plan.json')))).read_text());out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/plan['output'])));out.mkdir(parents=True,exist_ok=True)
source=Path(plan['source']['path']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(source)==plan['source']['sha256']
cached=Path(args.input or out/'contact-frontage-baked.blend');manifest=json.loads(Path(args.manifest or out/'manifest.json').read_text());assert manifest['source']['sha256']==plan['source']['sha256'];cacheSHA=sha(cached)
quality=plan.get('quality',{});uvName=quality.get('uvName','RuntimeIrradianceUV');size=quality.get('resolution',2048);samples=quality.get('samples',256);rayBias=quality.get('rayBiasM',.001)
bpy.ops.wm.open_mainfile(filepath=str(source));native=bpy.context.scene;assert native.name==plan['source']['scene'];native.frame_set(1);bpy.context.view_layer.update()
with bpy.data.libraries.load(str(cached))as(a,b):b.collections=['Runtime / contact-frontage']
collection=b.collections[0];targets=list(collection.objects);scene=bpy.data.scenes.new('Runtime / clean lighting build only');scene.world=native.world.copy();scene.collection.children.link(collection);bpy.context.window.scene=scene
def is_decal(ob):
 return any(m and m.use_nodes and any(n.type=='TEX_IMAGE'and n.image and any(k in n.image.name.lower()for k in ['graffiti','coming soon'])for n in m.node_tree.nodes)for m in ob.data.materials)
decals=[o for o in targets if is_decal(o)]
for ob in targets:
 me=ob.data
 if me.uv_layers.get(uvName):me.uv_layers.remove(me.uv_layers[uvName])
 assert len(me.uv_layers)<4,'Three/GLTF UV channels exceeded'
 me.uv_layers.new(name=uvName);me.uv_layers.active=me.uv_layers[uvName]
 for uv in me.uv_layers:uv.active_render=uv.name==uvName
 for mat in me.materials:
  mat['runtimeLightmapChannel']=list(me.uv_layers).index(me.uv_layers[uvName]);mat['runtimeDecal']=is_decal(ob)
 ob['runtimeLightmapChannel']=list(me.uv_layers).index(me.uv_layers[uvName]);ob['runtimeLightmapUV']=uvName
 if is_decal(ob):ob.visible_shadow=False
if quality.get('isolatedIrradianceTiles'):
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from irradiance_tiles import pack_light_tiles
 pack_light_tiles(targets,uvName,size)
else:
 for ob in scene.objects:ob.select_set(ob in targets)
 bpy.context.view_layer.objects.active=targets[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004,area_weight=0,correct_aspect=False);bpy.ops.uv.select_all(action='SELECT');bpy.ops.uv.average_islands_scale();bpy.ops.uv.pack_islands(rotate=True,margin=.004,margin_method='FRACTION');bpy.ops.object.mode_set(mode='OBJECT')
channelRows=[{'node':o.name,'channel':o['runtimeLightmapChannel'],'uvLayers':[u.name for u in o.data.uv_layers]}for o in targets]
vertices=[];polygons=[];uvs=[];normals=[];smooth=[]
for ob in targets:
 me=ob.data;normalMatrix=ob.matrix_world.to_3x3().inverted().transposed()
 for p in me.polygons:
  face=[]
  for li in p.loop_indices:
   face.append(len(vertices));vertices.append(tuple(ob.matrix_world@me.vertices[me.loops[li].vertex_index].co+(normalMatrix@me.corner_normals[li].vector).normalized()*rayBias));uvs.append(tuple(me.uv_layers[uvName].data[li].uv));normals.append(tuple((normalMatrix@me.corner_normals[li].vector).normalized()))
  polygons.append(face);smooth.append(p.use_smooth)
mesh=bpy.data.meshes.new('Build-only shared irradiance receiver');mesh.from_pydata(vertices,[],polygons);mesh.update();uv=mesh.uv_layers.new(name=uvName)
for d,p in zip(uv.data,uvs):d.uv=p
for f,s in zip(mesh.polygons,smooth):f.use_smooth=s
mesh.normals_split_custom_set(normals);receiver=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(receiver)
lo=Vector(tuple(min(p[i]for p in vertices)for i in range(3)))
hi=Vector(tuple(max(p[i]for p in vertices)for i in range(3)))
# The mesh now owns these arrays. Release the Python copies before Cycles
# allocates its BVH and textures, especially for the audience receiver.
del vertices,polygons,uvs,normals,smooth
for prop in ['visible_shadow','visible_diffuse','visible_glossy','visible_transmission']:setattr(receiver,prop,False)
mat=bpy.data.materials.new('Build-only neutral diffuse receiver');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,1,1,1);p.inputs['Roughness'].default_value=1;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=0;mesh.materials.append(mat)
image=bpy.data.images.new('Clean irradiance',width=size,height=size,alpha=False,float_buffer=True,is_data=True);image.colorspace_settings.name='Non-Color';tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.nodes.active=tex
faces={r['sourceObject']:r['sourceFaces']for r in manifest['objects']}
for row in manifest['objects']:
 for member in row.get('batchedSourceObjects',[]):faces[member]='ALL'
targetNames=set(faces);contextMats={};overrides=[]
def neutral_emission(m):
 if m.as_pointer()in contextMats:return contextMats[m.as_pointer()]
 c=m.copy();contextMats[m.as_pointer()]=c
 if c.use_nodes:
  for node in c.node_tree.nodes:
   key='Emission Strength'if node.type=='BSDF_PRINCIPLED'else'Strength'if node.type=='EMISSION'else None
   if key:
    for link in list(node.inputs[key].links):c.node_tree.links.remove(link)
    node.inputs[key].default_value=0
 return c
def suppress_emission(ob,restore=False):
 for slot in ob.material_slots:
  if not slot.material:continue
  original=slot.material;link=slot.link
  if restore:overrides.append((slot,link,original))
  slot.link='OBJECT';slot.material=neutral_emission(original)
for ob in targets:suppress_emission(ob,True)
lights=[];excluded=[]
for old in native.objects:
 if old.hide_render or old.get('contactPart')in ['native form label','native form illustration']:continue
 if old.type=='VOLUME'or(old.type=='MESH'and any(m and m.use_nodes and any(n.type in ['PRINCIPLED_VOLUME','VOLUME_ABSORPTION','VOLUME_SCATTER']for n in m.node_tree.nodes)for m in old.data.materials)):
  excluded.append(old.name);continue
 if old.type=='LIGHT':
  pos=old.matrix_world.translation;distance=math.sqrt(sum(max(lo[i]-pos[i],0,pos[i]-hi[i])**2 for i in range(3)));include=old.data.energy>0 and(not old.data.use_custom_distance or distance<old.data.cutoff_distance)
  if include:scene.collection.objects.link(old)
  lights.append({'name':old.name,'energy':old.data.energy,'included':include,'nativeCutoff':old.data.cutoff_distance if old.data.use_custom_distance else None});continue
 if old.name in targetNames and faces[old.name]=='ALL':continue
 c=old.copy();c.name='Lighting context / '+old.name;scene.collection.objects.link(c)
 if old.name in faces:
  c.data=old.data.copy();bm=bmesh.new();bm.from_mesh(c.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i]for i in faces[old.name]],context='FACES');bm.to_mesh(c.data);bm.free()
 if old.type=='MESH':
  suppress_emission(c)
  if is_decal(c):c.visible_shadow=False
for ob in scene.objects:ob.select_set(ob==receiver)
bpy.context.view_layer.objects.active=receiver;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=samples;scene.cycles.seed=plan['bake']['seed'];scene.cycles.max_bounces=3;scene.cycles.diffuse_bounces=2;scene.cycles.use_light_tree=True;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.bake.use_clear=True;scene.render.bake.margin=12;scene.render.bake.use_pass_color=False;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True
if quality.get('isolatedIrradianceTiles'):scene.render.bake.margin=2
print('QUALITY_BAKE_START',samples,len(mesh.vertices),len(mesh.polygons),flush=True);start=time.monotonic();bpy.ops.object.bake(type='DIFFUSE',uv_layer=uvName);values=np.empty(size*size*4,np.float32);image.pixels.foreach_get(values);assert np.isfinite(values).all();rgb=values.reshape(size,size,4)[...,:3];lit_fraction=float((rgb.max(axis=2)>1e-6).mean());assert lit_fraction>0,'The raw irradiance atlas is empty';print('RAW_IRRADIANCE_COVERAGE',lit_fraction,flush=True);pfm=out/'irradiance.raw.pfm';pfm.write_bytes(f'PF\n{size} {size}\n-1.0\n'.encode()+np.asarray(rgb,dtype='<f4').tobytes());image.filepath_raw=str(out/'lightmap.raw.hdr');image.file_format='HDR';image.save()
for slot,link,original in overrides:
 slot.link=link
 if link=='OBJECT':slot.material=original
bpy.data.libraries.write(str(out/'contact-frontage-baked.blend'),{collection,scene.world},fake_user=True,compress=True)
manifest.update(version=plan['version'],source=plan['source'],artworkUnmodified=True,masterUnchanged=True)
manifest['bake']={'engine':'Cycles CPU; combined bake-only receiver','samples':samples,'seed':plan['bake']['seed'],'bounces':3,'diffuseBounces':2,'resolution':[size,size],'uvName':uvName,'fogBaked':False,'method':'Dense area-weighted shared UV atlas; proxy has no shadow/diffuse/glossy/transmission visibility; original PBR meshes supply occlusion and bounce; transparent paint casts no rectangular shadow','lightmapIntensity':math.pi,'volumeExclusions':excluded,'lightSelection':lights,'channelBindings':channelRows,'rawPFMSHA256':sha(pfm),'seconds':time.monotonic()-start,'sampleBiasM':rayBias,'previousBakedComponentSHA256':cacheSHA,'decalsWithoutShadow':[o.name for o in decals],'denoising':'Pending OIDN RTLightmap; must pass numerical no-op guard'}
manifest['sourceBakedDerivative']={'file':'contact-frontage-baked.blend','sha256':sha(out/'contact-frontage-baked.blend'),'bytes':(out/'contact-frontage-baked.blend').stat().st_size};(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert sha(source)==plan['source']['sha256'];print('QUALITY_BAKE_PASS',manifest['bake']['seconds'],flush=True)
