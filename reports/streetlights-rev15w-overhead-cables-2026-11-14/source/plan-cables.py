import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'source/lighting-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=plan['source']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for link,(ia,ib) in enumerate(plan['cableLinks']):
 a=plan['lamps'][ia];b=plan['lamps'][ib];count=3 if link<plan.get('sideLinkCount',8) else 2
 for wire in range(count):
  span=(Vector(b['position'])-Vector(a['position'])).length;sags=[min(1.12,max(.42,span*.033))+wire*.08,.35+wire*.1,.8+wire*.1,1.35+wire*.07];chosen=None;attempts=[]
  for mountingHeight in [5.61+wire*.06,5.55,5.70,5.80,5.45,5.9,5.35]:
   start=Vector(a['position'])+Vector((a['armDirection']*.065,(wire-1)*.045,mountingHeight));end=Vector(b['position'])+Vector((b['armDirection']*.065,(wire-1)*.045,mountingHeight))
   for sag in sags:
    points=[start.lerp(end,t)-Vector((0,0,4*sag*t*(1-t))) for t in [i/40 for i in range(41)]];hits=[]
    for p,q in zip(points,points[1:]):
     axis=q-p
     if axis.length<.0001:continue
     hit,loc,norm,idx,obj,matrix=s.ray_cast(dg,p,axis.normalized(),distance=axis.length)
     if hit:hits.append(obj.name)
    clearance=min(p.z-((1-i/40)*a['position'][2]+(i/40)*b['position'][2]) for i,p in enumerate(points));navHit=any(-3.45<p.x<3.45 and 10.7<p.y<11.25 and 9.0<p.z<14.5 for p in points);attempts.append({'sag':sag,'mountingHeight':mountingHeight,'hits':sorted(set(hits)),'navigationVolumeHit':navHit,'minimumInterpolatedRoadClearance':clearance})
    if not hits and not navHit and clearance>4.05:chosen=(points,sag,clearance);break
   if chosen:break
  assert chosen,('No unobstructed overhead cable path',ia,ib,wire,attempts)
  points,sag,clearance=chosen;rows.append({'from':a['id'],'to':b['id'],'wire':wire,'radius':.007 if wire==0 else .0045,'points':[list(p) for p in points],'sag':sag,'minimumInterpolatedRoadClearance':clearance,'obstructionAttempts':attempts})
plan['cables']=rows;plan['minimumCableClearance']=min(c['minimumInterpolatedRoadClearance'] for c in rows);plan['flickerPeriodSeconds']=8.4;plan['flickerKeys']=[[0,1],[1.7,1],[1.78,.18],[1.92,1],[4.6,1],[4.68,.35],[4.82,1],[6.75,1],[6.86,.06],[7.08,1],[8.4,1]];(R/'source/lighting-plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({'status':'PASS','cables':len(rows),'minimumClearance':plan['minimumCableClearance'],'noSourceMeshIntersections':True,'navigationTextVolumeAvoided':True}))
