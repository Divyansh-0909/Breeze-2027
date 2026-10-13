"""Blender4.3.2: correct one existing rock's surface/joins without modifying locked maps."""
import bpy,bmesh,sys,json,math,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from corrected_wall_joins import JOINS,build_join
from corrected_wall_geometry import HOST,ANCHOR,VERTICES,FACES,CENTER,ADJ,TARGET,sculpt,region,uv,PROTECTED,edge_distance
root=Path(__file__).resolve().parents[2];src=root/'assets-source/gullyverse/first-wall-corrected';out=root/'public/models/gullyverse/first-wall-corrected';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Load the exact approved material node tree/packed maps; no material regeneration.
material_library=src/'approved-limestone-material.blend'
if not material_library.exists():material_library=root/'assets-source/gullyverse/first-wall-section/first-wall-section.blend'
with bpy.data.libraries.load(str(material_library),link=False) as (data,to):to.materials=['Approved_Cool_Grey_Limestone_Family']
mat=to.materials[0];assert mat is not None
hostmat=bpy.data.materials.new('Original_Unchanged_Host_Rock');hostmat.use_nodes=True;hostmat.use_backface_culling=True
hostbsdf=hostmat.node_tree.nodes.get('Principled BSDF');hostbsdf.inputs['Base Color'].default_value=(*ANCHOR['oldVertexColor'],1);hostbsdf.inputs['Roughness'].default_value=.98;hostbsdf.inputs['Metallic'].default_value=0
joinmat=bpy.data.materials.new('Original_Unchanged_Contact_Rock3');joinmat.use_nodes=True;joinmat.use_backface_culling=True;node=joinmat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*JOINS[0]['color'],1);node.inputs['Roughness'].default_value=.98;node.inputs['Metallic'].default_value=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
mastercol=bpy.data.collections.new('EDITABLE_VOLUMETRIC_GEOLOGY');scene.collection.children.link(mastercol);runtimecol=bpy.data.collections.new('RUNTIME_ONE_LOD_ONLY');scene.collection.children.link(runtimecol);proxycol=bpy.data.collections.new('ORIGINAL_HOST_COLLISION_PROXY');scene.collection.children.link(proxycol)
verts=[];original=[];triangles=[];faceids=[];index={};proposal=0
n=90
for faceid,ids in enumerate(FACES):
 poly=VERTICES[ids];center=poly.mean(axis=0);coords=[];localfaces=[];keys={}
 def point(p):
  k=tuple(np.round(p,7))
  if k not in keys:keys[k]=len(coords);coords.append(p)
  return keys[k]
 if faceid==TARGET or faceid in ADJ:
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   grid={}
   for i in range(n+1):
    for j in range(n+1-i):grid[(i,j)]=point(center+(a-center)*i/n+(b-center)*j/n)
   for i in range(n):
    for j in range(n-i):
     localfaces.append([grid[(i,j)],grid[(i+1,j)],grid[(i,j+1)]])
     if i+j<n-1:localfaces.append([grid[(i+1,j)],grid[(i+1,j+1)],grid[(i,j+1)]])
 else:
  centerid=point(center);boundary=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   for i in range(n):boundary.append(point(a+(b-a)*i/n))
  localfaces=[[centerid,boundary[i],boundary[(i+1)%len(boundary)]] for i in range(len(boundary))]
 coords=np.array(coords);moved=sculpt(coords,faceid);mapping={}
 for i,(p,q) in enumerate(zip(coords,moved)):
  k=tuple(np.round(p,5))
  if k in index:
   vi=index[k];proposal=max(proposal,float(np.linalg.norm(np.array(verts[vi])-q)))
  else:vi=len(verts);index[k]=vi;original.append(p);verts.append(q)
  mapping[i]=vi
 for f in localfaces:triangles.append([mapping[v] for v in f]);faceids.append(faceid)
assert proposal<1e-5,('boundary mismatch',proposal)
componentRanges=[(4,0,len(verts))];pinPoints=list(VERTICES)
for j,join in enumerate(JOINS):
 points,source,faces,corners,_=build_join(join);offset=len(verts);verts.extend(points);original.extend(source);triangles.extend([[v+offset for v in f]for f in faces]);faceids.extend([12+j]*len(faces));componentRanges.append((join['rock'],offset,len(verts)));pinPoints.extend(corners)
verts=np.array(verts);original=np.array(original)
# Convert metric glTF coordinates to Blender Z-up without object rotations/scales.
blender=np.stack([verts[:,0],-verts[:,2],verts[:,1]],axis=-1)
mesh=bpy.data.meshes.new('Wall_Master_Volume');mesh.from_pydata(blender.tolist(),[],triangles);mesh.update();master=bpy.data.objects.new('Wall_Master',mesh);mastercol.objects.link(master);mesh.materials.append(mat);mesh.materials.append(hostmat);mesh.materials.append(joinmat)
uv0=mesh.uv_layers.new(name='Metre_Scale_Unique_Face');uv1=mesh.uv_layers.new(name='Fine_Mineral_Metre')
tri=np.array(triangles,dtype=np.int32);faceids=np.array(faceids);centroids=original[tri].mean(axis=1);materials=(faceids!=TARGET).astype(np.int32)
for faceid in ADJ:
 selected=faceids==faceid;p=centroids[selected];authored=(region(p,faceid)>.03)&(edge_distance(p,PROTECTED)>.06);materials[selected]=np.where(authored,0,1)
materials[faceids==12]=2
mesh.polygons.foreach_set('material_index',materials);mesh.polygons.foreach_set('use_smooth',(materials==0))
loopids=tri.reshape(-1);loopfaces=np.repeat(faceids,3);uvbase=np.zeros((len(loopids),2));uvfine=uvbase.copy()
for faceid in range(12):
 selected=loopfaces==faceid;base,fine=uv(original[loopids[selected]],faceid);uvbase[selected]=base;uvfine[selected]=fine
uv0.data.foreach_set('uv',uvbase.reshape(-1));uv1.data.foreach_set('uv',uvfine.reshape(-1))
mesh.uv_layers.active=uv0;mesh.set_sharp_from_angle(angle=math.radians(65))
# Pin original corners; retain complete host extremities and sky/outer silhouette edges.
corner_ids=[min(range(len(original)),key=lambda i:float(np.linalg.norm(original[i]-p))) for p in pinPoints]
for rock,start,end in componentRanges:
 group=master.vertex_groups.new(name=f'SOURCE_SOLID_{rock}');group.add(list(range(start,end)),1,'REPLACE')
group=master.vertex_groups.new(name='DECIMATE_INTERIOR_ONLY');group.add([i for i in range(len(verts)) if i not in corner_ids],1,'REPLACE')
master.data.calc_loop_triangles();sourceTriangles=len(master.data.loop_triangles)
solidData={4:(VERTICES,FACES)}
for join in JOINS:
 points=(np.array(join['vertices'])-__import__('corrected_wall_geometry').ORIGIN)@__import__('corrected_wall_geometry').R;solidData[join['rock']]=(points,join['faces'])
solidPlanes={}
for rock,(points,faceIndices)in solidData.items():
 planes=[]
 for ids in faceIndices:
  p=points[ids];normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal);planes.append((normal,p[0]))
 solidPlanes[rock]=planes
def project_hull(ob):
 positions=np.array([[v.co.x,v.co.z,-v.co.y]for v in ob.data.vertices]);over=0
 for rock,planes in solidPlanes.items():
  groupid=ob.vertex_groups[f'SOURCE_SOLID_{rock}'].index;ids=[v.index for v in ob.data.vertices if any(g.group==groupid and g.weight>.5 for g in v.groups)];p=positions[ids]
  for normal,a in planes:over=max(over,float(((p-a)@normal).max()))
  for _ in range(6):
   for normal,a in planes:p-=np.maximum(0,(p-a)@normal)[:,None]*normal
  positions[ids]=p
 for v,p in zip(ob.data.vertices,positions):v.co=(p[0],-p[2],p[1])
 ob.data.update();return over
lods=[]
for i,target in enumerate([32000,10000,4000]):
 ob=master.copy();ob.data=master.data.copy();ob.name=f'Wall_LOD{i}';ob.data.name=ob.name+'_Mesh';runtimecol.objects.link(ob);bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new('Feature_Weighted_Volumetric_Decimation','DECIMATE');mod.ratio=target/sourceTriangles;mod.use_collapse_triangulate=True;mod.vertex_group='DECIMATE_INTERIOR_ONLY';mod.vertex_group_factor=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 over=project_hull(ob);ob.data.set_sharp_from_angle(angle=math.radians(65));ob['hull_projection_max_m']=over
 for p in pinPoints:
  point=np.array([p[0],-p[2],p[1]]);assert min(np.linalg.norm(np.array(v.co)-point)for v in ob.data.vertices)<2e-5,(ob.name,'lost host corner')
 lods.append(ob)
# Full original closed host proxy, not the old2m panel prism. Walking polygons remain untouched.
proxyVertices=[];proxyFaces=[]
for points,faceIndices in solidData.values():
 offset=len(proxyVertices);proxyVertices.extend([[p[0],-p[2],p[1]]for p in points]);proxyFaces.extend([[offset+face[0],offset+face[i],offset+face[i+1]]for face in faceIndices for i in range(1,4)])
proxyMesh=bpy.data.meshes.new('Wall_Collision_Mesh');proxyMesh.from_pydata(proxyVertices,[],proxyFaces);proxyMesh.materials.append(hostmat);proxy=bpy.data.objects.new('Wall_Collision',proxyMesh);proxycol.objects.link(proxy);proxy.display_type='WIRE'
anchor=bpy.data.objects.new('wall_anchor',None);runtimecol.objects.link(anchor);anchor['world_position']=ANCHOR['anchor'];anchor['one_existing_host_rock']=4
rows=[]
for ob in [master,*lods,proxy]:
 ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert non==0 and volume>0,(ob.name,non,volume)
 rows.append({'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'nonManifoldEdges':non,'signedVolumeM3':volume})
# Gray-surface screen-space bounds rather than the unchanged invisible rear extent.
graypoints=np.array([[v.co.x,v.co.z,-v.co.y]for p in lods[0].data.polygons if p.material_index==0 for v in [lods[0].data.vertices[i]for i in p.vertices]]);lo=graypoints.min(axis=0);hi=graypoints.max(axis=0);spherecenter=(lo+hi)/2;radius=np.linalg.norm(graypoints-spherecenter,axis=1).max()
lockfiles={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'assets-source/gullyverse/first-wall-section/textures').iterdir()if p.is_file()}
manifest={**ANCHOR,'strategy':'replace only existing host rock4; sculpt its inward surface and adjoining return faces as one closed volume; original outer edges and corners retained','correction':'one complete existing host rock; irregular authored collar across its five adjoining faces; localized fitted contact-face correction; no additional quarry section','hostRange':HOST['hostRange'],'joinRanges':[part for join in JOINS for part in join['sourceRanges']],'joiningContacts':JOINS,'hostVerticesWorld':HOST['vertices'],'hostFaces':FACES,'protectedOuterEdges':sorted(PROTECTED),'reworkedInternalEdges':sorted(__import__('corrected_wall_geometry').JOIN_EDGES),'detailSphere':{'center':spherecenter.tolist(),'radius':float(radius)},'materialPolicy':'exact approved packed material/maps imported from existing master; only UV edge unfolding/reflection repair; central body and fine normal metre scale retained','lockedTextures':lockfiles,'blender':bpy.app.version_string,'units':'metres','normalStrength':.58,'blenderUp':'Z','glTFUp':'Y','lodMethod':'quadric decimation of common volumetric master; host corners and contact perimeter corners pinned; hull constrained','nodes':rows,'sharedBoundaryProposalErrorM':proposal,'defaultEnabled':False,'collisionPolicy':'compound original solids at the host and contacts; no change to player movement polygons'}
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)
export(out/'first-wall-corrected.glb',[*lods,proxy,anchor])
for i,o in enumerate(lods):export(out/f'wall-lod{i}.glb',[o,anchor])
export(out/'wall-collision.glb',[proxy,anchor])
for o in [master,proxy,*lods[1:]]:o.hide_set(True)
mastercol.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(src/'first-wall-corrected.blend'));(src/'manifest.json').write_text(json.dumps(manifest,indent=2,default=lambda value: value.item() if isinstance(value,np.generic) else value));(out/'manifest.json').write_text(json.dumps(manifest,indent=2,default=lambda value: value.item() if isinstance(value,np.generic) else value));print('CORRECTED_MANIFEST',json.dumps(manifest,default=lambda value: value.item() if isinstance(value,np.generic) else value))
