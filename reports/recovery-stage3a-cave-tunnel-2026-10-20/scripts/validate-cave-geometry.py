"""Strict local cave validation; inherited quarry defects stay separate."""
from pathlib import Path
import bpy,numpy as np,json,struct,collections,hashlib
from mathutils.bvhtree import BVHTree
from mathutils import Vector
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw'
W=json.loads((ROOT/'public/models/gullyverse/blockout.layout.json').read_text())
def center(z):return float(np.interp(-z,[-p[1]for p in W['tunnel']['centerline']],[p[0]for p in W['tunnel']['centerline']]))
def load(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);data=raw[28+n:];wd={'VEC2':2,'VEC3':3,'VEC4':4,'SCALAR':1};dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}
 def read(k):
  a=j['accessors'][k];v=j['bufferViews'][a['bufferView']];d=np.dtype(dt[a['componentType']]);w=wd[a['type']];return np.ndarray((a['count'],w),dtype=d,buffer=data,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*d.itemsize),d.itemsize)).copy()
 out={}
 for node in j['nodes']:
  if'mesh'not in node:continue
  p=j['meshes'][node['mesh']]['primitives'][0];a={k:read(i)for k,i in p['attributes'].items()};i=read(p['indices']).reshape(-1,3);out[node['name']]=(a,i)
 return out
new=load(ROOT/'public/models/gullyverse/c9-cave-recovery/cave-entrance.glb');terrain=load(ROOT/'public/models/gullyverse/c9-cave-recovery/entry-clearance.glb');old=load(ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb')
manifest=json.loads((ROOT/'public/models/gullyverse/c9-cave-recovery/manifest.json').read_text());entry=json.loads((ROOT/'public/models/gullyverse/c9-cave-recovery/entry-clearance.json').read_text())
rows=[];border={};fail=[];all_positions={}
for name,(a,idx)in new.items():
 p=a['POSITION'];lookup={};mapping=[];unique=[]
 for v in p:
  key=tuple(np.round(v/1e-6).astype('int64'))
  if key not in lookup:lookup[key]=len(unique);unique.append(v)
  mapping.append(lookup[key])
 mapping=np.array(mapping);f=mapping[idx];edges=collections.Counter(tuple(sorted((int(x),int(y))))for tri in f for x,y in zip(tri,np.roll(tri,-1)))
 area=np.linalg.norm(np.cross(p[idx[:,1]]-p[idx[:,0]],p[idx[:,2]]-p[idx[:,0]]),axis=1)
 boundary=set(k for e,c in edges.items()if c==1 for k in e);border[name]=np.array(unique)[list(boundary)];all_positions[name]=np.array(unique)
 inside=[]
 for i,v in enumerate(p):
  if -41.999<=v[2]<=.5 and .1<v[1]<2.5 and abs(v[0]-center(v[2]))<2.38-2e-5:inside.append(i)
 uv=a['TEXCOORD_0'];tangent=a['TANGENT'];norm=a['NORMAL'];det=np.cross(np.c_[uv[idx[:,1]]-uv[idx[:,0]],np.zeros(len(idx))],np.c_[uv[idx[:,2]]-uv[idx[:,0]],np.zeros(len(idx))])[:,2]
 r={'name':name,'triangles':len(idx),'positionVertices':len(p),'weldedVertices':len(unique),'boundaryVertices':len(boundary),'nonManifoldEdges':sum(c>2 for c in edges.values()),'degenerateTriangles':int((area<1e-12).sum()),'minimumDoubleArea':float(area.min()),'walkingEnvelopeIntrusions':len(inside),'zeroAreaUVTriangles':int((np.abs(det)<1e-12).sum()),'maxNormalLengthError':float(abs(np.linalg.norm(norm,axis=1)-1).max()),'maxTangentLengthError':float(abs(np.linalg.norm(tangent[:,:3],axis=1)-1).max()),'maxNormalTangentDot':float(abs((norm*tangent[:,:3]).sum(1)).max())}
 if r['nonManifoldEdges']or r['degenerateTriangles']or inside or r['zeroAreaUVTriangles']or r['maxNormalTangentDot']>1e-4:fail.append(r)
 rows.append(r)
seams=[]
def distances(a,b):
 d=[]
 for points,other in [(a,b),(b,a)]:
  for chunk in np.array_split(points,max(1,len(points)//200)):d.extend(np.linalg.norm(chunk[:,None]-other[None,:],axis=2).min(1).tolist())
 return max(d)
for part in manifest['parts']:
 reference=border[part['nodes'][0]]
 for level in [1,2]:
  candidate=border[part['nodes'][level]];err=distances(reference,candidate)
  row={'part':part['id'],'LOD':level,'maximumSharedBoundaryDistanceM':err,'toleranceM':2e-5};seams.append(row)
  if err>2e-5:fail.append(row)
# Exact shared interfaces, including independently selected neighbouring LODs.
joins=[]
for pa,pb,z in [('Throat','Passage1',-6),('Passage1','Passage2',-15),('Passage2','Passage3',-24),('Passage3','Passage4',-33)]:
 for la in range(3):
  for lb in range(3):
   a=border[f'Cave_{pa}_LOD{la}'];a=a[abs(a[:,2]-z)<1e-5]
   b=border[f'Cave_{pb}_LOD{lb}'];b=b[abs(b[:,2]-z)<1e-5]
   err=distances(a,b);row={'a':pa,'b':pb,'levels':[la,lb],'z':z,'maxDistanceM':err,'toleranceM':2e-5};joins.append(row)
   if err>2e-5:fail.append(row)
def tree(a,idx):return BVHTree.FromPolygons([Vector(v)for v in a['POSITION']],idx.tolist(),all_triangles=True)
# All terrain tiles, actual private replacements, not just one historical tile.
p=[];f=[];original_p=[];original_f=[]
replacement=dict(zip(entry['targetNodes'],entry['runtimeNodes']))
for name,(a,idx)in old.items():
 if not name.startswith('Foundation_Terrain_')or not name.endswith('LOD0'):continue
 original_f.extend((idx+len(original_p)).tolist());original_p.extend(a['POSITION'].tolist())
 if name in replacement:a,idx=terrain[replacement[name]]
 f.extend((idx+len(p)).tolist());p.extend(a['POSITION'].tolist())
oldbv=BVHTree.FromPolygons([Vector(v)for v in original_p],original_f,all_triangles=True);newbv=BVHTree.FromPolygons([Vector(v)for v in p],f,all_triangles=True)
survey=[]
for z in np.linspace(11.5,-41.5,108):
 eye=Vector((center(z),1.72,z));target=Vector((center(z-3),1.72,z-3));d=(target-eye).normalized();h0=oldbv.ray_cast(eye,d,3);h1=newbv.ray_cast(eye,d,3)
 survey.append({'eye':list(eye),'originalDistance':h0[3],'correctedDistance':h1[3]})
 if h1[0]is not None:fail.append({'terrainIntrusion':survey[-1]})
# Full interior: horizontal, upward and diagonal first hits on real geometry.
rayrows=[]
for level in range(3):
 p=[];f=[];face_parts=[]
 for part in manifest['parts']:
  a,idx=new[part['nodes'][level]];f.extend((idx+len(p)).tolist());p.extend(a['POSITION'].tolist());face_parts.extend([part['id']]*len(idx))
 bv=BVHTree.FromPolygons([Vector(v)for v in p],f,all_triangles=True);inverted=[];uncovered=[];clearance=[];total=0
 for z in np.linspace(1,-41.5,86):
  for height in [1.72,2.3]:
   eye=Vector((center(z),height,z))
   for angle in np.linspace(0,np.pi,49):
    for depth in [-.28,0,.28]:
     d=Vector((np.cos(angle),np.sin(angle),depth)).normalized();hit=bv.ray_cast(eye,d,35);total+=1
     if hit[0]is not None:
      if hit[1].dot(d)>.03:inverted.append({'eye':list(eye),'direction':list(d),'distance':hit[3],'normalDotRay':hit[1].dot(d),'part':face_parts[hit[2]],'face':hit[2],'point':list(hit[0])})
      if hit[3]<2.38 and abs(d.y)<.02:clearance.append({'eye':list(eye),'direction':list(d),'distance':hit[3]})
     elif -1>z>-40 and abs(depth)<1e-5:uncovered.append({'eye':list(eye),'direction':list(d)})
 r={'LOD':level,'rays':total,'invertedFirstHitCount':len(inverted),'uncoveredInteriorCount':len(uncovered),'horizontalClearanceFailures':len(clearance),'invertedFirstHits':inverted,'uncovered':uncovered,'clearance':clearance};rayrows.append(r)
 if inverted or uncovered or clearance:fail.append({'LOD':level,'inverted':len(inverted),'uncovered':len(uncovered),'clearance':len(clearance)})
result={'status':'PASS'if not fail else'FAIL','inputSHA256':{f:hashlib.sha256((ROOT/'public/models/gullyverse/c9-cave-recovery'/f).read_bytes()).hexdigest()for f in ['cave-entrance.glb','entry-clearance.glb']},'scope':'Complete private cave geometry and local terrain; unrelated quarry survey remains historical and unchanged','topology':rows,'crossLODBoundaries':seams,'adjacentCrossLODJoins':joins,'entryTerrainSurvey':survey,'newCaveVisibility':rayrows,'failures':fail,'inheritedQuarryVisibilityDefects':'7 previously documented defects remain; unrelated upper quarry not modified or declared fixed','newTerrainEyeHeightHits':sum(r['correctedDistance']is not None for r in survey),'oldTerrainEyeHeightHits':sum(r['originalDistance']is not None for r in survey)}
(R/'full-cave-geometry-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('VALIDATION',result['status'],json.dumps({'topology':rows,'joinsMax':max(r['maxDistanceM']for r in joins),'failures':fail,'terrainOld':result['oldTerrainEyeHeightHits'],'terrainNew':result['newTerrainEyeHeightHits']}),flush=True)
