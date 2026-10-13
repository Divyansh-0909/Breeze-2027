from pathlib import Path
import json,struct,hashlib,numpy as np
r=Path('reports/stage-2c-quarry-rollout-2026-10-12');source=json.loads(Path('assets-source/gullyverse/quarry-rollout/source-topology.json').read_text());path=Path('public/models/gullyverse/quarry-rollout/quarry-limestone.glb');b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];rows=[]
def array(i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dt={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];dim={'SCALAR':1,'VEC3':3}[a['type']];return np.frombuffer(binary,dtype=dt,count=a['count']*dim,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dim)
for rock in source['rocks']:
 corners=np.array(rock['vertices']);center=np.array(rock['center']);planes=[]
 for face in rock['faces']:
  v=corners[face];normal=np.cross(v[1]-v[0],v[2]-v[0]);normal/=np.linalg.norm(normal);planes.append((v[0],normal))
 for level in range(3):
  node=next(x for x in d['nodes']if x.get('name')==f"Quarry_Rock_{rock['id']:02d}_LOD{level}");points=np.concatenate([array(p['attributes']['POSITION'])for p in d['meshes'][node['mesh']]['primitives']]);outside=max(float(((points-v)@normal).max())for v,normal in planes);cornerError=max(float(np.linalg.norm(points-c,axis=1).min())for c in corners);row={'rock':rock['id'],'LOD':level,'maxOutsideOriginalHullM':outside,'originalCornerMaxErrorM':cornerError,'bounds':[points.min(axis=0).tolist(),points.max(axis=0).tolist()]};rows.append(row);assert outside<3e-5,row;assert cornerError<3e-5,row
# No authored collar triangles pass through visitor eye positions in the current tunnel.
capRows=[]
def center(z):
 path=source['tunnel']['centerline']
 for(x1,z1),(x2,z2)in zip(path,path[1:]):
  if z<=z1 and z>=z2:return x1+(x2-x1)*(z-z1)/(z2-z1)
 return path[-1][0]
for level in range(3):
 node=next(x for x in d['nodes']if x.get('name')==f'Quarry_Exit_LOD{level}');pr=d['meshes'][node['mesh']]['primitives'][0];v=array(pr['attributes']['POSITION']);f=array(pr['indices']).reshape(-1,3);tri=v[f];hits=[]
 for z in np.linspace(-41.95,-38.8,28):
  for offset in[-1.85,0,1.85]:
   # Count upward intersections of a closed mesh to test inside-solid.
   p=np.array([center(z)+offset,1.72,z]);direction=np.array([.012,1.,.031]);direction/=np.linalg.norm(direction);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=(e1*h).sum(axis=1);valid=np.abs(det)>1e-8;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);s=p-tri[:,0];u=inv*(s*h).sum(axis=1);q=np.cross(s,e1);w=inv*(q*direction).sum(axis=1);t=inv*(q*e2).sum(axis=1);cross=valid&(u>=0)&(w>=0)&(u+w<=1)&(t>1e-5)
   if int(cross.sum())%2:hits.append(p.tolist())
 row={'LOD':level,'eyeSamples':84,'insideCollarSamples':hits};capRows.append(row);assert not hits,row
result={'status':'PASS','positions':'Float32 unchanged by attribute quantization; each rock contained in its actual original solid with retained corners','rocks':rows,'tunnelCorridor':capRows};(r/'raw/shape-validation.json').write_text(json.dumps(result,indent=2));print('PASS',len(rows),'rock LODs; corridor',capRows)
