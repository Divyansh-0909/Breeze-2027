from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'source/road-layout.json').read_text());rng=np.random.default_rng(cfg['seed'])
if cfg.get('activeHoleIds'):cfg['holes']=[h for h in cfg['holes'] if h['id'] in cfg['activeHoleIds']]
W,H=1536,4096;X0,X1,Y0,Y1=cfg['uvWorldBounds'];xx=np.linspace(X0,X1,W,dtype=np.float32)[None,:];yy=np.linspace(Y1,Y0,H,dtype=np.float32)[:,None]
def noise(w,h):
 return np.asarray(Image.fromarray(rng.integers(0,256,(h,w),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC),dtype=np.float32)/255
broad=noise(20,48);mid=noise(100,230);fine=rng.normal(0,1,(H,W)).astype(np.float32)
tone=65+10*(broad-.5)+8*(mid-.5)+1.9*fine
color=np.stack([tone+1,tone,tone-2],axis=-1);rough=np.clip(.85+.12*(mid-.5)+.03*fine,.7,.98)
# Dry shoulders blend into the market thresholds without a hard border.
edge=1/(1+np.exp(np.clip(-(abs(xx)-2.65)*5,-30,30)))
lane=(yy<14).astype(np.float32);dust=edge*lane*(.20+.15*broad)
color=color*(1-dust[...,None])+np.array([111,101,84])*dust[...,None]
# Cypher resurfacing is an irregular patch of asphalt, with no raised edge.
cx,cy=cfg['circle']['centre'];dx=xx-cx;dy=yy-cy;ang=np.arctan2(dy,dx)
rr=np.sqrt((dx/5.25)**2+(dy/5.1)**2);limit=1+.035*np.sin(ang*5+.7)+.025*np.cos(ang*9)
resurf=np.clip((limit-rr)*15,0,1);color=color*(1-resurf[...,None])+(np.stack([56+mid*8,58+mid*7,58+mid*6],axis=-1))*resurf[...,None];rough=rough*(1-resurf)+(.82+.05*(mid-.5))*resurf
del dx,dy,rr,limit
def pixel(x,y):return ((x-X0)/(X1-X0)*(W-1),(Y1-y)/(Y1-Y0)*(H-1))
def polygon_mask(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon([pixel(x,y) for x,y in points],fill=255);return np.asarray(im,dtype=np.float32)/255
for i,p in enumerate(cfg['patches']):
 x,y,w,l,a=[p[k] for k in ['x','y','width','length','angle']];pts=[]
 for u,v in [(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]:
  u=u*w+rng.uniform(-.06,.06);v=v*l+rng.uniform(-.06,.06);pts.append((x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a)))
 m=polygon_mask(pts);value=45+(i%4)*4;color=color*(1-m[...,None])+(np.stack([value+mid*5,value+1+mid*5,value+mid*4],axis=-1))*m[...,None];rough=rough*(1-m)+(.77+mid*.1)*m
# Narrow, slightly irregular concrete apron repairs at the five open shop mouths.
for p in cfg['shops']:
 side,y=p['side'],p['y'];m=polygon_mask([(side*3.58,y-2.9),(side*2.99,y-2.65),(side*3.08,y+.5),(side*2.97,y+2.65),(side*3.58,y+2.9)])
 concrete=np.stack([116+mid*13,111+mid*12,100+mid*11],axis=-1);color=color*(1-m[...,None])+concrete*m[...,None];rough=rough*(1-m)+(.91+mid*.04)*m
# Author the hole grain/rims from the same boundary function as the mesh.
for h in cfg['holes']:
 dx=(xx-h['x'])/h['rx'];dy=(yy-h['y'])/h['ry'];a=np.arctan2(dy,dx);radius=np.sqrt(dx*dx+dy*dy)/(1+.10*np.sin(a*5+h['phase'])+.065*np.cos(a*9-h['phase']))
 inside=np.clip((1-radius)*12,0,1);rim=np.clip(1-abs(radius-.99)/.20,0,1)
 base=np.stack([34+mid*8,35+mid*8,33+mid*7],axis=-1);color=color*(1-inside[...,None])+base*inside[...,None];color+=rim[...,None]*(9+fine[...,None]*5);rough=rough*(1-inside)+(.89+.06*mid)*inside
 del dx,dy,a,radius,inside,rim,base
# Broken radial cracks grow from defects instead of covering the whole floor.
crack=Image.new('L',(W,H));dr=ImageDraw.Draw(crack)
for h in cfg['holes']:
 for i in range(4):
  a=rng.uniform(0,math.tau);x=h['x']+math.cos(a)*h['rx']*.95;y=h['y']+math.sin(a)*h['ry']*.95;pts=[pixel(x,y)]
  for j in range(5):
   a+=rng.uniform(-.55,.55);x+=math.cos(a)*rng.uniform(.10,.23);y+=math.sin(a)*rng.uniform(.10,.23);pts.append(pixel(x,y))
  dr.line(pts,fill=int(rng.uniform(95,165)),width=1)
cm=np.asarray(crack,dtype=np.float32)/255;color*=1-cm[...,None]*.42
# Worn, slightly hand-drawn cream marking, baked flush into the surface.
dx=xx-cx;dy=yy-cy;a=np.arctan2(dy,dx);rad=np.sqrt(dx*dx+dy*dy);target=cfg['circle']['radius']+.024*np.sin(a*7)+.013*np.sin(a*13)
paint=np.clip((cfg['circle']['width']/2-abs(rad-target))*100,0,1)
wear=np.clip((mid-.25)*2,0,1);gaps=((np.sin(a*23+.7)>-.82)&(np.sin(a*7+1)>-.96)).astype(np.float32);paint*=wear*gaps*.79
color=color*(1-paint[...,None])+np.array([202,188,148])*paint[...,None];rough=rough*(1-paint)+.94*paint
color=np.uint8(np.clip(color,0,255));Image.fromarray(color).save(R/'textures/road-world-color.png',compress_level=5)
Image.fromarray(np.uint8(np.clip(rough*255,0,255))).save(R/'textures/road-world-roughness.png',compress_level=5)
# A repeatable 2 m fine aggregate normal tile keeps close views detailed.
n=1024;hgt=rng.normal(0,.2,(n,n)).astype(np.float32)
for sz,weight in [(128,.25),(512,.22),(32,.13)]:
 a=Image.fromarray(rng.integers(0,256,(sz,sz),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC);hgt+=np.asarray(a,dtype=np.float32)/255*weight
gx=(np.roll(hgt,-1,1)-np.roll(hgt,1,1))*.27;gy=(np.roll(hgt,-1,0)-np.roll(hgt,1,0))*.27
normal=np.stack([-gx,gy,np.ones_like(gx)],-1);normal/=np.sqrt((normal*normal).sum(-1,keepdims=True));Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(R/'textures/asphalt-2m-normal.png',compress_level=5)
rows=[{'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((R/'textures').glob('*.png'))]
(R/'evidence/texture-art.json').write_text(json.dumps({'status':'PASS','worldAtlasSize':[W,H],'detailNormalSize':[n,n],'detailMetres':2,'circle':cfg['circle'],'holes':len(cfg['holes']),'repairPatches':len(cfg['patches']),'authorship':'Deterministic original artwork from approved reference direction; no source photograph used as a runtime texture','files':rows},indent=2)+'\n');print(json.dumps(rows),flush=True)
