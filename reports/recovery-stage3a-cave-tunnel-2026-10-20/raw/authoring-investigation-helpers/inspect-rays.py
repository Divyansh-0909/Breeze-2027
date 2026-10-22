import bpy,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
r=Path('/workspace/Breeze-2027-navigation');src=r/'assets-source/gullyverse/quarry-fidelity-correction/licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.objects['coastal_cliff_04_LOD2'];m=o.data
bv=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(p.vertices)for p in m.polygons],all_triangles=True)
for z in [1,3,5,7,9]:
 print('FRONT',z,[(x,round(hit[0].y,2)if hit[0]is not None else None)for x in [-25,-15,-5,0,5,15,25]for hit in [bv.ray_cast(Vector((x,-35,z)),Vector((0,1,0))) ]],flush=True)
