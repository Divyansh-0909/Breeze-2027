import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15X1-Accommodation-Clean-Wall.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();d=json.loads((R/'evidence/survey.json').read_text());window=json.loads((R.parent/'cypher-houses-rev15v-walls-windows-2026-11-14/source/architecture-plan.json').read_text());w=next(w for w in window['windows']if w['id']=='R1-W23');n=Vector(w['normal']);t=Vector(w['tangent']);u0=(w['uMin']+w['uMax'])/2;removed=[]
for row in d['objects']:
 bb=row['bounds'];name=row['name']
 if bb[0][1]<-8.2and any(k in name for k in ['Entry parapet return','jointed parapet coping','coping sealant joint','parapet base mineral flashing','rainwater collector lip']):removed.append(name)
def components(me):
 graph=[set()for _ in me.vertices]
 for e in me.edges:a,b=e.vertices;graph[a].add(b);graph[b].add(a)
 unseen=set(range(len(graph)))
 while unseen:
  start=min(unseen);unseen.remove(start);found={start};stack=[start]
  while stack:
   for i in graph[stack.pop()]:
    if i in unseen:unseen.remove(i);found.add(i);stack.append(i)
  yield found
changes=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 if not ('/ R1 /'in ob.name or 'R1 window detail batch'in ob.name):continue
 if not any(k in ob.name for k in ['glazing','sash','shutters','window detail batch']):continue
 faces=[];componentbounds=[]
 for comp in components(ob.data):
  pts=[ob.matrix_world@ob.data.vertices[i].co for i in comp];u=[p.dot(t)for p in pts];depth=[p.dot(n)for p in pts];z=[p.z for p in pts]
  if min(z)<7.8or max(z)>9.68or min(u)<w['uMin']-.45or max(u)>w['uMax']+.45or min(depth)<w['depth']-.4or max(depth)>w['depth']+.6:continue
  faces.extend(f.index for f in ob.data.polygons if f.vertices[0]in comp);componentbounds.append({'u':[min(u),max(u)],'depth':[min(depth),max(depth)],'z':[min(z),max(z)]})
 if faces:changes.append({'object':ob.name,'removeFaces':faces,'componentBounds':componentbounds})
actors=[]
for ob in s.objects:
 if ob.type!='MESH'or not ob.data.name.startswith('REV13A shared'):continue
 if any(x['mesh']==ob.data.name for x in actors):continue
 if len(actors)>=8:break
 iris={i for f in ob.data.polygons if 'iris'in ob.material_slots[f.material_index].material.name for i in f.vertices};p=sum((ob.data.vertices[i].co for i in iris),Vector())/max(1,len(iris));actors.append({'object':ob.name,'mesh':ob.data.name,'archetype':ob.get('archetype'),'pose':ob.get('poseFamily'),'irisCentre':list(p),'minZ':min(v.co.z for v in ob.data.vertices),'maxZ':max(v.co.z for v in ob.data.vertices)})
deps=bpy.context.evaluated_depsgraph_get();header=[]
for u in [u0-.4,u0+1,u0+2.4,u0+3.2]:
 for z in [9.65,9.85,10.05]:
  p=t*u+n*(-20.5)+Vector((0,0,z));hit=s.ray_cast(deps,p,-n,distance=4);header.append({'u':u,'z':z,'hit':hit[4].name if hit[0]else None,'depth':hit[1].dot(n)if hit[0]else None,'point':list(hit[1])if hit[0]else None})
plan={'status':'PASS','window':w,'normal':list(n),'tangent':list(t),'openCentreU':u0,'removedAccommodationBarrierObjects':removed,'windowEdits':changes,'actorChoices':actors,'headerSamples':header,'personWidthM':1.18,'messageWidthM':3.28,'dividerWidthM':.1,'messageWidthFraction':3.28/(1.18+3.28+.1)};(R/'source/plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan))
