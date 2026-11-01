import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path('/workspace/gullyverse-world-concept/2026-10-25/05-banner-organic-crowd-shop-shelves');rows=[]
for side,y,i in [(-1,-25,0),(-1,-7,2),(-1,2,3),(1,-16,1),(1,-7,2)]:
 o=bpy.data.objects[f'Building / {side} / {i}'];floor=6+1.2*min(1,max(0,(y+10)/24));origin=o.matrix_basis.inverted()@Vector((side*3.8,y,floor+1.5));direction=o.matrix_basis.inverted().to_3x3()@Vector((side,0,0));hit=o.ray_cast(origin,direction,distance=6);rows.append({'building':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'solidCuboid':len(o.data.vertices)==8 and len(o.data.polygons)==6,'rayHitsFrontAtWorld':list(o.matrix_basis@hit[1])if hit[0]else None,'proposedInteriorRecess':{'side':side,'centerY':y,'xDepthMetres':[4.0,7.8],'openingWidthM':6.2,'openingHeightM':2.85,'counterPreserved':True}})
(p/'evidence/shop-solid-host-and-recess-proposal.json').write_text(json.dumps(rows,indent=2)+'\n');print('SOLID_HOSTS',len(rows),all(r['solidCuboid']for r in rows))
