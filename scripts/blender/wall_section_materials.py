"""Original compatible cool-grey PBR maps, approved palette/grain in metre coordinates."""
from pathlib import Path
import numpy as np
from PIL import Image
from wall_section_surface import LOW,HIGH,SIZE,maps
root=Path(__file__).resolve().parents[2];out=root/'assets-source/gullyverse/first-wall-section/textures';out.mkdir(parents=True,exist_ok=True)
n=2048;x,y=np.meshgrid(LOW[0]+(np.arange(n)+.5)/n*SIZE[0],HIGH[1]-(np.arange(n)+.5)/n*SIZE[1]);color,micro,rough,ao=maps(x,y)
# Fine normal uses a separate metre-scaled UV channel: same approved mineral frequencies
# over a 12x10m microdetail tile, while albedo/AO stay unique to this complete face.
from rock_pilot_surface import value_noise
tx,ty=np.meshgrid(-6+(np.arange(n)+.5)/n*12,5-(np.arange(n)+.5)/n*10)
grain=value_noise(tx*44,ty*48,139);mid=value_noise(tx*2.9+ty*.31,ty*3.15,127);fine=value_noise(tx*116,ty*120,149);pores=np.maximum(0,value_noise(tx*21,ty*24,157)-.76)
fineheight=(grain-.5)*.0018+(mid-.5)*.0013+(fine-.5)*.0008-pores*.006
dy,dx=np.gradient(fineheight,10/n,12/n);normal=np.stack([-dx,dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1)[...,None]
for name,data in [('basecolor',color.astype(np.uint8)),('normal',np.clip((normal*.5+.5)*255,0,255).astype(np.uint8)),('roughness',np.uint8(rough*255)),('ao',np.uint8(ao*255))]:
 im=Image.fromarray(data);im.save(out/f'wall-{name}-2048.png');resolution=512 if name in ['roughness','ao'] else 1024;im=im.resize((resolution,resolution),Image.Resampling.LANCZOS)
 if name=='basecolor':im.save(out/'wall-basecolor-1024.jpg',quality=91,subsampling=0)
 else:im.save(out/f'wall-{name}-{resolution}.png')
print('Compatible grey maps authored. Base/normal1024, AO/rough512; same metric palette/grain; local .62m seam blend only.')
