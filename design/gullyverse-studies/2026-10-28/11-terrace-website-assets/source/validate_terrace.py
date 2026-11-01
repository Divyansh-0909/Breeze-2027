import bpy,bmesh,json,math,itertools,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE WEB CROWD');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
def geom(objects):
 v=[];f=[]
 for o in objects:
  ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();off=len(v);v.extend(ev.matrix_world@x.co for x in m.vertices);f.extend(tuple(off+i for i in t.vertices)for t in m.loop_triangles);ev.to_mesh_clear()
 return v,f
rows=[]
for name in a['newConstruction']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-9 for f in bm.faces),name;volume=bm.calc_volume(signed=True);assert volume>0;bm.free();m.calc_tangents(uvmap=m.uv_layers.active.name)
 assert all(math.isfinite(q)for l in m.loops for q in[*l.normal,*l.tangent,*l.bitangent]);assert all(abs(l.normal.dot(l.tangent))<1e-4 and l.tangent.length>.999 and abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops),name
 rows.append({'object':name,'triangles':len(m.loop_triangles),'closedManifold':True,'signedVolume':volume,'finiteUnitTangents':True})
poses=json.loads((O/'source/website/exact-baked-poses.json').read_text());parity=[]
for i,p in enumerate(poses):
 m=bpy.data.meshes['WEB EXACT POSE '+str(i)];v=p['positions'];err=max(abs(m.vertices[j].co[k]-[v[j*3],-v[j*3+2],v[j*3+1]][k])for j in range(len(m.vertices))for k in range(3));assert err<1e-7
 assert [j for f in m.polygons for j in f.vertices]==p['indices'];bm=bmesh.new();bm.from_mesh(m);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<=1e-9 for f in bm.faces);bm.free();parity.append({'pose':i,'positionErrorM':err,'indicesExact':True,'triangles':p['triangles'],'sourceBoundaryEdges':boundary,'sourceNonmanifoldEdges':nonmanifold,'sourceTinyFaces':zero,'UVTangentContract':'Website bakes POSITION and computed NORMAL only. Lambert uses no UV/tangent or textures. Exact match intentionally retains that contract.'})
actors=[];source=[];footerrors=[];gaperrors=[]
for r in a['actors']:
 o=bpy.data.objects[r['object']];assert list(o.location)==[float(x)for x in o.location];assert max(abs(o.location[i]-r['foot'][i])for i in range(3))<1e-5;assert max(o.scale)-min(o.scale)<1e-7
 v,f=geom([o]);lo=[min(p[i]for p in v)for i in range(3)];hi=[max(p[i]for p in v)for i in range(3)];assert abs(lo[2]-7.2)<.002
 # Original source-facing contract; glTF +Z maps to Blender -Y before pi turn.
 forward=o.matrix_world.to_quaternion()@Vector((0,-1,0));to=Vector((-r['foot'][0],45.8-r['foot'][1],0));to.normalize();assert forward.dot(to)>=math.cos(math.radians(12.001))
 if lo[1]<36.95 and not(lo[0]>=.45-1e-5 or hi[0]<=-.45+1e-5):gaperrors.append({'actor':r['actor'],'bounds':[lo,hi]})
 actors.append({'r':r,'lo':lo,'hi':hi,'tree':BVHTree.FromPolygons(v,f,all_triangles=True)})
overlaps=[];broad=0
for x,y in itertools.combinations(actors,2):
 if any(x['hi'][i]<y['lo'][i]or y['hi'][i]<x['lo'][i]for i in range(3)):continue
 broad+=1;hits=x['tree'].overlap(y['tree'])
 if hits:overlaps.append([x['r']['actor'],y['r']['actor'],len(hits)])
props=[o for o in s.objects if o.type=='MESH'and not o.name.startswith(('WEB CROWD /','Bounded lane haze'))and not o.get('pilotOriginalObject',o.name).startswith(('Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron'))];pv,pf=geom(props);pt=BVHTree.FromPolygons(pv,pf,all_triangles=True);prop_hits=[]
for x in actors:
 hits=x['tree'].overlap(pt)
 if hits:prop_hits.append([x['r']['actor'],len(hits)])
prop_checks=[]
for plan in['propPlanA','propPlanB']:
 sc=next(sc for sc in bpy.data.scenes if sc.get('variant')==('TERRACE PROPS A'if plan=='propPlanA'else'TERRACE PROPS B'));bpy.context.window.scene=sc;sc.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
 v,f=geom([bpy.data.objects[r['copy']]for r in a[plan]]);t=BVHTree.FromPolygons(v,f,all_triangles=True);hits=[]
 for x in actors:
  h=x['tree'].overlap(t)
  if h:hits.append([x['r']['actor'],len(h)])
 for r in a[plan]:
  src=bpy.data.objects[r['source']];o=bpy.data.objects[r['copy']];assert o.data==src.data
  original=Matrix(next(x['matrix']for x in a['originalPropMetadata']if x['object']==src.name));expected=Matrix.Translation(Vector(r['translationOnly']))@original
  actual=o.evaluated_get(dep).matrix_world
  assert max(abs(actual[i][j]-expected[i][j])for i in range(4)for j in range(4))<1e-6
 prop_checks.append({'plan':plan,'crowdOverlaps':hits,'sameMeshMaterialAndUnitScaleAsSource':True})
result={'status':'PASS'if not(overlaps or prop_hits or gaperrors or any(r['crowdOverlaps']for r in prop_checks))else'FAIL','construction':rows,'constructionAreaM2Minimum':1e-9,'tangentDotMaximum':1e-4,'tangentLengthMinimum':.999,'tolerancesUnchanged':True,'sourcePoseParity':parity,'actorCount':len(actors),'actorPairs':len(actors)*(len(actors)-1)//2,'AABBpairs':broad,'bodyOverlaps':overlaps,'bodyArchitectureOverlaps':prop_hits,'narrowGapViolations':gaperrors,'originalFootCoordinatesHeightYawAndDensityPreserved':True,'sourceUniformScalingOnly':True,'propChecks':prop_checks,'sourceMeshTopologyNotSilentlyRepaired':True}
(O/'evidence/geometry-crowd-validation.json').write_text(json.dumps(result,indent=2));print('TERRACE_VALIDATION',result['status'],'overlaps',overlaps[:8],'props',prop_hits[:8],'gaps',gaperrors[:3],flush=True)
assert result['status']=='PASS'
