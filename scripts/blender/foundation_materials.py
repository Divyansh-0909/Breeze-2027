"""CC0 photographic source -> dark, tileable mineral microdetail, not fake scan.
Original source files remain intact. Large fractures are authored geometry;
recognisable leaf-litter/whole-rock motifs are deliberately suppressed here.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets-source/gullyverse/quarry-foundation'
OUT=SRC/'textures';OUT.mkdir(parents=True,exist_ok=True)

def load(asset,slot,n):
    path=next((SRC/'licensed-source'/asset).glob('*_'+slot+'_*'))
    im=Image.open(path);a=np.asarray(im)
    if a.max()>255:
        a=a.astype(float)/65535
        if a.ndim==2:a=np.repeat(a[...,None],3,axis=2)
        channels=[]
        for i in range(3):
            channel=Image.fromarray(a[...,i].astype(np.float32),mode='F').resize((n,n),Image.Resampling.BILINEAR)
            channels.append(np.asarray(channel))
        return np.stack(channels,axis=-1)
    return np.asarray(im.convert('RGB').resize((n,n),Image.Resampling.LANCZOS),dtype=float)/255

def lowpass(a,sigma):
    # Periodic Gaussian in frequency space: repeat-safe derivative and grain.
    h,w=a.shape[:2];fy=np.fft.fftfreq(h)[:,None];fx=np.fft.fftfreq(w)[None,:]
    kernel=np.exp(-2*np.pi*np.pi*sigma*sigma*(fx*fx+fy*fy))
    if a.ndim==3:kernel=kernel[...,None]
    return np.fft.ifft2(np.fft.fft2(a,axes=(0,1))*kernel,axes=(0,1)).real

def periodic(a):
    # Remove boundary jump without multiplying a repeating edge vignette.
    n=a.shape[0];x=np.linspace(0,1,n)[None,:];y=x.T
    if a.ndim==3:x=x[...,None];y=y[...,None]
    a=a.copy();a-=x*(a[:,-1:]-a[:,:1]);a-=y*(a[-1:]-a[:1])
    return a

def save(name,a,quality=95):
    im=Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5))
    im.save(OUT/name,**({'quality':quality,'subsampling':0}if name.endswith('.jpg')else{}))

spec=[]
for asset,family,n,metres in [('rock_face_04','dark-rock',2048,2),('rocky_terrain','dry-terrain',1024,90)]:
    rgb=load(asset,'diff',n);height=load(asset,'disp',n)[...,0]
    if family=='dark-rock':
        lum=rgb@np.array([.2126,.7152,.0722])
        # A source-derived mineral residual, not a pasted 2m fractured/leaf panel.
        residual=periodic(lum-lowpass(lum,18))
        residual=np.clip(residual,-.10,.10)
        broad=lowpass(periodic(lum),58);broad-=broad.mean()
        albedo=np.array([108.3,106.9,100.4])[None,None,:]/255
        albedo=np.clip(albedo+residual[...,None]*.56+broad[...,None]*.11,0,1)
        h=periodic(height-lowpass(height,22));h=lowpass(h,1.1)
        h=np.clip(h,-.12,.12)*.06 # chosen microrelief amplitude, not measured metres
        rough=np.clip(.91+(load(asset,'rough',n)[...,0]-.5)*.10,.84,.98)
        ao=np.clip(.94+np.minimum(h,0)*3,.90,1)
    else:
        albedo=periodic(rgb)*.64+np.array([.10,.10,.083]);albedo=np.clip(albedo,0,1)
        h=lowpass(periodic(height),1.2)*.7
        rough=np.clip(.91+(load(asset,'rough',n)[...,0]-.5)*.08,.85,.99)
        ao=np.clip(.9+.1*load(asset,'ao',n)[...,0],.89,1)
    du=(np.roll(h,-1,axis=1)-np.roll(h,1,axis=1))/(2*metres/n)
    dv=(np.roll(h,-1,axis=0)-np.roll(h,1,axis=0))/(2*metres/n)
    normal=np.stack([-du,dv,np.ones_like(du)],axis=-1)
    normal/=np.linalg.norm(normal,axis=-1)[...,None]
    save(family+'-basecolor.jpg',albedo)
    # Source remains2k;1k normal retains millimetre grain over a2m tile and
    # reduces upload/decoded cost. Renormalize after filtering the vectors.
    packed=[]
    for i in range(3):packed.append(np.asarray(Image.fromarray(normal[...,i].astype(np.float32),mode='F').resize((1024,1024),Image.Resampling.BILINEAR)))
    normal=np.stack(packed,axis=-1);normal/=np.maximum(1e-9,np.linalg.norm(normal,axis=-1))[...,None]
    save(family+'-normal.png',normal*.5+.5)
    # ORM uses shared R occlusion / G roughness / B metallic=0.
    orm=np.stack([ao,rough,np.zeros_like(rough)],axis=-1)
    Image.fromarray(np.uint8(orm*255+.5)).resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/(family+'-orm.png'))
    save(family+'-height.png',np.clip(h/(.024 if family=='dark-rock'else 1)+.5,0,1))
    spec.append({'family':family,'source':asset,'albedoMeanSRGB255':(albedo.mean((0,1))*255).tolist(),
                 'physicalUVTileMetres':metres,'albedoResolution':n,'normalResolution':1024,'ormResolution':1024,
                 'roughnessRange':[float(rough.min()),float(rough.max())],
                 'normalTechnique':'Periodic source-height residual gradients; amplitude selected artistically, not measured scan depth',
                 'sourceMethodClaim':'Photographic PBR source; capture method not certified by provider API'})
files=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in OUT.iterdir()if p.is_file()]
(SRC/'material-manifest.json').write_text(json.dumps({'license':'CC0','metallic':0,'lightingChanged':False,
    'rockColourReference':'Original Stage2A pilot mean, before any world lighting',
    'macroVariation':'Low-contrast vertex colour tied to actual stratigraphy and regional weathering; no mirrored atlas',
    'materials':spec,'files':files},indent=2))
print(json.dumps(spec,indent=2))
