import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];rows=[]
for variant in['SQUARE BEFORE','SQUARE C180']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();v=[];f=[];names=[]
 for o in s.objects:
  if o.type!='MESH'or o.name.startswith('Bounded lane haze'):continue
  ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();off=len(v);v.extend(ev.matrix_world@x.co for x in m.vertices);f.extend(tuple(off+i for i in p.vertices)for p in m.loop_triangles);names.extend([o.get('pilotOriginalObject',o.name)]*len(m.loop_triangles));ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(v,f,all_triangles=True)
 targets=[('EXISTING GULLYVERSE hero raster',Vector((0,13,8.87))),('Existing Aftermovie / center',Vector((0,36.5,8.92)))]
 targets +=[(o.name,Vector(((1 if o.location.x>0 else -1)*10.8,o.location.y,8.92)))for o in s.objects if o.name.startswith(('TEAM authorized portrait','EVENTS clearly labelled'))]
 for name,origin in targets:
  o=bpy.data.objects[name];ps=[o.matrix_world@x.co for x in o.data.vertices];c=sum(ps,Vector())/len(ps);hits=[]
  for target in[c]+[c*.75+p*.25 for p in ps]:
   d=target-origin;h=tree.ray_cast(origin,d.normalized(),d.length+.02);hits.append(names[h[2]]if h[0]is not None else None)
  rows.append({'variant':variant,'target':name,'samples':len(hits),'visible':sum(h==name for h in hits),'firstHits':hits})
for r in rows:
 if r['variant']!='SQUARE BEFORE':
  a=next(x for x in rows if x['variant']=='SQUARE BEFORE'and x['target']==r['target']);assert r['visible']>=a['visible'],(r,a)
(O/'evidence/destination-sightlines.json').write_text(json.dumps({'status':'PASS_NO_NEW_OCCLUSION','rows':rows,'baselinePartialOcclusionsNotConcealed':True},indent=2)+'\n');print('SIGHTLINES_PASS',flush=True)
