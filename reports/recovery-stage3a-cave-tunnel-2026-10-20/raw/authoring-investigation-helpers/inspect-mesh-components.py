from pathlib import Path
import sys,json,struct,numpy as np,collections
p=Path(sys.argv[1]);b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);data=b[28+n:]
def read(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];d=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]);w={'VEC2':2,'VEC3':3,'VEC4':4,'SCALAR':1}[a['type']];return np.ndarray((a['count'],w),dtype=d,buffer=data,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',d.itemsize*w),d.itemsize)).copy()
for no in j['nodes']:
 if 'mesh'not in no or not no.get('name','').endswith('LOD0'):continue
 pr=j['meshes'][no['mesh']]['primitives'][0];P=read(pr['attributes']['POSITION']);F=read(pr['indices']).reshape(-1,3);lookup={};mapping=[]
 for v in P:
  key=tuple(np.round(v,5));lookup.setdefault(key,len(lookup));mapping.append(lookup[key])
 f=np.array(mapping)[F];parent=list(range(len(lookup)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def union(a,b):
  x,y=find(a),find(b)
  if x!=y:parent[x]=y
 for a,c,d in f:union(a,c);union(c,d)
 components=collections.defaultdict(list)
 for i,tri in enumerate(f):components[find(tri[0])].append(i)
 rows=[]
 for ids in components.values():
  pp=P[F[ids]];cross=np.cross(pp[:,1]-pp[:,0],pp[:,2]-pp[:,0]);area=np.linalg.norm(cross,axis=1)/2;rows.append({'triangles':len(ids),'area':float(area.sum()),'bounds':[pp.min((0,1)).tolist(),pp.max((0,1)).tolist()]})
 print(json.dumps({'name':no['name'],'components':len(rows),'largest':sorted(rows,key=lambda r:-r['triangles'])[:30]}))
