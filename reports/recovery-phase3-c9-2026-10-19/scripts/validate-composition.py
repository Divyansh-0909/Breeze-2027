"""Actual GLB validation; unchanged 2e-5 border and .03 ray-facing gates."""
from pathlib import Path
import bpy,json,numpy as np,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();RAW=ROOT/'reports/recovery-phase3-c9-2026-10-19/raw'
sys.path.insert(0,str(ROOT/'scripts/blender'))
import refined_foundation_geometry as foundation
geo=foundation.old
def B(p):return Vector((p[0],-p[2],p[1]))
def G(p):return [p[0],p[2],-p[1]]
def imported(path):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
 return [o for o in bpy.data.objects if o not in before and o.type=='MESH']
def tree(objects):
 verts=[];faces=[];names=[]
 for ob in objects:
  offset=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
  faces.extend([[offset+i for i in p.vertices]for p in ob.data.polygons]);names.extend([ob.name]*len(ob.data.polygons))
 return BVHTree.FromPolygons(verts,faces,all_triangles=False,epsilon=1e-6),names
def facing_cast(t,origin,direction):
 hit=t[0].ray_cast(B(origin),direction,650)
 return {'distance':hit[3],'normalDotRay':hit[1].dot(direction)if hit[1]is not None else None,'mesh':t[1][hit[2]]if hit[2]is not None else None}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
candidate=imported(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb')
candidate.sort(key=lambda o:o.name)
protected=json.loads((ROOT/'assets-source/gullyverse/quarry-scanned-composition/protected-host-boundaries.json').read_text())
topology=[];failures=[]
for level,ob in enumerate(candidate):
 m=ob.data;m.calc_loop_triangles();xyz=np.array([G(ob.matrix_world@v.co)for v in m.vertices]);faces=np.array([t.vertices[:]for t in m.loop_triangles]);normal=np.array([n.vector[:]for n in m.corner_normals]);uvs=[]
 # Exact positional welding restores geometric topology across legitimate UV seams.
 _,indices,rev=np.unique(xyz,axis=0,return_index=True,return_inverse=True);wf=rev[faces]
 ed=np.sort(np.concatenate([wf[:,[0,1]],wf[:,[1,2]],wf[:,[2,0]]]),axis=1);edges,counts=np.unique(ed,axis=0,return_counts=True)
 nonmanifold=int((counts>2).sum());boundary=xyz[indices[np.unique(edges[counts==1])]]
 expected=np.array(protected[level]['vertices']);error=0
 for chunks in np.array_split(expected,10):error=max(error,float(np.sqrt(((chunks[:,None]-boundary[None,:])**2).sum(2)).min(1).max()))
 for layer_index in range(len(m.uv_layers)):
  layer=m.uv_layers[layer_index];layer_name=layer.name
  uv=np.array([v.uv[:]for v in layer.data]);m.calc_tangents(uvmap=layer_name)
  lengths=np.linalg.norm(np.array([l.tangent[:]for l in m.loops]),axis=1)
  uvs.append({'name':layer_name,'finite':bool(np.isfinite(uv).all()),'badTangentCorners':int((lengths<.99).sum())})
 row={'LOD':level,'triangles':len(faces),'exportVertices':len(xyz),'weldedPositionVertices':len(indices),'nonManifoldInteriorEdges':nonmanifold,'openBoundaryVertices':len(boundary),'expectedProtectedVertices':len(expected),'maximumProtectedBorderErrorM':error,'zeroAreaTriangles':sum(t.area<1e-10 for t in m.loop_triangles),'invalidNormals':int((np.linalg.norm(normal,axis=1)<.99).sum()),'UVs':uvs}
 topology.append(row)
 if error>=2e-5 or nonmanifold or row['zeroAreaTriangles'] or row['invalidNormals'] or any(not u['finite']or u['badTangentCorners']for u in uvs):failures.append({'geometry':row})

# The original retained passage is an occluder only, never a new collider.
source=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
tunnel=np.array(source['tunnelAttributes']['position']).reshape(-1,3);keep=np.ones(len(tunnel),dtype=bool)
for r in source['tunnelRearRanges']:keep[r['start']:r['start']+r['count']]=False
retained=tunnel[keep];mesh=bpy.data.meshes.new('Unchanged_Passage_Occlusion');mesh.from_pydata([B(p)for p in retained],[],np.arange(len(retained)).reshape(-1,3).tolist());tube=bpy.data.objects.new('Unchanged_Passage_Occlusion',mesh)
baseline=[];new=[]
for level in range(3):
 obs=imported(ROOT/f'public/models/gullyverse/quarry-foundation-refined/foundation-lod{level}.glb');baseline.append(tree(obs+[tube]))
 host=next(o for o in obs if o.name.split('.')[0]==f'Foundation_Wall_15_LOD{level}')
 protected_positions={tuple(v)for v in protected[level]['vertices']};original_normals={}
 for loop in host.data.loops:
  key=tuple(G(host.matrix_world@host.data.vertices[loop.vertex_index].co))
  if key in protected_positions:original_normals[key]=host.matrix_world.to_3x3()@host.data.corner_normals[loop.index].vector
 dot=1.
 for loop in candidate[level].data.loops:
  key=tuple(G(candidate[level].matrix_world@candidate[level].data.vertices[loop.vertex_index].co))
  if key in original_normals:
   n=candidate[level].matrix_world.to_3x3()@candidate[level].data.corner_normals[loop.index].vector
   dot=min(dot,n.normalized().dot(original_normals[key].normalized()))
 topology[level]['maximumProtectedNormalAngleDegrees']=math.degrees(math.acos(max(-1.,min(1.,dot))))
 topology[level]['protectedNormalMinimumDot']=dot
 if dot<1-1e-6:failures.append({'LOD':level,'protectedNormalDot':dot,'requiredMinimum':1-1e-6})
 new.append(tree([candidate[level]if o==host else o for o in obs]+[tube]))

eyes=[[0,1.72,-51],[0,1.72,-96],[-18,1.72,-55],[-18,1.72,-62],[-17,1.72,-69],[-10.5,1.72,-110.8],[17.4,1.72,-72.55]]
rows=[];new_inverted=[];inherited_inverted=[];added_gaps=[];skyline=[]
for eye in eyes:
 for pitch in [0,5,10,15,20,25,30,35,40,45,50,60,70]:
  for yaw in range(0,360,3):
   a,b=math.radians(pitch),math.radians(yaw);d=B([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)])
   oldhits=[facing_cast(t,eye,d)for t in baseline];hits=[facing_cast(t,eye,d)for t in new]
   row={'eye':eye,'pitch':pitch,'yaw':yaw,'baseline':oldhits,'candidate':hits};rows.append(row)
   if any(h['distance']is None for h in hits)and any(h['distance']is not None for h in hits):
    oldmask=[h['distance']is None for h in oldhits];mask=[h['distance']is None for h in hits]
    skyline.append({'eye':eye,'pitch':pitch,'yaw':yaw,'inherited':oldmask==mask,'mask':mask,'baselineMask':oldmask})
   for level,(old,h)in enumerate(zip(oldhits,hits)):
    if pitch==0 and h['distance']is None and old['distance']is not None:added_gaps.append({**row,'LOD':level})
    if h['normalDotRay']is not None and h['normalDotRay']>.03 and h['mesh']!='Unchanged_Passage_Occlusion':
     issue={**row,'LOD':level}
     if not h['mesh'].startswith('C9_'):
      # A BVH tie at an original coincident wall/terrain intersection can return
      # another unchanged face after local replacement. Verify its OWN baseline
      # surface, rather than attributing untouched terrain to the new scan.
      exact=[ob for ob in bpy.data.objects if ob.type=='MESH' and ob.name==h['mesh']]
      assert len(exact)==1
      check=facing_cast(tree(exact),eye,d)
      assert check['distance']is not None and abs(check['distance']-h['distance'])<2e-5 and check['normalDotRay']>.03
      inherited_inverted.append({**issue,'verifiedUnchangedSurface':check,'coincidentBaselineTie':old['mesh']!=h['mesh']})
     else:new_inverted.append(issue)

clearances=[];boundary=np.array(geo.WORLD['quarry']['boundary'])
for level,ob in enumerate(candidate):
 xyz=np.array([G(ob.matrix_world@v.co)for v in ob.data.vertices]);inside=np.ones(len(xyz),dtype=bool)
 for a,b in zip(boundary,np.roll(boundary,-1,axis=0)):
  delta=b-a;n=np.array([delta[1],-delta[0]])/np.linalg.norm(delta);inside &= ((xyz[:,[0,2]]-a)@n)>0
 bad=xyz[inside&(xyz[:,1]>.25)];clearances.append({'LOD':level,'verticesInsideProtectedQuarryPolygon':len(bad)})
 if len(bad):failures.append({'clearance':clearances[-1],'sample':bad[:10].tolist()})
if new_inverted or added_gaps or any(not x['inherited']for x in skyline):failures.append({'newInvertedHits':len(new_inverted),'addedHorizontalGaps':len(added_gaps),'newSkylineDisagreements':sum(not x['inherited']for x in skyline)})
result={'status':'PASS'if not failures else'FAIL','fullSceneVisibilityStatus':'FAIL_INHERITED'if inherited_inverted else'PASS','candidateIntroducesNoNewVisibilityDefect':not(new_inverted or added_gaps or any(not x['inherited']for x in skyline)),'raysPerVersion':len(rows),'baseline':'actual surviving C5.1, not lost C6.2','sharedBorderToleranceM':2e-5,'invertedRayThreshold':.03,'topology':topology,'clearances':clearances,'newInvertedHits':new_inverted,'inheritedInvertedHits':inherited_inverted,'addedHorizontalGaps':added_gaps,'crossLODSkylineDisagreements':skyline,'failures':failures,'rays':rows,'limitations':'Exact positional weld used for topology inspection only; no runtime geometry mutation. Ray sampling is not an exhaustive intersection proof. Historical C9 upper defects are not presumed present in surviving C5.1. PASS concerns the new candidate gates; fullSceneVisibilityStatus explicitly retains failures on unchanged baseline surfaces.'}
(RAW/'composition-validation.json').write_text(json.dumps(result,indent=2));print('VALIDATION',result['status'],json.dumps({'topology':topology,'failures':failures,'newInverted':len(new_inverted),'inheritedInverted':len(inherited_inverted),'skyline':len(skyline)}),flush=True)
assert not failures,'See composition-validation.json; strict gates unchanged'
