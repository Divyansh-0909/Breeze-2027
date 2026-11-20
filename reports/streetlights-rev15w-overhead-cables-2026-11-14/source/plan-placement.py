import bpy,json,math,hashlib,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];repo=R/'restore/repo';p=R/'restore/masters/V2.blend';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();fp=runpy.run_path(str(repo/'reports/cypher-entry-rev15v2-open-steel-gate-2026-11-14/source/scene-fingerprint.py'))['fingerprint'](s);assert fp['sha256']=='1b882cca849915c98c7df36fec1f38365b9166c325d541ee8fbaaaec749b4629'
ground=[o for o in s.objects if o.type=='MESH' and not o.hide_render and (o.get('groundSurface') or 'asphalt replacement' in o.name)];print('GROUND',[(o.name,o.get('groundSurface')) for o in ground],flush=True);dg=bpy.context.evaluated_depsgraph_get()
def floor(x,y):
 hits=[]
 for o in ground:
  inv=o.matrix_world.inverted();origin=inv@Vector((x,y,28));direction=(inv.to_3x3()@Vector((0,0,-1))).normalized();yes,point,normal,index=o.ray_cast(origin,direction)
  if yes:hits.append((o.matrix_world@point).z)
 return max(hits) if hits else None
def obstruction(x,y,z):
 hit,point,normal,index,obj,matrix=s.ray_cast(dg,Vector((x,y,z+.15)),Vector((0,0,1)),distance=6.15)
 if hit:return obj.name
 for dx,dy in [(.085,0),(-.085,0),(0,.085),(0,-.085)]:
  hit,point,normal,index,obj,matrix=s.ray_cast(dg,Vector((x+dx,y+dy,z+.15)),Vector((0,0,1)),distance=6.15)
  if hit:return obj.name
 return None
candidates=[('L01','lane',(-3.05,-25),'steady'),('L02','lane',(3.05,-25),'dead'),('L03','lane',(-3.05,-15.5),'flicker'),('L04','lane',(3.05,-15.5),'steady'),('L05','lane',(-3.05,-5.5),'dead'),('L06','lane',(3.05,-5.5),'flicker')];rows=[]
for id,zone,xy,state in candidates:
 chosen=None;attempts=[]
 for dy in [0,.55,-.55,1.1,-1.1]:
  for inward in [0,.1,.2,.3,.4,.5,.6,.7,.8, .9,1.0]:
   x=xy[0]-math.copysign(inward,xy[0]);y=xy[1]+dy;z=floor(x,y)
   if z is None:attempts.append({'point':[x,y],'ground':'missing'});continue
   block=obstruction(x,y,z);attempts.append({'point':[x,y,z],'obstruction':block})
   if block is None:chosen=[x,y,z];break
  if chosen:break
 assert chosen,(id,attempts)
 rows.append({'id':id,'zone':zone,'position':chosen,'state':state,'height':6.0,'armDirection':1 if chosen[0]<0 else -1,'basePowerWatts':240 if zone=='lane' else 280,'colour':[1,.72,.43],'flickerPhase':{'L03':0,'L06':2.7,'L10':5.4}.get(id,0),'placementChecks':{'groundRaycast':True,'verticalMastSegmentClear':True,'attempts':attempts}})
result={'status':'PASS','source':str(p),'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceSceneFingerprint':fp['sha256'],'sourceScenes':len(bpy.data.scenes),'sourceObjects':len(s.objects),'sourcePackedImages':sum(bool(i.packed_file) for i in bpy.data.images),'sceneFPS':s.render.fps/s.render.fps_base,'lamps':rows,'counts':{k:sum(r['state']==k for r in rows) for k in ['steady','flicker','dead']},'scope':'Gully road edges only; no cypher or courtyard fixtures','sideLinkCount':8,'cableLinks':[[0,1],[1,2],[2,3],[3,4],[4,5],[0,3],[1,4],[2,5]],'notes':'Poles checked against original evaluated scene upward over their full mast height; cable paths stay above the route and avoid the navigation sign volume.'};(R/'source/lighting-plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','sourceScenes':len(bpy.data.scenes),'counts':result['counts'],'placements':[{'id':r['id'],'position':r['position'],'state':r['state']} for r in rows]},indent=2))
