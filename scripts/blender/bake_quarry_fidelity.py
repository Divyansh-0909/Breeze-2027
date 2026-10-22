"""Geometry-only middle/far normal atlas and C8-material editable master.
Run after compose_quarry_fidelity_volume.py. Source scan remains unchanged. No new fine
PBR family; one 1024 image, owned by a separate hidden holder at runtime.
"""
from pathlib import Path
import bpy,json,numpy as np,hashlib,struct,time,sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fidelity_runtime_border import restore_authoritative_border
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'assets-source/gullyverse/quarry-fidelity-correction';OUT=ROOT/'public/models/gullyverse/quarry-fidelity-correction'
RAW=ROOT/'reports/recovery-quarry-fidelity-2026-10-19/raw';WORK=SOURCE/'.authoring-cache';WORK.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb_read(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def glb_write(path,d,b):
 d['buffers']=[{'byteLength':len(b)}];j=json.dumps(d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b=bytes(b)+b'\0'*((-len(b))%4)
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b)

bpy.ops.wm.open_mainfile(filepath=str(WORK/'fidelity-unbaked.blend'))
spec=json.loads((OUT/'manifest.json').read_text());scene=bpy.context.scene
objects=[bpy.data.objects[f'Fidelity_Wall_15_LOD{i}']for i in range(3)]
natives=[bpy.data.objects['Fidelity_Composed_High'],bpy.data.objects['C9_Native_High_Unique_Uniform_0_9']]
assert len(natives)==2
# Inspect a real float32 glTF round trip before baking. Its normal splitting can
# reveal a corner whose Mikk frame was stable only inside Blender's source mesh.
# Mark the corresponding real fracture face hard; no positions/UV0 change and no
# fake tangent vectors. Bake after this correction so UV1 uses the final frame.
before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(OUT/'fidelity-region.glb'))
roundtrip=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];frame_repairs=[]
def key(ob,face):return tuple(sorted(tuple(ob.data.vertices[v].co)for v in face.vertices))
for imported in roundtrip:
 level=int(imported.name.split('_LOD')[1][0]);ob=objects[level];lookup={key(ob,p):p.index for p in ob.data.polygons};badfaces=set()
 for index in range(len(imported.data.uv_layers)):
  name=imported.data.uv_layers[index].name;imported.data.calc_tangents(uvmap=name)
  bad={l.index for l in imported.data.loops if np.linalg.norm(l.tangent[:])<.99}
  for p in imported.data.polygons:
   if set(p.loop_indices)&bad:badfaces.add(lookup[key(imported,p)])
 if badfaces:
  normals=[n.vector[:]for n in ob.data.corner_normals]
  for fi in badfaces:
   p=ob.data.polygons[fi];p.use_smooth=False
   for li in p.loop_indices:normals[li]=p.normal[:]
  ob.data.normals_split_custom_set(normals)
  frame_repairs.append({'LOD':level,'hardFractureFaces':sorted(badfaces),'positionsAndUV0Changed':False})
for q in roundtrip:bpy.data.objects.remove(q,do_unlink=True)
with bpy.data.libraries.load(str(ROOT/'assets-source/gullyverse/recovered-c8-material/recovered-c8-material.blend'),link=False)as(src,dst):
 dst.materials=['Recovered_C8_Scanned_Multi_PBR']
stone=dst.materials[0]
plain=bpy.data.materials.new('BAKE_GEOMETRY_ONLY_NO_FINE_NORMAL');plain.use_nodes=True
for native in natives:
 native.data.materials.clear();native.data.materials.append(plain)
# Retained near host and annulus, excluding the decimated near source. The full
# native high scan supplies that region; there are no overlapping bake faces.
near=objects[0];tags=json.loads(bpy.data.texts['NEAR_FACE_SOURCE_TAGS'].as_string())
assert len(tags)==len(near.data.polygons)
indices=[i for i,tag in enumerate(tags)if tag=='host' or tag.startswith('join_')]
mesh=bpy.data.meshes.new('C9_Bake_High_Retained_Host_And_Join');mesh.from_pydata([v.co[:]for v in near.data.vertices],[],[list(near.data.polygons[i].vertices)for i in indices]);mesh.update()
high=bpy.data.objects.new('C9_Bake_High_Retained_Host_And_Join',mesh);scene.collection.objects.link(high);high.data.materials.append(plain)
for p,fi in zip(high.data.polygons,indices):p.use_smooth=near.data.polygons[fi].use_smooth
mesh.normals_split_custom_set([near.data.corner_normals[li].vector[:]for fi in indices for li in near.data.polygons[fi].loop_indices])
image=bpy.data.images.new('Fidelity_Geometry_Only_Normal_1024',width=1024,height=1024,alpha=False,is_data=True)
pixels=np.tile(np.array([.5,.5,1,1],dtype=np.float32),1024*1024);image.pixels.foreach_set(pixels)
bake_mat=bpy.data.materials.new('C9_Bake_Target');bake_mat.use_nodes=True
target=bake_mat.node_tree.nodes.new('ShaderNodeTexImage');target.image=image;bake_mat.node_tree.nodes.active=target
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=4
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.bake.use_selected_to_active=True;scene.render.bake.use_clear=False;scene.render.bake.margin=3
scene.render.bake.cage_extrusion=.7;scene.render.bake.max_ray_distance=1.6;scene.render.bake.normal_space='TANGENT'
rows=[]
for level in [1,2]:
 ob=objects[level]
 # Separate chart halves, fixed independently from approved fine UV0 sampling.
 for uv in ob.data.uv_layers[1].data:
  uv.uv.x=uv.uv.x*.99+.005;uv.uv.y=uv.uv.y*.49+(.005 if level==1 else .505)
 ob.data.uv_layers.active_index=1;ob.data.materials.clear();ob.data.materials.append(bake_mat)
 for q in scene.objects:
  q.select_set(False)
  if q.type=='MESH':q.hide_render=True
 for q in natives+[high,ob]:q.hide_set(False);q.hide_render=False;q.select_set(True)
 bpy.context.view_layer.objects.active=ob;start=time.monotonic();bpy.ops.object.bake(type='NORMAL')
 rows.append({'LOD':level,'seconds':time.monotonic()-start,'UV1AtlasHalf':[0,.5]if level==1 else[.5,1]})
print('GEOMETRY_BAKE',json.dumps(rows),flush=True)
image.filepath_raw=str(SOURCE/'geometry-normal-1024.png');image.file_format='PNG';image.save();image.pack()
far=stone.copy();far.name='Fidelity_C8_3x_With_Geometry_Bake'
nodes=far.node_tree.nodes;links=far.node_tree.links;bsdf=nodes.get('Principled BSDF')
for link in list(bsdf.inputs['Normal'].links):links.remove(link)
uv_node=nodes.new('ShaderNodeUVMap');uv_node.uv_map=objects[1].data.uv_layers[1].name
tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';links.new(uv_node.outputs['UV'],tex.inputs['Vector'])
normal=nodes.new('ShaderNodeNormalMap');normal.uv_map=uv_node.uv_map;normal.inputs['Strength'].default_value=1;links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
for level,ob in enumerate(objects):
 ob.data.materials.clear();ob.data.materials.append(stone if level==0 else far)
 ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
 ob.hide_set(False);ob.hide_render=False
for q in scene.objects:q.select_set(False)
for ob in objects:ob.select_set(True)
temporary=WORK/'composition-with-authoring-materials.glb'
bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_yup=True,export_animations=False)
d,b=glb_read(temporary)
bindings=[]
for node in d['nodes']:
 if 'mesh'not in node:continue
 p=d['meshes'][node['mesh']]['primitives'][0];mat=d['materials'][p['material']];channel=mat['normalTexture'].get('texCoord',0)
 bindings.append({'node':node['name'],'normalTextureChannel':channel})
 assert channel==(0 if node['name'].endswith('LOD0')else 1),'exported tangent/normal UV frame mismatch'
# Runtime local geometry retains only accessor buffers. C8 maps remain in their
# existing Phase2 owner, and the new baked image has one independent holder.
used={a['bufferView']for a in d['accessors']};views=[];mapping={};payload=bytearray()
for i,view in enumerate(d['bufferViews']):
 if i not in used:continue
 payload.extend(b'\0'*((-len(payload))%4));mapping[i]=len(views);v=dict(view);v['byteOffset']=len(payload);views.append(v)
 payload.extend(b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])
for a in d['accessors']:a['bufferView']=mapping[a['bufferView']]
d['bufferViews']=views
for key in ['images','textures','samplers','extensionsUsed','extensionsRequired']:d.pop(key,None)
d['materials']=[{'name':'BORROW_RECOVERED_C8_3X_AND_C9_GEOMETRY_BAKE','pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':1}}]
for m in d['meshes']:
 for p in m['primitives']:p['material']=0
glb_write(OUT/'fidelity-region.glb',d,payload)
# Tiny geometry-normal ownership proxy; never inserted into the rendered scene.
holder_mat=bpy.data.materials.new('Fidelity_Geometry_Normal_Holder');holder_mat.use_nodes=True;hn=holder_mat.node_tree.nodes;hl=holder_mat.node_tree.links
huv=hn.new('ShaderNodeUVMap');huv.uv_map='Geometry_Bake_UV1';ht=hn.new('ShaderNodeTexImage');ht.image=image;hl.new(huv.outputs['UV'],ht.inputs['Vector']);hno=hn.new('ShaderNodeNormalMap');hno.uv_map=huv.uv_map;hl.new(ht.outputs['Color'],hno.inputs['Color']);hl.new(hno.outputs['Normal'],hn.get('Principled BSDF').inputs['Normal'])
hm=bpy.data.meshes.new('Hidden_Fidelity_Bake_Holder');hm.from_pydata([(0,0,0),(.001,0,0),(0,.001,0)],[],[(0,1,2)]);hm.materials.append(holder_mat)
for name in ['UV0','Geometry_Bake_UV1']:
 layer=hm.uv_layers.new(name=name)
 for v,coord in zip(layer.data,[(0,0),(1,0),(0,1)]):v.uv=coord
hm.uv_layers.active_index=0;hm.uv_layers[0].active_render=True
holder=bpy.data.objects.new('Fidelity_Bake_Holder_Not_Rendered',hm);scene.collection.objects.link(holder)
for q in scene.objects:q.select_set(False)
holder.select_set(True);bpy.context.view_layer.objects.active=holder
bpy.ops.export_scene.gltf(filepath=str(OUT/'fidelity-bake.glb'),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_yup=True,export_animations=False)
holder.select_set(False);holder.hide_render=True;holder.hide_set(True)
for q in natives+[high]:q.hide_render=True;q.hide_set(True)
for level,q in enumerate(objects):q.hide_render=level!=0;q.hide_set(level!=0)
spec['runtimeProtectedNormalRestoration']=restore_authoritative_border(ROOT)
frames=subprocess.run(['node',str(ROOT/'scripts/blender/fidelity_mikktspace.mjs'),str(OUT/'fidelity-region.glb')],cwd=ROOT,text=True,capture_output=True,check=True)
spec['runtimeTangentProduction']=json.loads(frames.stdout);print('ACTUAL_GLTF_TANGENT_FRAMES',frames.stdout,flush=True)
spec['runtimeBytes']=(OUT/'fidelity-region.glb').stat().st_size;spec['runtimeSHA256']=sha(OUT/'fidelity-region.glb');spec['newGeometryBakeImages']=1
spec['normalBake']={'runtime':'fidelity-bake.glb','bytes':(OUT/'fidelity-bake.glb').stat().st_size,'sha256':sha(OUT/'fidelity-bake.glb'),'resolution':1024,'estimatedRGBA8MipBytes':1024*1024*4*4/3,'channels':[0,1,1],'content':'geometry-only high-to-low, no fine C8 normal baked twice','UV0SamplingUnchanged':True,'lostOldC62BakeNotRecreated':True}
spec['authoringMaster']='assets-source/gullyverse/quarry-fidelity-correction/quarry-fidelity-correction.blend'
bpy.data.texts['QUARRY_FIDELITY_CONTRACT'].clear();bpy.data.texts['QUARRY_FIDELITY_CONTRACT'].write(json.dumps(spec,indent=2));
# Remove only unused data inside this NEW master; provider originals are unchanged.
for table in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
 for item in list(table):
  if item.users==0:table.remove(item)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'quarry-fidelity-correction.blend'))
for p in [OUT/'manifest.json',SOURCE/'composition-contract.json']:p.write_text(json.dumps(spec,indent=2)+'\n')
(RAW/'normal-bake-production.json').write_text(json.dumps({'status':'PASS','bakes':rows,'float32RoundTripFrameRepairs':frame_repairs,'bindingsBeforeGeometryOnlyPacking':bindings,'normalSourceSHA256':sha(SOURCE/'geometry-normal-1024.png'),'geometryBytes':spec['runtimeBytes'],'bakeHolderBytes':spec['normalBake']['bytes'],'finePBRSourceImagesUnchanged':True,'masterSHA256':sha(SOURCE/'quarry-fidelity-correction.blend')},indent=2)+'\n')
print('BAKE_AND_PACK_COMPLETE',spec['runtimeBytes'],spec['normalBake']['bytes'],flush=True)
