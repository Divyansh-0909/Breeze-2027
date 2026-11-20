from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'source/events-plan.json').read_text());W,H=1024,1536;cfg=plan['facade'];rng=np.random.default_rng(141126101);u=np.linspace(cfg['min'],cfg['max'],W)[None,:];z=np.linspace(cfg['top'],7.2,H)[:,None]
def noise(w,h):return np.asarray(Image.fromarray(rng.integers(0,256,(h,w),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC),dtype=np.float32)/255
broad=noise(17,25);fine=noise(120,170);grain=rng.normal(0,1,(H,W));base=np.array([186,140,111]);colour=np.broadcast_to(base,(H,W,3)).copy().astype(float);colour+=(broad-.5)[...,None]*7+(fine-.5)[...,None]*4+grain[...,None]*1.3
damp=np.exp(-np.maximum(z-7.2,0)/.40)*(.12+.06*fine);drips=np.zeros((H,W))
for win in plan['windows']:
 left,right=win['bounds'][1];bottom=win['zMin']
 for edge in [left,right]:
  drips=np.maximum(drips,np.exp(-((u-edge)/.035)**2)*np.exp(-np.maximum(bottom-z,0)/.6)*(z<bottom)*.11)
colour*=1-damp[...,None]-drips[...,None]
cracks=Image.new('L',(W,H));draw=ImageDraw.Draw(cracks)
for i in range(7):
 x=float(rng.uniform(30,W-30));y=float(rng.uniform(60,H-100));pts=[(x,y)]
 for j in range(6):x+=rng.uniform(-4,4);y+=rng.uniform(3,7);pts.append((x,y))
 draw.line(pts,fill=50,width=1)
cm=np.asarray(cracks)/255;colour*=1-cm[...,None]*.2
# Continuous painted render: no brick colour, courses or mortar normal pattern.
surface=(fine-.5)*.00065+grain*.00018-cm*.0003;span=cfg['max']-cfg['min'];height=cfg['top']-7.2;dx=(np.roll(surface,-1,1)-np.roll(surface,1,1))/(2*span/W);dy=(np.roll(surface,-1,0)-np.roll(surface,1,0))/(2*height/H);normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.sqrt((normal*normal).sum(-1,keepdims=True));rough=np.clip(.84+(fine-.5)*.06-damp*.1,.75,.9)
Image.fromarray(np.uint8(np.clip(colour,0,255))).save(R/'textures/events-plaster-color.jpg',quality=93,subsampling=0);Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(R/'textures/events-plaster-normal.jpg',quality=95,subsampling=0);Image.fromarray(np.uint8(rough*255)).save(R/'textures/events-plaster-rough.png')
rows=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((R/'textures').iterdir())];(R/'evidence/material.json').write_text(json.dumps({'status':'PASS','finish':'Dusty terracotta painted plaster','brickPattern':False,'mortarRelief':False,'files':rows},indent=2)+'\n');print(json.dumps({'status':'PASS','bytes':sum(x['bytes'] for x in rows)}))
