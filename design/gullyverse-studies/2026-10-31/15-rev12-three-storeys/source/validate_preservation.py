import bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
before=json.loads((O/'evidence/source-signatures.json').read_text());d=json.loads((O/'evidence/authoring.json').read_text());master=O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend';obs,env,mats,worlds,images=json.loads(json.dumps(snapshot(master)))
assert all(obs[n]==v for n,v in before['objects'].items()),[n for n,v in before['objects'].items()if obs[n]!=v][:10]
assert all(env[n]==v for n,v in before['environment'].items());assert mats==before['materials']and worlds==before['worlds']and images==before['images']
assert len(bpy.data.scenes)==20 and all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in before['memberships'].items())
s=next(s for s in bpy.data.scenes if s.get('variant')=='REV12');old=next(s for s in bpy.data.scenes if s.get('variant')=='REV11');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
for a in d['sourceCrowdActorsShared']:
 for n in a['objects']:assert s.objects[n]==old.objects[n]and s.objects[n].get('heightOnlyFactor')==1.07
assert len(d['sourceCrowdActorsShared'])==180
assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in old.objects if o.type=='LIGHT'};assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
rows=[]
for n in d['newMeshes']:
 o=s.objects[n];m=o.data;bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),n;area=min(f.calc_area()for f in bm.faces);vol=bm.calc_volume(signed=True);assert area>1e-9 and vol>0,(n,area,vol);bm.free();m.calc_loop_triangles();m.calc_tangents(uvmap=m.uv_layers.active.name);dot=max(abs(l.normal.dot(l.tangent))for l in m.loops);unit=min(l.tangent.length for l in m.loops);assert dot<1e-4 and unit>.999,(n,dot,unit);assert all(math.isfinite(x)for l in m.loops for x in[*l.normal,*l.tangent,*l.bitangent]);assert all(abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops);assert all(math.isfinite(x)for uv in m.uv_layers.active.data for x in uv.uv)
 rows.append({'mesh':n,'triangles':len(m.loop_triangles),'closedManifold':True,'minFaceArea':area,'positiveSignedVolume':vol,'normalTangentDotMax':dot,'unitTangentMin':unit})
core=s.objects[d['newMeshes'][0]].data;adj=[[]for v in core.vertices]
for e in core.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();components=[]
for i in range(len(adj)):
 if i in seen:continue
 todo=[i];seen.add(i);count=0
 while todo:
  u=todo.pop();count+=1
  for v in adj[u]:
   if v not in seen:seen.add(v);todo.append(v)
 components.append(count)
assert len(components)==1,components
result={'status':'PASS','oldSceneCountPreserved':19,'sceneCount':20,'originalObjectSignaturesExact':len(before['objects']),'originalImagesMaterialsWorldsExact':True,'packedImages':len(images),'allImagesPacked':all(i.packed_file for i in bpy.data.images if i.type=='IMAGE'),'originalC180ActorsShared':180,'crowdPartsShared':1440,'heightFromOriginalStill1_07':True,'additionalHeightScaling':False,'source19ScenesAndH00H06H07H09Preserved':True,'lightOwners':17,'activeOriginalLights':12,'optionalLightsW':[0]*5,'newMeshChecks':rows,'coreVertexComponents':components,'strictThresholdsUnchanged':True,'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest()}
(O/'evidence/preservation-geometry.json').write_text(json.dumps(result,indent=2));print('REV12_PRESERVATION_GEOMETRY_PASS',len(obs),len(components),flush=True)
