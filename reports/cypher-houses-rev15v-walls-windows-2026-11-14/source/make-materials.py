from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'source/architecture-plan.json').read_text());W,H=1024,1536
palettes={'L1':[193,188,170],'L2':[197,188,167],'L3':[181,177,160],'R1':[151,170,161],'R3':[192,182,164],'F1':[186,181,161],'F2':[188,180,163],'B1':[184,178,160],'B2':[177,184,172]}
used=sorted({g for o in plan['objects'] for _,g in o['wallFaces']});records=[]
for index,group in enumerate(used):
    cfg=plan['facades'][group];rng=np.random.default_rng(141126+index);span=cfg['max']-cfg['min'];height=cfg['top']-7.2
    u=np.linspace(cfg['min'],cfg['max'],W,dtype=np.float32)[None,:];z=np.linspace(cfg['top'],7.2,H,dtype=np.float32)[:,None]
    def noise(w,h):return np.asarray(Image.fromarray(rng.integers(0,256,(h,w),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC),dtype=np.float32)/255
    broad=noise(18,27);fine=noise(95,140);grain=rng.normal(0,1,(H,W)).astype(np.float32)
    base=np.array(palettes[group],dtype=np.float32);color=np.broadcast_to(base,(H,W,3)).copy();color+=(broad-.5)[...,None]*8+(fine-.5)[...,None]*5+grain[...,None]*1.9
    # Irregular loss of surface limewash reveals darker render beneath.
    loss=np.clip((noise(34,47)-.49)*4.4,0,1);loss*=np.clip(.22+.72*broad,0,1)
    render=base*np.array([.83,.84,.83]);color=color*(1-loss[...,None]*.25)+render*loss[...,None]*.25
    # Ground damp and the softer, broken lower margin found in the street references.
    damp=np.exp(-np.maximum(z-7.2,0)/(.44+.26*broad))*(.23+.22*fine);color*=1-damp[...,None];color-=damp[...,None]*np.array([5,4,0])
    # Local rain marks below actual window sills, rather than arbitrary uniform stripes.
    drips=np.zeros((H,W),dtype=np.float32)
    for win in plan['windows']:
        if win['house']!=group:continue
        axis=0 if cfg['axis']=='x' else 1;left,right=win['bounds'][axis];bottom=win['zMin'];length=float(rng.uniform(.6,1.65))
        for edge in [left,right]:
            width=float(rng.uniform(.025,.065));dx=np.exp(-((u-edge)/width)**2);tail=np.exp(-np.maximum(bottom-z,0)/length)*(z<bottom)*(z>bottom-length*2)
            drips=np.maximum(drips,dx*tail*(.18+.09*fine))
        broadRun=np.exp(-((u-(left+right)/2)/max((right-left)*.6,.2))**4)*np.exp(-np.maximum(bottom-z,0)/.20)*(z<bottom)
        drips=np.maximum(drips,broadRun*.14)
    color*=1-drips[...,None]
    # A few irregular brick exposures; Events retains its warm masonry band below the posters.
    patches=np.zeros((H,W),dtype=np.float32)
    for k in range(4):
        cx=float(rng.uniform(cfg['min']+.5,cfg['max']-.5));cz=float(rng.uniform(8.0,min(cfg['top']-1,17)));rx=float(rng.uniform(.3,.7));rz=float(rng.uniform(.25,.65))
        ellipse=((u-cx)/rx)**2+((z-cz)/rz)**2;patches=np.maximum(patches,np.clip((1.12-ellipse+(fine-.5)*.9)*5,0,1))
    if group=='L2':patches=np.maximum(patches,np.clip((9.84-z+(broad-.5)*.16)*18,0,1))
    row=np.floor((z-7.2)/.078);bx=(u-cfg['min']+np.mod(row,2)*.125)/.25;bz=(z-7.2)/.078
    mortar=(np.mod(bx,1)<.036)|(np.mod(bz,1)<.10)
    brick=np.zeros_like(color);variation=noise(100,140)
    brick[:]=[139,109,83];brick+=(variation-.5)[...,None]*34+grain[...,None]*2;brick[mortar.repeat(W,axis=1) if mortar.shape[1]==1 else mortar]=[107,105,91]
    color=color*(1-patches[...,None])+brick*patches[...,None]
    # Small branching cracks, authored at facade scale and kept below the window/paint details.
    cracks=Image.new('L',(W,H));draw=ImageDraw.Draw(cracks)
    for k in range(13):
        x=float(rng.uniform(25,W-25));y=float(rng.uniform(20,H-80));points=[(x,y)]
        for j in range(int(rng.integers(5,11))):x+=rng.uniform(-8,8);y+=rng.uniform(3,11);points.append((x,y))
        draw.line(points,fill=105,width=1)
        if k%3==0:draw.line([points[2],(points[2][0]+15,points[2][1]+16),(points[2][0]+20,points[2][1]+29)],fill=75,width=1)
    cm=np.asarray(cracks,dtype=np.float32)/255;color*=1-cm[...,None]*.36
    # Physical normal scale: sub-millimetre render grain with shallow mortar recesses.
    surface=(broad-.5)*.0016+(fine-.5)*.001+grain*.00028-loss*.0012-cm*.001
    surface=surface*(1-patches)+((~mortar).astype(np.float32)*.0035+grain*.00020)*patches
    dx=(np.roll(surface,-1,1)-np.roll(surface,1,1))/(2*span/W);dy=(np.roll(surface,-1,0)-np.roll(surface,1,0))/(2*height/H)
    normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.sqrt((normal*normal).sum(-1,keepdims=True));rough=np.clip(.87+.08*(fine-.5)-damp*.22-drips*.08,.60,.97)
    files=[]
    for suffix,array,quality in [('color',np.uint8(np.clip(color,0,255)),92),('normal',np.uint8(np.clip((normal*.5+.5)*255,0,255)),95)]:
        p=R/'textures'/f'{group}-{suffix}.jpg';Image.fromarray(array).save(p,quality=quality,subsampling=0);files.append(p.name)
    p=R/'textures'/f'{group}-rough.png';Image.fromarray(np.uint8(rough*255)).save(p);files.append(p.name)
    records.append({'facade':group,'pixels':[W,H],'physicalWidthMetres':span,'physicalHeightMetres':height,'files':files})
# Worn sash/shutter paint shared by the window frames, with shallow grain and exposed underpaint.
n=512;rng=np.random.default_rng(14112699);coarse=np.asarray(Image.fromarray(rng.integers(0,256,(18,42),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC),dtype=np.float32)/255;fine=rng.normal(0,1,(n,n)).astype(np.float32);chip=np.clip((coarse-.69)*5,0,1)
for kind,paint,under in [('sash',[151,159,145],[68,85,75]),('shutter',[86,109,91],[76,69,52])]:
    c=np.broadcast_to(np.array(paint,dtype=np.float32),(n,n,3)).copy();c+=(coarse-.5)[...,None]*8+fine[...,None]*1.2;c=c*(1-chip[...,None])+np.array(under)*chip[...,None]
    Image.fromarray(np.uint8(np.clip(c,0,255))).save(R/'textures'/f'{kind}-paint.jpg',quality=94,subsampling=0)
# Dirt collects at pane edges, leaving a darker, smoother centre for reflected light.
y,x=np.mgrid[0:n,0:n].astype(np.float32);x/=n-1;y/=n-1;edge=np.exp(-np.minimum.reduce([x,1-x,y,1-y])/.065);streak=(np.sin(x*73)+np.sin(x*131+1))*.5*.015;g=np.stack([19+edge*16,27+edge*14,29+edge*11],-1)+fine[...,None]*.5
Image.fromarray(np.uint8(np.clip(g,0,255))).save(R/'textures/glass-color.jpg',quality=92,subsampling=0);Image.fromarray(np.uint8(np.clip((.20+edge*.38+streak)*255,0,255))).save(R/'textures/glass-rough.png')
files=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((R/'textures').iterdir()) if p.is_file()]
(R/'evidence/material-authoring.json').write_text(json.dumps({'status':'PASS','facades':records,'files':files,'photographsUsedAsTextures':False,'designBasis':'Peeling pale render, damp base, window-sill runoff, chipped muted sash paint and barred windows observed in the sourced Delhi photographs.'},indent=2)+'\n');print(json.dumps({'status':'PASS','facades':len(records),'bytes':sum(x['bytes'] for x in files),'files':len(files)}))
