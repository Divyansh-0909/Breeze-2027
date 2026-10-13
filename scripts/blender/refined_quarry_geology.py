"""Two-section proof, not a perimeter generator. Metres / current world Y-up.

The section's foot is sampled from the CURRENT union of envelopes 22 and 23.
A single swept excavated face crosses their former independent peaks. Shared
faults/strata, crest and metric UVs are evaluated before splitting the volume.
No texture generation, lighting changes or coordinate-registry writes.
"""
import json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SOURCE=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
IDS=[23,22]
CENTER=np.array([-.9,0.,-103.75])
START=-122.8; END=-93.0; SPLIT=-108.2
ROCKS=[r for r in SOURCE['rocks'] if r['id'] in IDS]
PLANES=[]
for r in ROCKS:
 v=np.array(r['vertices']);planes=[]
 for f in r['faces']:
  a,b,c=v[f[:3]];n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
  planes.append((n,float(n@a)))
 PLANES.append(planes)

def direction(angle):
 a=np.radians(angle);return np.stack([np.sin(a),np.zeros_like(a),-np.cos(a)],axis=-1)

def radius_range(angle,y=0.):
 """Actual radial ground cross-section of the selected original envelopes."""
 d=direction(np.asarray(angle));lo=np.full(d.shape[:-1],np.inf);hi=-lo
 for planes in PLANES:
  lower=np.zeros_like(lo);upper=np.full_like(hi,np.inf);valid=np.ones_like(lo,dtype=bool)
  for n,c in planes:
   slope=d@n;rhs=c-n@CENTER-n[1]*y
   valid &= ~((np.abs(slope)<1e-9)&(rhs<0))
   limit=rhs/np.where(np.abs(slope)<1e-9,1,slope)
   upper=np.where(slope>1e-9,np.minimum(upper,limit),upper)
   lower=np.where(slope< -1e-9,np.maximum(lower,limit),lower)
  valid &= lower<=upper
  lo=np.where(valid,np.minimum(lo,lower),lo);hi=np.where(valid,np.maximum(hi,upper),hi)
 return lo,hi

def hermite(x,xs,ys):
 xs=np.array(xs);ys=np.array(ys);sec=np.diff(ys)/np.diff(xs);slopes=np.r_[sec[0],(sec[:-1]+sec[1:])*.5,sec[-1]]
 j=np.clip(np.searchsorted(xs,x)-1,0,len(xs)-2);t=np.clip((x-xs[j])/(xs[j+1]-xs[j]),0,1);h=xs[j+1]-xs[j]
 return (2*t**3-3*t*t+1)*ys[j]+(t**3-2*t*t+t)*h*slopes[j]+(-2*t**3+3*t*t)*ys[j+1]+(t**3-t*t)*h*slopes[j+1]

def along(angle):return (np.asarray(angle)-START)*math.pi/180*61.

def crest(angle):
 # Broad, unequal upper terraces replace the separate preserved pentagon tips.
 # Height stays in the selected pair's established 21--35m distribution.
 h=hermite(angle,[START,-120,-116,-112,-108.2,-103,-98,-95,END],[22.0,23.7,25.9,27.5,29.2,30.1,30.0,27.7,23.8])
 s=along(angle);h+=.23*np.sin(s*1.15)+.12*np.sin(s*2.7+.6)
 for at,width,amount in [(4.2,.5,.55),(11.7,.7,.7),(19.2,.4,.45),(26.8,.6,.6),(31.8,.45,.35)]:h-=amount*np.exp(-((s-at)/width)**4)
 return h

def relief(s,y):
 """Broad exposed faces with bounded interrupted joints, not radial Voronoi pits."""
 s=np.asarray(s);y=np.asarray(y)
 result=.23*np.sin(s*.16+y*.08)+.12*np.sin(s*.38-y*.21)+.08*np.cos(s*.7+y*.27)
 # Unequal bedding planes continue across both nodes, tilt and stop locally.
 for k,(level,slope,width,depth,start,end) in enumerate([(4.7,.09,.20,.27,0,27),(10.1,-.10,.16,.33,7,36),(17.6,.13,.24,.40,0,34),(24.5,-.09,.18,.25,12,36)]):
  path=level+slope*(s-17)+.30*np.sin(s*.24+k)
  finite=np.clip((s-start)/2,0,1)*np.clip((end-s)/2,0,1)
  result+=depth*np.maximum(0,1-np.abs(y-path)/width)*finite
 # Finite, branching joints have tapered ends and unequal directions/depths.
 for k,(offset,tilt,width,depth,low,high) in enumerate([(5.8,.18,.34,.62,1,26),(16.5,-.12,.26,.54,5,32),(28.0,.21,.40,.72,0,22)]):
  path=offset+tilt*y+.27*np.sin(y*.38+k)
  finite=np.clip((y-low)/1.4,0,1)*np.clip((high-y)/2.2,0,1)
  result+=depth*np.maximum(0,1-np.abs(s-path)/width)*finite
 for x,h,tilt,width,depth in [(11,13,.44,.22,.42),(22,20,-.57,.26,.46),(30,7,.65,.23,.31)]:
  joint=s-x-tilt*(y-h);span=np.maximum(0,1-np.abs(y-h)/3.5)
  result+=depth*np.maximum(0,1-np.abs(joint)/width)*span
 # Sparse chips/cavities; no regular diamond-shaped cell partition.
 for x,h,rx,ry,depth in [(3.8,8.1,1.1,.65,.35),(12.8,19.4,1.3,.75,.42),(24.5,4.2,.75,.65,.32),(29.2,24.0,1.3,.9,.37),(18.0,13.6,.85,.45,.30)]:
  dx=(s-x)/rx;dy=(y-h)/ry;outline=np.maximum.reduce([dx+.35*dy,-.85*dx+.35*dy,-.2*dx-.9*dy])
  result+=depth*np.maximum(0,1-outline)*np.clip(1-outline,0,1)
 return result

def front(angle,fraction):
 angle=np.asarray(angle);t=np.asarray(fraction);y=-1.5+(crest(angle)+1.5)*t
 lo,hi=radius_range(angle,0.);assert np.all(np.isfinite(lo)) and np.all(hi-lo>2.0)
 # Keep the ground foot exact, but do not extrude the two source pentagon
 # intersections into a straight vertical crease through the entire wall.
 # A shared broad excavation curve replaces those envelope-derived planes;
 # the finite fracture field remains sharp and independent of this macro form.
 macro=hermite(angle,[START,-120,-116,-112,-108.2,-104,-100,-96,END],[56.38,54.6,52.7,52.45,52.85,51.25,51.15,53.4,55.51])
 weight=np.clip((y-2.4)/3.5,0,1);weight=weight*weight*(3-2*weight);lo=lo*(1-weight)+macro*weight
 # No movement into circulation. The original foot stays in unchanged terrain.
 foot=np.clip((y-.2)/2.0,0,1);foot=foot*foot*(3-2*foot)
 r=lo+foot*(1.35*t+relief(along(angle),y))
 r=np.minimum(r,hi-3.5)
 return CENTER+direction(angle)*r[...,None]+np.stack([np.zeros_like(y),y,np.zeros_like(y)],axis=-1)

def back(angle,fraction):
 angle=np.asarray(angle);t=np.asarray(fraction);lo,hi=radius_range(angle,0.);y=-1.5+(crest(angle)+1.5)*t
 # Full closed mass. Outer radial/ground limits remain the original footprint.
 r=hi-.55*t+.14*np.sin(along(angle)*.38+y*.12)*np.sin(t*math.pi)
 return CENTER+direction(angle)*r[...,None]+np.stack([np.zeros_like(y),y,np.zeros_like(y)],axis=-1)

def reflect(x,lo,hi):
 q=(x-lo)%(2*(hi-lo));return lo+np.where(q<=hi-lo,q,2*(hi-lo)-q)

def triangulate_outline(p):
 """Ear clipping in physical plane; retain collinear boundary samples by fans.
 UV-domain fans are unsafe after deformation into a concave closing outline.
 """
 cross=lambda a,b:a[0]*b[1]-a[1]*b[0]
 signed=sum(cross(a,b)for a,b in zip(p,np.roll(p,-1,axis=0)))
 ring=list(range(len(p))) if signed>0 else list(range(len(p)-1,-1,-1));original=ring.copy()
 changed=True
 while changed and len(ring)>3:
  changed=False
  for j in range(len(ring)):
   a,b,c=[p[ring[k%len(ring)]]for k in [j-1,j,j+1]]
   if abs(cross(b-a,c-b))<1e-8 and np.dot(b-a,c-b)>=0:del ring[j];changed=True;break
 corners=ring.copy();tri=[]
 while len(ring)>3:
  found=False
  for j in range(len(ring)):
   a,b,c=[ring[k%len(ring)]for k in [j-1,j,j+1]];aa,bb,cc=p[[a,b,c]]
   if cross(bb-aa,cc-bb)<=1e-10:continue
   others=[k for k in ring if k not in [a,b,c]];q=p[others]
   contains=(cross(bb-aa,(q-aa).T)>=-1e-10)&(cross(cc-bb,(q-bb).T)>=-1e-10)&(cross(aa-cc,(q-cc).T)>=-1e-10)
   if np.any(contains):continue
   tri.append([a,b,c]);del ring[j];found=True;break
  assert found,'Closing outline self-intersects or cannot be triangulated'
 tri.append(ring)
 # Put every original intermediate boundary point back, without T-junctions.
 for a,b in zip(corners,corners[1:]+corners[:1]):
  i=original.index(a);between=[];j=(i+1)%len(original)
  while original[j]!=b:between.append(original[j]);j=(j+1)%len(original)
  if not between:continue
  k=next(k for k,t in enumerate(tri)if a in t and b in t);t=tri.pop(k);c=next(x for x in t if x not in [a,b]);chain=[a]+between+[b];tri.extend([[x,y,c]for x,y in zip(chain,chain[1:])])
 return np.array(tri,dtype=np.int32)

def build_section(rid,nx=96,ny=96,densities=None):
 start,end=(START,SPLIT) if rid==23 else (SPLIT,END)
 angles=np.linspace(start,end,nx+1);levels=np.linspace(0,1,ny+1)
 points=[];faces=[];tags=[];lookup={};pinned_ids=set()
 def add(p):
  key=tuple(np.round(p,8))
  if key not in lookup:lookup[key]=len(points);points.append(p)
  return lookup[key]
 def patch(grid,tag):
  ids=np.array([[add(p)for p in row]for row in grid])
  if tag in ['front','back','top','bottom']:
   pinned_ids.update(ids[0].tolist()+ids[-1].tolist()+ids[:,0].tolist()+ids[:,-1].tolist())
  for i in range(ids.shape[0]-1):
   for j in range(ids.shape[1]-1):
    a,b,c,d=ids[i,j],ids[i+1,j],ids[i+1,j+1],ids[i,j+1]
    # Alternate diagonals rather than a long directional triangulation bias.
    if (i+j)%2:faces.extend([[a,b,d],[b,c,d]])
    else:faces.extend([[a,b,c],[a,c,d]])
    tags.extend([tag,tag])
 def domain(sample,tag,width,height,bd_width,bd_height):
  if densities is not None and tag in ['top','bottom','start','end']:
   # Curved thin closure strips need matched rows, not long Delaunay fans.
   # A fan cutting across a receding/concave boundary can fold into the face.
   ss,tt=np.meshgrid(np.linspace(0,1,bd_width+1),np.linspace(0,1,bd_height+1),indexing='ij');ss=np.round(ss,10);tt=np.round(tt,10)
   grid=sample(ss.reshape(-1),tt.reshape(-1)).reshape(ss.shape+(3,))
   if tag=='top':patch(grid,tag);return
   outline=np.concatenate([grid[:,0],grid[-1,1:],grid[-2::-1,-1],grid[0,-2:0:-1]])
   ids=np.array([add(p)for p in outline]);pinned_ids.update(ids.tolist());proj=outline[:,[0,2]]if tag=='bottom'else outline[:,[0,1]];tri=triangulate_outline(proj)
   faces.extend(ids[tri].tolist());tags.extend([tag]*len(tri));return
  if densities is None:
   ss,tt=np.meshgrid(np.linspace(0,1,width+1),np.linspace(0,1,height+1),indexing='ij');patch(sample(ss,tt),tag);return
  from scipy.spatial import Delaunay
  edge=[]
  for s in np.linspace(0,1,bd_width+1):edge.extend([(s,0),(s,1)])
  for t in np.linspace(0,1,bd_height+1):edge.extend([(0,t),(1,t)])
  inside=[(s,t)for s in np.linspace(0,1,width+1)[1:-1]for t in np.linspace(0,1,height+1)[1:-1]]
  param=np.unique(np.round(np.array(edge+inside),10),axis=0);positions=sample(param[:,0],param[:,1]);ids=np.array([add(p)for p in positions]);tri=Delaunay(param).simplices
  if tag in ['front','back','top','bottom']:
   edgeMask=np.any((param==0)|(param==1),axis=1);pinned_ids.update(ids[edgeMask].tolist())
  faces.extend(ids[tri].tolist());tags.extend([tag]*len(tri))
 if densities:
  fn,fy,bn,by,cn,cy=densities
  domain(lambda s,t:front(start+(end-start)*s,t),'front',fn,fy,nx,ny)
  domain(lambda s,t:back(start+(end-start)*s,t),'back',bn,by,nx,ny)
 else:
  a,t=np.meshgrid(angles,levels,indexing='ij');patch(front(a,t),'front');patch(back(a,t)[:,::-1],'back')
 # Boundary sample counts match the front; interiors simplify during LOD bake.
 for at,label in [(0,'bottom'),(1,'top')]:
  if densities:
   def cap(s,t):
    angles=start+(end-start)*s;f=front(angles,np.full_like(angles,at));b=back(angles,np.full_like(angles,at));p=f*(1-t[:,None])+b*t[:,None]
    if at==1:p[:,1]+=.16*np.sin(along(angles)*.9+t*3.2)*np.sin(t*math.pi)
    return p
   domain(cap,label,cn,cy,nx,8);continue
  f=front(angles,np.full_like(angles,at));b=back(angles,np.full_like(angles,at))
  tt=np.linspace(0,1,9);grid=f[:,None]*(1-tt[None,:,None])+b[:,None]*tt[None,:,None]
  if at==1:
   # Weathered crown across the volume, not a uniformly rounded bevel.
   grid[:,:,1]+=(.16*np.sin(along(angles)[:,None]*.9+tt[None,:]*3.2))*np.sin(tt[None,:]*math.pi)
  patch(grid if at==0 else grid[:,::-1],label)
 for angle,label in [(start,'start'),(end,'end')]:
  if densities:
   def endcap(s,t):
    f=front(np.full_like(s,angle),s);b=back(np.full_like(s,angle),s);p=f*(1-t[:,None])+b*t[:,None];p[:,1]+=.16*np.sin(along(angle)*.9+t*3.2)*np.sin(t*math.pi)*s**8;return p
   domain(endcap,label,by,cy,ny,8);continue
  f=front(np.full_like(levels,angle),levels);b=back(np.full_like(levels,angle),levels);tt=np.linspace(0,1,9);grid=f[:,None]*(1-tt[None,:,None])+b[:,None]*tt[None,:,None]
  grid[:,:,1]+=.16*np.sin(along(angle)*.9+tt*3.2)[None,:]*np.sin(tt*math.pi)[None,:]*levels[:,None]**8
  if label=='start':grid=grid[::-1]
  patch(grid,label)
 points=np.array(points);faces=np.array(faces);p=points[faces.reshape(-1)];angle=np.degrees(np.arctan2(p[:,0]-CENTER[0],-(p[:,2]-CENTER[2])));s=along(angle);y=p[:,1]
 tags=np.repeat(np.array(tags),3);cross=np.linalg.norm(p[:,[0,2]]-CENTER[[0,2]],axis=1)
 surf=np.isin(tags,['top','bottom']);v=np.where(surf,cross-50,y)
 # The approved colour/ORM atlas is a pentagonal island with unpainted olive
 # padding. Rectangular re-use previously mapped that padding as giant wedges.
 # Use its interior only, at the SAME UV derivative / metres per pixel.
 # Images, colour, contrast, roughness, fine-normal UV scale and strength stay.
 uv0=np.stack([reflect((s+7.36)/15.57,.22,.72),reflect((v+9.65)/19.89,.24,.75)],axis=1);uv1=np.stack([(s+6)/12,(v+5)/10],axis=1)
 # All seam/outer-ring vertices are pinned in every LOD. UVs are continuous.
 pinned=np.array([i in pinned_ids for i in range(len(points))])
 return points,faces,uv0,uv1,np.array(tags[::3]),pinned
