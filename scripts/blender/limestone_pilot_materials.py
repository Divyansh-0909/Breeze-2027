"""Original unique-UV limestone PBR maps, source2048/runtime1024. No image sampling.
Run using ordinary Python with numpy and Pillow before author_limestone_pilot.py.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from limestone_pilot_surface import coordinates, slabs, dissolution
from rock_pilot_surface import value_noise as noise

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'assets-source/gullyverse/limestone-pilot/textures'
OUT.mkdir(parents=True, exist_ok=True)
n = 2048
u, v = np.meshgrid((np.arange(n)+.5)/n, 1-(np.arange(n)+.5)/n)
x, z = coordinates(np.clip((u-.02)/.86, 0, 1), np.clip((v-.03)/.94, 0, 1))
slab, gap = slabs(x, z)
large = noise(x*.48, z*.39, 121)
medium = noise(x*2.9+z*.31, z*3.15, 127)
grain = noise(x*44, z*48, 139)
fine = noise(x*116, z*120, 149)
pores = np.maximum(0, noise(x*21, z*24, 157)-.76)
solution = dissolution(x, z)
# Pale calcitic limestone, subtle warm fossil/mineral mottling and cool weathering stains.
variation = (large-.5)*22+(medium-.5)*11+(grain-.5)*8+(fine-.5)*4+slab*5
stain = np.clip((noise(x*.95+z*.12, z*.33, 163)-.57)*2.9, 0, 1)
iron = np.maximum(0, noise(x*8.7+z*.42, z*9.3, 167)-.77)*55
calcite = np.maximum(0, noise(x*13, z*12.6, 173)-.73)*28
color = np.stack([224+variation, 221+variation, 208+variation], axis=-1)
color -= stain[...,None]*np.array([16,15,11])
color[...,0] += iron*.18+calcite
color[...,1] -= iron*.16-calcite
color[...,2] -= iron*.45-calcite
cracks = 1-.14*np.exp(-(gap/.035)**2)
solution_shade = 1-np.clip(solution/.11, 0, 1)*.13
color *= (cracks*solution_shade)[...,None]
color -= pores[...,None]*35
color = np.clip(color, 95, 248).astype(np.uint8)
# Fine granular calcite/pitting, with larger solution cavities authored in geometry.
height = (grain-.5)*.0018+(medium-.5)*.0013+(fine-.5)*.0008-pores*.006
dz, dx = np.gradient(height, 10/n/.94, 12/n/.86)
norm = np.stack([-dx, dz, np.ones_like(dx)], axis=-1)
norm /= np.linalg.norm(norm, axis=-1)[...,None]
normal = np.clip((norm*.5+.5)*255, 0, 255).astype(np.uint8)
rough = np.clip(.9+(grain-.5)*.09+(medium-.5)*.04+stain*.025+pores*.08, .82, .99)
ao = np.clip(.985-(1-cracks)*.28-np.clip(solution/.11, 0, 1)*.13, .80, 1)
for name, arr in [('basecolor',color),('normal',normal),('roughness',(rough*255).astype(np.uint8)),('ao',(ao*255).astype(np.uint8))]:
    im = Image.fromarray(arr)
    im.save(OUT/f'limestone-{name}-2048.png')
    runtime = im.resize((1024,1024), Image.Resampling.LANCZOS)
    if name == 'basecolor':
        runtime.save(OUT/'limestone-basecolor-1024.jpg', quality=92, subsampling=0)
    else:
        runtime.save(OUT/f'limestone-{name}-1024.png')
print('Original pale limestone source/runtime maps generated at', OUT)
