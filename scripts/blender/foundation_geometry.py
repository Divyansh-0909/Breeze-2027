"""Two adjacent production study regions in the retained connected shell.
World registry, foot, tunnel lip and cross-LOD rim are read-only. Outer terrain
is constrained Cartesian triangulation, rather than stretched radial strips.
"""
import numpy as np
import limestone_excavation_geometry as old

START=float(old.BREAKS[13]);JOIN=float(old.BREAKS[15]);END=float(old.BREAKS[16])
REGIONS=[{'id':'broad-west-face','arc':[START,JOIN],'runtimeSectors':[13,14]},
         {'id':'northwest-curvature','arc':[JOIN,END],'runtimeSectors':[15]}]

def weight(s):
    return old.smooth((s-START)/4)*old.smooth((END-s)/4)

def rock_relief(s,y):
    u=s-START
    # Broad coherent exposed planes alternate with a broken corner. Small
    # slope changes are meaningful forms, not uniform high-frequency noise.
    r=.48*np.sin(u*.119+y*.09)+.19*np.sin(u*.27-y*.044)
    beds=[1.6,3.8,6.9,8.7,12.4,16.8,19.1,24.6,29.3,33.5]
    for j,h in enumerate(beds):
        line=h+.037*(u-25)+.14*np.sin(u*.13+j*2.31)
        delta=y-line
        interrupted=.25+.75*old.smooth((np.sin(u*.14+j*1.62)+.35)/.9)
        # Actual asymmetric recess/offset, unequal intervals and finite ends.
        r+=interrupted*(.24+.09*(j%3))*np.exp(-np.abs(delta)/(.16+.04*(j%2)))
        r+=interrupted*.11*np.tanh(delta/.17)*np.sin(j*1.71)
    for center,cy,slant,width,depth,extent in [(7,16,.12,.33,.7,10),(17,8,-.19,.25,.51,5),
        (23,23,.22,.48,.94,8),(32,14,-.17,.45,.86,12),(40,21,.24,.51,1.05,11),(48,9,-.12,.33,.64,7)]:
        d=u-center-slant*(y-cy)-.12*np.sin(y*.31+center)
        gate=np.exp(-((y-cy)/extent)**4)
        notch=np.maximum(0,1-np.abs(d)/width)**1.25
        r+=depth*notch*gate
        r+=.16*np.tanh(d/.18)*np.exp(-(d/2.1)**2)*gate
    # Local broken projection and ledge, not a uniform terraced ring.
    r-=.68*np.exp(-((u-37)/5.7)**4)*old.smooth((y-9.7)/1.4)*(1-old.smooth((y-14.6)/1.6))
    r+=.16*np.sin(u*1.19+y*.97)*np.exp(-((u-42)/9)**4)*np.exp(-((y-11)/10)**4)
    return r

def point(s,v):
    s,v=np.broadcast_arrays(np.asarray(s,dtype=float),np.asarray(v,dtype=float))
    p=old.wall_point(s,v,True)
    w=weight(s)*old.smooth(v/.045)*(1-old.smooth((v-.89)/.11))
    delta=(rock_relief(s,p[...,1])-old.relief(s,p[...,1],True))*w
    _,n,_=old.frame(s)
    p[...,0]+=n[...,0]*delta;p[...,2]+=n[...,1]*delta
    return p

def normal(s,v):
    ds=point(s+.006,v)-point(s-.006,v);dv=point(s,v+.0004)-point(s,v-.0004)
    n=-np.cross(ds,dv);return n/np.maximum(1e-10,np.linalg.norm(n,axis=-1))[...,None]

def colours(s,p):
    # Mineral/weathering follows geology at metre scale. Vertex values are
    # linear factors, not baked fake illumination or random camouflage.
    u=s-START;y=p[:,1]
    q=.96+.035*np.sin(s*.064+y*.015)+.022*np.sin(y*.39+s*.017)
    q-=.035*np.exp(-((y-2)/2.5)**2)
    # glTF COLOR_0 is normalized unsigned; Blender's exporter can wrap values
    # above1 rather than saturating them. Do not export invalid linear factors.
    return np.clip(np.stack([q,q*.998,q*.984],axis=-1),0,.999)

def sector(index,level):
    start,end=old.BREAKS[index:index+2];mid=(start+end)/2
    improved=index in[13,14,15]
    dense=bool(old.detail_weight(np.array(mid))>.25)
    step=([.24,.55,1.25]if improved else [.20,.52,1.3]if dense else[1.15,2,3.6])[level]
    nv=([145,70,32]if improved else[160,74,30]if dense else[43,28,20])[level]
    ss=np.linspace(start,end,max(2,int(np.ceil((end-start)/step)))+1)
    foot,_,_=old.frame(ss)
    if np.max(foot[:,1])>-42.25 and np.min(np.abs(foot[:,0]))<5:
        fine=np.linspace(start,end,max(16,int(np.ceil((end-start)/.14)))+1)
        ss=np.unique(np.round(np.r_[ss,fine[np.abs(old.frame(fine)[0][:,0])<3.5]],7))
    points=[];normals=[];uv=[];faces=[];cols=[];params=[];all_s=[]
    for i,s in enumerate(ss):
        vv=old.COMMON_V if i in[0,len(ss)-1]else np.linspace(0,1,nv+1)
        vv=np.unique(np.r_[vv[vv<old.RIM_CUT],old.RIM_CUT]);sv=np.full_like(vv,s)
        p=point(sv,vv);n=normal(sv,vv)
        cols.append(np.arange(len(points),len(points)+len(vv)).tolist());params.append(vv)
        points.extend(p);normals.extend(n);all_s.extend(sv)
        uv.extend(np.stack([sv/2,p[:,1]/2],axis=1))
    for a,b,va,vb in zip(cols,cols[1:],params,params[1:]):old.stitch(a,b,va,vb,faces)
    common_s=np.linspace(start,end,max(2,int(np.ceil((end-start)/2)))+1)
    rim=point(common_s,np.ones_like(common_s));ids=list(range(len(points),len(points)+len(rim)))
    points.extend(rim);normals.extend(normal(common_s,np.ones_like(common_s)));all_s.extend(common_s)
    uv.extend(np.stack([common_s/2,rim[:,1]/2],axis=1))
    bridge=[];old.stitch([c[-1]for c in cols],ids,ss,common_s,bridge);faces.extend(f[::-1]for f in bridge)
    if index==0:
        # Preserve exact original tunnel connector from the approved shell.
        p,f,_,n=old.surface_sector(0,level,True)
        # The final connection has two equal rings, after all terrain vertices.
        import json
        source=json.loads((old.ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
        body=np.array(source['tunnelAttributes']['position']).reshape(-1,3)[:56*10*3*6]
        inner=np.unique(np.round(body[np.abs(body[:,2]-old.WORLD['tunnel']['endZ'])<1e-5],6),axis=0)
        tail=f[-2*(len(inner)-1):]
        used=np.unique(tail);lookup={int(v):j+len(points)for j,v in enumerate(used)}
        points.extend(p[used]);normals.extend(n[used]);all_s.extend(np.zeros(len(used)))
        uv.extend(p[used][:,[0,1]]/2);faces.extend([[lookup[int(v)]for v in row]for row in tail])
    p=np.array(points);s=np.array(all_s)
    return p,np.array(faces,dtype=np.int32),np.array(uv),np.array(normals),colours(s,p)

def terrain():
    from mathutils import Vector
    from mathutils.geometry import delaunay_2d_cdt
    rim_s=np.unique(np.concatenate([np.linspace(a,b,max(2,int(np.ceil((b-a)/2)))+1)[:-1]
                                   for a,b in zip(old.BREAKS,old.BREAKS[1:])]))
    rim=point(rim_s,np.ones_like(rim_s));nr=len(rim)
    boundary=[[-280,-384],[280,-384],[280,176],[-280,176]]
    vertices=list(rim[:,[0,2]])+boundary
    edges=[(i,(i+1)%nr)for i in range(nr)]+[(nr+i,nr+(i+1)%4)for i in range(4)]
    def inside(x,z):
        poly=rim[:,[0,2]];c=False;j=len(poly)-1
        for i in range(len(poly)):
            a,b=poly[i],poly[j]
            if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:c=not c
            j=i
        return c
    # Cartesian points, fine only near the actual rim, modest far-land density.
    for z in np.arange(-384,177,8.):
        for x in np.arange(-280,281,8.):
            if not inside(x,z):vertices.append([x,z])
    for s in rim_s:
        p=point(np.array([s]),np.array([1]))[0];_,n,_=old.frame(np.array([s]))
        for d in[1.6,4.5,10,20]:vertices.append(p[[0,2]]+n[0]*d)
    vv,ee,ff,*_=delaunay_2d_cdt([Vector(q)for q in vertices],edges,[],0,1e-6)
    xz=np.array(vv);keep=[]
    for f in ff:
        c=xz[list(f)].mean(axis=0)
        if not inside(c[0],c[1])and -280-1e-5<=c[0]<=280+1e-5 and -384-1e-5<=c[1]<=176+1e-5:keep.append(f)
    x,z=xz[:,0],xz[:,1]
    # Surrounding land has independent Cartesian ridges, not radial swirls.
    plateau=29+2.2*np.sin((x+z*.23)/62)+1.65*np.cos((z-x*.31)/47)+.8*np.sin((x*.73+z)/31)
    distance=np.linalg.norm(xz[:,None,:]-rim[None,:,[0,2]],axis=-1);nearest=distance.argmin(axis=1)
    dist=distance[np.arange(len(xz)),nearest];blend=old.smooth(dist/17)
    h=rim[nearest,1]*(1-blend)+plateau*blend
    width=31+70*old.smooth(np.maximum(0,z)/140)
    forecourt=old.smooth((z+20)/15)*old.smooth((width-np.abs(x))/18)
    h=h*(1-forecourt)-.9*forecourt
    path=old.WORLD['tunnel']['centerline'];tx=np.interp(-z,[-q[1]for q in path],[q[0]for q in path])
    tube=(z>-42)&(z<0)&(np.abs(x-tx)<5);h=np.where(tube,np.maximum(h,7),h)
    h[dist<1e-5]=rim[nearest[dist<1e-5],1]
    p=np.stack([x,h,z],axis=1);faces=np.array(keep,dtype=np.int32)
    # +Y winding, matching actual geometry; averaged normals for material view.
    cross=np.cross(p[faces[:,1]]-p[faces[:,0]],p[faces[:,2]]-p[faces[:,0]])
    flip=cross[:,1]<0;faces[flip]=faces[flip][:,[0,2,1]]
    n=np.zeros_like(p);cross=np.cross(p[faces[:,1]]-p[faces[:,0]],p[faces[:,2]]-p[faces[:,0]])
    for i in range(3):np.add.at(n,faces[:,i],cross)
    n/=np.maximum(1e-12,np.linalg.norm(n,axis=1))[:,None]
    tiles=[]
    centroid=p[faces].mean(axis=1)
    # All terrain LODs share geometry: macro density is already modest and
    # exact borders avoid cracks. Refined terrain streaming is later work.
    for ix in range(4):
        for iz in range(4):
            selected=faces[(centroid[:,0]>=-280+ix*140)&(centroid[:,0]<-280+(ix+1)*140+.0001)&
                           (centroid[:,2]>=-384+iz*140)&(centroid[:,2]<-384+(iz+1)*140+.0001)]
            used=np.unique(selected);mapping=np.full(len(p),-1);mapping[used]=np.arange(len(used))
            if len(selected):tiles.append((f'Terrain_{ix}_{iz}',p[used],mapping[selected],xz[used]/90,n[used],np.ones((len(used),3))))
    return tiles,{'triangles':len(faces),'vertices':len(p),'rimSamples':nr,'cartesianTiles':len(tiles),
                  'exactRimMatch':float(np.max(np.abs(h[dist<1e-5]-rim[nearest[dist<1e-5],1])))}
