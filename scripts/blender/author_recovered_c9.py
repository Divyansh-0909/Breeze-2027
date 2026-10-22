"""Reconstruct one native Coastal Cliff 01 formation on the surviving C5.1 host.

No source fitting, solid Boolean or field-generated cliff. Exact original host
outer edges are retained separately at each LOD. New source vertices undergo
one rigid transform with uniform 0.9 scale. Run with Blender 4.3:
  blender -b -t 2 --python scripts/blender/author_recovered_c9.py
"""
from pathlib import Path
import bpy, bmesh, numpy as np, json, hashlib, math, sys
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets-source/gullyverse/quarry-scanned-composition'
OUT=ROOT/'public/models/gullyverse/recovered-c9-composition'
RAW=ROOT/'reports/recovery-phase3-c9-2026-10-19/raw'
CACHE=SOURCE/'.authoring-cache'
for p in [SOURCE,OUT,RAW,CACHE]:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts/blender'))
import refined_foundation_geometry as foundation

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def B(p):return (float(p[0]),-float(p[2]),float(p[1]))
def G(p):return np.array([p[0],p[2],-p[1]])
def mesh_object(name,xyz,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(xyz,[],faces);m.update()
 o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o)
 for p in m.polygons:p.use_smooth=True
 return o

def boundary_loops(mesh):
 # Directed half-edges preserve face winding. Non-manifold inputs are rejected.
 directed={};counts={}
 for p in mesh.polygons:
  vs=list(p.vertices)
  for a,b in zip(vs,vs[1:]+vs[:1]):
   key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1;directed[key]=(a,b)
 assert max(counts.values())<=2,'non-manifold input'
 edges=[directed[k]for k,n in counts.items()if n==1]
 outgoing={a:b for a,b in edges}
 assert len(outgoing)==len(edges),'branching boundary'
 loops=[]
 while outgoing:
  start=next(iter(outgoing));loop=[start];i=outgoing.pop(start)
  while i!=start:
   loop.append(i);assert i in outgoing,'open boundary chain';i=outgoing.pop(i)
  loops.append(loop)
 return loops

def clip_native(original):
 m=original.data.copy();bm=bmesh.new();bm.from_mesh(m)
 # Four slightly oblique real-space trim planes, not a rectangular fitted chart.
 planes=[((-35.15,0,4.5),(1,0,-.045)),((-24.85,0,4.5),(-1,0,-.028)),
         ((-30,0,.50),(.035,0,1)),((-30,0,8.92),(-.025,0,-1))]
 for point,normal in planes:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,
                        plane_co=Vector(point),plane_no=Vector(normal),clear_inner=True,clear_outer=False)
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
 # Bisect may leave two capture-boundary vertices a few micrometres apart.
 # Merge only sub-1mm source-boundary slivers before forming any runtime LOD.
 # This repairs geometry; exported border/tangent tolerances stay unchanged.
 micro_before=len(bm.verts)
 bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=.001)
 print('SOURCE_MICRO_CUT_CLEANUP',micro_before-len(bm.verts),flush=True)
 # Keep the main captured component, record rather than silently fill scan holes.
 remaining=set(bm.verts);components=[]
 while remaining:
  stack=[remaining.pop()];component=set(stack)
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in remaining:remaining.remove(q);component.add(q);stack.append(q)
  components.append(component)
 components.sort(key=len,reverse=True)
 discarded=[{'vertices':len(c),'faces':len({f for v in c for f in v.link_faces})}for c in components[1:]]
 if len(components)>1:bmesh.ops.delete(bm,geom=list(set.union(*components[1:])),context='VERTS')
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
 loops=boundary_loops(m)
 if len(loops)>1:
  loops.sort(key=len,reverse=True);repair=bmesh.new();repair.from_mesh(m);repair.verts.ensure_lookup_table()
  for hole in loops[1:]:
   pts=np.array([m.vertices[i].co[:]for i in hole]);span=float(np.linalg.norm(np.ptp(pts,axis=0)))
   print('NATIVE_CAPTURE_HOLE',len(hole),span,flush=True)
   assert len(hole)<=12 and span<.15,'large source gap requires a different crop'
   edges=[e for e in repair.edges if e.is_boundary and all(v.index in hole for v in e.verts)]
   bmesh.ops.holes_fill(repair,edges=edges,sides=0)
   discarded.append({'repair':'tiny native capture hole triangulated, original boundary vertices retained','vertices':len(hole),'spanM':span})
  bmesh.ops.triangulate(repair,faces=list(repair.faces));repair.to_mesh(m);repair.free();m.update();loops=boundary_loops(m)
 assert len(loops)==1,('source crop must be one bounded disk',list(map(len,loops)))
 xyz=np.array([v.co[:]for v in m.vertices]);faces=np.array([p.vertices[:]for p in m.polygons])
 return m,xyz,faces,planes,discarded

def simplify_source(master,level,target):
 o=bpy.data.objects.new('Source_Optimized_'+str(level),master.copy());bpy.context.scene.collection.objects.link(o)
 loops=boundary_loops(o.data);boundary=set(sum(loops,[]));group=o.vertex_groups.new(name='Interior_Only')
 group.add([i for i in range(len(o.data.vertices))if i not in boundary],1,'REPLACE')
 if len(o.data.polygons)>target:
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  mod=o.modifiers.new('Interior_Reduction_No_Border_Collapse','DECIMATE');mod.ratio=target/len(o.data.polygons)
  mod.vertex_group=group.name;mod.vertex_group_factor=1000;mod.use_collapse_triangulate=True
  bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
 # A decimated interior vertex can approach a locked cut edge and create a
 # needle face. Weld that interior vertex INTO the exact boundary landmark;
 # never collapse the source boundary or the authoritative host interface.
 bm=bmesh.new();bm.from_mesh(o.data);repairs=0
 for _ in range(10):
  mapping={}
  for e in bm.edges:
   if e.calc_length()>=.002:continue
   a,b=e.verts
   if a.is_boundary and b.is_boundary:continue
   if b.is_boundary:a,b=b,a
   if a not in mapping and b not in mapping:mapping[b]=a
  if not mapping:break
  repairs+=len(mapping);bmesh.ops.weld_verts(bm,targetmap=mapping)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 print('LOD_INTERIOR_SLIVER_REPAIR',level,repairs,flush=True)
 before={tuple(master.vertices[i].co)for i in boundary_loops(master)[0]}
 after={tuple(o.data.vertices[i].co)for i in boundary_loops(o.data)[0]}
 assert before==after,'native cut boundary changed in LOD reduction'
 return o

def bridge(outer,inner,xyz):
 # Both supplied boundaries follow retained-face half-edges. Reverse inner to
 # build an annulus, then dynamic-program the oriented 3-D triangulation.
 a=list(outer);b=list(reversed(inner));pa=xyz[a];pb=xyz[b]
 # Stable, shortest starting cross-edge. No resampling or deformation of source.
 dist=((pa[:,None]-pb[None,:])**2).sum(2);i,j=np.unravel_index(dist.argmin(),dist.shape)
 a=a[i:]+a[:i];b=b[j:]+b[:j];a=a+[a[0]];b=b+[b[0]]
 n,m=len(a)-1,len(b)-1;cost=np.full((n+1,m+1),np.inf);prev=np.zeros((n+1,m+1),np.uint8);cost[0,0]=0
 def score(x,y,z):
  ab=y-x;ac=z-x;bc=z-y
  area=np.linalg.norm(np.cross(ab,ac),axis=-1);length=(ab*ab).sum(-1)+(ac*ac).sum(-1)+(bc*bc).sum(-1)
  return length+.03*length*length/np.maximum(area,1e-12)
 qa=xyz[a];qb=xyz[b]
 sa=score(qa[:-1,None,:],qa[1:,None,:],qb[None,:,:])
 sb=score(qa[:,None,:],qb[None,1:,:],qb[None,:-1,:])
 for i in range(n+1):
  for j in range(m+1):
   if i:
    c=cost[i-1,j]+sa[i-1,j]
    if c<cost[i,j]:cost[i,j]=c;prev[i,j]=1
   if j:
    c=cost[i,j-1]+sb[i,j-1]
    if c<cost[i,j]:cost[i,j]=c;prev[i,j]=2
 faces=[];i,j=n,m
 while i or j:
  if prev[i,j]==1:faces.append([a[i],a[i-1],b[j]]);i-=1
  else:faces.append([a[i],b[j-1],b[j]]);j-=1
 return faces

def inside_convex(points,polygon,padding):
 # Polygon is the authored source boundary's convex envelope in site arc/height;
 # used ONLY to remove host faces, never to normalize or flatten the scan.
 sign=[]
 for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
  d=b-a;sign.append((d[0]*(points[:,1]-a[1])-d[1]*(points[:,0]-a[0]))/np.linalg.norm(d))
 return np.min(sign,axis=0)>-padding

def hull(points):
 p=sorted(set(map(tuple,points)));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for q in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return np.array(lo[:-1]+hi[:-1])

def regular_crop(faces,remove,protected):
 # A coarse triangulation may touch the crop at only one vertex. Resolve that
 # specific pinched fan by removing its incident interior faces (or retaining
 # the fan beside a protected edge). Never change protected vertices/faces.
 incident={}
 for fi,f in enumerate(faces):
  for v in f:incident.setdefault(int(v),[]).append(fi)
 forbidden=np.isin(faces,list(protected)).any(axis=1)
 for _ in range(30):
  counts={}
  for f in faces[~remove]:
   for a,b in zip(f,np.roll(f,-1)):
    k=tuple(sorted((int(a),int(b))));counts[k]=counts.get(k,0)+1
  degree={}
  for (a,b),n in counts.items():
   if n==1:degree[a]=degree.get(a,0)+1;degree[b]=degree.get(b,0)+1
  bad=[v for v,n in degree.items()if n>2]
  if not bad:return remove
  for v in bad:
   ids=incident[v];remove[ids]=not forbidden[ids].any()
  remove[forbidden]=False
 raise RuntimeError('Local crop pinch could not be repaired safely')

def make_uvs(ob,site,tangent,original_count,original_uv,source_indices):
 m=ob.data;uv=m.uv_layers.new(name='Metre_Scale_UV0')
 xyz=np.array([G(v.co)for v in m.vertices]);u=(xyz-site)@tangent/2+327/2;v=xyz[:,1]/2
 coords=np.column_stack([u,v]);coords[:original_count]=original_uv
 # Both the imported host and the authored source use Blender's bottom-left V.
 # The exporter performs the common glTF V-origin conversion once.
 # Whole approved atlas periods reduce float32 UV cancellation without changing
 # the C8 3x pattern's phase, scale, orientation or image bytes.
 repeat=json.loads((ROOT/'public/models/gullyverse/recovered-c8-material/manifest.json').read_text())['approvedUVRepeat']
 coords[:,0]-=10/repeat
 for p in m.polygons:
  indices=list(p.vertices);puv=coords[indices].copy()
  if abs(np.cross(puv[1]-puv[0],puv[2]-puv[0]))<1e-9:
   # Undercut horizontal/side faces need a physical projection, not zero UV area.
   vv=xyz[indices];normal=np.cross(vv[1]-vv[0],vv[2]-vv[0]);axis=int(np.argmax(abs(normal)))
   axes=[i for i in range(3)if i!=axis];puv=vv[:,axes]/2
  for i,li in enumerate(p.loop_indices):uv.data[li].uv=puv[i]
 # Separate UV1 chart for geometry-only high-to-low baking; no fine PBR grain.
 bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 if ob.name.endswith('LOD0'):
  layer=m.uv_layers.new(name='Unused_Near_UV1_Same_Metre_Scale')
  for a,b in zip(layer.data,uv.data):a.uv=b.uv
  m.uv_layers.active_index=0;ob.select_set(False);return coords
 m.uv_layers.new(name='Geometry_Bake_UV1');m.uv_layers.active_index=1
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.012,correct_aspect=True,scale_to_bounds=True)
 bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False);m.uv_layers.active_index=0
 return coords

def main():
 source_path=SOURCE/'licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend'
 bpy.ops.wm.open_mainfile(filepath=str(source_path));original=bpy.data.objects['coastal_cliff_01_LOD0']
 master,native,faces,planes,discarded=clip_native(original)
 # Current authoritative foot curve at arc 327; orientation is a rigid yaw only.
 foot,outward,_=foundation.old.frame(np.array([327.]));outward3=np.array([outward[0,0],0,outward[0,1]])
 tangent=np.array([-outward[0,1],0,outward[0,0]])
 rotation=np.column_stack([tangent,outward3,[0,1,0]])
 assert np.linalg.det(rotation)>.99999
 anchor=np.array([foot[0,0]-.25,.55,foot[0,1]-.15]);native_origin=np.array([-30,1.5,.5])
 linear=.9*rotation;translation=anchor-linear@native_origin
 world=native@linear.T+translation
 world_boundary=world[boundary_loops(master)[0]]
 site=np.array([foot[0,0],0,foot[0,1]])
 # Increasing source-X is decreasing wall arc; UV0 uses increasing wall arc.
 arc_tangent=-tangent
 chart=np.column_stack([(world_boundary-site)@arc_tangent+327,world_boundary[:,1]])
 envelope=hull(chart)
 # Preserve all original sources in an excluded authoring collection.
 original_collection=bpy.data.collections.new('LICENSED_NATIVE_SOURCES_UNCHANGED');bpy.context.scene.collection.children.link(original_collection)
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH':
   for c in list(ob.users_collection):c.objects.unlink(ob)
   original_collection.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
 original_collection.hide_render=True;original_collection.hide_viewport=True
 high=mesh_object('C9_Native_High_Unique_Uniform_0_9',[B(p)for p in world],faces.tolist());high.hide_render=True;high.hide_set(True)
 high['source_uniform_scale']=.9;high['no_source_fitting']=True
 # Import the actual surviving runtime. Never regenerate its original field.
 before=set(bpy.data.objects);base=ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'
 bpy.ops.import_scene.gltf(filepath=str(base))
 hosts={int(o.name[-1]):o for o in bpy.data.objects if o not in before and o.type=='MESH' and o.name.startswith('Foundation_Wall_15_LOD')}
 for ob in list(bpy.data.objects):
  if ob not in before and ob not in hosts.values():bpy.data.objects.remove(ob,do_unlink=True)
 # One material placeholder: C8 images are borrowed by runtime, never embedded.
 placeholder=bpy.data.materials.new('BORROW_RECOVERED_C8_3X');placeholder.use_nodes=True;placeholder.use_backface_culling=True
 exports=[];rows=[];protected=[]
 for level,target in enumerate([22000,6500,2100]):
  host=hosts[level];hm=host.data;hm.calc_loop_triangles();hp=np.array([G(v.co)for v in hm.vertices]);hf=np.array([t.vertices[:]for t in hm.loop_triangles]);hn=np.zeros((len(hp),3))
  # glTF imports authored normals as corner normals. Vertex.normal would
  # recompute a different average, especially on the LOD interface curves.
  for loop in hm.loops:hn[loop.vertex_index]=G(hm.corner_normals[loop.index].vector)
  host_uv=np.zeros((len(hp),2))
  for loop in hm.loops:host_uv[loop.vertex_index]=hm.uv_layers[0].data[loop.index].uv[:]
  original_border=boundary_loops(hm);assert len(original_border)==1
  original_border=set(original_border[0]);protected.append({'LOD':level,'vertices':hp[sorted(original_border)].tolist()})
  # The sampling chart is used to locate the hole in the EXISTING mesh only.
  host_chart=np.column_stack([host_uv[:,0]*2,hp[:,1]])
  centers=host_chart[hf].mean(1)
  remove=inside_convex(centers,envelope,.52)
  remove &= ~np.isin(hf,list(original_border)).any(axis=1)
  remove=regular_crop(hf,remove,original_border)
  print('HOST_CUT',level,'removed',int(remove.sum()),'chart',host_chart.min(0),host_chart.max(0),'envelope',envelope.min(0),envelope.max(0),flush=True)
  retained=hf[~remove]
  ho=mesh_object('Retained_Host_'+str(level),[B(p)for p in hp],retained.tolist())
  hloops=boundary_loops(ho.data);holes=[q for q in hloops if not set(q)&original_border]
  assert len(holes)==1,('host crop must make exactly one local hole',level,list(map(len,hloops)))
  so=simplify_source(master,level,target);sp=np.array([v.co[:]for v in so.data.vertices]);sf=np.array([p.vertices[:]for p in so.data.polygons]);sp=sp@linear.T+translation
  inner=boundary_loops(so.data)[0];xyz=np.concatenate([hp,sp]);outer=holes[0];offset=len(hp)
  joins=bridge(outer,[i+offset for i in inner],xyz)
  allfaces=retained.tolist()+(sf+offset).tolist()+joins
  ob=mesh_object(f'C9_Wall_15_LOD{level}',[B(p)for p in xyz],allfaces)
  # Keep unused host vertices out of runtime, without changing any surface.
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
  # Resolve exact host vertex identity after removing only isolated vertices.
  lookup={tuple(p):i for i,p in enumerate(hp)};obxyz=np.array([G(v.co)for v in ob.data.vertices]);uvs=np.zeros((len(obxyz),2))
  n_host=sum(tuple(p)in lookup for p in obxyz)
  # Native vertices remain in the trailing block; retained host vertices stay first.
  for i,p in enumerate(obxyz[:n_host]):uvs[i]=host_uv[lookup[tuple(p)]]
  make_uvs(ob,site,arc_tangent,n_host,uvs[:n_host],None)
  # Preserve original exterior normals exactly. Smooth native/annulus normals are
  # derived from their 3-D surfaces, not a doubled-sided shader workaround.
  normals=[];hole_indices=set(outer)
  for loop in ob.data.loops:
   pos=obxyz[loop.vertex_index];idx=lookup.get(tuple(pos));n=hn[idx] if idx is not None and idx not in hole_indices else G(ob.data.vertices[loop.vertex_index].normal)
   normals.append(B(n))
  ob.data.normals_split_custom_set(normals)
  ob.data.materials.append(placeholder)
  loops=boundary_loops(ob.data);assert len(loops)==1
  border=np.array([obxyz[i]for i in loops[0]])
  assert len(border)==len(original_border)
  assert {tuple(p)for p in border}=={tuple(hp[i])for i in original_border},'outer boundary modified'
  row={'LOD':level,'triangles':len(ob.data.polygons),'sourceTriangles':len(sf),'retainedHostTriangles':len(retained),'joinTriangles':len(joins),'originalHostTriangles':len(hf),'removedHostTriangles':int(remove.sum()),'bounds':[obxyz.min(0).tolist(),obxyz.max(0).tolist()],'nativeBounds':[sp.min(0).tolist(),sp.max(0).tolist()],'externalBoundaryVertices':len(border),'openBoundaryLoops':len(loops)}
  print('COMPOSITION_LOD',json.dumps(row),flush=True);rows.append(row);exports.append(ob)
  for q in [ho,so,host]:bpy.data.objects.remove(q,do_unlink=True)
 # An authoring cache outside the repository makes failed diagnostics reviewable;
 # it is not a runtime export or a claimed valid master.
 bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/'unvalidated-composition.blend'))
 # Validate geometry before producing an export. No threshold relaxation.
 for ob in exports:
  ob.data.calc_loop_triangles();assert min(t.area for t in ob.data.loop_triangles)>1e-10
  for idx in [0,1]:
   if idx==1 and ob.name.endswith('LOD0'):
    for a,b in zip(ob.data.uv_layers[1].data,ob.data.uv_layers[0].data):a.uv=b.uv
   for attempt in range(4):
    ob.data.free_tangents();ob.data.calc_tangents(uvmap=ob.data.uv_layers[idx].name)
    bad=[l.index for l in ob.data.loops if np.linalg.norm(l.tangent[:])<.99]
    if not bad:break
    if idx==1:
     badfaces=[face for face in ob.data.polygons if set(face.loop_indices)&set(bad)]
     if attempt==0:
      for uv in ob.data.uv_layers[1].data:uv.uv*=.96
     ns=[n.vector[:]for n in ob.data.corner_normals]
     for i,face in enumerate(badfaces):
      face.use_smooth=False
      assert i<20,'too many bake-chart corner repairs'
      x=.002+i*.045;y=.975
      for li,uv in zip(face.loop_indices,[(x,y),(x+.025,y),(x,y+.02)]):
       ob.data.uv_layers[1].data[li].uv=uv;ns[li]=face.normal[:]
     ob.data.normals_split_custom_set(ns)
     print('LOCAL_BAKE_CHART_REPAIR',ob.name,[f.index for f in badfaces],flush=True)
     continue
    repaired=[]
    for face in ob.data.polygons:
     if not set(face.loop_indices)&set(bad):continue
     xyz=np.array([G(ob.data.vertices[v].co)for v in face.vertices]);n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);axes=[i for i in range(3)if i!=int(np.argmax(abs(n)))]
     uv=xyz[:,axes]/2;uv[:,1]*=-1
     previous=np.array([ob.data.uv_layers[0].data[li].uv[:]for li in face.loop_indices]);uv+=previous.mean(0)-uv.mean(0)
     for li,coord in zip(face.loop_indices,uv):ob.data.uv_layers[0].data[li].uv=coord
     repaired.append(face.index)
    print('LOCAL_SIDE_FACE_UV_REPAIR',ob.name,idx,attempt,repaired,flush=True)
    if attempt==1:
     # At two narrow scan-cut/annulus corners the averaged smooth normal is
     # parallel to the derivative tangent. Split only those physical face
     # normals; keep the rest of the scan and protected exterior shading.
     ns=[n.vector[:]for n in ob.data.corner_normals]
     for fi in repaired:
      face=ob.data.polygons[fi]
      face.use_smooth=False
      for li in face.loop_indices:ns[li]=face.normal[:]
     ob.data.normals_split_custom_set(ns)
     print('LOCAL_FACE_NORMAL_SPLIT',ob.name,repaired,flush=True)
   assert not bad,'invalid tangent frame'
  ob.data.calc_tangents(uvmap=ob.data.uv_layers[0].name)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in exports:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'composition-region.glb'),export_format='GLB',use_selection=True,
   export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_yup=True,export_animations=False)
 for ob in exports:ob.select_set(False);ob.hide_set(not ob.name.endswith('LOD0'));ob.hide_render=not ob.name.endswith('LOD0')
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 # Source images and scanned geometry remain editable, not visitor downloads.
 bpy.ops.file.pack_all()
 contract={'phase':'Recovery Phase 3','source':'Poly Haven coastal_cliff_01','license':'CC0','sourceSHA256':sha(source_path),
  'sourceNativeDimensionsM':[91.97995376586914,10.966708660125732,10.325531363487244],
  'cropBoundsNativeM':[native.min(0).tolist(),native.max(0).tolist()],'cropDimensionsM':np.ptp(native,axis=0).tolist(),
  'cropTriangles':len(faces),'cropPlanes':[{'point':p,'inwardNormal':n}for p,n in planes],
  'discardedComponents':discarded,'uniformScale':.9,'transformWorldYUp':np.column_stack([linear,translation]).tolist(),
  'singularValues':np.linalg.svd(linear)[1].tolist(),'formationWorldBounds':[world.min(0).tolist(),world.max(0).tolist()],
  'hostPart':'Wall_15','historicalHostPart':'lower Wall_14 within LOST C6.2 partition',
  'hostGeometrySHA256':sha(base),'hostArcM':[315.07670942703663,337.02719558677654],
  'hostCompatibility':'Surviving C5.1 actual Wall_15 at arc327, not fabricated lost C6.2. Exact original outer boundary per LOD; local scan cut and connecting annulus reconstructed, not bit-identical.',
  'runtime':'composition-region.glb','runtimeBytes':(OUT/'composition-region.glb').stat().st_size,'runtimeSHA256':sha(OUT/'composition-region.glb'),
  'materialOwner':'recovered-c8-material/scanned-materials.glb','approvedTextureScale':3,'newPBRImages':0,'newGeometryBakeImages':0,
  'parts':[{'id':'Wall_15','nodes':[o.name for o in exports],'center':((np.array(rows[0]['bounds'][0])+rows[0]['bounds'][1])/2).tolist(),
    'radius':float(np.linalg.norm(np.array(rows[0]['bounds'][1])-rows[0]['bounds'][0])/2)}],
  'LODs':rows,'privateOnly':True,'publicDefaultChanged':False,'collisionChanged':False,'lightingChanged':False}
 txt=bpy.data.texts.new('RECOVERY_C9_CONTRACT');txt.write(json.dumps(contract,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'quarry-scanned-composition.blend'))
 import shutil
 shutil.copyfile(SOURCE/'quarry-scanned-composition.blend',CACHE/'base-unbaked.blend')
 (SOURCE/'protected-host-boundaries.json').write_text(json.dumps(protected,indent=2))
 (OUT/'manifest.json').write_text(json.dumps(contract,indent=2)+'\n');(SOURCE/'composition-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
 print('C9_COMPLETE',json.dumps(contract),flush=True)

if __name__=='__main__':main()
