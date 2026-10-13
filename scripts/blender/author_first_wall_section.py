"""Blender4.3.2: one original closed limestone face fitted to existing quarry boundary.
Only writes first-wall-section assets. Never runs stage/whole-site asset generation.
"""
import bpy,bmesh,json,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from wall_section_surface import POLYGON,LOW,HIGH,SIZE,ANCHOR,relief,edge_distance
root=Path(__file__).resolve().parents[2];src=root/'assets-source/gullyverse/first-wall-section';out=root/'public/models/gullyverse/first-wall-section';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
mat=bpy.data.materials.new('Approved_Cool_Grey_Limestone_Family');mat.use_nodes=True;mat.use_backface_culling=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0;bsdf.inputs['Roughness'].default_value=.9
for kind,file in [('basecolor','wall-basecolor-1024.jpg'),('normal','wall-normal-1024.png'),('roughness','wall-roughness-512.png'),('ao','wall-ao-512.png')]:
 image=bpy.data.images.load(str(src/'textures'/file));image.colorspace_settings.name='sRGB' if kind=='basecolor' else 'Non-Color';image.pack();node=nodes.new('ShaderNodeTexImage');node.image=image;node.name='WALL_'+kind
 if kind=='basecolor':links.new(node.outputs['Color'],bsdf.inputs['Base Color'])
 elif kind=='normal':
  coords=nodes.new('ShaderNodeUVMap');coords.uv_map='Fine_Mineral_Metre';links.new(coords.outputs['UV'],node.inputs['Vector'])
  normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.58;links.new(node.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
 elif kind=='roughness':links.new(node.outputs['Color'],bsdf.inputs['Roughness'])
 else:
  group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree');group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat');g=nodes.new('ShaderNodeGroup');g.node_tree=group;links.new(node.outputs['Color'],g.inputs['Occlusion'])
master=bpy.data.collections.new('EDITABLE_GEOLOGY_MASTER');scene.collection.children.link(master);runtime=bpy.data.collections.new('WALL_RUNTIME_LODS');scene.collection.children.link(runtime);proxycol=bpy.data.collections.new('COLLISION_REFERENCE');scene.collection.children.link(proxycol)
def create(name,n,col):
 xy=[];faces=[];index={}
 def vertex(x,y):
  key=(round(float(x),7),round(float(y),7))
  if key not in index:index[key]=len(xy);xy.append([float(x),float(y)])
  return index[key]
 for a,b in zip(POLYGON,np.roll(POLYGON,-1,axis=0)):
  grid={}
  for i in range(n+1):
   for j in range(n+1-i):
    p=(i*a+j*b)/n;grid[(i,j)]=vertex(*p)
  for i in range(n):
   for j in range(n-i):
    faces.append([grid[(i,j)],grid[(i+1,j)],grid[(i,j+1)]])
    if i+j<n-1:faces.append([grid[(i+1,j)],grid[(i+1,j+1)],grid[(i,j+1)]])
 frontcount=len(faces);xy=np.array(xy);depth=relief(xy[:,0],xy[:,1]);verts=np.stack([xy[:,0],-depth,xy[:,1]],axis=-1).tolist()
 boundary=[]
 for a,b in zip(POLYGON,np.roll(POLYGON,-1,axis=0)):
  for i in range(n):boundary.append(vertex(*(a+(b-a)*i/n)))
 back=[]
 for x,y in POLYGON:
  back.append(len(verts));verts.append([x,2.,y])
 bc=len(verts);verts.append([0,2.,0])
 for edge in range(5):
  for i in range(n):
   a=boundary[edge*n+i];b=boundary[(edge*n+i+1)%len(boundary)];faces.append([a,back[edge],b])
  end=boundary[((edge+1)*n)%len(boundary)];faces.append([end,back[edge],back[(edge+1)%5]]);faces.append([bc,back[(edge+1)%5],back[edge]])
 mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);mesh.materials.append(mat);uv=mesh.uv_layers.new(name='Metre_Scale_Unique_Face');fineuv=mesh.uv_layers.new(name='Fine_Mineral_Metre')
 for p in mesh.polygons:
  p.use_smooth=p.index<frontcount
  for li in p.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((v.x-LOW[0])/SIZE[0],(v.z-LOW[1])/SIZE[1]);fineuv.data[li].uv=((v.x+6)/12,(v.z+5)/10)
 mesh.uv_layers.active=uv;mesh.set_sharp_from_angle(angle=math.radians(62))
 group=ob.vertex_groups.new(name='INTERIOR_DETAIL');interior=np.flatnonzero(edge_distance(xy[:,0],xy[:,1])>.08).tolist();group.add(interior,1.,'REPLACE')
 ob['units']='metres';ob['surface_role']='replaces existing rock4 face3 only';ob['fixed_boundary']=True;ob['relief_direction']='recessed into original solid';ob['material_family']='latest user-approved cool grey limestone';ob['production_default_enabled']=False
 return ob
sculpt=create('Wall_Master',220,master);sculpt.data.calc_loop_triangles();sourceTriangles=len(sculpt.data.loop_triangles);lods=[]
for i,target in enumerate([21500]):
 ob=sculpt.copy();ob.data=sculpt.data.copy();ob.name=f'Wall_LOD{i}';ob.data.name=ob.name+'_Mesh';runtime.objects.link(ob);bpy.context.view_layer.objects.active=ob
 modifier=ob.modifiers.new('Feature_Weighted_Quadric_Collapse','DECIMATE');modifier.ratio=target/sourceTriangles;modifier.use_collapse_triangulate=True;modifier.vertex_group='INTERIOR_DETAIL';modifier.vertex_group_factor=1
 bpy.ops.object.modifier_apply(modifier=modifier.name);ob.data.set_sharp_from_angle(angle=math.radians(62))
 # Corners must survive decimation; straight boundary subdivisions may collapse along their line.
 for x,y in POLYGON:
  assert min((v.co.x-x)**2+v.co.y**2+(v.co.z-y)**2 for v in ob.data.vertices)<1e-9,(ob.name,'lost fixed corner')
 lods.append(ob)
lods.append(create('Wall_LOD1',32,runtime))
lods.append(create('Wall_LOD2',18,runtime))
# Reference proxy is a conservative prism inside the original rock; walking polygons unchanged.
verts=[[x,0,y] for x,y in POLYGON]+[[x,2.1,y] for x,y in POLYGON];mesh=bpy.data.meshes.new('Wall_Collision_Mesh');mesh.from_pydata(verts,[],[]);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.convex_hull(bm,input=list(bm.verts));bm.to_mesh(mesh);bm.free();proxy=bpy.data.objects.new('Wall_Collision',mesh);proxycol.objects.link(proxy);proxy.display_type='WIRE';proxy['active_walk_collision']=False
anchor=bpy.data.objects.new('wall_anchor',None);runtime.objects.link(anchor);anchor['world_position']=ANCHOR['anchor'];anchor['original_rock']=4;anchor['original_face']=3
# Keep editable source maps available; source image texels are original mathematical materials.
for p in (src/'textures').glob('*2048.png'):bpy.data.images.load(str(p)).pack()
manifest={**ANCHOR,'blender':bpy.app.version_string,'units':'metres','BlenderUp':'Z','glTFUp':'Y','frontBlender':'-Y','frontGLTF':'+Z','pivot':'existing face centroid','normalStrength':.58,'roughnessRange':[.82,.99],'materialFamily':'approved grey limestone RGB184/188/193, metre-grain recipe retained; .62m perimeter blend to actual untouched neighbours','textureSizes':{'basecolor':1024,'normal':1024,'ORM':512},'normalUV':'second UV channel, 12x10m fine mineral tile; unique complete-face albedo/AO/roughness on first UV','LODMethod':'near feature-weighted quadric collapse; middle/far sample same continuous geology at lower density; fixed rim, sharp normals62deg','texturePayloadRGBA8MipEstimateBytes':12582912,'compression':'ordinary GLB, no Draco/Meshopt/KTX2','singleSided':True,'nodes':[]}
for ob in [sculpt,*lods,proxy]:
 ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert non==0 and volume>0,(ob.name,non,volume);manifest['nodes'].append({'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'nonManifoldEdges':non,'signedVolumeM3':volume})
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)
export(out/'first-wall-section.glb',[*lods,proxy,anchor])
for i,o in enumerate(lods):export(out/f'wall-lod{i}.glb',[o,anchor])
export(out/'wall-collision.glb',[proxy,anchor])
for o in [sculpt,proxy,*lods[1:]]:o.hide_set(True)
master.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(src/'first-wall-section.blend'));(src/'manifest.json').write_text(json.dumps(manifest,indent=2));(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('WALL_MANIFEST',json.dumps(manifest))
