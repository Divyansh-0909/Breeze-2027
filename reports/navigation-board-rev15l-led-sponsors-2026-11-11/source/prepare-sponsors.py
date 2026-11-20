import json,hashlib,re,subprocess,shutil,io
from pathlib import Path
import numpy as np
from PIL import Image
import cairosvg

O=Path(__file__).resolve().parents[1];R=O.parents[1]
(O/'viewer/logos').mkdir(exist_ok=True)
files={}
for folder in ['public/images/sponsors','public/spons-image']:
 for p in sorted((R/folder).glob('*.png')):
  key=re.sub(r'\s*\(\d+\)$','',p.stem).lower();files.setdefault(key,p)
seen={};logos=[];duplicates=[]
priority=['stoknchill','group108','redbull','pepsi','cocacola','jio','amd']
for key in sorted(files,key=lambda k:(priority.index(k) if k in priority else 999,k)):
 p=files[key];data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if digest in seen:duplicates.append({'source':str(p.relative_to(R)),'sameAs':seen[digest]});continue
 seen[digest]=str(p.relative_to(R));original=O/'inputs/logos'/p.name;shutil.copy2(p,original)
 raster=O/'viewer/logos'/p.name;kind='original PNG'
 if data.lstrip().startswith(b'<svg') or data.lstrip().startswith(b'<?xml'):
  # Render the repository vector artwork faithfully; do not redraw sponsor marks.
  assert b'<script' not in data and b'<!ENTITY' not in data
  cairosvg.svg2png(bytestring=data,write_to=str(raster),output_width=1024)
  kind='SVG stored with .png extension; faithfully rasterized using CairoSVG'
 else:
  source_image=Image.open(p)
  if source_image.format!='PNG':
   source_image.convert('RGBA').save(raster,'PNG')
   kind=source_image.format+' stored with .png extension; lossless decoded-pixel PNG encoding'
  else:shutil.copy2(p,raster)
 im=Image.open(raster).convert('RGBA');arr=np.array(im)/255;alpha=arr[:,:,3];rgb=arr[:,:,:3]
 transparent=float((alpha<.05).mean())>.005
 corners=np.concatenate([rgb[:3,:3].reshape(-1,3),rgb[-3:,:3].reshape(-1,3),rgb[:3,-3:].reshape(-1,3),rgb[-3:,-3:].reshape(-1,3)])
 bg=np.median(corners,axis=0)
 if transparent:
  ay,ax=np.where(alpha>.05)
  if len(ax):
   x0,x1,y0,y1=int(ax.min()),int(ax.max()+1),int(ay.min()),int(ay.max()+1)
   if (alpha[y0:y1,x0:x1]>.05).mean()>.93:
    border=np.concatenate([rgb[y0,x0:x1],rgb[y1-1,x0:x1],rgb[y0:y1,x0],rgb[y0:y1,x1-1]])
    bg=np.median(border,axis=0);transparent=False
 mask=alpha>.05 if transparent else (np.max(abs(rgb-bg),axis=2)>.12)&(alpha>.05)
 whiteOnly=bool((np.min(rgb[alpha>.2],axis=1)>.85).mean()>.85)
 yy,xx=np.where(mask);box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else [0,0,im.width,im.height]
 aspect=(box[2]-box[0])/(box[3]-box[1]);logoW=min(150,48*aspect);logoH=logoW/aspect;tile=2*int(np.ceil(max(64,logoW+24)/2))
 logos.append({'index':len(logos),'name':p.stem,'source':str(p.relative_to(R)),'originalFile':'inputs/logos/'+p.name,'file':'viewer/logos/'+p.name,'sourceSHA256':digest,'sha256':hashlib.sha256(raster.read_bytes()).hexdigest(),'bytes':raster.stat().st_size,'sourceKind':kind,'size':[im.width,im.height],'transparentBackground':transparent,'whiteOnly':whiteOnly,'backgroundRGB':bg.tolist(),'bounds':box,'uv':[box[0]/im.width,1-box[3]/im.height,box[2]/im.width,1-box[1]/im.height],'tileCells':tile,'logoCells':[logoW,logoH]})
period=0
for r in logos:r['startCell']=period;period+=r['tileCells']
m={'version':'REV15L','branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'gitHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'authority':'User identifies the current branch sponsor-logo bank as past sponsors. Include all unique available logo assets; no invented marks or new sponsor claims.','sourceDirectories':['public/images/sponsors','public/spons-image'],'duplicatesExcluded':duplicates,'logoCount':len(logos),'periodCells':period,'screenCells':[384,64],'cellsPerSecond':30,'logos':logos}
(O/'evidence/sponsors.json').write_text(json.dumps(m,indent=2));(O/'viewer/sponsors.json').write_text(json.dumps(m,indent=2))
print(json.dumps({'logos':len(logos),'periodCells':period,'loopSeconds':period/30,'sourceBytes':sum(r['bytes'] for r in logos),'duplicates':duplicates}))
