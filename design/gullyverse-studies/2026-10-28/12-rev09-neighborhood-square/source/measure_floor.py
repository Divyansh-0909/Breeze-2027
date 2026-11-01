import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];result=[]
for variant in['SQUARE BEFORE','SQUARE C180']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();v=[];f=[]
 for o in s.objects:
  if o.type!='MESH'or o.name.startswith('Bounded lane haze'):continue
  ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();off=len(v);v.extend(ev.matrix_world@x.co for x in m.vertices);f.extend(tuple(off+i for i in p.vertices)for p in m.loop_triangles);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(v,f,all_triangles=True);cells=[]
 for ix in range(63):
  for iy in range(67):
   x=-15.5+ix*.5;y=14.5+iy*.5;blocked=False
   for z in[8.0,8.92]:
    for j in range(16):
     a=j*math.tau/16;hit=tree.ray_cast(Vector((x,y,z)),Vector((math.cos(a),math.sin(a),0)),.35)
     if hit[0]is not None:blocked=True;break
    if blocked:break
   cells.append(not blocked)
 result.append({'variant':variant,'gridSamples':len(cells),'gridStepM':.5,'capsuleRadiusM':.35,'heightsM':[.8,1.72],'clearCells':sum(cells),'clearCellsApproxAreaM2':sum(cells)*.25,'cells':cells})
a,b=result;regress=[i for i,(x,y)in enumerate(zip(a['cells'],b['cells']))if x and not y];assert not regress,regress[:20]
for r in result:r.pop('cells')
proof={'status':'PASS_NO_NEW_GRID_OBSTRUCTIONS','sourceFloorReferenceM2':1088,'sampledCenterGridAreaM2':63*67*.25,'method':'0.5m center grid and 16 horizontal clearance rays at .8/1.72m above unchanged floor; includes original crowd/props; estimate, not legal access certification. Full routes and exact crowd triangles checked separately.','newlyBlockedClearCells':len(regress),'rows':result};(O/'evidence/open-floor-comparison.json').write_text(json.dumps(proof,indent=2));print('OPEN_FLOOR_PASS',result,flush=True)
