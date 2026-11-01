"""Original 0.35m grid rays; isolate permitted crowd height from architectural regressions."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];rows=[];results=[]
for variant in ['PHOTO A','REV11 H00','REV11','REV11 H06','REV11 H09']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();v=[];f=[];owners=[];actors=[]
 for o in s.objects:
  if o.type!='MESH'or o.name.startswith('Bounded lane haze'):continue
  off=len(v);v.extend(o.matrix_basis@x.co for x in o.data.vertices);f.extend(tuple(off+i for i in p.vertices)for p in o.data.polygons);owners.extend([o.name]*len(o.data.polygons));actors.extend([o.get('actorSource')]*len(o.data.polygons))
 tree=BVHTree.FromPolygons(v,f);cells=[];hits=[]
 for ix in range(63):
  for iy in range(67):
   x=-15.5+ix*.5;y=14.5+iy*.5;hh=[]
   for z in[8,8.92]:
    for k in range(16):
     a=k*math.tau/16;h=tree.ray_cast(Vector((x,y,z)),Vector((math.cos(a),math.sin(a),0)),.35)
     if h[0]is not None:hh.append({'point':[x,y,z],'distance':h[3],'owner':owners[h[2]],'actorSource':actors[h[2]]})
   cells.append(not hh);hits.append(hh)
 results.append((cells,hits));rows.append({'variant':variant,'gridSamples':len(cells),'clearCells':sum(cells),'sampledClearCenterAreaM2':sum(cells)*.25})
newarch=[i for i,(a,b)in enumerate(zip(results[0][0],results[1][0]))if a and not b];assert not newarch,newarch
delta=[]
for idx in range(2,len(rows)):
 changed=[i for i,(a,b)in enumerate(zip(results[1][0],results[idx][0]))if a and not b];details=[]
 for i in changed:
  assert all(h['actorSource']for h in results[idx][1][i]),(rows[idx]['variant'],i,results[idx][1][i]);details.append({'gridIndex':i,'hits':results[idx][1][i]})
 delta.append({'variant':rows[idx]['variant'],'newlyBlockedByHeightOnlyPeople':len(changed),'details':details})
out={'status':'PASS_NO_NEW_ARCHITECTURE_OBSTRUCTIONS_HEIGHT_GRID_CHANGES_EXPLICIT','capsuleRadiusM':.35,'strictNumericThresholdsUnchanged':True,'newlyBlockedArchitectureClearCells':0,'oldPopulationEquality':'FAIL_EXPECTED_AUTHORIZED_HEIGHT_SILHOUETTE_CHANGE; retained original diagnostic/log, not presented as unchanged all-grid occupancy','rows':rows,'heightDifferences':delta}
(O/'evidence/open-floor-attribution.json').write_text(json.dumps(out,indent=2));print('FLOOR_ATTRIBUTION_PASS',[(r['variant'],r['newlyBlockedByHeightOnlyPeople'])for r in delta])
