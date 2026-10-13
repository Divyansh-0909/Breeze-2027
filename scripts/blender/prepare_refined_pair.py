"""Constrained-by-shared-boundary planar triangulation, NumPy/SciPy offline.
All LOD perimeter samples are identical. Only face INTERIOR sampling reduces.
Blender handles editable masters, normals/tangents/UVs and actual GLB export.
"""
from pathlib import Path
import numpy as np
from refined_quarry_geology import ROOT,IDS,build_section
out=ROOT/'assets-source/gullyverse/quarry-refinement/prepared';out.mkdir(parents=True,exist_ok=True)
for rid in IDS:
 for i,density in enumerate([(64,64,12,12,96,8),(32,32,6,6,96,8),(12,16,3,3,96,8)]):
  points,faces,u,v,tags,pinned=build_section(rid,96,96,density)
  np.savez_compressed(out/f'rock-{rid}-lod{i}.npz',points=points,faces=faces,uv0=u,uv1=v,tags=tags,pinned=pinned)
  print(rid,i,len(faces),len(points),flush=True)
