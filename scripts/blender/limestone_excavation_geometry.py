"""Stage 2C.2: one continuous metre-scale excavation field, never per-rock slabs.

The approved Grey limestone pilot supplies the material. This module defines
the larger geological surface, common rim, terrain and three detailed zones.
Runtime partitions sample the SAME field and share fixed cross-LOD borders.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
WORLD = json.loads((ROOT/'public/models/gullyverse/blockout.layout.json').read_text())
BOUNDARY = np.array(WORLD['quarry']['boundary'], dtype=float)
HEIGHTS = np.array(WORLD['quarry']['wallHeights'], dtype=float)
TAU = 2*np.pi

def smooth(x):
    t=np.clip(x,0,1)
    return t*t*(3-2*t)

def periodic_delta(x):
    return (x+LENGTH/2)%LENGTH-LENGTH/2

# A restrained periodic Hermite curve follows the existing usable footprint.
samples=[];heights=[]
for j in range(len(BOUNDARY)):
    a,b=BOUNDARY[j],BOUNDARY[(j+1)%len(BOUNDARY)]
    ma=.38*(b-BOUNDARY[(j-1)%len(BOUNDARY)])
    mb=.38*(BOUNDARY[(j+2)%len(BOUNDARY)]-a)
    t=np.arange(256)/256
    p=(2*t**3-3*t**2+1)[:,None]*a+(-2*t**3+3*t**2)[:,None]*b
    p+=(t**3-2*t**2+t)[:,None]*ma+(t**3-t**2)[:,None]*mb
    samples.extend(p)
    heights.extend(HEIGHTS[j]*(1-smooth(t))+HEIGHTS[(j+1)%len(HEIGHTS)]*smooth(t))
PATH=np.array(samples);HS=np.array(heights)
direction=np.roll(PATH,-1,axis=0)-np.roll(PATH,1,axis=0)
direction/=np.linalg.norm(direction,axis=1)[:,None]
OUTWARD=np.stack([-direction[:,1],direction[:,0]],axis=1)
FOOT=PATH+OUTWARD*3.2
# Preserve the actual tunnel mouth at z=-42. No invented tunnel route.
mouth=smooth((12-np.abs(FOOT[:,0]))/6)*smooth((FOOT[:,1]+48)/3)
FOOT[:,1]=FOOT[:,1]*(1-mouth)+WORLD['tunnel']['endZ']*mouth
distance=np.linalg.norm(np.roll(FOOT,-1,axis=0)-FOOT,axis=1)
ARC=np.r_[0,np.cumsum(distance)]
LENGTH=float(ARC[-1]);FOOT=np.vstack([FOOT,FOOT[0]]);HS=np.r_[HS,HS[0]]
OUTWARD=np.vstack([OUTWARD,OUTWARD[0]])
TILE_CYCLES=2*.86*round(LENGTH/24)

def painted_uv(uv):
    # The isolated pilot paints u=.02..88 and v=.03..97. Sampling its padded
    # end-cap strip on a continuous wall produces rectangular horizontal
    # smear bands. Reflect within the painted front region, retaining the
    # original metre-scale derivative and exact colour/normal/roughness maps.
    uv=np.asarray(uv,dtype=float).copy()
    for axis,offset,width in[(0,.02,.86),(1,.03,.94)]:
        q=((uv[:,axis]-offset)/width)%2
        uv[:,axis]=offset+width*np.where(q<=1,q,2-q)
    return uv

def frame(s):
    s=np.asarray(s,dtype=float)%LENGTH
    x=np.interp(s,ARC,FOOT[:,0]);z=np.interp(s,ARC,FOOT[:,1])
    nx=np.interp(s,ARC,OUTWARD[:,0]);nz=np.interp(s,ARC,OUTWARD[:,1])
    n=np.stack([nx,nz],axis=-1);n/=np.linalg.norm(n,axis=-1)[...,None]
    return np.stack([x,z],axis=-1),n,np.interp(s,ARC,HS)

DETAIL_TARGETS=[('navigation-wall',[-42,-70],13.),
                ('curved-corner',[-42,-141],15.),
                ('stage-return-wall',[33,-57],14.)]
DETAIL=[]
for name,target,width in DETAIL_TARGETS:
    i=np.argmin(np.linalg.norm(FOOT[:-1]-target,axis=1))
    DETAIL.append({'id':name,'arcCenter':float(ARC[i]),'halfWidth':width,
                   'targetXZ':target,'footXZ':FOOT[i].tolist()})

def detail_weight(s):
    weights=[smooth((d['halfWidth']-np.abs(periodic_delta(s-d['arcCenter'])))/4)
             for d in DETAIL]
    return np.maximum.reduce(weights)

BEDS=np.array([.78,1.73,2.85,4.26,5.13,6.82,8.27,9.61,11.98,13.38,
               15.75,18.23,20.46,23.81,25.74,28.66,31.92,35.47,39.6,43.8])
rng=np.random.default_rng(2026101322)
FAULTS=[tuple(rng.uniform([0,3,-.27,.095,.13,3.5],
                        [LENGTH,36,.27,.25,.38,9.0])) for _ in range(33)]
CHIPS=[tuple(rng.uniform([0,.8,.18,.12,.025],
                       [LENGTH,35,.8,.55,.15])) for _ in range(145)]

def relief(s,y,detailed=True):
    p=TAU*s/LENGTH
    # Broad natural exposed faces; no independent pentagonal envelopes.
    r=.22*np.sin(p*7+y*.075)+.12*np.sin(p*19-y*.11)
    r+=.08*np.sin(p*31+y*.19)
    weight=detail_weight(s) if detailed else np.zeros_like(s)
    for j,bed in enumerate(BEDS):
        line=bed+.13*np.sin(p*3+j*.71)+.08*np.sin(p*13+j*1.67)
        delta=y-line
        coverage=.38+.62*smooth((np.sin(p*(4+j%3)+j*1.4)+.68)/1.5)
        # Unequal offset beds, not continuous evenly spaced shelves.
        width=.09+.035*(j%3)
        r+=(.065+.07*weight)*np.exp(-(delta/width)**2)*coverage
        r+=.065*np.tanh(delta/.065)*np.sin(j*2.73+.5)*coverage
    for center,cy,slope,width,depth,extent in FAULTS:
        signed=periodic_delta(s-center-slope*(y-cy)-.07*np.sin(y*1.8+center))
        interrupted=np.exp(-((y-cy)/extent)**4)
        r+=weight*depth*np.exp(-(signed/width)**2)*interrupted
        r+=weight*.055*np.tanh(signed/(width*.6))*interrupted*np.exp(-(signed/1.7)**2)
    for center,cy,rx,ry,depth in CHIPS:
        dx=periodic_delta(s-center)/rx;dy=(y-cy)/ry
        r+=weight*depth*np.maximum(0,1-np.maximum.reduce([dx+.25*dy,-.8*dx+.6*dy,-.2*dx-.9*dy]))**2
    return r*smooth((y+.4)/1.8)

def rim_height(s):
    _,_,h=frame(s);p=TAU*s/LENGTH
    return h*.91+.65*np.sin(p*7)+.24*np.sin(p*23)+.13*np.sin(p*49)

def arch_floor(s):
    foot,_,_=frame(s);x,z=foot[...,0],foot[...,1]
    xs=np.array([-3.15,-2.95,-2.85,-2.65,-2.15,-1.1,.3,1.55,2.55,2.9,3.03,3.18])
    ys=np.array([-.8,.08,1.43,2.98,4.23,5.23,5.68,5.13,3.93,2.68,1.0,-.8])
    opening=np.interp(x,xs,ys,left=-.8,right=-.8)
    return np.where((np.abs(x)<3.18)&(z>-42.25)&(z<-41.75),opening,-.8)

def wall_point(s,v,detailed=True):
    s,v=np.broadcast_arrays(np.asarray(s,dtype=float),np.asarray(v,dtype=float))
    foot,n,_=frame(s);p=TAU*s/LENGTH;low=arch_floor(s);top=rim_height(s)
    y=low+(top-low)*v
    slope=4.7+2.7*np.sin(p*2+.8)+1.4*np.sin(p*5-1.1)
    retreat=slope*(v*.65+v*v*.35)
    retreat+=(.85*np.sin(p*4+v*1.9)+.46*np.sin(p*9-v*.8))*np.sin(np.pi*v)
    # Restrained localized excavation bench; no perfectly terraced arena.
    bench=smooth((np.cos(p*3-.8)-.40)/.55)*.95
    retreat+=bench*(smooth((y-13.3)/1.4)-smooth((y-17.4)/1.8))
    retreat+=relief(s,y,detailed)
    # Geological toe buried into existing terrain, not a flat exposed panel edge.
    retreat-=.55*np.exp(-((y+.1)/1.3)**2)
    xz=foot+n*retreat[...,None]
    return np.stack([xz[...,0],y,xz[...,1]],axis=-1)

def wall_normal(s,v,detailed=True):
    ds=wall_point(s+.015,v,detailed)-wall_point(s-.015,v,detailed)
    dv=wall_point(s,v+.0007,detailed)-wall_point(s,v-.0007,detailed)
    normal=-np.cross(ds,dv)
    normal/=np.maximum(1e-10,np.linalg.norm(normal,axis=-1))[...,None]
    return normal

def terrain_point(s,t,detailed=True):
    s,t=np.broadcast_arrays(np.asarray(s,dtype=float),np.asarray(t,dtype=float))
    foot,n,_=frame(s);rim=wall_point(s,np.ones_like(s),detailed);p=TAU*s/LENGTH
    center=np.array([-.9,-104.])
    radial=foot-center;radial/=np.linalg.norm(radial,axis=-1)[...,None]
    # Surrounding land continues to a large terrain patch, not back down to
    # the quarry floor in a concentric hill/ring. Its far edge is outside the
    # ordinary map frame. The floor itself remains completely untouched.
    far=center+radial*(280/np.max(np.abs(radial),axis=-1))[...,None]
    xz=rim[...,::2]*(1-t[...,None])+far*t[...,None]
    plateau=29+2.1*np.sin(xz[...,0]/51)+1.4*np.sin(xz[...,1]/37)+.8*np.cos((xz[...,0]+xz[...,1])/79)
    blend=smooth(t/.28)
    shoulder=1.5*np.sin(np.pi*np.minimum(t/.16,1))
    y=rim[...,1]*(1-blend)+plateau*blend+shoulder
    # Leave the existing entrance/forecourt open; no new terrain placed over
    # its camera or portal. The original enclosed passage stays below rock.
    forecourt_width=31+70*smooth(np.maximum(0,xz[...,1])/140)
    forecourt=smooth((xz[...,1]+20)/15)*smooth((forecourt_width-np.abs(xz[...,0]))/18)
    y=y*(1-forecourt)-.9*forecourt
    # Outer geology stays above the unchanged enclosed passage.
    path=WORLD['tunnel']['centerline'];tx=np.interp(-xz[...,1],[-q[1]for q in path],[q[0]for q in path])
    tube=(xz[...,1]>-42)&(xz[...,1]<0)&(np.abs(xz[...,0]-tx)<5)
    y=np.where(tube,np.maximum(y,7.0),y)
    return np.stack([xz[...,0],y,xz[...,1]],axis=-1)

def terrain_normal(s,t,detailed=True):
    ds=terrain_point(s+.02,t,detailed)-terrain_point(s-.02,t,detailed)
    dt=terrain_point(s,t+.001,detailed)-terrain_point(s,t-.001,detailed)
    normal=-np.cross(ds,dt);normal/=np.maximum(1e-10,np.linalg.norm(normal,axis=-1))[...,None]
    return normal

def stitch(a,b,va,vb,faces):
    i=j=0
    while i<len(a)-1 or j<len(b)-1:
        na=va[i+1] if i<len(a)-1 else np.inf
        nb=vb[j+1] if j<len(b)-1 else np.inf
        if abs(na-nb)<1e-9:
            faces.extend([[a[i],b[j+1],b[j]],[a[i],a[i+1],b[j+1]]]);i+=1;j+=1
        elif na<nb:faces.append([a[i],a[i+1],b[j]]);i+=1
        else:faces.append([a[i],b[j+1],b[j]]);j+=1

# Broad culling partitions, not individually sculpted rock masses. Detail-zone
# borders are inside partitions; geological fields continue across all joins.
BREAKS=np.unique(np.r_[np.linspace(0,LENGTH,13),
                      [d['arcCenter']-d['halfWidth'] for d in DETAIL],
                      [d['arcCenter']+d['halfWidth'] for d in DETAIL]])
BREAKS=BREAKS[(BREAKS>=0)&(BREAKS<=LENGTH)]
RIM_CUT=.90
COMMON_V=np.r_[np.linspace(0,RIM_CUT,145),1.]

def surface_sector(index,level,detailed=True):
    start,end=BREAKS[index:index+2];mid=(start+end)/2
    dense=bool(detailed and detail_weight(np.array(mid))>.25)
    step=([.20,.52,1.3]if dense else[1.15,2.0,3.6])[level]
    ns=max(2,int(np.ceil((end-start)/step)))
    ss=np.linspace(start,end,ns+1)
    # Exact samples at the original tunnel-profile x positions.
    foot,_,_=frame(ss)
    if np.max(foot[:,1])>-42.25 and np.min(np.abs(foot[:,0]))<5:
        fine=np.linspace(start,end,max(16,int(np.ceil((end-start)/.14)))+1)
        keep=np.abs(frame(fine)[0][:,0])<3.5
        ss=np.unique(np.round(np.r_[ss,fine[keep]],7))
    nv=([160,74,30]if dense else[43,28,20])[level]
    points=[];normals=[];uv=[];faces=[];cols=[];params=[]
    for i,s in enumerate(ss):
        vv=COMMON_V if i in[0,len(ss)-1]else np.linspace(0,1,nv+1)
        vv=np.unique(np.r_[vv[vv<RIM_CUT],RIM_CUT])
        p=wall_point(np.full_like(vv,s),vv,detailed)
        n=wall_normal(np.full_like(vv,s),vv,detailed)
        cols.append(np.arange(len(points),len(points)+len(vv)).tolist());params.append(vv)
        points.extend(p);normals.extend(n)
        uv.extend(np.stack([np.full_like(vv,s/LENGTH*TILE_CYCLES+.02),p[:,1]*.094+.03],axis=1))
    for a,b,va,vb in zip(cols,cols[1:],params,params[1:]):stitch(a,b,va,vb,faces)
    # A modest common upper band/rim is identical in every LOD. Its lower
    # edge uses each body's actual vertices, so it introduces neither an
    # overlapping cover mesh nor a T-junction gap. This prevents rare upward
    # rays changing hit/miss when a coarser LOD samples the skyline differently.
    common_s=np.linspace(start,end,max(2,int(np.ceil((end-start)/2)))+1)
    rim=wall_point(common_s,np.ones_like(common_s),detailed)
    rim_ids=list(range(len(points),len(points)+len(common_s)))
    points.extend(rim);normals.extend(wall_normal(common_s,np.ones_like(common_s),detailed))
    uv.extend(np.stack([common_s/LENGTH*TILE_CYCLES+.02,rim[:,1]*.094+.03],axis=1))
    bridge=[];stitch([c[-1]for c in cols],rim_ids,ss,common_s,bridge)
    faces.extend(f[::-1]for f in bridge)
    # Terrain is part of the same excavation section, attached at the exact rim.
    cols=[];params=[]
    tt=np.array([0,.008,.02,.04,.065,.10,.16,.25,.40,.65,1.])
    for s in common_s:
        p=terrain_point(np.full_like(tt,s),tt,detailed)
        n=terrain_normal(np.full_like(tt,s),tt,detailed)
        cols.append(np.arange(len(points),len(points)+len(tt)).tolist());params.append(tt)
        points.extend(p);normals.extend(n)
        rim=wall_point(np.full_like(tt,s),np.ones_like(tt),detailed)
        # Keep the wall UV exactly at the rim and use metre-scale X/Z
        # displacement thereafter; no texture stretched over 200m of land.
        uv.extend(np.stack([np.full_like(tt,s/LENGTH*TILE_CYCLES+.02)+(p[:,0]-rim[:,0])*.071667,
                            (p[:,1]+p[:,2]-rim[:,2])*.094+.03],axis=1))
    for a,b,va,vb in zip(cols,cols[1:],params,params[1:]):stitch(a,b,va,vb,faces)
    if index==0:
        # Actual original passage end -> new continuous opening. This short
        # geological return closes the lip without remodelling the tunnel.
        source=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
        body=np.array(source['tunnelAttributes']['position']).reshape(-1,3)[:56*10*3*6]
        end=body[np.abs(body[:,2]-WORLD['tunnel']['endZ'])<1e-5]
        inner=np.unique(np.round(end,6),axis=0)
        inner=inner[np.argsort(np.arctan2(inner[:,0],inner[:,1]-2.4))]
        mouth_ids=np.flatnonzero((np.abs(FOOT[:-1,0])<5)&(FOOT[:-1,1]>-42.25))
        mx=FOOT[mouth_ids,0];order=np.argsort(mx);mx=mx[order];ms=ARC[mouth_ids][order]
        outer_s=np.interp(inner[:,0]*1.075,mx,ms)
        outer=wall_point(outer_s,np.zeros_like(outer_s),detailed)
        outer_uv=np.stack([outer_s/LENGTH*TILE_CYCLES+.02,outer[:,1]*.094+.03],axis=1)
        inner_uv=outer_uv+np.stack([(inner[:,0]-outer[:,0])*.071667,(inner[:,1]-outer[:,1])*.094],axis=1)
        offset=len(points);points.extend(inner);points.extend(outer)
        normals.extend(np.tile([0,0,-1],(len(inner)*2,1)));uv.extend(inner_uv);uv.extend(outer_uv)
        for j in range(len(inner)-1):
            for f in [[offset+j,offset+j+1,offset+len(inner)+j+1],
                      [offset+j,offset+len(inner)+j+1,offset+len(inner)+j]]:
                q=np.array(points)[f]
                if np.cross(q[1]-q[0],q[2]-q[0])[2]>0:f=f[::-1]
                faces.append(f)
    return np.array(points),np.array(faces,dtype=np.int32),painted_uv(np.array(uv)),np.array(normals)

def description():
    return {'arcLengthMetres':LENGTH,'usableFootprint':BOUNDARY.tolist(),
            'rimHeightRange': [float(rim_height(ARC).min()),float(rim_height(ARC).max())],
            'detailAreas':DETAIL,'cullingPartitions':len(BREAKS)-1,
            'partitionArcs':BREAKS.tolist(),'textureCyclesAroundPerimeter':TILE_CYCLES,
            'uvScaleMetres': {'nominalPilotWidth':12,'nominalPilotHeight':10,
                              'normalAndRoughnessMaps':'Exact Grey limestone pilot'},
            'contact':'buried -0.8m except the actual tunnel opening',
            'boundaryPolicy':'identical 146-point partition borders and common upper-rim/terrain geometry at every LOD'}
