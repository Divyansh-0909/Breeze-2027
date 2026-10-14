"""Suppress oversized photo motifs in the outer-land material only.
Same licensed C5 source, same dark-earth colour mean and roughness family.
Accepted cliff maps remain byte-for-byte unchanged; no additional runtime maps.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'assets-source/gullyverse/quarry-foundation'
OUT=ROOT/'assets-source/gullyverse/quarry-foundation-refined/textures';OUT.mkdir(parents=True,exist_ok=True)
def lowpass(a,sigma):
    h,w=a.shape[:2];fy=np.fft.fftfreq(h)[:,None];fx=np.fft.fftfreq(w)[None,:]
    k=np.exp(-2*np.pi*np.pi*sigma*sigma*(fx*fx+fy*fy))
    if a.ndim==3:k=k[...,None]
    return np.fft.ifft2(np.fft.fft2(a,axes=(0,1))*k,axes=(0,1)).real
def periodic(a):
    n=a.shape[0];x=np.linspace(0,1,n)[None,:];y=x.T
    if a.ndim==3:x=x[...,None];y=y[...,None]
    a=a.copy();a-=x*(a[:,-1:]-a[:,:1]);a-=y*(a[-1:]-a[:1]);return a
def save(name,a):
    im=Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5))
    im.save(OUT/name,**({'quality':95,'subsampling':0}if name.endswith('.jpg')else{}))
base=np.asarray(Image.open(OLD/'textures/dry-terrain-basecolor.jpg').convert('RGB'),float)/255
source=periodic(base);grain=np.clip(source-lowpass(source,13),-.16,.16)
# Preserve dark dry-earth mean. Macro variation belongs to the world-space
# erosion/elevation vertex field, not giant rocks printed every22metres.
albedo=np.clip(base.mean((0,1))[None,None,:]+grain*.53,0,1)
save('dry-terrain-basecolor.jpg',albedo)
height=np.asarray(Image.open(OLD/'textures/dry-terrain-height.png').convert('L'),float)/255
h=lowpass(periodic(height)-lowpass(periodic(height),19),1.1)*.11
du=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*22/1024)
dv=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*22/1024)
normal=np.stack([-du,dv,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=-1)[...,None]
save('dry-terrain-normal.png',normal*.5+.5)
shutil.copy2(OLD/'textures/dry-terrain-orm.png',OUT/'dry-terrain-orm.png')
manifest={'scope':'Outer terrain only; all accepted cliff maps and material factors unchanged',
 'source':'Stage2C.5 CC0 rocky_terrain derived maps; retained photographic originals and provider provenance',
 'method':'Periodic high-frequency source residual,13px albedo lowpass and19px height lowpass; no generated random colour noise',
 'albedoMeanSRGB255':(albedo.mean((0,1))*255).tolist(),'tileMetres':22,
 'normalAmplitude':'Artistic shallow relief; not physical scan amplitude','maps':[]}
for p in sorted(OUT.iterdir()):manifest['maps'].append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT.parent/'terrain-material-refinement.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
