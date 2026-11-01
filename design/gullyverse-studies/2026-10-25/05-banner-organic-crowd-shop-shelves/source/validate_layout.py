import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1]
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
def tree(objects,deps):
    verts=[];faces=[];owners=[]
    for o in objects:
        if o.type!='MESH' or o.name.startswith('Bounded lane haze'):continue
        ev=o.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles();base=len(verts)
        verts.extend(ev.matrix_world@v.co for v in mesh.vertices)
        faces.extend(tuple(base+i for i in t.vertices)for t in mesh.loop_triangles)
        owners.extend([o.name]*len(mesh.loop_triangles));ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces,all_triangles=True),owners
routes={'straightEntry':[(0,-27),(0,-10),(0,14),(0,22)],'straightScreen':[(0,22),(0,36.5)],'team':[(0,22),(12.8,22),(13.3,28)],'events':[(0,22),(-12.8,20.4),(-13.3,28)]}
records=[];rigs=[]
for scene in sorted(bpy.data.scenes,key=lambda s:s.name):
    bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    full,names=tree(scene.objects,deps);arch,_=tree(bpy.data.collections['00_SHARED_SITE_ARCHITECTURE'].objects,deps)
    surveys=[]
    for label,points in routes.items():
        errors=[];maxfloor=0;minimum=10;count=0
        for a,b in zip(points,points[1:]):
            steps=max(2,math.ceil(math.dist(a,b)/.3))
            for j in range(steps+1):
                t=j/steps;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t;z=floor(y);count+=1
                hit=arch.ray_cast(Vector((x,y,z+.3)),Vector((0,0,-1)),1)
                if hit[0]is None:errors.append({'type':'noFloor','point':[x,y,z]})
                else:maxfloor=max(maxfloor,abs(hit[0].z-z))
                for height in [.8,1.72]:
                    for angle in range(0,360,15):
                        rad=math.radians(angle);hit=full.ray_cast(Vector((x,y,z+height)),Vector((math.cos(rad),math.sin(rad),0)),1.6)
                        if hit[0]is not None:
                            minimum=min(minimum,hit[3])
                            if hit[3]<.35:errors.append({'type':'capsuleClearance','point':[x,y,z+height],'hit':names[hit[2]],'distance':hit[3]})
        surveys.append({'route':label,'samples':count,'capsuleRadiusM':.35,'floorToleranceM':.002,'maxFloorHeightErrorM':maxfloor,'minimumMeasuredRayClearanceM':minimum if minimum<10 else '>1.6','errors':errors})
    cam=bpy.data.objects['13-CONTINUOUS-STRAIGHT-WALK'];maxx=0;maxeye=0;maxyaw=0;collisions=[];ys=[]
    for frame in range(1,961):
        scene.frame_set(frame);bpy.context.view_layer.update();p=cam.location.copy();ys.append(p.y)
        maxx=max(maxx,abs(p.x));maxeye=max(maxeye,abs(p.z-floor(p.y)-1.72))
        direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1));maxyaw=max(maxyaw,abs(direction.x))
        for angle in range(0,360,30):
            rad=math.radians(angle);hit=full.ray_cast(p,Vector((math.cos(rad),math.sin(rad),0)),.35)
            if hit[0]is not None:collisions.append({'frame':frame,'hit':names[hit[2]],'distance':hit[3]})
    scene.frame_set(1);bpy.context.view_layer.update()
    rigs.append([{'name':o.name,'matrix':[list(r)for r in o.matrix_world],'lens':o.data.lens,'type':o.data.type}for o in sorted(bpy.data.collections['04_SHARED_CAMERA_RIG'].objects,key=lambda o:o.name)])
    records.append({'variant':scene['variant'],'routes':surveys,'walkFramesChecked':960,'maxAbsoluteX':maxx,'maxEyeHeightErrorM':maxeye,'maxViewDirectionX':maxyaw,'strictlyForwardY':all(b>a for a,b in zip(ys,ys[1:])),'cameraIntersectionsWithin035m':collisions})
assert rigs[0]==rigs[1]==rigs[2]
status='PASS'if all(not r['cameraIntersectionsWithin035m']and r['maxAbsoluteX']<1e-5 and r['maxEyeHeightErrorM']<.002 and r['maxViewDirectionX']<1e-5 and r['strictlyForwardY']and all(not s['errors']and s['maxFloorHeightErrorM']<.002 for s in r['routes'])for r in records)else'FAIL'
result={'status':status,'scope':'Blender concept only; not current website collision registry or regulatory certification. Existing numeric clearances/tolerances retained.','sharedABCCameras':True,'routes':routes,'variants':records,'crowdValidatedSeparately':'body-overlap-validation.json','protectedAisleHalfWidthM':1.65,'noHiddenScreenOrRevealRequirement':True}
(O/'evidence/layout-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('LAYOUT_VALIDATION',status,[(r['variant'],[(s['route'],len(s['errors']))for s in r['routes']],len(r['cameraIntersectionsWithin035m']))for r in records],flush=True)
assert status=='PASS'
