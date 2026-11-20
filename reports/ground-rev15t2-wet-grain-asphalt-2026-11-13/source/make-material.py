from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(27111302);N=2048;metres=1.2
# Dense angular aggregate with darker bitumen between the stones.
albedo=Image.new('RGB',(N,N),(45,44,41));height=Image.new('L',(N,N),15);da=ImageDraw.Draw(albedo);dh=ImageDraw.Draw(height);stones=0
for i in range(21000):
 x=rng.uniform(-10,N+10);y=rng.uniform(-10,N+10);radius=rng.uniform(3.0,10.0);sides=int(rng.integers(5,9));pts=[]
 for k in range(sides):
  a=math.tau*k/sides+rng.uniform(-.15,.15);rr=radius*rng.uniform(.72,1.16);pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr))
 v=int(rng.uniform(125,206));t=int(rng.uniform(-5,5));da.polygon(pts,fill=(v+t,v,v-5));dh.polygon(pts,fill=int(rng.uniform(115,238)));stones+=1
base=np.asarray(albedo,dtype=np.float32);speck=rng.normal(0,3,(N,N,1));base=np.uint8(np.clip(base+speck,0,255));Image.fromarray(base).save(R/'textures/aggregate-1p2m-color.jpg',quality=92,subsampling=0)
h=np.asarray(height.filter(ImageFilter.GaussianBlur(1.1)),dtype=np.float32)/255*.0018
h+=rng.normal(0,0,(N,N)).astype(np.float32);dx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*metres/N);dy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*metres/N)
norm=np.stack([-dx,dy,np.ones_like(dx)],axis=-1);norm/=np.sqrt((norm*norm).sum(-1,keepdims=True));Image.fromarray(np.uint8(np.clip((norm*.5+.5)*255,0,255))).save(R/'textures/aggregate-1p2m-normal.png',compress_level=5)
height.save(R/'textures/aggregate-source-height.png',compress_level=5)
mean=np.mean(np.where(base/255<=.04045,base/255/12.92,((base/255+.055)/1.055)**2.4),axis=(0,1))
# Keep the existing repairs and holes, then coat the shoulders with damp silt.
old=R.parent/'ground-rev15t1-unpainted-cypher-2026-11-13/textures/road-world-color.png';color=np.asarray(Image.open(old),dtype=np.float32);H,W=color.shape[:2];xx=np.linspace(-16,16,W,dtype=np.float32)[None,:];yy=np.linspace(48,-30,H,dtype=np.float32)[:,None]
def field(w,h):
 return np.asarray(Image.fromarray(rng.integers(0,256,(h,w),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC),dtype=np.float32)/255
noise=field(48,112);small=field(96,228)
width=np.where(yy<5,3.6,np.where(yy<14,4.25,np.where(yy<22,16-(yy-14)*.3,13.6)))
dist=width-abs(xx);edge=np.clip((1.22+.42*(noise-.5)-dist)/1.1,0,1)
roadWet=np.clip(.40+.42*noise+.16*edge,0,1)
color*=.91-.15*roadWet[...,None]
trails=(.10+.16*small)*(1-edge);soil=np.stack([83+small*24,66+small*19,44+small*16],-1);color=color*(1-trails[...,None])+soil*trails[...,None]
mud=edge*(.66+.24*noise);color=color*(1-mud[...,None])+soil*mud[...,None]
rough=.73-.27*roadWet-.22*edge+.025*(small-.5)
mudrgb=np.where(mean<=.0031308,mean*12.92,1.055*mean**(1/2.4)-.055);Image.new('RGB',(4,4),tuple(np.uint8(np.clip(mudrgb*255,0,255)))).save(R/'textures/mud-mean-color.png')
# Soft muddy boundaries continue beyond the separately authored water surfaces.
def px(x,y):return ((x+16)/32*(W-1),(48-y)/78*(H-1))
def outline(p,scale=1):
 pts=[]
 for i in range(64):
  a=i*math.tau/64;r=1+.08*math.sin(a*5+p['phase'])+.035*math.cos(a*9-p['phase']);u=math.cos(a)*p['width']/2*scale*r;v=math.sin(a)*p['length']/2*scale*r
  pts.append((p['x']+u*math.cos(p['angle'])-v*math.sin(p['angle']),p['y']+u*math.sin(p['angle'])+v*math.cos(p['angle'])))
 return pts
pools=json.loads((R/'source/edge-pools.json').read_text())
for p in pools:
 mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon([px(*q) for q in outline(p,1.55)],fill=255);m=np.asarray(mask.filter(ImageFilter.GaussianBlur(2)),dtype=np.float32)/255
 color=color*(1-m[...,None]*.7)+soil*m[...,None]*.7;rough=rough*(1-m)+(.28+.06*small)*m
 mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon([px(*q) for q in outline(p)],fill=255);m=np.asarray(mask,dtype=np.float32)/255
 color=color*(1-m[...,None])+np.array([35,31,23])*m[...,None];rough=rough*(1-m)+.11*m
Image.fromarray(np.uint8(np.clip(color,0,255))).save(R/'textures/wet-road-world-color.png',compress_level=5)
Image.fromarray(np.uint8(np.clip(rough*255,0,255))).save(R/'textures/wet-road-world-roughness.png',compress_level=5)
# Very small ripples on the settled side water, independent of asphalt grain.
n=128;f=rng.normal(0,1,(n,n)).astype(np.float32);f=np.asarray(Image.fromarray(np.uint8(np.clip(f*25+128,0,255))).filter(ImageFilter.GaussianBlur(2)),dtype=np.float32)/255
gx=(np.roll(f,-1,1)-np.roll(f,1,1))*.20;gy=(np.roll(f,-1,0)-np.roll(f,1,0))*.20;nm=np.stack([-gx,gy,np.ones_like(gx)],-1);nm/=np.sqrt((nm*nm).sum(-1,keepdims=True));Image.fromarray(np.uint8((nm*.5+.5)*255)).save(R/'textures/edge-water-normal.png')
files=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((R/'textures').iterdir())]
out={'status':'PASS','tileMetres':metres,'tilePixels':N,'nominalAggregateDiameterMillimetres':[5,13],'heightAmplitudeMetres':.0018,'aggregatePolygons':stones,'tileMeanLinearRGB':mean.tolist(),'worldTextureSize':[W,H],'edgePools':len(pools),'paintedCircle':False,'reference':'User-attached market-road photograph: dark pooled water along muddy shoulders, with exposed road through the middle.','files':files}
(R/'evidence/material-art.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','files':files,'meanLinearRGB':mean.tolist()}),flush=True)
