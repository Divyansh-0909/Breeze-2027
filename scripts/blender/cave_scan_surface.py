"""Editable scan-derived retopology for the protected cave, in real metres.

This is not a scanned cave. A 1:1 metric crop of genuine CC0 cliff geometry
supplies geological relief. We remove the capture's broad coastal inclination
before using that relief as a sculpt source on the cave body. No random noise,
5x chart fit, Boolean union or runtime displacement. Re-entrant captured
surfaces cannot survive this front-envelope transfer; that is an art limitation.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def make_source(ROOT):
 source=ROOT/'assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend'
 with bpy.data.libraries.load(str(source),link=False)as(a,b):
  b.objects=['coastal_cliff_01_LOD2']
 original=b.objects[0];bpy.context.scene.collection.objects.link(original)
 original.name='CC0_Coastal01_Native_Tunnel_Sculpt_Source'
 original.hide_render=True;original.hide_set(True)
 verts=[v.co for v in original.data.vertices]
 bv=BVHTree.FromPolygons(verts,[list(p.vertices)for p in original.data.polygons],all_triangles=True)
 # 1 sample metre = 1 source metre, both chart axes. The two sides use
 # different adjacent crops, not an enlarged copy of a small source mesh.
 xs=np.arange(-29.,30.0001,.15);zs=np.arange(.15,9.3001,.15)
 depth=np.empty((len(zs),len(xs)));missing=[]
 for j,z in enumerate(zs):
  for i,x in enumerate(xs):
   p,_,_,_=bv.ray_cast(Vector((x,-20,z)),Vector((0,1,0)),40)
   depth[j,i]=p.y if p is not None else np.nan
   if p is None:missing.append((i,j))
 initial_missing=len(missing)
 # Close tiny sampling holes only; broad missing scan areas are rejected.
 for iteration in range(20):
  m=np.isnan(depth)
  if not np.any(m):break
  v=np.pad(np.nan_to_num(depth),1,mode='edge');c=np.pad(np.isfinite(depth).astype(float),1,mode='edge')
  total=np.zeros_like(depth);count=np.zeros_like(depth)
  for y,x in [(0,1),(1,0),(2,1),(1,2)]:
   total+=v[y:y+depth.shape[0],x:x+depth.shape[1]];count+=c[y:y+depth.shape[0],x:x+depth.shape[1]]
  keep=m&(count>0);depth[keep]=(total/np.maximum(count,1))[keep]
 assert np.isfinite(depth).all(),'Unsuitable source crop: do not invent missing cliff geometry'
 # Subtract only the broad captured coastal slope. Actual local depth remains
 # measured in metres, never normalized to wall width or height.
 baseline=depth.copy();sigma=.85;r=int(math.ceil(sigma/.15*3))
 u=np.arange(-r,r+1)*.15;k=np.exp(-.5*(u/sigma)**2);k/=k.sum()
 for axis in [0,1]:baseline=np.apply_along_axis(lambda q:np.convolve(np.pad(q,r,mode='edge'),k,mode='valid'),axis,baseline)
 relief=depth-baseline
 def sample(x,z):
  ix=float(np.clip((x-xs[0])/.15,0,len(xs)-1.000001));iz=float(np.clip((z-zs[0])/.15,0,len(zs)-1.000001));i=int(ix);j=int(iz);u=ix-i;v=iz-j
  return float((relief[j,i]*(1-u)+relief[j,i+1]*u)*(1-v)+(relief[j+1,i]*(1-u)+relief[j+1,i+1]*u)*v)
 info={'sourceFile':str(source.relative_to(ROOT)),'sourceSHA256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'license':'CC0 1.0','page':'https://polyhaven.com/a/coastal_cliff_01','nativeDimensionsM':[91.97974,10.95954,10.32364],'sampleStepM':.15,'samplingAxesScale':[1,1],'depthNormalization':False,'coastalSlopeRemovalGaussianSigmaM':sigma,'missingSamplesLocallyInterpolated':initial_missing,'sampleCount':depth.size,'physicalReliefQuantilesM':np.quantile(relief,[0,.01,.5,.99,1]).tolist(),'limitations':'Front-envelope retopology loses hidden scanned overhangs; this is source-derived cave sculpting, not a cave photogrammetry scan.'}
 return sample,info

def passage(ROOT,W,center,mesh,source_points,working,path):
 sample,info=make_source(ROOT)
 profile=np.array([[-3.6,-.16],[-3.52,1.3],[-3.38,2.65],[-2.9,3.7],[-1.8,4.6],[-.35,5.05],[1.2,4.8],[2.5,4.05],[3.35,2.7],[3.5,1.2],[3.6,-.16]])
 arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(profile,axis=0),axis=1))];total=arc[-1];arc/=total
 old=np.array(W['tunnel']['profile']);oa=np.r_[0,np.cumsum(np.linalg.norm(np.diff(old,axis=0),axis=1))];oa/=oa[-1]
 stations=np.array([0,4,9,14,19,24,29,34,38,42]);left=np.array([0,.12,.3,.08,-.05,.21,.34,.13,.08,0]);right=np.array([0,.05,-.12,.18,.33,.09,-.04,.27,.15,0]);top=np.array([0,.04,-.15,.09,.23,.02,-.08,.12,.03,0])
 constraints={'walkClearanceVerticesMoved':0,'overburdenClearanceVerticesMoved':0}
 def smooth(t):t=float(np.clip(t,0,1));return t*t*(3-2*t)
 def point(y,s,count_constraints=False):
  p=np.array([np.interp(s,arc,profile[:,k])for k in [0,1]])
  # Real-metre sampling continues around each half of the vault. Opposite
  # walls select different source positions; no random per-face distribution.
  az=s*total;z=.15+min(az,total-az)
  d0=sample(y-28,z);d1=sample(y-14,z);blend=smooth((s-.43)/.14);d=d0*(1-blend)+d1*blend
  # A continuously varying radial frame avoids the folded slivers created by
  # a discontinuous face-normal offset at a profile corner. The source relief
  # still remains in real metres; no normal inversion is papered over.
  out=p-np.array([0.,1.9]);out/=np.linalg.norm(out)
  foot=smooth(p[1]/.8);p+=out*d*foot
  p[0]+=np.interp(y,stations,left if p[0]<0 else right)*(-1 if p[0]<0 else 1);p[1]+=np.interp(y,stations,top)*foot
  if .05<p[1]<2.7 and abs(p[0])<2.55:
   p[0]=math.copysign(2.55,p[0]);constraints['walkClearanceVerticesMoved']+=int(count_constraints)
  if p[1]>6.65:
   p[1]=6.65;constraints['overburdenClearanceVerticesMoved']+=int(count_constraints)
  # Exact established exit ring, with a 3m geological return before the rim.
  t=smooth((y-39)/3)
  q=np.array([np.interp(s,oa,old[:,k])for k in [0,1]])
  p=p*(1-t)+q*t
  return np.array([center(y)+p[0],y,p[1]])
 # Every old exit-profile corner and every source mouth parameter is retained.
 # Shared ring vertices are frozen identically in every adjacent part/LOD.
 source_points=np.array(source_points)
 ss=np.r_[0,np.cumsum(np.linalg.norm(np.diff(source_points,axis=0),axis=1))];ss/=ss[-1]
 common=np.unique(np.r_[np.linspace(0,1,81),arc,oa,ss])
 # Subdivide the actual scan cut edge at every shared parameter. This makes
 # the mouth, throat and passage one position-weldable boundary, not T-joints.
 bm=bmesh.new();bm.from_mesh(working.data);bm.verts.ensure_lookup_table()
 oldverts=[bm.verts[int(i)]for i in path]
 for j,(a,b)in enumerate(zip(oldverts[:-1],oldverts[1:])):
  current=a;last=ss[j]
  for u in common[(common>ss[j]+1e-12)&(common<ss[j+1]-1e-12)]:
   edge=bm.edges.get((current,b));assert edge is not None
   _,v=bmesh.utils.edge_split(edge,current,float((u-last)/(ss[j+1]-last)))
   v.co=a.co.lerp(b.co,float((u-ss[j])/(ss[j+1]-ss[j])))
   current=v;last=u
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(working.data);bm.free();working.data.update()
 source_points=np.array([[np.interp(u,ss,source_points[:,k])for k in range(3)]for u in common]);ss=common
 highs=[]
 for j,(a,b)in enumerate([(6.,15.),(15.,24.),(24.,33.),(33.,42.)]):
  yy=np.linspace(a,b,int(math.ceil((b-a)/.18))+1);V=[point(y,s,True).tolist()for y in yy for s in common];F=[];n=len(common)
  for k in range(len(yy)-1):
   for i in range(n-1):
    u=k*n+i;F.extend([[u,u+n,u+n+1],[u,u+n+1,u+1]])
  o=mesh(f'Cave_Passage{j+1}_Authored_High',V,F)
  uv=o.data.uv_layers.new(name='UVMap');repeat=1/json.loads((ROOT/'assets-source/gullyverse/recovered-c8-material/material-manifest.json').read_text())['hostUVUnitMetres']
  for loop in o.data.loops:
   v=loop.vertex_index;uv.data[loop.index].uv=(o.data.vertices[v].co.y*repeat,float(common[v%n])*total*repeat)
  highs.append((f'Passage{j+1}',o,[6400,2900,1500]))
 # Mouth retopology meets the same scan-derived ring; no smooth annular insert.
 V=[];F=[];rings=13
 for j in range(rings):
  t=j/(rings-1)
  for i,p in enumerate(source_points):
   q=point(6,float(ss[i]));v=p*(1-t)+q*t;v[0]+=center(v[1])-((1-t)*center(p[1])+t*center(6))
   # Local scan-derived roughness in the return has full physical depth. Its
   # zero envelope protects both true-source and passage interfaces exactly.
   s=float(ss[i]);p2=np.array([np.interp(s,arc,profile[:,k])for k in [0,1]])
   out=p2-np.array([0.,1.9]);out/=np.linalg.norm(out)
   d=sample(v[1]-21,.15+min(s,1-s)*total)*math.sin(math.pi*t)**2
   v[0]+=out[0]*d;v[2]+=out[1]*d
   if .05<v[2]<2.7 and abs(v[0]-center(v[1]))<2.55:v[0]=center(v[1])+math.copysign(2.55,v[0]-center(v[1]))
   V.append(v.tolist())
 n=len(source_points)
 for j in range(rings-1):
  for i in range(n-1):
   a=j*n+i;F.extend([[a,a+n,a+n+1],[a,a+n+1,a+1]])
 # Selective retopology fairing at the diagnosed left throat fold. It moves
 # only internal vertices in a 1.35m brush; both shared interfaces are pinned.
 # This is a repair of a specific source/return fold, not a whole-rock noise pass.
 grid=np.array(V).reshape(rings,n,3);original_grid=grid.copy()
 brush_center=np.array([-4.50,4.13,1.72])
 for iteration in range(24):
  next_grid=grid.copy()
  for j in range(1,rings-1):
   for i in range(1,n-1):
    weight=math.exp(-float(np.linalg.norm(grid[j,i]-brush_center))**2/(1.35**2))*.55
    if weight<.002:continue
    average=(grid[j-1,i]+grid[j+1,i]+grid[j,i-1]+grid[j,i+1])*.25
    next_grid[j,i]=grid[j,i]*(1-weight)+average*weight
  grid=next_grid
 delta=np.linalg.norm(grid-original_grid,axis=2)
 info['localFoldRepair']={'method':'Constrained local Laplacian retopology fairing, fixed mouth and passage rings','brushCenterBlenderM':brush_center.tolist(),'brushRadiusM':1.35,'iterations':24,'maximumMovementM':float(delta.max()),'movedVertices':int((delta>1e-6).sum())}
 throat=mesh('Cave_Throat_Authored_High',grid.reshape(-1,3).tolist(),F);uv=throat.data.uv_layers.new(name='UVMap')
 for loop in throat.data.loops:
  i=loop.vertex_index%n;uv.data[loop.index].uv=(throat.data.vertices[loop.vertex_index].co.y*repeat,float(ss[i])*total*repeat)
 # Exact piecewise-linear shared throat/passsage interface: the passage first
 # ring must include source s parameters to prevent T-junction silhouette gaps.
 # Return authored data and parameters for the caller's seam validation.
 info.update({'passageLengthM':42,'replacedInteriorM':42,'protectedWalkingHalfWidthPlusRadiusM':2.38,'minimumVisualSideClearanceM':2.55,'ceilingClearanceToTerrainM':.35,'constraints':constraints,'crossSectionProfile':profile.tolist(),'crossSectionArcM':float(total),'partStationsM':[[6,15],[15,24],[24,33],[33,42]],'visibleFixtures':0,'newPBRImages':0,'sharedParameterCount':len(common),'mouthParameterCount':len(ss)})
 # Visual dust/gravel surface only, 12mm above the unchanged authoritative
 # ground. It borrows the existing dry-terrain image owner, not a new map set.
 floor_y=np.unique(np.r_[np.linspace(-4,42,93),0,6,15,24,33,39,42]);FV=[];FF=[];FA=[];laterals=[-1.,-.8,0.,.8,1.]
 for y in floor_y:
  edges=[]
  for s in [0.,1.]:
   p=point(max(6,y),s)
   if y<6:
    width=(4.8*(1-s)+4.5*s)*(1-smooth((y+3)/9))+abs(p[0]-center(6))*smooth((y+3)/9)
    x=center(y)+(-width if s==0 else width)
   else:x=p[0]
   edges.append(x)
  for u in laterals:
   x=edges[0]*(1-(u+1)/2)+edges[1]*(u+1)/2;FV.append([float(x),float(y),.012])
   FA.append(smooth((y+4)/6)*smooth((42-y)/2)*smooth((1-abs(u))/.2))
 for i in range(len(floor_y)-1):
  for j in range(len(laterals)-1):
   a=i*len(laterals)+j;FF.extend([[a,a+1,a+1+len(laterals)],[a,a+1+len(laterals),a+len(laterals)]])
 floor=mesh('Cave_Floor_Authored_High',FV,FF);uv=floor.data.uv_layers.new(name='UVMap')
 for loop in floor.data.loops:
  p=floor.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/5,p.y/5)
 col=floor.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 for i,alpha in enumerate(FA):col.data[i].color=(1,1,1,alpha)
 highs.append(('Floor',floor,[len(FF)]*3))
 info['floorVisualOffsetM']=.012;info['floorCollisionChanged']=False
 return throat,highs,info
