import json,struct,numpy as np
from pathlib import Path
r=Path('reports/stage-2b-first-wall-2026-10-12/raw');old=json.loads((r/'quarry-before.json').read_text());anchor=json.loads(Path('assets-source/gullyverse/first-wall-section/anchor.json').read_text());p=np.array(old['attributes']['position']).reshape(-1,3)[216:324];planes=[]
for i in range(0,len(p),9):
 n=np.cross(p[i+1]-p[i],p[i+2]-p[i]);n/=np.linalg.norm(n);planes.append((n,p[i]))
rotation=np.array([anchor['uAxis'],anchor['vAxis'],anchor['normal']]).T;origin=np.array(anchor['anchor']);results=[]
for file in Path('public/models/gullyverse/first-wall-section').glob('*.glb'):
 b=file.read_bytes();length=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+length]);binary=b[28+length:];meshes=[]
 def array(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],count)
 for mesh in doc['meshes']:
  for primitive in mesh['primitives']:
   pos=array(primitive['attributes']['POSITION']);world=pos@rotation.T+origin;outside=max(float(((world-a)@n).max()) for n,a in planes)
   finite=all(np.isfinite(array(index)).all() for index in primitive['attributes'].values());assert finite
   if mesh['name']!='Wall_Collision_Mesh':assert outside<2e-5,(mesh['name'],outside)
   corners=np.array(anchor['boundaryWorld']);error=max(float(np.linalg.norm(world-c,axis=1).min()) for c in corners);assert error<2e-5,(mesh['name'],error)
   meshes.append({'name':mesh['name'],'triangles':len(array(primitive['indices']))//3,'finiteAttributes':finite,'maxOutsideOriginalRockM':outside,'originalCornerMaxErrorM':error,'normalTextureUV1Present':'TEXCOORD_1' in primitive['attributes']})
 results.append({'file':file.name,'bytes':len(b),'materials':doc.get('materials',[]),'meshes':meshes})
(r/'asset-fit.json').write_text(json.dumps({'status':'PASS','results':results},indent=2));print([(x['file'],x['bytes']) for x in results])
