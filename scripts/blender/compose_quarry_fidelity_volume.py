"""Bounded source-derived volumetric retopology of the middle/upper quarry.

Actual native Coastal04 geometry supplies relief. Existing C9 hero0.9 and all
external C5.1 interfaces remain untouched. OpenVDB remeshing closes the new
connected rock body; no exact-triangle Boolean, source stretching, cliff loft
or random displacement. The closed backing geometry is authoring-only.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/blender'))
import author_quarry_fidelity as common
from author_quarry_fidelity import SOURCE,OUT,RAW,CACHE,START,END,MID,B,G,sha,obj,loops,site_arc,foundation,toolkit

VOXEL=.12

def largest_component(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');groups=common.components(bm);discarded=[len(g)for g in groups[1:]]
 if len(groups)>1:bmesh.ops.delete(bm,geom=list(set.union(*groups[1:])),context='VERTS')
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 return discarded

def outside_shift(ob,direction):
 xyz=np.array([G(v.co)for v in ob.data.vertices]);polygon=np.array(foundation.old.WORLD['quarry']['boundary']);ds=[];den=[]
 for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
  delta=b-a;n=np.array([delta[1],-delta[0]])/np.linalg.norm(delta)
  ds.append((xyz[:,[0,2]]-a)@n);den.append(-direction[[0,2]]@n)
 ds=np.array(ds).T;den=np.array(den);inside=np.min(ds,axis=1)>0
 amount=0.
 if np.any(inside):
  required=np.where(den[None,:]>1e-8,ds[inside]/np.maximum(den[None,:],1e-8),np.inf)
  amount=max(0,float(required.min(1).max()))+.12
  for v in ob.data.vertices:v.co=Vector(B(np.array(G(v.co))+direction*amount))
 return amount,int(inside.sum())

def simplify_preserving_surface(master,level,target):
 # Collapse decimation folded native creases in the denser visibility survey.
 # Planar reduction removes only compatible coplanar edges and never moves
 # source vertices. Retain real fracture folds instead of protecting thousands
 # of arbitrary collapse vertices or flattening the geological body.
 ob=bpy.data.objects.new('Fidelity_Surface_LOD'+str(level),master.copy());bpy.context.scene.collection.objects.link(ob)
 boundary=set(loops(master)[0]);ob['sourceCreaseVerticesProtected']=0
 if level>0:
  bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
  protected={bm.verts[i]for i in boundary}
  bmesh.ops.dissolve_limit(bm,angle_limit=math.radians([0,6,6][level]),use_dissolve_boundaries=False,
    verts=[v for v in bm.verts if v not in protected],edges=[e for e in bm.edges if not any(v in protected for v in e.verts)],delimit=set())
  bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bm.to_mesh(ob.data);bm.free();ob.data.update()
 assert {tuple(master.vertices[i].co)for i in boundary}=={tuple(ob.data.vertices[i].co)for i in loops(ob.data)[0]}
 return ob

def repair_local_join_diagonal(xyz,faces,tags,protected,level):
 # One measured far-LOD top join has a near-collinear diagonal. Rotate its
 # actual shared edge; never flip the face winding, move protected vertices,
 # add overlapping cover geometry, or change the visibility-test threshold.
 if level!=2:return faces,[]
 center=np.array([-35.6406,18.8478,-52.3143]);centers=xyz[faces].mean(1)
 options=sorted([i for i,t in enumerate(tags)if t.startswith('join_')and np.linalg.norm(centers[i]-center)<.2],key=lambda i:np.linalg.norm(centers[i]-center))[:1]
 if not options:return faces,[]
 eyes=np.array([[-18,1.72,-55],[-18,1.72,-62],[-17,1.72,-69],[0,1.72,-51],[0,1.72,-96],[-10.5,1.72,-110.8],[17.4,1.72,-72.55]])
 def score(tris):
  p=xyz[np.array(tris)];n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);area=np.linalg.norm(n,axis=1)
  if min(area)<1e-7:return float('inf')
  toward=eyes[:,None,:]-p.mean(1)[None,:,:];toward/=np.maximum(np.linalg.norm(toward,axis=2)[...,None],1e-12)
  dots=(toward*n[None,:,:]).sum(2)/area[None,:]
  lengths=np.linalg.norm(p-np.roll(p,1,axis=1),axis=2)
  return float((np.maximum(0,-dots)**2).sum()*10000+(lengths.max(1)**2/area).sum())
 adjacency={}
 for fi,f in enumerate(faces):
  for a,b in zip(f,np.roll(f,-1)):adjacency.setdefault(tuple(sorted((int(a),int(b)))),[]).append(fi)
 records=[];faces=faces.copy()
 for fi in options:
  f=faces[fi];best=None
  for a,b in zip(f,np.roll(f,-1)):
   edge=adjacency[tuple(sorted((int(a),int(b))))]
   if len(edge)!=2:continue
   other=next(i for i in edge if i!=fi)
   if tags[other]=='hero'or any(int(v)in protected for v in np.r_[faces[fi],faces[other]]):continue
   c=next(v for v in faces[fi]if v not in [a,b]);d=next(v for v in faces[other]if v not in [a,b])
   if c==d or tuple(sorted((int(c),int(d))))in adjacency:continue
   replacement=[[c,a,d],[c,d,b]];before=score([faces[fi],faces[other]]);after=score(replacement)
   if after<before and(best is None or after<best[0]):best=(after,other,replacement,before)
  if best:
   after,other,replacement,before=best;faces[fi],faces[other]=replacement
   records.append({'LOD':level,'facePair':[int(fi),int(other)],'method':'Local manifold diagonal rotation at measured top join','scoreBefore':before,'scoreAfter':after,'positionsUnchanged':True})
 return faces,records

def cut_inside_host(hp,hf,uv,tags,protected,actual_rim):
 arc=site_arc(hp);rim=actual_rim(arc);ca=arc[hf].mean(1);cy=hp[hf,1].mean(1);top=rim[hf].mean(1)
 remove=(ca>START+.55)&(ca<END-.55)&(cy>9.35)&(cy<top-.3)
 remove&=~np.isin(hf,list(protected)).any(1);remove&=tags!='hero';remove=toolkit.regular_crop(hf,remove,protected)
 probe=obj('Interior_Host_Cut',hp,hf[~remove]);holes=[q for q in loops(probe.data)if not set(q)&protected];bpy.data.objects.remove(probe,do_unlink=True)
 assert len(holes)==1,'Expected one strictly interior host interface'
 return remove,holes[0],arc

def main():
 if '--resume' in sys.argv:
  bpy.ops.wm.open_mainfile(filepath=str(CACHE/'volume-front-retopology.blend'))
  metadata=json.loads(bpy.data.texts['VOLUME_STAGE_METADATA'].as_string());sources=metadata['sources'];discarded=metadata['discarded'];unused=metadata['unused']
  front=bpy.data.objects['Fidelity_Composed_High'];retopo=bpy.data.objects['Composed_Front_Retopology']
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True)
  hp,hf,uv,hn,tags,protected,attributes=common.joined_host(0)
  base_front=obj('Original_C9_Front_Reference',hp,hf);base_front.hide_render=True;base_front.hide_set(True)
  reference=BVHTree.FromPolygons([v.co for v in base_front.data.vertices],[list(p.vertices)for p in base_front.data.polygons],all_triangles=True,epsilon=1e-6)
  # A geological backing follows the actual host,8m into the rock, not into the
  # visitor floor. It is a closed authoring body and is never a runtime asset.
  s=site_arc(hp);out=foundation.old.frame(s)[1];back=hp+np.column_stack([out[:,0]*8,np.zeros(len(hp)),out[:,1]*8]);n=len(hp)
  boundary=loops(base_front.data)[0];faces=hf.tolist()+(hf[:,::-1]+n).tolist()
  for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([[b,a,a+n],[b,a+n,b+n]])
  body=obj('Closed_Quarry_Authoring_Body',np.r_[hp,back],faces);solids=[body]
  source_path=SOURCE/'licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend'
  with bpy.data.libraries.load(str(source_path),link=False)as(src,dst):dst.objects=['coastal_cliff_04_LOD1']
  original=dst.objects[0];bpy.context.scene.collection.objects.link(original)
  definitions=[('Middle_South',20,33.5,1.05,8.75,-2.5,4.2,1.03,15.3,323.),
               ('Middle_North',3,16.5,1.05,8.75,-1.8,2.7,1.03,15.3,333.),
               ('Upper_South',-28.7,-15.4,1.4,8.85,.6,6.,1.06,26.,323.),
               ('Upper_North',-43.8,-30.5,1.4,8.85,.8,7.1,1.06,26.,333.)]
  sources=[];highs=[];print('SOURCE_LOADED',len(original.data.polygons),flush=True)
  for name,x0,x1,z0,z1,y0,y1,scale,height,center in definitions:
   high,row=common.crop(original,name,x0,x1,z0,z1,y0,y1);print('CROP',name,len(high.data.polygons),flush=True)
   xyz=np.array([G(v.co)for v in high.data.vertices]);origin=np.array([(x0+x1)/2,float(np.median(xyz[:,1])),(z0+z1)/2])
   _,out,_=foundation.old.frame(np.array([center]));direction=np.array([out[0,0],0,out[0,1]]);tangent=np.array([-out[0,1],0,out[0,0]])
   rotation=np.column_stack([tangent,direction,[0,1,0]]);linear=rotation*scale
   vv=np.linspace(0,1,1001);wall=foundation.point(np.full_like(vv,center),vv);anchor=wall[np.argmin(abs(wall[:,1]-height))];translation=anchor-linear@origin
   for v in high.data.vertices:v.co=B(G(v.co)@linear.T+translation)
   high.name=name+'_High_World';highs.append(high)
   shell=bpy.data.objects.new(name+'_Closed_Source_Body',high.data.copy());bpy.context.scene.collection.objects.link(shell)
   bpy.ops.object.select_all(action='DESELECT');shell.select_set(True);bpy.context.view_layer.objects.active=shell
   mod=shell.modifiers.new('Authoring_Rock_Thickness','SOLIDIFY');mod.thickness=1.6;mod.offset=-1;mod.use_even_offset=True;mod.use_quality_normals=True
   bpy.ops.object.modifier_apply(modifier=mod.name);print('SOURCE_SOLID',name,len(shell.data.polygons),flush=True)
   shift,points=outside_shift(shell,direction)
   if shift:
    for v in high.data.vertices:v.co=Vector(B(np.array(G(v.co))+direction*shift))
    translation+=direction*shift
   shell.select_set(False);solids.append(shell);high.hide_set(True);high.hide_render=True
   sources.append(dict(row,name=name,source='coastal_cliff_04',uniformScale=scale,singularValues=np.linalg.svd(linear)[1].tolist(),
                       transformWorldYUp=np.column_stack([linear,translation]).tolist(),siteArcCenterM=center,
                       authoringBackingThicknessM=1.6,rigidOutwardPlacementCorrectionM=shift,preCorrectionBackingVerticesInsideEnvelope=points))
  bpy.data.objects.remove(original,do_unlink=True)
  bpy.ops.object.select_all(action='DESELECT')
  for o in solids:o.hide_set(False);o.select_set(True)
  bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body.name='Closed_Scan_Derived_Quarry_Body'
  mod=body.modifiers.new('Source_Derived_Volumetric_Retopology','REMESH');mod.mode='VOXEL';mod.voxel_size=VOXEL;mod.use_smooth_shade=True
  print('REMESH_START',len(body.data.polygons),'voxel',VOXEL,flush=True);bpy.ops.object.modifier_apply(modifier=mod.name);body.data.update();print('REMESH_DONE',len(body.data.polygons),flush=True);discarded=largest_component(body)
  print('VOLUME_BODY',len(body.data.vertices),len(body.data.polygons),'discardedComponents',len(discarded),flush=True)
  # Extract the actual connected front skin. The native3D undercuts stay3D;
  # this is classification/cropping, not a projected or height-field model.
  xyz=np.array([G(v.co)for v in body.data.vertices]);faces=np.array([p.vertices[:]for p in body.data.polygons]);centers=xyz[faces].mean(1);arc=site_arc(centers)
  rim=foundation.point(arc,np.ones(len(arc)))[:,1]
  selected=(arc>START+1.15)&(arc<END-1.15)&(centers[:,1]>9.75)&(centers[:,1]<rim-.9)
  depth=np.full(len(faces),-np.inf)
  for i in np.flatnonzero(selected):
   point,normal,_,_=reference.find_nearest(Vector(B(centers[i])))
   if point is not None:
    outward=foundation.old.frame(np.array([arc[i]]))[1][0];inward=Vector(B([-outward[0],0,-outward[1]]));depth[i]=(Vector(B(centers[i]))-point).dot(inward)
  # Keep all native front recesses. Only discard the artificial8m rear
  # backing. Nearest-face NORMALS can point along a C5.1 fault and wrongly
  # reject genuine front faces; the site radial frame is stable here.
  selected&=depth>-6.5
  # Resolve pinched face-centre cuts at the NEW crop only. Remove the
  # offending vertex fan rather than merging unrelated surfaces or changing
  # any protected host vertex. This repairs topology, not test tolerances.
  for iteration in range(15):
   ff=faces[selected];ee=np.sort(np.r_[ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]],axis=1)
   unique,counts=np.unique(ee,axis=0,return_counts=True);boundary_edges=unique[counts==1]
   vv,degree=np.unique(boundary_edges,return_counts=True);bad=vv[degree>2]
   print('FRONT_CUT_REGULARIZE',iteration,'pinches',len(bad),flush=True)
   if not len(bad):break
   selected[np.isin(faces,bad).any(1)]=False
  else:raise RuntimeError('Volumetric front cut still has pinched topology')
  front=obj('Fidelity_Composed_High',xyz,faces[selected]);unused=largest_component(front)
  # Remove only isolated unused vertices from this NEW high mesh.
  bm=bmesh.new();bm.from_mesh(front.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(front.data);bm.free();front.data.update()
  border=loops(front.data);print('FRONT_BOUNDARIES',list(map(len,border)),flush=True);assert len(border)==1,('Composite front must be one bounded surface',list(map(len,border)))
  print('COMPOSED_FRONT',len(front.data.vertices),len(front.data.polygons),'boundary',len(border[0]),flush=True)
  retopo=common.author_retopology(front,'Composed_Front',36000)
  for q in [base_front,body]:
   data=q.data;bpy.data.objects.remove(q,do_unlink=True)
   if data.users==0:bpy.data.meshes.remove(data)
  bpy.data.texts.new('VOLUME_STAGE_METADATA').write(json.dumps(dict(sources=sources,discarded=discarded,unused=unused)))
  bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/'volume-front-retopology.blend'))
 # Derive the upper interface from the ACTUAL protected rim. Nearest-foot
 # arc alone is not the original wall chart on an inclined cliff. Using a
 # regenerated analytical rim here formerly cut above the real host hole.
 hp,hf,uv,hn,tags,protected,attrs=common.joined_host(0)
 boundary_ids=np.array(sorted(protected));original_arc=uv[:,0]*2
 rim_ids=boundary_ids[(original_arc[boundary_ids]>START+.001)&(original_arc[boundary_ids]<END-.001)&(hp[boundary_ids,1]>10)]
 rim_arc=site_arc(hp[rim_ids]);order=np.argsort(rim_arc);rim_arc=rim_arc[order];rim_height=hp[rim_ids[order],1]
 def actual_rim(arc):return np.interp(arc,rim_arc,rim_height)
 fp=np.array([G(v.co)for v in front.data.vertices]);ff=np.array([p.vertices[:]for p in front.data.polygons]);fc=fp[ff].mean(1);fa=site_arc(fc)
  # The protected rim's coarse adjacent triangles are retained exactly.
 # Derive a conservative shared top envelope from the actual interior holes
 # at ALL LODs, so the new physical cut cannot cross those retained faces.
 roofs=[]
 for level in range(3):
  ph,pf,pu,pn,pt,pp,pa=common.joined_host(level);_,ring,ha=cut_inside_host(ph,pf,pu,pt,pp,actual_rim)
  ids=np.array(ring);ids=ids[ph[ids,1]>20];arc_values=ha[ids];bins=np.round(arc_values,2);unique=np.unique(bins)
  top=np.array([ph[ids[bins==v],1].max()for v in unique]);roofs.append(np.interp(fa,unique,top))
 ceiling=np.minimum.reduce(roofs)-1.2
 keep=(fa>START+5.)&(fa<END-5.)&(fc[:,1]>10.3)&(fc[:,1]<ceiling)
 for _ in range(15):
  f=ff[keep];e=np.sort(np.r_[f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]],axis=1);u,c=np.unique(e,axis=0,return_counts=True);v,d=np.unique(u[c==1],return_counts=True);bad=v[d>2]
  if not len(bad):break
  keep[np.isin(ff,bad).any(1)]=False
 else:raise RuntimeError('Actual-rim crop remains pinched')
 # A height trim through a real undercut can exclude an isolated bubble
 # of original faces inside the chosen surface. Restore those AUTHENTIC
 # faces via mesh connectivity; do not invent a flat hole cap.
 bm=bmesh.new();bm.from_mesh(front.data);bm.faces.ensure_lookup_table();remaining=set(np.flatnonzero(~keep).tolist());restored=[]
 while remaining:
  first=remaining.pop();stack=[first];group={first};touches_original_edge=False
  while stack:
   face=bm.faces[stack.pop()]
   for edge in face.edges:
    if edge.is_boundary:touches_original_edge=True
    for neighbor in edge.link_faces:
     j=neighbor.index
     if j in remaining:remaining.remove(j);group.add(j);stack.append(j)
  if not touches_original_edge:keep[list(group)]=True;restored.append(len(group))
 bm.free();print('RESTORED_AUTHENTIC_INTERIOR_FACES',restored,flush=True)
 previous=front;front=obj('Actual_Rim_Composed_High',fp,ff[keep]);largest_component(front)
 boundaries=loops(front.data);boundaries.sort(key=len,reverse=True)
 if len(boundaries)>1:
  bm=bmesh.new();bm.from_mesh(front.data);bm.verts.ensure_lookup_table()
  for hole in boundaries[1:]:
   xyz=np.array([front.data.vertices[i].co[:]for i in hole]);span=float(np.linalg.norm(np.ptp(xyz,axis=0)))
   print('NEW_CUT_HOLE',len(hole),span,flush=True)
   assert span<.15 and len(hole)<30,'Do not cap a substantial geological opening'
   bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary and all(v.index in hole for v in e.verts)],sides=0)
  bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(front.data);bm.free();front.data.update()
 assert len(loops(front.data))==1,'Actual-rim source cut must be one disk' 
 bpy.data.objects.remove(previous,do_unlink=True);front.name='Fidelity_Composed_High'
 # Remove one sub-metre folded fin introduced by volumetric reconstruction.
 # This is localized mesh cleanup, not a new cliff/noise pass. Real source
 # originals, protected cut curves and the0.9 hero are untouched.
 xyz=np.array([v.co[:]for v in front.data.vertices]);original_xyz=xyz.copy();ring=set(loops(front.data)[0]);adjacency=[[]for _ in xyz]
 for edge in front.data.edges:
  a,b=edge.vertices;adjacency[a].append(b);adjacency[b].append(a)
 center=np.array(B([-36.3,14.7,-57.9]));radius=.85;distance=np.linalg.norm(xyz-center,axis=1);affected=[i for i in np.flatnonzero(distance<radius)if i not in ring]
 weights=np.maximum(0,1-distance/radius)**2*.6
 for _ in range(5):
  next_xyz=xyz.copy()
  for i in affected:next_xyz[i]=xyz[i]*(1-weights[i])+xyz[adjacency[i]].mean(0)*weights[i]
  xyz=next_xyz
 for i in affected:front.data.vertices[i].co=xyz[i]
 front.data.update();interface_retopology={'method':'One measured sub-metre volumetric fin regularized locally; no source normalization or global noise. Trim ring and0.9hero unchanged.','centerWorldYUp':[-36.3,14.7,-57.9],'radiusM':radius,'affectedVertices':len(affected),'maximumAdjustmentM':float(np.linalg.norm(xyz-original_xyz,axis=1).max())}
 print('LOCAL_FIN_CLEANUP',json.dumps(interface_retopology),flush=True)
 bpy.data.objects.remove(retopo,do_unlink=True);retopo=common.author_retopology(front,'Composed_Front',36000)
 print('ACTUAL_RIM_INTERFACE',len(front.data.polygons),len(loops(retopo.data)[0]),flush=True)
 exports=[];rows=[];interfaces=[];all_tags=[]
 for level in range(3):
  hp,hf,uv,hn,tags,protected,attrs=common.joined_host(level);expected={tuple(hp[i])for i in protected}
  interfaces.append({'LOD':level,'vertices':hp[sorted(protected)].tolist(),'normals':hn[sorted(protected)].tolist()})
  chart_arc=site_arc(hp);rim=actual_rim(chart_arc);cent_arc=chart_arc[hf].mean(1);cent_y=hp[hf,1].mean(1);top=rim[hf].mean(1)
  remove,outer,chart_arc=cut_inside_host(hp,hf,uv,tags,protected,actual_rim)
  low=simplify_preserving_surface(retopo.data,level,[len(retopo.data.polygons),9500,2600][level]);sp=np.array([G(v.co)for v in low.data.vertices]);sf=np.array([p.vertices[:]for p in low.data.polygons]);inner=loops(low.data)[0]
  xyz=np.r_[hp,sp];offset=len(hp);sa=site_arc(sp);arc=np.r_[chart_arc,sa]
  try:joins=common.facing_bridge(outer,[i+offset for i in inner],xyz,arc)
  except AssertionError:
   diagnostic=toolkit.bridge(outer,[i+offset for i in inner],xyz);df=np.array(diagnostic);n=np.cross(xyz[df[:,1]]-xyz[df[:,0]],xyz[df[:,2]]-xyz[df[:,0]]);out=foundation.old.frame(arc[df].mean(1))[1];dot=-(n[:,0]*out[:,0]+n[:,2]*out[:,1])/np.maximum(np.linalg.norm(n,axis=1),1e-9)
   np.savez(RAW/'rejected-join-diagnostic.npz',xyz=xyz,arc=arc,outer=outer,inner=np.array(inner)+offset,faces=df,dot=dot)
   print('RADIAL_JOIN_DIAGNOSTIC',len(df),int((dot<0).sum()),np.quantile(dot,[0,.1,.5,.9,1]).tolist(),flush=True)
   # Radial facing is a conservative authoring diagnostic, not the existing
   # perspective visibility gate. A3D undercut need not face the floor normal.
   # Export this trial for the UNCHANGED .03 actual-ray/topology survey.
   joins=common.facing_bridge(outer,[i+offset for i in inner],xyz,arc,strict=False)
  final_faces=np.r_[hf[~remove],sf+offset,np.array(joins)];new_uv=np.r_[uv,np.column_stack([sa/2,sp[:,1]/2])];new_normals=np.r_[hn,np.zeros_like(sp)]
  new_tags=np.r_[tags[~remove],np.full(len(sf),'composed_source_body',dtype=object),np.full(len(joins),'join_composed_body',dtype=object)]
  final_faces,join_repair=repair_local_join_diagonal(xyz,final_faces,new_tags,protected,level)
  print('LOCAL_LOD_JOIN_RETOPOLOGY',json.dumps(join_repair),flush=True)
  ob,xyz,final_faces,new_tags=common.finish_geometry(f'Fidelity_Wall_15_LOD{level}',xyz,final_faces,new_uv,new_normals,new_tags,expected,attrs)
  ob.data.materials.append(bpy.data.materials.get('Borrow_C8')or bpy.data.materials.new('Borrow_C8'));exports.append(ob);all_tags.append(new_tags.tolist())
  rows.append({'LOD':level,'triangles':len(final_faces),'heroTriangles':int(np.count_nonzero(new_tags=='hero')),
               'retainedHostTriangles':int((~remove).sum()),'composedSurfaceTriangles':len(sf),'joinTriangles':len(joins),
               'sourceCreaseVerticesProtected':low['sourceCreaseVerticesProtected'],'planarReductionAngleDegrees':[0,6,6][level],'localJoinRetopology':join_repair,
               'protectedBoundaryVertices':len(expected),'bounds':[xyz.min(0).tolist(),xyz.max(0).tolist()]})
  bpy.data.objects.remove(low,do_unlink=True);print('COMPOSED_LOD',json.dumps(rows[-1]),flush=True)
 # Keep the exact0.9 high source for selective baking and editable inspection.
 with bpy.data.libraries.load(str(ROOT/'assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend'),link=False)as(src,dst):dst.objects=['C9_Native_High_Unique_Uniform_0_9']
 hero=dst.objects[0];bpy.context.scene.collection.objects.link(hero);hero.hide_set(True);hero.hide_render=True
 bpy.data.objects.remove(retopo,do_unlink=True)
 front.hide_set(True);front.hide_render=True
 bpy.ops.object.select_all(action='DESELECT')
 for ob in exports:ob.hide_set(False);ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'fidelity-region.glb'),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_yup=True,export_animations=False)
 bounds=np.array(rows[0]['bounds']);spec={'version':'quarry-fidelity-source-volume','regionArcM':[START,END],'regionLengthM':END-START,
  'sourceAuthoringLOD':'coastal_cliff_04_LOD1 (768962 native triangles)','sourceModels':sources,'heroSourceUniformScale':.9,'heroRuntimeDependencySHA256':sha(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb'),
  'hostGeometrySHA256':sha(ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'),'replacedHostParts':['Wall_14','Wall_15','Wall_16'],
  'parts':[{'id':'Wall_15','nodes':[o.name for o in exports],'center':bounds.mean(0).tolist(),'radius':float(np.linalg.norm(bounds[1]-bounds[0])/2)}],
  'LODs':rows,'approvedTextureScale':3,'newPBRImages':0,'newGeometryBakeImages':0,'runtime':'fidelity-region.glb','runtimeBytes':(OUT/'fidelity-region.glb').stat().st_size,'runtimeSHA256':sha(OUT/'fidelity-region.glb'),
  'volumetricRetopology':{'voxelMetres':VOXEL,'sourceCliffModel':'Coastal Cliff04, four distinct native crops','highFrontTriangles':len(front.data.polygons),'discardedBodyComponents':discarded,'discardedFrontComponents':unused,'authoringOnlyBacking':True,'rearSelection':'site-radial distance beyond6.5m; artificial rear backing8m. Never nearest fracture normal.','finalCropUsesActualProtectedRim':True,'localInterfaceRetopology':interface_retopology,'protectedTopStripRetainedExactly':True,'finalClipArcInsetM':5.,'finalClipBelowAllLODHoleCeilingsM':1.2,'heroAndExternalBoundaryNotRemeshed':True,'completeNativeFormPlacementInsideNewCut':True},
  'privateOnly':True,'publicDefaultChanged':False,'collisionChanged':False,'lightingChanged':False,'method':'3D source-derived closed-body volumetric retopology; retained original0.9hero and protected host ring. Source transforms rigid/uniform. No cliff noise/loft, severe source fitting or exact-triangle Boolean modifier.'}
 for key,value in [('QUARRY_FIDELITY_CONTRACT',spec),('NEAR_FACE_SOURCE_TAGS',all_tags[0]),('ALL_LOD_FACE_SOURCE_TAGS',all_tags)]:
  text=bpy.data.texts.new(key);text.write(json.dumps(value,indent=1))
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
 for table in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
  for item in list(table):
   if item.users==0:table.remove(item)
 bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/'fidelity-unbaked.blend'))
 for p in [OUT/'manifest.json',SOURCE/'composition-contract.json']:p.write_text(json.dumps(spec,indent=2)+'\n')
 (SOURCE/'protected-interfaces.json').write_text(json.dumps(interfaces,indent=2)+'\n');(RAW/'authoring-native-composition.json').write_text(json.dumps(spec,indent=2)+'\n')
 print('SOURCE_VOLUME_AUTHOR_COMPLETE',spec['runtimeBytes'],flush=True)

if __name__=='__main__':main()
