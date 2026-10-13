import json,struct,numpy as np
from pathlib import Path
root=Path('public/models/gullyverse/quarry-refinement');rows=[]
for path in sorted(root.glob('*.glb')):
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);binary=data[28+n:]
 def array(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];dim={'SCALAR':1,'VEC3':3}[a['type']];dt={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.frombuffer(binary,dtype=dt,count=a['count']*dim,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dim)
 for mesh in doc['meshes']:
  points=[];lookup={};faces=[]
  for primitive in mesh['primitives']:
   mapping=[]
   for p in array(primitive['attributes']['POSITION']):
    key=tuple(float(x)for x in p)
    if key not in lookup:lookup[key]=len(points);points.append(p.astype(np.float64))
    mapping.append(lookup[key])
   faces.extend([[mapping[int(i)]for i in f]for f in array(primitive['indices']).reshape(-1,3)])
  p=np.array(points);f=np.array(faces);edges={};balance={}
  for a,b,c in faces:
   for x,y in [(a,b),(b,c),(c,a)]:
    key=tuple(sorted((x,y)));edges[key]=edges.get(key,0)+1;balance[key]=balance.get(key,0)+(1 if x<y else -1)
  parent=list(range(len(points)))
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for a,b,c in faces:
   for x,y in [(a,b),(b,c)]:parent[find(x)]=find(y)
  volumes={}
  for a,b,c in faces:
   key=find(a);volumes[key]=volumes.get(key,0)+float(np.dot(p[a],np.cross(p[b],p[c])))/6
  assert all(v>0 for v in volumes.values()),volumes
  volume=float(np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()/6)
  row={'file':str(path),'mesh':mesh['name'],'triangles':len(faces),'geometricVertices':len(points),'boundaryOrNonmanifoldEdges':sum(v!=2 for v in edges.values()),'inconsistentWindingEdges':sum(v!=0 for v in balance.values()),'signedVolumeM3':volume,'closedComponentVolumesM3':list(volumes.values()),'method':'Exact float32 position welding across material/UV/normal splits; each visual LOD assembled separately'}
  assert row['boundaryOrNonmanifoldEdges']==0 and row['inconsistentWindingEdges']==0 and volume>0,row
  rows.append(row)
Path('reports/stage-2c1-geological-refinement-2026-10-13/raw/exported-topology-validation.json').write_text(json.dumps({'status':'PASS','meshes':rows},indent=2));print([(r['mesh'],r['triangles'],r['boundaryOrNonmanifoldEdges'])for r in rows])
