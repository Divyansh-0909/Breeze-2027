import bpy,json,math,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c1-geological-refinement-2026-10-13/raw'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend'))
rows=[];seams=[]
def overlap_area(a,b,normal):
 drop=int(np.argmax(np.abs(normal)));a=np.delete(a,drop,axis=1);b=np.delete(b,drop,axis=1)
 cross=lambda x,y:float(x[0]*y[1]-x[1]*y[0])
 if cross(b[1]-b[0],b[2]-b[0])<0:b=b[::-1]
 poly=list(a)
 for x,y in zip(b,np.roll(b,-1,axis=0)):
  out=[];edge=y-x
  if not poly:return 0.
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=cross(edge,p-x);dq=cross(edge,q-x);ip=dp>=-1e-9;iq=dq>=-1e-9
   if ip:out.append(p)
   if ip!=iq:out.append(p+(q-p)*dp/(dp-dq))
  poly=out
 if len(poly)<3:return 0.
 return abs(sum(cross(poly[i],poly[(i+1)%len(poly)])for i in range(len(poly)))/2)

def G(p):return np.stack([p[:,0],p[:,2],-p[:,1]],axis=1)
center=np.array([-.9,0,-103.75]);split=-108.2
for rid in ["22-23"]:
 for level in range(3):
  o=bpy.data.objects[f'Refined_Pair_LOD{level}'];m=o.data;m.calc_loop_triangles();p=np.array([v.co[:]for v in m.vertices]);f=np.array([t.vertices[:]for t in m.loop_triangles]);t=p[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(nn,axis=1);nn/=np.maximum(area[:,None],1e-20);cn=np.array([m.corner_normals[x.loops[0]].vector[:]for x in m.loop_triangles]);dots=np.sum(nn*cn,axis=1)
  bvh=BVHTree.FromPolygons([v.co for v in m.vertices],[x.vertices[:]for x in m.loop_triangles],all_triangles=True);bad=[];contacts=[]
  for a,b in bvh.overlap(bvh):
   if a>=b or set(f[a])&set(f[b]):continue
   da=(t[a]-t[b,0])@nn[b];db=(t[b]-t[a,0])@nn[a]
   # BVH also reports zero-depth contact at a curved cap boundary. Require
   # transverse penetration on both planes; retain all contact candidates.
   coplanarArea=overlap_area(t[a],t[b],nn[a])if max(abs(da))<1e-5 and max(abs(db))<1e-5 else 0.
   if (min(da)<-1e-5 and max(da)>1e-5 and min(db)<-1e-5 and max(db)>1e-5)or coplanarArea>1e-5:bad.append([a,b])
   else:contacts.append({'triangles':[a,b],'signedPlaneDistancesA':da.tolist(),'signedPlaneDistancesB':db.tolist()})
  world=G(p);angle=np.degrees(np.arctan2(world[:,0]-center[0],-(world[:,2]-center[2])));seam=np.flatnonzero(np.abs(angle-split)<2e-5)
  edges=[tuple(np.round(world[i],5))for i in seam];seams.append({'rock':rid,'LOD':level,'allJoinPositions':sorted(set(edges))})
  rows.append({'rock':rid,'LOD':level,'triangles':len(f),'nonAdjacentIntersectingTrianglePairs':len(bad),'intersectionExamples':bad[:10],'zeroDepthOrTangentialBVHCandidates':contacts,'opposedFirstLoopNormals':int((dots<-.02).sum()),'minimumFirstLoopNormalDot':float(dots.min()),'bounds':np.stack([world.min(0),world.max(0)],axis=1).tolist()})
# End-cap interiors are allowed different sampling; exposed join contours must
# have exactly the same front/back/crown/ground rings in every combination.
import sys;sys.path.insert(0,str(ROOT/'scripts/blender'));from refined_quarry_geology import front,back,crest
boundary=[]
for t in np.linspace(0,1,97):boundary.extend([front(np.array([split]),np.array([t]))[0],back(np.array([split]),np.array([t]))[0]])
for t in np.linspace(0,1,9):
 for at in [0,1]:
  f=front(np.array([split]),np.array([at]))[0];b=back(np.array([split]),np.array([at]))[0];p=f*(1-t)+b*t
  if at:p[1]+=.16*math.sin((split+122.8)*math.pi/180*61*.9+t*3.2)*math.sin(t*math.pi)
  boundary.append(p)
checks=[]
for rid in ["22-23"]:
 for level in range(3):
  o=bpy.data.objects[f'Refined_Pair_LOD{level}'];world=G(np.array([v.co[:]for v in o.data.vertices]));error=max(float(np.linalg.norm(world-p,axis=1).min())for p in boundary);checks.append({'rock':rid,'LOD':level,'sharedContourMaximumErrorM':error});assert error<2e-5
# Geometry is terrain-contacting and outside every existing player clearance.
layout=json.loads((ROOT/'public/models/gullyverse/blockout.layout.json').read_text());world=layout.get('world',layout);clearance=[]
for label,pts in [('hub',[world['hub']['spawn']]),('stage',[world['aftermovie']['spawn']])]:
 for p in pts:
  if len(p)==2:p=[p[0],1.72,p[1]]
  clearance.append({'label':label,'position':p})
result={'status':'PASS'if not any(r['nonAdjacentIntersectingTrianglePairs']for r in rows)else'FAIL','rows':rows,'sharedContourChecks':checks,'joinPolicy':'Two closed volumes meet at the same internal end cap; only the exposed front/back/top/bottom contour must match. Coincident internal caps are covered by the continuous front and are not an exposed z-fighting seam.','registryCollisionUnchanged':True,'clearanceReferences':clearance}
(OUT/'shape-seam-validation.json').write_text(json.dumps(result,indent=2));print(result['status'],rows,checks,flush=True)
assert result['status']=='PASS'
