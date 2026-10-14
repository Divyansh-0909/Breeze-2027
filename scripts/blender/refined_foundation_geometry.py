"""Stage2C.5.1: bounded refinement of the SAME connected excavation.

No changes to the world registry, tube, walking floor or remaining cliff faces.
Field phase is shared across sectors13--15. Runtime splits are not art borders.
"""
import numpy as np
import foundation_geometry as prior

old=prior.old
START,JOIN,END=prior.START,prior.JOIN,prior.END
REGIONS=prior.REGIONS
weight=prior.weight
_prior_colours=prior.colours

# Finite, nonuniform joints. Each locus changes direction where it meets a bed;
# unequal arms are deliberately interrupted instead of full-height knife cuts.
JOINTS=[
 (6.8,[4,7.2,10.5,13.1,16.7],[.1,1.05,-.62,.18,1.1],.65,.52),
 (15.9,[12.2,15.3,18.9,21.1,24.7],[1.15,.2,.6,-.6,-.1],.92,.55),
 (22.4,[3,5.8,9.5,12.4],[.2,-.7,-.35,.8],.76,.42),
 (29.8,[7.8,11.4,14.3,17.8,20.3],[.1,.6,-.3,.7,.9],1.05,.62),
 (37.1,[16,19.8,23.4,27.2,30],[1.6,.2,-.25,.85,.1],.84,.56),
 (46.5,[3.2,6.7,10.4,13.7,17.6],[.3,-.35,.7,.2,1.35],.78,.46),
]
rng=np.random.default_rng(2026101451)
# Finite chipped bed ends and broken planar recesses, not uniform noise.
CHIPS=[tuple(rng.uniform([4,1.3,.55,.32,-.24,-.4],
                         [END-START-4,31.5,1.5,1.05,.44,.4]))for _ in range(51)]
BEDS=[2.1,4.8,8.3,11.6,16.1,20.9,25.8,31.2]
BED_PATCHES=[]
for j,h in enumerate(BEDS):
    for _ in range(3 if j%3 else 2):
        center=rng.uniform(4,END-START-4);length=rng.uniform(3.8,9.8)
        BED_PATCHES.append((h,center,length,rng.uniform(-.065,.065),
                           rng.uniform(.19,.38),rng.uniform(.55,1.1),j))

def stratigraphy(u,y):
    # Fault throw offsets the bedding rather than drawing unrelated cracks
    # over unbroken horizontal lines. Bounded local changes, not a whole ring.
    throw=np.zeros_like(u)
    for c,cy,extent,amp in[(16.4,18.5,8.2,.72),(30.5,13.7,7.4,-.63),(38.4,24,8.1,.52)]:
        d=u-c-.13*(y-cy)
        throw+=amp*(old.smooth((d+.7)/1.4)-.5)*np.exp(-(d/9)**4)*np.exp(-((y-cy)/extent)**4)
    return y-throw

def rock_relief(s,y):
    u=s-START;t=stratigraphy(u,y)
    # Broad weathered faces interspersed with cut planes and recessed masses.
    r=.15*np.sin(u*.11+t*.047)+.09*np.sin(u*.24-t*.071)
    for cu,cy,rx,ry,depth,tilt in[(11,12,7,8,.4,.03),(27,22,9,9,-.37,-.02),
                                (42,11,7,5,.55,.055),(34,6,5,4,-.3,-.04)]:
        mask=old.smooth((1-np.maximum(np.abs((u-cu)/rx),np.abs((t-cy)/ry)))/.26)
        r+=mask*(depth+tilt*(t-cy))
    for h,c,length,slope,offset,thickness,j in BED_PATCHES:
        line=h+slope*(u-c)+.18*np.sin((u-c)*.34+j)
        d=t-line;gate=old.smooth((length-np.abs(u-c))/1.6)
        # A broken projecting lip with a sloping recess behind it. No long
        # exponential groove, no evenly repeated smooth horizontal shelf.
        profile=old.smooth((d+thickness)/(.25+thickness*.32))*(1-old.smooth((d-.08)/.55))
        r-=offset*profile*gate
        r+=offset*.38*old.smooth((d-.27)/.48)*(1-old.smooth((d-1.2)/.8))*gate
    for j,(c,heights,offsets,width,depth) in enumerate(JOINTS):
        lo,hi=heights[0],heights[-1]
        locus=c+np.interp(t,heights,offsets)
        locus+=.12*np.sin(t*1.23+c)+.06*np.sin(t*2.67+j)
        d=u-locus
        gate=old.smooth((t-lo)/1.4)*old.smooth((hi-t)/1.8)
        # Local bridge interrupts a joint; widths change around broken beds.
        # Actual unbroken rock bridges, not merely a shallower still-lit
        # continuous incision. Unequal gaps differ by joint; neighbouring
        # chipped plates interrupt both the notch and its side-face throw.
        for fraction,halfwidth in[(.27+.025*(j%3),.69+.07*(j%2)),
                                   (.59-.019*(j%2),.91-.06*(j%3))]:
            bridge=old.smooth(np.maximum(0,1-np.abs(t-(lo+fraction*(hi-lo)))/halfwidth)/.40)
            gate*=1-bridge
        w=width*(.82+.19*np.sin(t*.68+j)+.11*np.sin(t*1.37+c))
        profile=old.smooth(np.maximum(0,1-np.abs(d)/w))
        r+=depth*profile*gate
        # A small asymmetric rock-face throw, not a long smooth exposed cap.
        r+=.08*(old.smooth((d+.38)/.76)-.5)*np.exp(-(d/2.3)**4)*gate
        # One interrupted oblique branch from selected joints.
        if j in[0,2,3,4]:
            branch_y=lo+.32*(hi-lo);bd=d-(.57 if j%2 else -.64)*(t-branch_y)
            bg=old.smooth((t-branch_y)/.5)*old.smooth((branch_y+3.1-t)/.9)
            r+=depth*.45*old.smooth(np.maximum(0,1-np.abs(bd)/(.58+w*.23)))*bg
    for cu,cy,rx,ry,depth,tilt in CHIPS:
        dx=(u-cu)/rx;dy=(t-cy)/ry
        # Intersection of three uneven break planes produces an asymmetrical
        # chipped face. Moderate edge slope; no randomly extruded sharp spikes.
        shape=np.maximum.reduce([dx+.33*dy,-.79*dx+.62*dy,-.19*dx-.86*dy])
        r+=depth*old.smooth((1-shape)/.42)*np.exp(-((dx*dx+dy*dy)/2.8)**2)*(1+tilt*dy)
    return r

def point(s,v):
    s,v=np.broadcast_arrays(np.asarray(s,dtype=float),np.asarray(v,dtype=float))
    p=old.wall_point(s,v,True);u=s-START;w=weight(s)
    # Preserve the original buried foot. Refined bed relief continues up to
    # a softened rim transition, with only bounded local macro adjustment.
    body=old.smooth(v/.045)*(1-old.smooth((v-.88)/.12))
    delta=(rock_relief(s,p[...,1])-old.relief(s,p[...,1],True))*w*body
    macro=.9*np.exp(-((u-11)/7.5)**4)*old.smooth((v-.29)/.24)
    macro-=.64*np.exp(-((u-31)/7.3)**4)*np.sin(np.pi*v)**2
    macro+=1.1*np.exp(-((u-44)/5.2)**4)*old.smooth((v-.48)/.28)
    # A single partial quarry-cut ledge, never an annular repeated terrace.
    macro+=.65*np.exp(-((u-23)/6)**4)*old.smooth((p[...,1]-10.8)/1.1)*(1-old.smooth((p[...,1]-15.1)/1.2))
    delta+=w*macro*old.smooth(v/.09)
    _,n,_=old.frame(s)
    p[...,0]+=n[...,0]*delta;p[...,2]+=n[...,1]*delta
    p[...,1]+=w*old.smooth((v-.70)/.30)*(.43*np.sin(u*.23)+.22*np.sin(u*.59+.4))
    return p

def normal(s,v):
    ds=point(s+.007,v)-point(s-.007,v);dv=point(s,v+.00045)-point(s,v-.00045)
    n=-np.cross(ds,dv);return n/np.maximum(1e-10,np.linalg.norm(n,axis=-1))[...,None]

def colours(s,p):
    # Keep the accepted colour family and nearly identical bounded factors.
    return _prior_colours(s,p)

def sector(index,level):
    # Reuse the proven partition/stitch/export policy with this shared field.
    if index not in[13,14,15]:return prior.sector(index,level)
    fn=prior.point;nm=prior.normal;cl=prior.colours
    try:
        prior.point=point;prior.normal=normal;prior.colours=colours
        return prior.sector(index,level)
    finally:prior.point=fn;prior.normal=nm;prior.colours=cl

def terrain():
    from mathutils import Vector
    from mathutils.geometry import delaunay_2d_cdt
    rim_s=np.unique(np.concatenate([np.linspace(a,b,max(2,int(np.ceil((b-a)/2)))+1)[:-1]
                                   for a,b in zip(old.BREAKS,old.BREAKS[1:])]))
    rim=point(rim_s,np.ones_like(rim_s));nr=len(rim)
    vertices=list(rim[:,[0,2]])+[[-280,-384],[280,-384],[280,176],[-280,176]]
    edges=[(i,(i+1)%nr)for i in range(nr)]+[(nr+i,nr+(i+1)%4)for i in range(4)]
    def inside(x,z):
        poly=rim[:,[0,2]];c=False;j=len(poly)-1
        for i in range(len(poly)):
            a,b=poly[i],poly[j]
            if (a[1]>z)!=(b[1]>z)and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:c=not c
            j=i
        return c
    # Jittered Cartesian samples avoid repeated triangle bands; graded density
    # rather than identical offset rings around the excavation.
    rng=np.random.default_rng(2026101457)
    for z in np.arange(-384,177,9.):
        for x in np.arange(-280,281,9.):
            q=np.array([x,z])+rng.uniform(-1.8,1.8,2)
            if not inside(*q)and -280<q[0]<280 and -384<q[1]<176:vertices.append(q)
    for j,s in enumerate(rim_s):
        p=point(np.array([s]),np.array([1]))[0];_,n,_=old.frame(np.array([s]))
        tangent=np.array([-n[0,1],n[0,0]])
        for d in[1.3,3.7,8,15,25]:
            q=p[[0,2]]+n[0]*(d+rng.uniform(-.18,.18)*d)+tangent*rng.uniform(-.5,.5)
            if not inside(*q):vertices.append(q)
    vv,ee,ff,*_=delaunay_2d_cdt([Vector(q)for q in vertices],edges,[],0,1e-6)
    xz=np.array(vv);keep=[]
    for f in ff:
        c=xz[list(f)].mean(axis=0)
        if not inside(*c)and -280-1e-5<=c[0]<=280+1e-5 and -384-1e-5<=c[1]<=176+1e-5:keep.append(f)
    x,z=xz[:,0],xz[:,1]
    # Independent broad ridges, local gullies and gentle asymmetric saddles.
    land=29+2.1*np.sin((x+z*.23)/62)+1.55*np.cos((z-x*.31)/47)+.65*np.sin((x*.73+z)/31)
    land+=2.7*np.exp(-((x+101)/58)**2-((z+109)/93)**2)
    land-=2.1*np.exp(-((z+.46*x+115)/19)**2)*np.exp(-((x+79)/90)**2)
    distance=np.linalg.norm(xz[:,None,:]-rim[None,:,[0,2]],axis=-1)
    # Weighted nearest rim interpolation removes angular nearest-sample
    # terracing and matches each exact contact vertex independently.
    nearest=distance.argmin(1);dist=distance[np.arange(len(xz)),nearest]
    k=np.argsort(distance,axis=1)[:,:5];d=np.take_along_axis(distance,k,axis=1)
    weights=1/np.maximum(.05,d)**3
    rim_y=(rim[k,1]*weights).sum(1)/weights.sum(1)
    arc=(rim_s[k]*weights).sum(1)/weights.sum(1);_,out,_=old.frame(arc)
    v=np.full_like(arc,1);nn=normal(arc,v)
    # Match the wall's geometric normal over the first0.7m before transitioning
    # to weathered ground. Its tiny rounded shoulder is not a broad annular bank.
    rise=np.clip(-(nn[:,0]*out[:,0]+nn[:,2]*out[:,1])/np.maximum(.12,nn[:,1]),0,2.8)
    shoulder=rise*.55*(1-np.exp(-dist/.55))*np.exp(-dist/3.7)
    blend=old.smooth(dist/(8.5+2.5*np.sin(x*.021+z*.037)))
    h=(rim_y+shoulder)*(1-blend)+land*blend
    width=31+70*old.smooth(np.maximum(0,z)/140)
    forecourt=old.smooth((z+20)/15)*old.smooth((width-np.abs(x))/18)
    h=h*(1-forecourt)-.9*forecourt
    path=old.WORLD['tunnel']['centerline'];tx=np.interp(-z,[-q[1]for q in path],[q[0]for q in path])
    tube=(z>-42)&(z<0)&(np.abs(x-tx)<5);h=np.where(tube,np.maximum(h,7),h)
    h[dist<1e-5]=rim[nearest[dist<1e-5],1]
    p=np.stack([x,h,z],axis=1);faces=np.array(keep,dtype=np.int32)
    cross=np.cross(p[faces[:,1]]-p[faces[:,0]],p[faces[:,2]]-p[faces[:,0]])
    flip=cross[:,1]<0;faces[flip]=faces[flip][:,[0,2,1]]
    n=np.zeros_like(p);cross=np.cross(p[faces[:,1]]-p[faces[:,0]],p[faces[:,2]]-p[faces[:,0]])
    for i in range(3):np.add.at(n,faces[:,i],cross)
    n/=np.maximum(1e-12,np.linalg.norm(n,axis=1))[:,None]
    n[dist<1e-5]=normal(rim_s[nearest[dist<1e-5]],np.ones(np.count_nonzero(dist<1e-5)))
    # Source maps are unchanged. UV density is corrected:90m exposed giant
    # source motifs;22m reads as local dry-rock grain in the existing map view.
    uv=xz/22
    # A low-contrast erosion/landform field supplies non-repeating mineral
    # variation. It is shared across culling tiles, not random camouflage.
    q=.953+.021*np.sin((x+z*.18)/24)+.016*np.cos((z-x*.3)/17)
    q-=.027*np.exp(-((z+.46*x+115)/19)**2)*np.exp(-((x+79)/90)**2)
    colours=np.clip(np.stack([q,q*.995,q*.982],axis=-1),.88,.999)
    tiles=[];centroid=p[faces].mean(axis=1)
    for ix in range(4):
        for iz in range(4):
            selected=faces[(centroid[:,0]>=-280+ix*140)&(centroid[:,0]<-280+(ix+1)*140+.0001)&
                           (centroid[:,2]>=-384+iz*140)&(centroid[:,2]<-384+(iz+1)*140+.0001)]
            used=np.unique(selected);mapping=np.full(len(p),-1);mapping[used]=np.arange(len(used))
            if len(selected):tiles.append((f'Terrain_{ix}_{iz}',p[used],mapping[selected],uv[used],n[used],colours[used]))
    return tiles,{'triangles':len(faces),'vertices':len(p),'rimSamples':nr,'cartesianTiles':len(tiles),
                  'exactRimMatch':float(np.max(np.abs(h[dist<1e-5]-rim[nearest[dist<1e-5],1]))),
                  'terrainUVMetres':22,'wallRimNormalShared':True,'gradedJitteredSampling':True}

def scree():
    """Sparse irregular clusters outside all visitor polygons; no extra textures."""
    rng=np.random.default_rng(2026101481);vp=[];fp=[];up=[];np_=[];cp=[]
    for center_s,count in[(START+8,7),(START+20.2,11),(START+30.8,9),(START+43.5,13),(END-5,5)]:
        for j in range(count):
            s=center_s+rng.uniform(-2.2,2.2);base=point(np.array([s]),np.array([0]))[0];_,n,_=old.frame(np.array([s]))
            center=np.array([base[0],.0,base[2]])-np.array([n[0,0],0,n[0,1]])*rng.uniform(.03,.8)
            radius=rng.uniform(.09,.43);h=rng.uniform(.06,.22);angle=rng.uniform(0,2*np.pi)
            ring=np.arange(6)*2*np.pi/6+angle+rng.uniform(-.19,.19,6)
            bottom=np.c_[np.cos(ring)*radius*rng.uniform(.7,1.2,6),np.full(6,-.05),np.sin(ring)*radius*.7]+center
            top=np.c_[np.cos(ring)*radius*.48,rng.uniform(h*.6,h,6),np.sin(ring)*radius*.43]+center
            p=np.vstack([bottom,top]);f=[]
            for a in range(6):b=(a+1)%6;f.extend([[a,6+a,6+b],[a,6+b,b]])
            for a in range(1,5):f.extend([[0,a,a+1],[6,6+a+1,6+a]])
            f=np.array(f);normals=np.zeros_like(p);cross=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
            for a in range(3):np.add.at(normals,f[:,a],cross)
            normals/=np.maximum(1e-12,np.linalg.norm(normals,axis=1))[:,None]
            fp.extend(f+len(vp));vp.extend(p);np_.extend(normals);up.extend(p[:,[0,2]]/2);cp.extend(np.ones((len(p),3))*.96)
    return np.array(vp),np.array(fp),np.array(up),np.array(np_),np.array(cp)
