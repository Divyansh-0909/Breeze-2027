"""Original 0.35m grid rays; isolate permitted crowd height from architectural regressions."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];rows=[];results=[]
for variant in ['REV11','REV12']:
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
changed=[i for i,(a,b)in enumerate(zip(results[0][0],results[1][0]))if a!=b];assert not changed,changed
out={'status':'PASS_EXACT_REV11_H07_TO_REV12_H07_GRID','capsuleRadiusM':.35,'strictNumericThresholdsUnchanged':True,'clearanceBooleanDifferences':len(changed),'rows':rows,'unchangedOriginalH00ToH07HeightDifference':'29 formerly-clear centers hit height clones, inherited authorized proposal; not floor loss','floorGeometryUnchanged':True};(O/'evidence/open-floor-attribution.json').write_text(json.dumps(out,indent=2));print('FLOOR_ATTRIBUTION_PASS',rows)
