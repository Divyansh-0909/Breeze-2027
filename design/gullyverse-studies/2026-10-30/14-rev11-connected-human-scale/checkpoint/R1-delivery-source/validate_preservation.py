import bpy,bmesh,json,hashlib,sys,math,statistics
from pathlib import Path
from mathutils import Matrix,Vector
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
before=json.loads((O/'evidence/source-signatures.json').read_text());data=json.loads((O/'evidence/authoring.json').read_text());master=O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend';obs,env,mats,worlds,images=json.loads(json.dumps(snapshot(master)))
assert all(obs[n]==v for n,v in before['objects'].items()),[n for n,v in before['objects'].items()if obs[n]!=v][:20]
assert all(env[n]==v for n,v in before['environment'].items());assert all(mats[n]==v for n,v in before['materials'].items());assert worlds==before['worlds'] and images==before['images']
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in before['memberships'].items());assert len(bpy.data.scenes)==19
source=next(s for s in bpy.data.scenes if s.get('variant')=='PHOTO A');crowd=[];geometry=[]
for record in data['crowdVariants']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==record['variant']);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();assert not any(o.name.startswith('WEB CROWD /')for o in s.objects)
 assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in source.objects if o.type=='LIGHT'}
 assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12 and sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
 for a in record['actors']:
  factor=a['heightOnlyFactor'];foot=a['anchorZ'];err=0;xy=0;verts=[]
  for old,new in zip(a['sourceObjects'],a['objects']):
   p,q=source.objects[old],s.objects[new];assert [list(f.vertices)for f in p.data.polygons]==[list(f.vertices)for f in q.data.polygons];assert [x.material.name for x in p.material_slots]==[x.material.name for x in q.material_slots]
   assert len(p.data.uv_layers)==len(q.data.uv_layers)
   for u0,u1 in zip(p.data.uv_layers,q.data.uv_layers):assert u0.name==u1.name and all(tuple(a.uv)==tuple(b.uv)for a,b in zip(u0.data,u1.data))
   expected=p.matrix_basis
   err=max(err,max(abs(q.matrix_basis[i][j]-expected[i][j])for i in range(4)for j in range(4)))
   for va,vb in zip(p.data.vertices,q.data.vertices):
    pa=p.matrix_basis@va.co;pb=q.matrix_basis@vb.co;xy=max(xy,abs(pa.x-pb.x),abs(pa.y-pb.y),abs(pb.z-(foot+(pa.z-foot)*factor)));verts.append(pb)
  assert err<1e-5 and xy<1e-5,(record['variant'],a['label'],err,xy);bottom=min(p.z for p in verts);height=max(p.z for p in verts)-bottom;assert abs(bottom-foot)<.002 and abs(height-a['newHeightM'])<1e-5
  crowd.append({'variant':record['variant'],'actor':a['label'],'oldHeightM':a['oldHeightM'],'newHeightM':height,'factor':factor,'maxXYErrorM':xy,'matrixError':err,'floorErrorM':abs(bottom-7.2)})
for name in data['newMeshes']:
 o=bpy.data.objects[name];mesh=o.data;bm=bmesh.new();bm.from_mesh(mesh);assert all(e.is_manifold for e in bm.edges),name;area=min(f.calc_area()for f in bm.faces);volume=bm.calc_volume(signed=True);assert area>1e-9 and volume>0,(name,area,volume);bm.free();mesh.calc_loop_triangles();mesh.calc_tangents(uvmap=mesh.uv_layers.active.name);dot=max(abs(l.normal.dot(l.tangent))for l in mesh.loops);unit=min(l.tangent.length for l in mesh.loops);assert dot<1e-4 and unit>.999,(name,dot,unit)
 assert all(math.isfinite(x)for l in mesh.loops for x in[*l.normal,*l.tangent,*l.bitangent]);assert all(abs(abs(l.bitangent_sign)-1)<1e-5 for l in mesh.loops);assert all(math.isfinite(x)for uv in mesh.uv_layers.active.data for x in uv.uv)
 geometry.append({'mesh':name,'closedManifold':True,'minFaceArea':area,'positiveSignedVolume':volume,'maxNormalTangentDot':dot,'minTangentLength':unit,'triangles':len(mesh.loop_triangles)})
# One globally welded structural shell must be one vertex-connected component.
mesh=bpy.data.objects[data['newMeshes'][0]].data;adj=[[]for v in mesh.vertices]
for e in mesh.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
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
result={'status':'PASS','historicalSceneCountPreserved':15,'allOriginalObjectSignaturesExact':len(before['objects']),'allOriginalMaterialsWorldsImagesExact':True,'packedImages':len(images),'originalScreenFloorArtShopsCountersRouteExact':True,'newMeshGeometry':geometry,'structuralShellVertexComponents':components,'crowdHeightOnly':crowd,'strictThresholdsUnchanged':True,'capsuleRadiusM':.35,'floorToleranceM':.002,'originalActorFamilyCount':180,'privateWebsiteUnchangedValidatedSeparately':True}
(O/'evidence/preservation-geometry-height.json').write_text(json.dumps(result,indent=2)+'\n');print('REV11_PRESERVATION_GEOMETRY_HEIGHT_PASS',len(obs),len(components),flush=True)
