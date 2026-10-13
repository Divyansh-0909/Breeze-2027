import bpy,numpy as np,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=str(Path.cwd()/'assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend'))
o=bpy.data.objects['Refined_Rock_22_LOD0'];o.data.calc_loop_triangles()
for i in [631,9426,9553,146]:
 t=o.data.loop_triangles[i];print(i,[[float(x)for x in o.data.vertices[j].co]for j in t.vertices],t.normal[:],flush=True)
