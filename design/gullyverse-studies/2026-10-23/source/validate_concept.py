import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];scenes=sorted(bpy.data.scenes,key=lambda s:s.name);results=[]
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
def tree(objects,deps):
 verts=[];faces=[];owners=[]
 for o in objects:
  if o.type!='MESH'or o.name.startswith('Bounded lane haze'):continue
  m=o.evaluated_get(deps).to_mesh();m.calc_loop_triangles();base=len(verts);verts.extend([o.matrix_world@v.co for v in m.vertices]);faces.extend([tuple(base+i for i in t.vertices)for t in m.loop_triangles]);owners.extend([o.name]*len(m.loop_triangles));o.evaluated_get(deps).to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces,all_triangles=True),owners
route={'entry':[(0,-27),(0,-12),(0,4),(-1.8,7.8),(-6.1,10.9),(-6.1,18),(0,22)],'screen':[(0,22),(0,25.2),(-.7,30.7),(.45,33.3),(0,36.5)],'team':[(0,22),(12.8,22),(13.3,28)],'events':[(0,22),(-12.8,20.4),(-13.3,28)]}
shared_ids={c.name:[o.name for o in c.objects]for c in bpy.data.collections if c.name.startswith(('00_','01_','02_','03_','04_'))};rig=[]
for scene in scenes:
 bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();full,names=tree(scene.objects,deps);arch,archNames=tree(bpy.data.collections['00_SHARED_SITE_ARCHITECTURE'].objects,deps)
 # Screen rays stop at actual visible image plane; haze is excluded as a participating volume.
 visibility={}
 for camera in ['01-landing','03-opening','09-screen-reveal']:
  origin=bpy.data.objects[camera].location;checks=[]
  for panel in [o for o in scene.objects if o.name.startswith('Existing Aftermovie /')]:
   for u,v in [(-.45,-.45),(0,0),(.45,.45),(-.45,.45),(.45,-.45)]:
    target=panel.matrix_world@Vector((u,v,0));delta=target-origin;hit=full.ray_cast(origin,delta.normalized(),delta.length+.01);visible=hit[0]is None or hit[3]>=delta.length-.025
    checks.append({'panel':panel.name,'visible':visible,'firstHit':names[hit[2]]if hit[2]is not None else None,'distance':hit[3]})
  visibility[camera]={'visible':sum(c['visible']for c in checks),'samples':len(checks),'rays':checks}
 silhouettes=[]
 for i,(x,y)in enumerate([(1.9,7.8),(2.9,8.8),(1.7,9.8)]):
  origin=bpy.data.objects['01-landing'].location;target=Vector((x,y,floor(y)+1.5));d=target-origin;hit=arch.ray_cast(origin,d.normalized(),d.length-.05);silhouettes.append({'id':i,'unblockedByArchitecture':hit[0]is None,'firstHit':archNames[hit[2]]if hit[2]is not None else None})
 surveys=[]
 for label,points in route.items():
  bad=[];minclear=10;floorError=0;count=0
  for a,b in zip(points,points[1:]):
   dist=math.dist(a,b);steps=max(2,math.ceil(dist/.3))
   for j in range(steps+1):
    t=j/steps;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t;z=floor(y);count+=1
    hit=arch.ray_cast(Vector((x,y,z+.3)),Vector((0,0,-1)),1)
    if hit[0]is None:bad.append({'type':'noFloor','point':[x,y,z]})
    else:floorError=max(floorError,abs(hit[0].z-z))
    for height in [.8,1.72]:
     for angle in range(0,360,15):
      rad=math.radians(angle);hit=full.ray_cast(Vector((x,y,z+height)),Vector((math.cos(rad),math.sin(rad),0)),1.6)
      if hit[0]is not None:
       minclear=min(minclear,hit[3])
       if hit[3]<.35:bad.append({'type':'capsuleClearance','point':[x,y,z+height],'hit':names[hit[2]],'distance':hit[3]})
  surveys.append({'route':label,'samples':count,'capsuleRadiusM':.35,'horizontalProbeLimitM':1.6,'minimumMeasuredRayClearanceM':minclear if minclear<10 else '>1.6','maxFloorHeightErrorM':floorError,'errors':bad})
 # Actual editable animated camera path: all 480 frames, bounded side clearance.
 motion=[];cam=bpy.data.objects['13-CROWD-MOVE-20s']
 for f in [*range(1,481,12),480]:
  scene.frame_set(f);bpy.context.view_layer.update();p=cam.location.copy();near=[]
  for angle in range(0,360,30):
   rad=math.radians(angle);hit=full.ray_cast(p,Vector((math.cos(rad),math.sin(rad),0)),.35)
   if hit[0]is not None:near.append(names[hit[2]])
  motion.append({'frame':f,'position':list(p),'cameraIntersectionsWithin035m':near})
 scene.frame_set(1);cameraRows=[{'name':o.name,'matrix':[list(r)for r in o.matrix_world],'lens':o.data.lens,'sensor':o.data.sensor_width,'type':o.data.type}for o in bpy.data.collections['04_SHARED_CAMERA_RIG'].objects];rig.append(cameraRows)
 results.append({'variant':scene['variant'],'screenVisibility':visibility,'distantSilhouettes':silhouettes,'routes':surveys,'cameraMoveSamples':motion,'actualLightCount':sum(o.type=='LIGHT'for o in scene.objects),'meshObjects':sum(o.type=='MESH'for o in scene.objects),'sharedCollections':{c.name:[o.name for o in c.objects]for c in scene.collection.children if c.name in shared_ids}})
assert rig[0]==rig[1]==rig[2],'Matched camera rig changed'
for r in results:assert r['sharedCollections']==shared_ids,'Shared layout changed'
status='PASS'if all(not s['errors']and s['maxFloorHeightErrorM']<.002 for r in results for s in r['routes'])and all(r['screenVisibility']['01-landing']['visible']==0 and r['screenVisibility']['09-screen-reveal']['visible']>=12 and all(s['unblockedByArchitecture']for s in r['distantSilhouettes'])and not any(p['cameraIntersectionsWithin035m']for p in r['cameraMoveSamples'])for r in results)else'REVIEW_FAILURES'
(O/'evidence/concept-feasibility.json').write_text(json.dumps({'status':status,'scope':'Concept mesh/ray/capsule feasibility only; not current website collision/runtime/device verification. No current registry coordinate compatibility claimed.','matchedCameraRig':True,'sharedSiteGeometry':True,'routePolylines':route,'results':results},indent=2));print(status,[(r['variant'],[(k,v['visible'])for k,v in r['screenVisibility'].items()],[(s['route'],len(s['errors']),s['maxFloorHeightErrorM'])for s in r['routes']])for r in results],flush=True)
