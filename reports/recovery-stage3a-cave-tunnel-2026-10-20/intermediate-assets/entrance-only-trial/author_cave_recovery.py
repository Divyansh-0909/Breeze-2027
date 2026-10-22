"""Private natural cave composition, real-source cropping and boundary retopology.

No change to C9 or movement registry; no Boolean, folded-plane cliff or random
rock displacement. Source geometry is uniformly transformed, cut around the
protected bent corridor and retained in the editable master. All runtime maps
are borrowed from the existing approved C8 3x owner.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,hashlib,sys,subprocess
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'assets-source/gullyverse/c9-cave-recovery';O=ROOT/'public/models/gullyverse/c9-cave-recovery';R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw'
for p in [S,O,R]:p.mkdir(parents=True,exist_ok=True)
W=json.loads((ROOT/'public/models/gullyverse/blockout.layout.json').read_text())
# Blender Z up, site WebGL Y up; site travel -Z maps to Blender +Y.
def B(p):return (float(p[0]),-float(p[2]),float(p[1]))
def G(p):return (float(p[0]),float(p[2]),-float(p[1]))
def center(y):return float(np.interp(np.clip(y,0,42),[-p[1]for p in W['tunnel']['centerline']],[p[0]for p in W['tunnel']['centerline']]))
def mesh(name,xyz,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(xyz,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o

def decimate(o,target,protect=True):
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 group=o.vertex_groups.new(name='Protected_Shared_Interfaces')
 if protect:
  bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();boundary=[v.index for v in bm.verts if v.is_boundary];bm.free()
  if boundary:group.add(boundary,1.0,'REPLACE')
 m=o.modifiers.new('Source_Form_Retopology','DECIMATE');m.ratio=min(1,target/len(o.data.polygons));m.use_collapse_triangulate=True
 if protect:m.vertex_group=group.name;m.invert_vertex_group=True;m.vertex_group_factor=1000
 bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return o

def chains(edges):
 adjacency={}
 for a,b in edges:
  adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
 assert all(len(v)<=2 for v in adjacency.values()),('Branched cut',[(k,len(v))for k,v in adjacency.items()if len(v)>2][:10])
 paths=[]
 while adjacency:
  start=next((k for k,v in adjacency.items()if len(v)==1),next(iter(adjacency)))
  path=[];previous=None;current=start
  while current in adjacency:
   path.append(current);neighbors=adjacency.pop(current);n=next((j for j in neighbors if j!=previous and j in adjacency),None)
   if n is None:break
   previous,current=current,n
  paths.append(path)
 return paths

# Actual scanned three-dimensional source. Keep original geometry editable.
src=ROOT/'assets-source/gullyverse/quarry-fidelity-correction/licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));native=bpy.data.objects['coastal_cliff_04_LOD2'];native_mesh=native.data.copy();native_world=native.matrix_world.copy()
for original_object in list(bpy.data.objects):
 bpy.data.objects.remove(original_object,do_unlink=True)
reference=bpy.data.objects.new('CC0_Coastal04_Original_Native_Reference',native_mesh);bpy.context.scene.collection.objects.link(reference);reference.matrix_world=native_world
reference.hide_render=True;reference.hide_set(True)
working=bpy.data.objects.new('Cave_Entrance_Authored_High',native_mesh.copy());bpy.context.scene.collection.objects.link(working)
# 1.7 uniformly in XYZ: original ~11m vertical capture becomes ~18.7m;
# no directional expansion. The 58m original entrance width is cropped, not fitted.
scale=1.7
for v in working.data.vertices:
 p=native_world@v.co;v.co=(p.x*scale,p.y*scale+3.0,p.z*scale-.3)
working.data.materials.clear();decimate(working,85000,False)
# Temporarily express X relative to the existing bent path for the cut only.
# Restore every surviving source vertex to its original rigid-transformed X.
bm=bmesh.new();bm.from_mesh(working.data)
for v in bm.verts:v.co.x-=center(v.co.y)
for point,normal in [((-29,0,0),(1,0,0)),((30,0,0),(-1,0,0)),((0,0,-.38),(0,0,1)),((0,-4,0),(0,1,0))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=point,plane_no=normal,clear_inner=True)
# Deliberately asymmetric mouth, constrained outside the 2.38m protected route.
profile=np.array([[-4.15,-.5],[-4.0,1.8],[-3.65,3.6],[-2.7,5.0],[-1.35,5.85],[.65,6.25],[2.1,5.65],[3.4,4.3],[3.95,2.3],[4.15,-.5]])
planes=[]
for a,b in zip(profile[:-1],profile[1:]):
 tangent=b-a;n=np.array([tangent[1],-tangent[0]]);n/=np.linalg.norm(n);planes.append((a,n))
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(a[0],0,a[1]),plane_no=(n[0],0,n[1]))
inside=lambda x,z: all(np.dot(np.array([x,z])-a,n)>=-1e-6 for a,n in planes)
remove=[f for f in bm.faces if inside(f.calc_center_median().x,f.calc_center_median().z)]
bmesh.ops.delete(bm,geom=remove,context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=1e-6)
# The true scan cut edge is shared by the authored throat. No overlaid rocks.
bm.verts.ensure_lookup_table();cut=[]
for e in bm.edges:
 if not e.is_boundary:continue
 a,b=e.verts
 if min(a.co.z,b.co.z)<-.35:continue
 if all(min(abs(np.dot(np.array([v.co.x,v.co.z])-p,n))for p,n in planes)<2e-4 for v in [a,b]):cut.append((a.index,b.index))
paths=chains(cut);paths.sort(key=len,reverse=True)
print('MOUTH_PATHS',[(len(p),float(max(bm.verts[i].co.z for i in p)),[list(bm.verts[p[0]].co),list(bm.verts[p[-1]].co)])for p in paths],flush=True)
arches=[p for p in paths if max(bm.verts[i].co.z for i in p)>4]
assert len(arches)==1,'The selected source does not produce one safe raised mouth; do not hide capture defects.'
path=arches[0]
for v in bm.verts:v.co.x+=center(v.co.y)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(working.data);bm.free();working.data.update()
# Save the genuine edge before any further authoring, to diagnose source suitability.
cut_points=[list(working.data.vertices[i].co)for i in path]
(R/'mouth-native-cut.json').write_text(json.dumps({'source':str(src.relative_to(ROOT)),'uniformScaleXYZ':[scale]*3,'profile':profile.tolist(),'points':cut_points,'triangles':len(working.data.polygons)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-entrance-source-trial.blend'),compress=True)
print('ENTRANCE_TRIAL_READY',len(working.data.polygons),flush=True)

# Entrance-only checkpoint. Interior roof authoring waits for the explicit
# 'no visible ceiling' clarification; legacy passage/reveal is retained.
if path[0]and cut_points[0][0]>cut_points[-1][0]:path=list(reversed(path));cut_points=list(reversed(cut_points))
source_points=np.array(cut_points)
# Exact existing internal ring at 6m: 8 original .75m route sections.
legacy=np.array(W['tunnel']['profile']);end=[]
for a,b in zip(legacy[:-1],legacy[1:]):
 for t in [0,1/3,2/3]:
  x,z=a+(b-a)*t;noise=(math.sin(-6*1.43+z*2.1)*.1+math.sin(-6*2.74-z*3.8)*.055)*math.sin(6/42*math.pi)
  end.append([center(6)+x+noise,6,z+(noise*.5 if z>1 else 0)])
x,z=legacy[-1];noise=(math.sin(-6*1.43+z*2.1)*.1+math.sin(-6*2.74-z*3.8)*.055)*math.sin(6/42*math.pi);end.append([center(6)+x+noise,6,z])
end=np.array(end);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(source_points,axis=0),axis=1))];s/=s[-1]
e=np.r_[0,np.cumsum(np.linalg.norm(np.diff(end[:,[0,2]],axis=0),axis=1))];e/=e[-1]
# Blend the true irregular scan edge into the protected old passage, not a flat
# annulus. Mouth thickness is actual 3-D geometry, near-to-far interfaces exact.
V=[];F=[];rings=9
for j in range(rings):
 t=j/(rings-1)
 for i,p in enumerate(source_points):
  q=np.array([np.interp(s[i],e,end[:,k])for k in range(3)])
  # Keep centerline bending authoritative while the rock body returns inward.
  pos=p*(1-t)+q*t;pos[0]+=center(pos[1])-((1-t)*center(p[1])+t*center(6));V.append(pos.tolist())
for j in range(rings-1):
 for i in range(len(source_points)-1):
  a=j*len(source_points)+i;b=a+len(source_points);F.extend([[a,b,b+1],[a,b+1,a+1]])
throat=mesh('Cave_Throat_Authored_High',V,F)
# Per-source face UV projection preserves real metre density, including returns
# and undersides. No black AO mask, no duplicate PBR images, no face randomness.
base_repeat=json.loads((ROOT/'public/models/gullyverse/recovered-c8-material/manifest.json').read_text())['baseUVRepeat']
throat_uv=throat.data.uv_layers.new(name='UVMap')
arc_length=float(np.linalg.norm(np.diff(legacy,axis=0),axis=1).sum())
for loop in throat.data.loops:
 i=loop.vertex_index%len(source_points)
 throat_uv.data[loop.index].uv=(throat.data.vertices[loop.vertex_index].co.y*base_repeat,float(s[i])*arc_length*base_repeat)
mat=bpy.data.materials.new('Cave_Borrowed_C8_3x_PBR');mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.2,.18,.16,1);shader.inputs['Roughness'].default_value=.94

def finish(o):
 m=o.data
 if not m.uv_layers:m.uv_layers.new(name='UVMap')
 uv=m.uv_layers[0].data
 for face in m.polygons:
  n=np.abs(face.normal);axis=int(np.argmax(n))
  axes=([1,2]if axis==0 else[0,2]if axis==1 else[0,1])
  for li in [] if 'Throat'in o.name else face.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co
   # Explicit authored projection islands, offset by exact texture periods.
   # Identical numeric UVs at different projection orientations must not share
   # a tangent average. The offset changes no approved 3x visible sample.
   uv[li].uv=(v[axes[0]]*base_repeat+axis*300,v[axes[1]]*base_repeat)
  face.use_smooth='Throat'not in o.name
 col=m.color_attributes.get('Color')or m.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for i,v in enumerate(m.vertices):col.data[i].color=(1,1,1,1)
 m.materials.clear();m.materials.append(mat);m.update()

runtime=[];parts=[]
for name,high,targets in [('Entrance',working,[18000,9000,4200]),('Throat',throat,[len(throat.data.polygons),1500,900])]:
 nodes=[];counts=[]
 for level,target in enumerate(targets):
  o=bpy.data.objects.new(f'Cave_{name}_LOD{level}',high.data.copy());bpy.context.scene.collection.objects.link(o)
  decimate(o,target,True);finish(o);runtime.append(o);nodes.append(o.name);counts.append(len(o.data.polygons))
 high.hide_render=True;high.hide_set(True)
 xyz=np.array([G(v.co)for v in high.data.vertices]);lo=xyz.min(0);hi=xyz.max(0);c=(lo+hi)/2
 parts.append({'id':name,'nodes':nodes,'triangles':counts,'center':c.tolist(),'radius':float(np.linalg.norm(hi-lo)/2),'bounds':[lo.tolist(),hi.tolist()]})
# Corrected throat side orientation is inspected from the protected centerline.
for o in runtime:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if 'Throat'in o.name:
  score=0
  for f in bm.faces:
   c=f.calc_center_median();to=Vector((center(c.y)-c.x,0,2.2-c.z));score+=f.normal.dot(to)*f.calc_area()
  if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 # Captured fracture corners cannot average opposite surface normals/tangent
 # derivatives. Split shading at real >55-degree edges; position is unchanged.
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 split=o.modifiers.new('Physical_Fracture_Shading_Boundaries','EDGE_SPLIT')
 split.split_angle=math.radians(55);split.use_edge_angle=True;split.use_edge_sharp=False
 bpy.ops.object.modifier_apply(modifier=split.name);o.select_set(False);finish(o)
# Authoring source remains a separate hidden collection, excluded from runtime.
for o in bpy.context.selected_objects:o.select_set(False)
for o in runtime:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=runtime[0]
filepath=O/'cave-entrance.glb'
bpy.ops.export_scene.gltf(filepath=str(filepath),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_vertex_color='ACTIVE',export_materials='EXPORT',export_animations=False,export_extras=True)
subprocess.run(['node',str(ROOT/'scripts/blender/cave_mikktspace.mjs'),str(filepath)],cwd=ROOT,check=True)
manifest={'version':'stage3a-entrance-working-checkpoint','privateOnly':True,'completeStage3A':False,'interiorStatus':'PENDING ceiling clarification; exact original artwork unavailable; retained protected legacy interior after 6m','runtime':filepath.name,'runtimeBytes':filepath.stat().st_size,'runtimeSHA256':hashlib.file_digest(filepath.open('rb'),'sha256').hexdigest(),'parts':parts,'source':{'asset':'coastal_cliff_04','license':'CC0 1.0','page':'https://polyhaven.com/a/coastal_cliff_04','sourceFile':str(src.relative_to(ROOT)),'uniformScaleXYZ':[scale]*3,'croppedNotFit':True},'originalTunnelInterfaceMetres':6,'approvedTextureScale':3,'newPBRImages':0,'C9Changed':False,'collisionRegistryChanged':False,'visibleFixtures':0,'suppliedArtistArt':'PENDING; generic historical artwork omitted'}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'entrance-working-runtime.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.file.pack_all()
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-entrance-working.blend'),compress=True)
print('PRIVATE_ENTRANCE_RUNTIME',json.dumps(manifest),flush=True)
