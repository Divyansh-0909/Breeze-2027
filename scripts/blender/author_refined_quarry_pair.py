"""Blender 4.3.2: bounded two-section geological continuity proof.
Writes only quarry-refinement directories. Never saves over Stage 2C sources.
"""
import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from refined_quarry_geology import ROOT,IDS,START,END,SPLIT,CENTER,build_section,front,crest
SRC=ROOT/'assets-source/gullyverse/quarry-refinement';OUT=ROOT/'public/models/gullyverse/quarry-refinement';SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
material_source=ROOT/'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend'
# The review ZIP includes this editable master's same packed family, avoiding
# a 313MB dependency merely to recover a material when reproducing standalone.
if not material_source.exists():material_source=SRC/'refined-limestone-pair.blend'
with bpy.data.libraries.load(str(material_source),link=False)as(data,to):to.materials=['Approved_Cool_Grey_Limestone_Family']
mat=to.materials[0];assert mat
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
masterCollection=bpy.data.collections.new('EDITABLE_CONTINUOUS_LIMESTONE');scene.collection.children.link(masterCollection)
cols=[];levels=[];objects=[[],[],[]];rows=[];parts=[]
for i in range(3):
 c=bpy.data.collections.new(f'REFINED_LOD{i}');scene.collection.children.link(c);cols.append(c);p=bpy.data.objects.new(f'Refined_LOD{i}',None);c.objects.link(p);levels.append(p)
def B(p):return np.stack([p[:,0],-p[:,2],p[:,1]],axis=1)
def G(p):return np.stack([p[:,0],p[:,2],-p[:,1]],axis=1)
def stats(ob):
 ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 assert non==0 and volume>0,(ob.name,non,volume)
 row={'name':ob.name,'triangles':len(ob.data.loop_triangles),'vertices':len(ob.data.vertices),'nonManifoldEdges':non,'signedVolumeM3':volume};rows.append(row);return row
def fix_normals(ob):
 # End caps are internal; keep surface derivatives continuous at the shared join.
 # The two end caps face opposite directions and never overlap an exposed face.
 mesh=ob.data;mesh.update();p=G(np.array([v.co[:]for v in mesh.vertices]));angle=np.degrees(np.arctan2(p[:,0]-CENTER[0],-(p[:,2]-CENTER[2])));frac=(p[:,1]+1.5)/(crest(angle)+1.5);seam=np.flatnonzero(np.abs(angle-SPLIT)<2e-5)
 shared={}
 for i in seam:
  a=angle[i];t=frac[i]
  if np.linalg.norm(front(np.array([a]),np.array([t]))[0]-p[i])>2e-4:continue
  d1=front(np.array([a+.001]),np.array([t]))[0]-front(np.array([a-.001]),np.array([t]))[0]
  d2=front(np.array([a]),np.array([t+.0001]))[0]-front(np.array([a]),np.array([t-.0001]))[0]
  n=np.cross(d1,d2);n/=np.linalg.norm(n)
  if np.dot(n,CENTER-p[i])<0:n=-n
  shared[i]=Vector((n[0],-n[2],n[1]))
 normals=[c.vector.copy()for c in mesh.corner_normals]
 for poly in mesh.polygons:
  if abs(poly.normal.dot(Vector((math.cos(math.radians(SPLIT)),-math.sin(math.radians(SPLIT)),0))))>.95:continue
  for l in poly.loop_indices:
   i=mesh.loops[l].vertex_index
   if i in shared:normals[l]=shared[i]
 for poly in mesh.polygons:
  for l in poly.loop_indices:
   if poly.normal.dot(normals[l])<0:normals[l]=poly.normal.copy()
 mesh.normals_split_custom_set(normals)
def create(name,points,faces,u,v,collection):
 mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(B(points).tolist(),[],faces.tolist());mesh.materials.append(mat);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 # Recalculation can reverse polygon loop order. Assign each UV by its vertex
 # and face-domain, retaining geological metric mapping on top/back/end faces.
 original={tuple(sorted(f)):j for j,f in enumerate(faces)}
 a=mesh.uv_layers.new(name='Approved_Limestone_Metre_Face');b=mesh.uv_layers.new(name='Fine_Mineral_Metre')
 for poly in mesh.polygons:
  j=original[tuple(sorted(poly.vertices))];idx=list(faces[j])
  for l in poly.loop_indices:
   at=idx.index(mesh.loops[l].vertex_index);a.data[l].uv=u[j*3+at];b.data[l].uv=v[j*3+at]
 mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool));mesh.set_sharp_from_angle(angle=math.radians(58));mesh.uv_layers.active=a
 ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);fix_normals(ob);return ob
for rid in IDS:
 points,faces,u,v,tags,pinned=build_section(rid,96,96);master=create(f'Refined_Rock_{rid:02d}_Master',points,faces,u,v,masterCollection);stats(master)
 lods=[]
 for level in range(3):
  data=np.load(SRC/'prepared'/f'rock-{rid}-lod{level}.npz');ob=create(f'Refined_Rock_{rid:02d}_LOD{level}',data['points'],data['faces'],data['uv0'],data['uv1'],cols[level]);ob.parent=levels[level]
  stats(ob);lods.append(ob);objects[level].append(ob)
 lo=points.min(0);hi=points.max(0);parts.append({'id':rid,'name':f'Refined_Rock_{rid:02d}','center':((lo+hi)/2).tolist(),'radius':float(np.linalg.norm((hi-lo)/2)),'bounds':np.stack([lo,hi],axis=1).tolist(),'nodes':[o.name for o in lods]})
 master.hide_set(True)
# One continuous volume spans the TWO selected anchors. Separate internal caps
# are unnecessary and can draw a hairline even with equal sampled boundaries.
# Weld the real shared contour, remove only those internal cap faces, and select
# one LOD for the joined geological mass. Original region masters stay editable.
def join_regions(sources,name,collection):
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for source in sources:
  o=source.copy();o.data=source.data.copy();collection.objects.link(o);o.parent=None;o.hide_set(False);o.select_set(True);copies.append(o)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=copies[0];ob.name=name;ob.data.name=name+'_Mesh';bm=bmesh.new();bm.from_mesh(ob.data);remove=[]
 for face in bm.faces:
  pos=np.array([v.co[:]for v in face.verts]);p=G(pos);angle=np.degrees(np.arctan2(p[:,0]-CENTER[0],-(p[:,2]-CENTER[2])))
  if np.max(np.abs(angle-SPLIT))<2e-5:remove.append(face)
 bmesh.ops.delete(bm,geom=remove,context='FACES');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob.data.set_sharp_from_angle(angle=math.radians(58));fix_normals(ob);stats(ob);return ob
masterJoined=join_regions([bpy.data.objects[f'Refined_Rock_{rid:02d}_Master']for rid in IDS],'Refined_Pair_Master',masterCollection);masterJoined.hide_set(True)
joined=[]
for i in range(3):
 ob=join_regions(objects[i],f'Refined_Pair_LOD{i}',cols[i]);ob.parent=levels[i];joined.append(ob)
 for old in objects[i]:old.hide_set(True)
 objects[i]=[ob]
lo=np.min([np.array(p['bounds'])[:,0]for p in parts],axis=0);hi=np.max([np.array(p['bounds'])[:,1]for p in parts],axis=0);regions=parts
parts=[{'id':'22-23','name':'Refined_Pair','center':((lo+hi)/2).tolist(),'radius':float(np.linalg.norm((hi-lo)/2)),'bounds':np.stack([lo,hi],axis=1).tolist(),'nodes':[o.name for o in joined]}]
def export(path,selected):
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)
export(OUT/'refined-pair.glb',[o for level in objects for o in level]+levels)
for i in range(3):export(OUT/f'refined-lod{i}.glb',objects[i]+[levels[i]])
masterCollection.hide_render=True
for i in [1,2]:levels[i].hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'refined-limestone-pair.blend'))
manifest={'version':1,'blender':bpy.app.version_string,'units':'metres','blenderUp':'Z','glTFUp':'Y','selectedParts':IDS,'angularDomainDegrees':[START,END],'splitDegrees':SPLIT,'worldCenter':CENTER.tolist(),'parts':parts,'sourceRegions':regions,'nodes':rows,'material':'Approved_Cool_Grey_Limestone_Family','materialPolicy':'Runtime borrows the exact Stage2C material/textures; geometry-only GLB after postprocessing. Editable master retains packed approved maps.','collisionPolicy':'Existing movement/world collision unchanged; selected original proxies remain the collision reference.','baselineGLBSHA256':hashlib.sha256((ROOT/'public/models/gullyverse/quarry-rollout/quarry-limestone.glb').read_bytes()).hexdigest(),'joinPolicy':'Two original regions welded into one closed volume, internal caps removed; one coordinated LOD prevents a level mismatch across the join.'}
for p in [SRC/'manifest.json',OUT/'manifest.json']:p.write_text(json.dumps(manifest,indent=2))
print('REFINED_PAIR',parts,flush=True)
