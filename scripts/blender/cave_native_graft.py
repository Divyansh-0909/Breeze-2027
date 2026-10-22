"""Local native-triangle geological graft; no front-envelope or noise transfer.

The native mesh is rigidly rotated and uniformly scaled, then cropped with an
irregular convex geological outline. The existing cave body is cut to the same
outline. Both real boundary loops are subdivided at their union of parameters
before bridging, yielding actual matching topology rather than overlapping rock.
"""
import bpy,bmesh,math,numpy as np
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree


def make_mesh(name,vertices,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
 o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o


def signed_area(poly):
 return sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,np.roll(poly,-1,axis=0)))*.5


def planes_for(poly):
 if signed_area(poly)<0:poly=poly[::-1]
 return [(a,np.array([-(b-a)[1],(b-a)[0]])/np.linalg.norm(b-a))for a,b in zip(poly,np.roll(poly,-1,axis=0))]


def clip_polygon(vertices,point,normal,keep_inside):
 if not vertices:return []
 out=[]
 for a,b in zip(vertices,vertices[1:]+vertices[:1]):
  da=float(np.dot(np.array([a[0],a[2]])-point,normal));db=float(np.dot(np.array([b[0],b[2]])-point,normal))
  aa=da>=-1e-8 if keep_inside else da<=1e-8
  bb=db>=-1e-8 if keep_inside else db<=1e-8
  if aa:out.append(a)
  if aa!=bb:
   t=da/(da-db);out.append(a+(b-a)*t)
 return out


def polygon_triangles(polys):
 lookup={};verts=[];faces=[]
 def vi(p):
  key=tuple(round(float(x),7)for x in p)
  if key not in lookup:lookup[key]=len(verts);verts.append(tuple(float(x)for x in p))
  return lookup[key]
 for poly in polys:
  if len(poly)<3:continue
  ids=[vi(p)for p in poly]
  ids=[v for i,v in enumerate(ids)if v!=ids[i-1]]
  for j in range(1,len(ids)-1):
   a,b,c=[np.array(verts[k][:3])for k in [ids[0],ids[j],ids[j+1]]]
   if np.linalg.norm(np.cross(b-a,c-a))>1e-11:faces.append([ids[0],ids[j],ids[j+1]])
 return verts,faces


def boundary_loops(o,poly=None):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();ad={}
 for e in bm.edges:
  if not e.is_boundary:continue
  if poly is not None:
   ok=all(min(abs(np.dot(np.array([v.co.x,v.co.z])-a,n))for a,n in planes_for(poly))<2e-5 for v in e.verts)
   if not ok:continue
  a,b=[v.index for v in e.verts];ad.setdefault(a,[]).append(b);ad.setdefault(b,[]).append(a)
 assert all(len(v)==2 for v in ad.values()),('Open or branched native geological crop',o.name,[(k,len(v))for k,v in ad.items()if len(v)!=2][:12])
 loops=[]
 while ad:
  start=next(iter(ad));p=[];current=start;last=None
  while current in ad:
   p.append(current);neighbors=ad.pop(current);n=next((x for x in neighbors if x!=last and x in ad),None)
   if n is None:break
   last,current=current,n
  loops.append(p)
 bm.free();return loops


def conform_cut_edges(o):
 """Split true T-junctions introduced by attributed triangle subtraction.

 Polygon subtraction partitions adjoining triangles differently outside the
 hole. A vertex on the same old edge must be inserted in BOTH neighbours.
 This changes topology at the cut only; no shape or validation tolerance moves.
 """
 bm=bmesh.new();bm.from_mesh(o.data)
 counts=[]
 for iteration in range(4):
  bm.verts.ensure_lookup_table();bm.verts.index_update();kd=KDTree(len(bm.verts))
  for v in bm.verts:kd.insert(v.co,v.index)
  kd.balance();added=0
  for edge in list(bm.edges):
   if not edge.is_valid or not edge.is_boundary:continue
   a,b=edge.verts;d=b.co-a.co;length=d.length
   if length<2e-6:continue
   midpoint=(a.co+b.co)*.5;inside=[]
   for p,index,_ in kd.find_range(midpoint,length*.5+1e-6):
    if index in [a.index,b.index]:continue
    t=(p-a.co).dot(d)/(length*length)
    if 1e-7<t<1-1e-7 and(p-(a.co+d*t)).length<1e-6:inside.append((t,p.copy()))
   current=a;last=0;layer=bm.verts.layers.float_vector.get('graft_original_position');wa=a[layer].copy()if layer else None;wb=b[layer].copy()if layer else None
   for t,p in sorted(inside,key=lambda x:x[0]):
    if t-last<1e-7:continue
    e=bm.edges.get((current,b))
    if e is None:continue
    _,v=bmesh.utils.edge_split(e,current,(t-last)/(1-last));v.co=p
    if layer:v[layer]=wa.lerp(wb,t)
    current=v;last=t;added+=1
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);counts.append(added)
  if not added:break
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 print('LOCAL_CUT_CONFORMITY',counts,flush=True)


def planar_parameter(p,poly):
 best=None;lengths=np.linalg.norm(np.roll(poly,-1,axis=0)-poly,axis=1);starts=np.r_[0,np.cumsum(lengths)]
 q=np.array([p[0],p[2]])
 for j,(a,b)in enumerate(zip(poly,np.roll(poly,-1,axis=0))):
  d=b-a;t=float(np.clip(np.dot(q-a,d)/np.dot(d,d),0,1));err=float(np.linalg.norm(q-(a+d*t)))
  result=(err,float(starts[j]+t*lengths[j]))
  if best is None or err<best[0]:best=result
 assert best[0]<3e-5,('Boundary is not on protected crop outline',best,p)
 return best[1]/starts[-1]


def native_boundary_parameters(o,loop,poly):
 """Preserve re-entrant scan edges using intrinsic 3D boundary length.

 A real overhang can intersect one trim plane more than once. Sorting it by
 projected position destroys the topology. Instead retain its actual order and
 match the eight geological corners, distributing each edge by 3D arc length.
 """
 coords=np.array([[o.data.vertices[i].co.x,o.data.vertices[i].co.z]for i in loop])
 if signed_area(coords)<0:loop=list(reversed(loop));coords=coords[::-1]
 first=int(np.argmin(np.linalg.norm(coords-poly[0],axis=1)));loop=loop[first:]+loop[:first];coords=np.roll(coords,-first,axis=0)
 corners=[0];previous=0
 for corner in poly[1:]:
  candidates=np.where(np.linalg.norm(coords-corner,axis=1)<3e-5)[0];candidates=candidates[candidates>previous]
  assert len(candidates),('Missing topological source crop corner',corner.tolist())
  previous=int(candidates[0]);corners.append(previous)
 corners.append(len(loop));lengths=np.linalg.norm(np.roll(poly,-1,axis=0)-poly,axis=1);offsets=np.r_[0,np.cumsum(lengths)];out={}
 for j,(a,b)in enumerate(zip(corners,corners[1:])):
  indices=loop[a:b]+[loop[b%len(loop)]];points=np.array([list(o.data.vertices[i].co)for i in indices]);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
  for index,s in zip(indices[:-1],arc[:-1]):out[index]=float((offsets[j]+lengths[j]*s/arc[-1])/offsets[-1])
 return out


def subdivide_loop(o,loop,parameters,poly,original_parameters=None):
 bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
 verts=[bm.verts[i]for i in loop];t=[original_parameters[v.index]if original_parameters is not None else planar_parameter(v.co,poly)for v in verts]
 # Canonical order along the outline; each adjacent pair must be an actual edge.
 ordered=sorted(zip(t,verts),key=lambda x:x[0]);result={}
 for j,(a,va)in enumerate(ordered):
  b,vb=ordered[(j+1)%len(ordered)];b+=int(j==len(ordered)-1)
  e=bm.edges.get((va,vb));assert e is not None,('Nonmonotone captured boundary',o.name,a,b)
  result[round(a,10)]=va;current=va;last=a;origin=va.co.copy();layer=bm.verts.layers.float_vector.get('graft_original_position');wa=va[layer].copy()if layer else None;wb=vb[layer].copy()if layer else None
  target=vb.co.copy()
  for u in parameters:
   uu=float(u)
   if j==len(ordered)-1 and uu<a:uu+=1
   if not a+1e-9<uu<b-1e-9:continue
   e=bm.edges.get((current,vb));_,v=bmesh.utils.edge_split(e,current,(uu-last)/(b-last))
   v.co=origin.lerp(target,(uu-a)/(b-a))
   if layer:v[layer]=wa.lerp(wb,(uu-a)/(b-a))
   result[round(float(u),10)]=v;current=v;last=uu
 bm.verts.index_update();bm.verts.ensure_lookup_table();indices={u:v.index for u,v in result.items()}
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return indices


def graft(body,ROOT,*,source_x=-27.,source_z=4.6,station=11.2,side=-1,width=6.2,height=3.2,depth_offset=3.25):
 """Operate in orthonormal local coordinates U along route, D into wall, V up.

 Source 01 is cropped after a RIGID plane-normal alignment; native forms are
 never normalized to a chart or squeezed in depth. Final XYZ scale is 1.0.
 """
 source=ROOT/'assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend'
 with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=['coastal_cliff_01_LOD2']
 ref=b.objects[0];bpy.context.scene.collection.objects.link(ref);ref.name='Native_Coastal01_Graft_Reference';ref.hide_render=True;ref.hide_set(True)
 points=np.array([list(ref.matrix_world@v.co)for v in ref.data.vertices]);tri=np.array([list(f.vertices)for f in ref.data.polygons])
 centers=points[tri].mean(1);sel=(abs(centers[:,0]-source_x)<width*.65)&(abs(centers[:,2]-source_z)<height*.75)
 plane=np.linalg.lstsq(np.c_[centers[sel,0]-source_x,centers[sel,2]-source_z,np.ones(sel.sum())],centers[sel,1],rcond=None)[0]
 # Rotate the fitted native normal to frontal -Y, preserving all 3D distances.
 normal=Vector((float(plane[0]),-1,float(plane[1]))).normalized();rotation=normal.rotation_difference(Vector((0,-1,0))).to_matrix()
 origin=Vector((source_x,float(plane[2]),source_z));p=np.array([list(rotation@(Vector(x)-origin))for x in points])
 # Irregular convex cut follows the broad broken-body form, never a rectangle.
 outline=np.array([[-width*.50,-height*.32],[-width*.33,-height*.50],[width*.29,-height*.47],[width*.49,-height*.19],[width*.45,height*.25],[width*.22,height*.50],[-width*.26,height*.47],[-width*.51,height*.18]])
 assert signed_area(outline)>0
 polys=[]
 for ids in tri:
  vv=[p[i]for i in ids]
  if any(max(float(np.dot(np.array([v[0],v[2]])-a,n))for v in vv)<-1e-8 for a,n in planes_for(outline)):continue
  for a,n in planes_for(outline):vv=clip_polygon(vv,a,n,True)
  if len(vv)>=3:polys.append(vv)
 v,f=polygon_triangles(polys);native_crop_triangles=len(f);patch=make_mesh('Native_Actual_Triangles_Graft',v,f)
 loops=boundary_loops(patch)
 if len(loops)!=1:raise ValueError(('Unsuitable source crop has interior holes or disconnected captured faces',len(loops),[len(x)for x in loops]))
 # Tiny incomplete scan-edge notches are locally retopologized onto the crop
 # outline, never stretched across the panel. Reject larger missing areas.
 edge_repairs=[]
 for i in loops[0]:
  v=patch.data.vertices[i];q=np.array([v.co.x,v.co.z]);best=None
  for a,b in zip(outline,np.roll(outline,-1,axis=0)):
   d=b-a;t=float(np.clip(np.dot(q-a,d)/np.dot(d,d),0,1));target=a+d*t;err=float(np.linalg.norm(target-q))
   if best is None or err<best[0]:best=(err,target)
  assert best[0]<.08,('Unsuitable original scan gap at cropped boundary',best[0])
  if best[0]>2e-6:
   edge_repairs.append(best[0]);v.co.x=float(best[1][0]);v.co.z=float(best[1][1])
 bm=bmesh.new();bm.from_mesh(patch.data);bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=1e-6);bm.to_mesh(patch.data);bm.free();patch.data.update();loops=boundary_loops(patch)
 print('NATIVE_CROP_EDGE_REPAIR',{'count':len(edge_repairs),'maximumM':max(edge_repairs,default=0)},flush=True)
 # A rigid site frame follows this existing straight route leg, not a chart fit.
 slope=-3.8/8.;along=Vector((slope,1,0)).normalized();out=Vector((1,-slope,0))*side;out.normalize();up=Vector((0,0,1))
 center_x=float(np.interp(station,[0,8,16,24,34,42],[0,-2.2,-6,-6,-2.6,0]));site=Vector((center_x,station,2.05))
 frame=Matrix((along,out,up)).transposed()
 # Local X always runs forward; reversing native triangle winding for the
 # reflected left-hand frame is a geometric orientation correction.
 inv=frame.inverted()
 # Cut in the body's existing continuous authoring chart, not in a projection
 # through its potentially re-entrant surface. Preserve the actual old XYZ as
 # an interpolated attribute; this repairs the failing one-to-one assumption
 # rather than forcing a nonmonotone physical boundary into a sorted collar.
 old_uv={loop.vertex_index:body.data.uv_layers[0].data[loop.index].uv.copy()for loop in body.data.loops}
 old=np.array([[float(old_uv[v.index].x*2-station),float((inv@(v.co-site)).y),float(old_uv[v.index].y*2-2.20),*list(v.co)]for v in body.data.vertices]);oldfaces=[list(f.vertices)for f in body.data.polygons]
 outside=[]
 for ids in oldfaces:
  vv=[old[i]for i in ids]
  if max(v[1]for v in vv)<1.2 or any(max(float(np.dot(np.array([v[0],v[2]])-a,n))for v in vv)<-1e-8 for a,n in planes_for(outline)):
   outside.append(vv);continue
  inside=vv
  for a,n in planes_for(outline):
   outside.append(clip_polygon(inside,a,n,False));inside=clip_polygon(inside,a,n,True)
   if not inside:break
 v,f=polygon_triangles(outside);shell=make_mesh('Existing_Cave_With_Authored_Cut',[x[:3]for x in v],f)
 world_attribute=shell.data.attributes.new(name='graft_original_position',type='FLOAT_VECTOR',domain='POINT')
 for row,value in zip(world_attribute.data,v):row.vector=value[3:]
 conform_cut_edges(shell)
 shell_loops=boundary_loops(shell,outline);assert len(shell_loops)==1,('Incorrect shell cut',len(shell_loops))
 # Put the nearest native rock surface outside the exact route envelope. This
 # is a rigid translation only; all native depth/thickness remains unchanged.
 nearest=min(v.co.y for v in patch.data.vertices);offset=depth_offset-nearest
 for v in patch.data.vertices:v.co.y+=offset
 patchloop=loops[0];shellloop=shell_loops[0]
 native_parameters=native_boundary_parameters(patch,patchloop,outline)
 params=sorted(set([round(v,10)for v in native_parameters.values()]+[round(planar_parameter(shell.data.vertices[i].co,outline),10)for i in shellloop]))
 a=subdivide_loop(shell,shellloop,params,outline);b=subdivide_loop(patch,patchloop,params,outline,native_parameters)
 assert set(a)==set(b)==set(params),('Boundary parameter union incomplete',len(a),len(b),len(params))
 vertices=[list(v.vector)for v in shell.data.attributes['graft_original_position'].data];faces=[list(f.vertices)for f in shell.data.polygons];start=len(vertices)
 vertices.extend(list(site+frame@v.co)for v in patch.data.vertices);faces.extend([[i+start for i in f.vertices]for f in patch.data.polygons])
 max_bridge=0
 for u,v in zip(params,params[1:]+params[:1]):
  ia,ib,ic,id=a[u],a[v],b[v]+start,b[u]+start
  distance=max(np.linalg.norm(np.array(vertices[ia])-vertices[id]),np.linalg.norm(np.array(vertices[ib])-vertices[ic]));max_bridge=max(max_bridge,float(distance))
  faces.extend([[ia,ib,ic],[ia,ic,id]])
 result=make_mesh('Cave_Passage1_Deep_Authored_High',vertices,faces)
 bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 score=sum(f.normal.dot(Vector((float(np.interp(f.calc_center_median().y,[0,8,16,24,34,42],[0,-2.2,-6,-6,-2.6,0]))-f.calc_center_median().x,0,2.1-f.calc_center_median().z)))*f.calc_area()for f in bm.faces)
 if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(result.data);bm.free();result.data.update()
 for o in [shell,patch]:bpy.data.objects.remove(o,do_unlink=True)
 return result,{'sourceFile':str(source.relative_to(ROOT)),'sourceOriginM':list(origin),'uniformXYZScale':[1,1,1],'rigidRotation3x3':[list(r)for r in rotation],'siteFrame3x3':[list(r)for r in frame],'nativeTrianglesCroppedNotEnvelope':True,'nativeCropWidthM':width,'nativeCropHeightM':height,'rigidWallDepthTranslationM':offset,'maximumBoundaryReturnDepthM':max_bridge,'boundaryParameters':len(params),'siteStationM':station,'side':side,'polygon':outline.tolist(),'sourceTriangulatedFaces':native_crop_triangles,'completeCaveTriangles':len(faces),'method':'True native triangles, rigid uniform transform, irregular cut, union-parameter boundary retopology. No Boolean/noise/front-envelope/anisotropic normalization.'}
