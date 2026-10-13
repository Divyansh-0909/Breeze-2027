"""Original non-tiled stone texture authoring. No photographed textures or external art.
Run with ordinary Python (numpy/Pillow), before author_rock_pilot_2a.py.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from rock_pilot_surface import coordinates,slabs
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets-source/gullyverse/rock-pilot-2a/textures'
OUT.mkdir(parents=True,exist_ok=True)
def noise(x,y,seed):
 ix=np.floor(x).astype(np.int64);iy=np.floor(y).astype(np.int64);fx=x-ix;fy=y-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 def rnd(a,b):
  n=(a*374761393+b*668265263+seed*1442695041)&0xffffffff;n=(n^(n>>13))*1274126177&0xffffffff
  return ((n^(n>>16))&0xffffffff)/4294967295
 a=rnd(ix,iy);b=rnd(ix+1,iy);c=rnd(ix,iy+1);d=rnd(ix+1,iy+1)
 return (a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy
n=2048
u,v=np.meshgrid((np.arange(n)+.5)/n,1-(np.arange(n)+.5)/n)
x,z=coordinates(np.clip((u-.02)/.86,0,1),np.clip((v-.03)/.94,0,1))
slab,gap=slabs(x,z)
large=noise(x*.51,z*.43,27);mid=noise(x*2.8+z*.3,z*3.1,31);grains=noise(x*38,z*41,19);fine=noise(x*110,z*116,12)
warp=.21*noise(x*.83,z*.7,15)+.12*np.sin(x*.48)+.035*x
bed=z+warp
bands=.5+.5*np.sin(bed*10.7+noise(x*.42,z*.37,55)*2.3)
cracks=np.ones_like(x);joints=np.ones_like(x)
for j,height in enumerate([.69,1.54,2.28,3.48,4.11,5.44,6.23,7.39,8.6,9.36]):
 line=height+.08*np.sin(x*(.65+j*.09)+j*1.7)+.018*x
 d=np.abs(z-line)
 cracks=np.minimum(cracks,1-.20*np.exp(-(d/.038)**2))
for j,(px,pz,slope) in enumerate([(-4.8,1.9,.16),(-2.7,4.5,-.15),(.4,2.3,.11),(3.5,7.5,-.13),(5.1,4.6,.12),(-4.2,8.1,-.08),(1.1,8.7,.21),(2.3,5.1,.25)]):
 d=np.abs(x-px-slope*(z-pz)-.028*np.sin(z*8+j));fade=np.exp(-((z-pz)/1.9)**4)
 joints=np.minimum(joints,1-.20*np.exp(-(d/.031)**2)*fade)
variation=(large-.5)*29+(mid-.5)*13+(grains-.5)*17+(fine-.5)*7+(bands-.5)*6
variation+=slab*13
color=np.stack([110+variation+(large-.5)*8,109+variation,103+variation-(mid-.5)*7],axis=-1)*((cracks*joints*(1-.13*np.exp(-(gap/.03)**2)))[...,None])
# Sparse original iron mineral veins and pale mineral inclusions; no periodic tile repeat.
mineral=np.maximum(0,noise(x*9+z*.7,z*11,87)-.73)*90
color[...,0]+=mineral*.7;color[...,1]+=mineral*.3
color=np.clip(color,25,174).astype(np.uint8)
h=(grains-.5)*.004+(mid-.5)*.003+(fine-.5)*.0016
# Map covers unique front patch; OpenGL tangent +Y convention. Geometric bed fractures are already in mesh.
dz,dx=np.gradient(h,10/n/.94,12/n/.86);ny=dz # image rows run toward negative world Z
norm=np.stack([-dx,ny,np.ones_like(dx)],axis=-1);norm/=np.linalg.norm(norm,axis=-1)[...,None]
normal=np.clip((norm*.5+.5)*255,0,255).astype(np.uint8)
rough=np.clip(.88+(grains-.5)*.12+(mid-.5)*.065+(1-cracks*joints*(1-.13*np.exp(-(gap/.03)**2)))*.10,.76,.99)
ao=np.clip(.98-(1-cracks*joints*(1-.13*np.exp(-(gap/.03)**2)))*.39,.70,1)
for name,arr in [('basecolor',color),('normal',normal),('roughness',(rough*255).astype(np.uint8)),('ao',(ao*255).astype(np.uint8))]:
 im=Image.fromarray(arr);im.save(OUT/f'rock-{name}-2048.png')
 runtime=im.resize((1024,1024),Image.Resampling.LANCZOS)
 if name=='basecolor':runtime.save(OUT/'rock-basecolor-1024.jpg',quality=92,subsampling=0)
 else:runtime.save(OUT/f'rock-{name}-1024.png')
print('Original 2048 source maps / 1024 runtime maps generated at',OUT)
