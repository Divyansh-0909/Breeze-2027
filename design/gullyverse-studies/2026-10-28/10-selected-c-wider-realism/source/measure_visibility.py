import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from world_cameras import add
rows=[]
for variant in['C+A PILOT','C+A WORLD']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);add(s);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();v=[];f=[];names=[]
 for o in s.objects:
  if o.type not in{'MESH','CURVE','FONT'}or o.name.startswith('Bounded lane haze'):continue
  ev=o.evaluated_get(dep);m=ev.to_mesh()
  if m:
   m.calc_loop_triangles();off=len(v);v.extend(ev.matrix_world@x.co for x in m.vertices);f.extend(tuple(off+i for i in p.vertices)for p in m.loop_triangles);names.extend([o.name]*len(m.loop_triangles))
  ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(v,f,all_triangles=True)
 for pose in['01-lane-entry','02-whole-street','04-shop-group-left','10-lane-roof-transition','11-rooftop-wide','17-rooftop-reverse','18-mobile-lane']:
  cam=bpy.data.objects['WORLD REVIEW / '+pose];portrait='mobile'in pose;s.render.resolution_x=576 if portrait else 1280;s.render.resolution_y=1024 if portrait else 720;fr=cam.data.view_frame(scene=s);lo=Vector((min(p.x for p in fr),min(p.y for p in fr),fr[0].z));hi=Vector((max(p.x for p in fr),max(p.y for p in fr),fr[0].z));counts={}
  for y in range(45):
   for x in range(80):
    q=Vector((lo.x+(hi.x-lo.x)*(x+.5)/80,lo.y+(hi.y-lo.y)*(y+.5)/45,lo.z));hit=tree.ray_cast(cam.location,(cam.matrix_world.to_3x3()@q).normalized(),250);name=names[hit[2]]if hit[0]is not None else'SKY';counts[name]=counts.get(name,0)+1
  rows.append({'variant':variant,'pose':pose,'grid':[80,45],'newConstructionPercent':sum(n for k,n in counts.items()if k.startswith('WORLD static /'))/36,'updatedSurfacePercent':sum(n for k,n in counts.items()if k.startswith('WORLD /'))/36,'silhouetteOccupancyPercent':100-counts.get('SKY',0)/36,'counts':counts})
(O/'evidence/visibility-coverage.json').write_text(json.dumps({'status':'MEASURED','method':'coarse evaluated first-hit camera rays; haze excluded; coverage is not a realism score','rows':rows},indent=2)+'\n');print('COVERAGE_MEASURED',flush=True)
