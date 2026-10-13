"""Blender 4.3 original geological segment author/export, metres, no production overwrite.
blender --background --python scripts/blender/author_rock_pilot_2a.py
Prerequisite: python3 scripts/blender/rock_pilot_materials.py
"""
import bpy,math,json,random,bmesh,sys
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from rock_pilot_surface import surface
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'assets-source/gullyverse/rock-pilot-2a';OUT=ROOT/'public/models/gullyverse/pilot-rock'
SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
random.seed(20271011)
mat=bpy.data.materials.new('Quarry_Pilot_Original_Stone_PBR');mat.use_nodes=True
ns=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=ns.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Roughness'].default_value=.88
images={}
for kind,path in [('basecolor','rock-basecolor-1024.jpg'),('normal','rock-normal-1024.png'),('roughness','rock-roughness-1024.png'),('ao','rock-ao-1024.png')]:
 im=bpy.data.images.load(str(SRC/'textures'/path));im.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color';images[kind]=im
 node=ns.new('ShaderNodeTexImage');node.name='PILOT_'+kind;node.image=im
 if kind=='basecolor':links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
 elif kind=='normal':
  normal=ns.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.7;links.new(node.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
 elif kind=='roughness':links.new(node.outputs['Color'],bsdf.inputs['Roughness'])
 else:
  group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree');group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat');gn=ns.new('ShaderNodeGroup');gn.node_tree=group;links.new(node.outputs['Color'],gn.inputs['Occlusion'])
mat.diffuse_color=(.16,.15,.13,1)
master=bpy.data.collections.new('MASTER_SCULPT');scene.collection.children.link(master)
exports=bpy.data.collections.new('RUNTIME_LODS');scene.collection.children.link(exports)
proxies=bpy.data.collections.new('COLLISION_PROXY');scene.collection.children.link(proxies)
def create(name,nx,nz,collection):
 u,v=np.meshgrid(np.linspace(0,1,nx+1),np.linspace(0,1,nz+1));xs,ys,zs=surface(u,v);verts=np.stack([xs,ys,zs],axis=-1).reshape(-1,3).tolist();faces=[];uvs=[];idx=lambda i,j:j*(nx+1)+i
 for j in range(nz):
  for i in range(nx):
   face=[idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)];faces.append(face);uvs.append([(.02+.86*(k%(nx+1))/nx,.03+.94*(k//(nx+1))/nz) for k in face])
 # Close the independently authored cliff slab. Irregular perimeter, common base/pivot, conserved units.
 boundary=[idx(i,0) for i in range(nx+1)]+[idx(nx,j) for j in range(1,nz+1)]+[idx(i,nz) for i in range(nx-1,-1,-1)]+[idx(0,j) for j in range(nz-1,0,-1)]
 back=[]
 for k in boundary:
  x,y,z=verts[k];back.append(len(verts));verts.append((x,1.35+.10*math.sin(x*.7+z),z))
 for j,a in enumerate(boundary):
  jj=(j+1)%len(boundary);b=boundary[jj];faces.append([a,back[j],back[jj],b]);uvs.append([(.9,.03+.94*j/len(boundary)),(.94,.03+.94*j/len(boundary)),(.94,.03+.94*(j+1)/len(boundary)),(.9,.03+.94*(j+1)/len(boundary))])
 center=len(verts);verts.append((0,1.35,4.85))
 for j in range(len(back)):
  jj=(j+1)%len(back);faces.append([center,back[jj],back[j]]);uvs.append([(.95+.04*max(0,min(1,(verts[k][0]+6.2)/12.4)),.03+.94*max(0,min(1,verts[k][2]/10.1))) for k in [center,back[jj],back[j]]])
 mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);ob.data.materials.append(mat)
 uv=mesh.uv_layers.new(name='UV_Original_Atlas')
 for poly,coords in zip(mesh.polygons,uvs):
  poly.use_smooth=True
  for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
 # Preserve a crisp perimeter/back cap and remove inappropriate smoothing across it.
 for poly in mesh.polygons[nx*nz:]:poly.use_smooth=False
 ob['metres']=True;ob['forward_blender']='-Y';ob['forward_gltf']='+Z';ob['anchor']='bottom_center';ob['material_license']='original-generated-for-project';ob['production_default_enabled']=False
 return ob
sculpt=create('Rock_Master_Sculpt',256,192,master)
lods=[create('Rock_LOD0',144,108,exports),create('Rock_LOD1',80,60,exports),create('Rock_LOD2',40,30,exports)]
for level,o in enumerate(lods):o['lod_level']=level;o['lod_selection']='explicit preview selection; no automatic runtime policy'
# Conservative convex proxy generated from boundary landmarks, never registered into production movement.
allverts=[v.co for o in lods for v in o.data.vertices]
low=[min(v[i] for v in allverts) for i in range(3)];high=[max(v[i] for v in allverts) for i in range(3)]
mesh=bpy.data.meshes.new('Rock_Collision_Mesh');mesh.from_pydata([(x,y,z) for x in [low[0],high[0]] for y in [low[1],high[1]] for z in [low[2],high[2]]],[],[]);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.to_mesh(mesh);bm.free();mesh.update();proxy=bpy.data.objects.new('Rock_Collision',mesh);proxies.objects.link(proxy);proxy.display_type='WIRE';proxy['collision_proxy']=True;proxy['proxy_kind']='Conservative axis-aligned hull of all runtime LOD vertices, not production walk polygon';proxy['production_default_enabled']=False
anchor=bpy.data.objects.new('pilot_anchor',None);exports.objects.link(anchor);anchor['units']='metres';anchor['pivot']='bottom_center';anchor['authoring']='Blender Z-up -> glTF Y-up';anchor['world_registry_modified']=False
# Store provenance/workflow as editable master Text. No external imagery is packed as a texture.
text=bpy.data.texts.new('PILOT_README');text.write('Original stratified excavated rock pilot. Front -Y Blender/+Z glTF. Master sculpt + three runtime LODs + conservative collision proxy. PBR source 2048, runtime1024. Do not place into approved world without explicit opt-in. Script regenerates only new pilot paths.\n')
for im in images.values():im.pack()
# Source-detail maps are accessible in the master without being exported as extra runtime textures.
for path in sorted((SRC/'textures').glob('*2048.png')):bpy.data.images.load(str(path)).pack()
master.hide_render=True;master.hide_viewport=True;proxies.hide_render=True
manifest={'blender':bpy.app.version_string,'units':'metres','BlenderUp':'Z','glTFUp':'Y','BlenderForward':'-Y','glTFForward':'+Z','pivot':[0,0,0],'provenance':'Original mathematical geological morphology and original generated UV textures; reference photos not sampled','runtimeTextureResolution':1024,'authorTextureResolution':2048,'normalConvention':'OpenGL tangent +Y','compression':'ordinary GLB, JPEG basecolor and PNG normal/ORM; no Draco/Meshopt/KTX2','lods':[]}
for o in [sculpt,*lods,proxy]:
 o.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);bm.free();bounds=[[min(v.co[i] for v in o.data.vertices) for i in range(3)],[max(v.co[i] for v in o.data.vertices) for i in range(3)]]
 manifest['lods'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'nonManifoldEdges':non,'blenderBounds':bounds})
# Selection/export does not alter approved scene; all output paths are dedicated to this pilot.
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_image_format='AUTO',export_animations=False)
export(OUT/'quarry-rock-pilot.glb',[*lods,proxy,anchor])
for o in lods:export(OUT/(o.name.lower().replace('rock_','rock-')+'.glb'),[o,anchor])
export(OUT/'rock-collision.glb',[proxy,anchor])
for o in lods[1:]:o.hide_set(True)
proxy.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'quarry-rock-pilot.blend'))
(SRC/'asset-manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
print('PILOT_MANIFEST',json.dumps(manifest))
