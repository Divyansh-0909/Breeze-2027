"""Private mouth clearance by attributed triangle clipping, never solid union.

Both terrain tiles were identified by exact-runtime landing-camera intersections.
The protected floor, C9 and original GLBs remain read-only. Outside triangles
retain every original attribute; all LODs use identical local cut boundaries.
"""
from pathlib import Path
import json,struct,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2]
O=ROOT/'public/models/gullyverse/c9-cave-recovery'
R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw'
source=ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'
raw=source.read_bytes();jl=struct.unpack_from('<I',raw,12)[0]
doc=json.loads(raw[20:20+jl]);data=raw[28+jl:]
width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
types={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1',5122:'<i2',5120:'i1'}
def read(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
 dt=np.dtype(types[a['componentType']]);w=width[a['type']]
 s=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',w*dt.itemsize)
 out=np.ndarray((a['count'],w),dtype=dt,buffer=data,offset=s,strides=(stride,dt.itemsize)).copy()
 if a.get('normalized'):out=out.astype(float)/np.iinfo(dt).max
 return out
lo=np.array([-4.5,-.12,-7.5]);hi=np.array([4.5,7.5,13.0])
planes=[(axis,limit,sgn)for axis in range(3)for limit,sgn in [(lo[axis],1),(hi[axis],-1)]]
buffer=bytearray();views=[];accessors=[];meshes=[];nodes=[];stats=[];targets=[];runtime=[]
def append(a,kind,component,target,minmax=False):
 while len(buffer)%4:buffer.append(0)
 s=len(buffer);payload=a.tobytes();buffer.extend(payload);vi=len(views)
 views.append({'buffer':0,'byteOffset':s,'byteLength':len(payload),'target':target})
 ai=len(accessors);acc={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if minmax:acc.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 accessors.append(acc);return ai
for tile in ['1_2','2_2']:
 node=next(n for n in doc['nodes']if n.get('name')==f'Foundation_Terrain_{tile}_LOD0')
 assert not any(k in node for k in ['matrix','translation','rotation','scale'])
 p=doc['meshes'][node['mesh']]['primitives'][0]
 attrs={k:read(i).astype(float)for k,i in p['attributes'].items()};I=read(p['indices']).reshape(-1,3)
 keys=list(attrs);offsets={};cursor=0
 for k,a in attrs.items():offsets[k]=slice(cursor,cursor+a.shape[1]);cursor+=a.shape[1]
 A=np.concatenate([attrs[k]for k in keys],axis=1);pos=offsets['POSITION']
 def split(poly,axis,limit,sgn):
  inside=[];outside=[]
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   da=sgn*(a[pos][axis]-limit);db=sgn*(b[pos][axis]-limit);ia=da>=0;ib=db>=0
   (inside if ia else outside).append(a)
   if ia!=ib:
    q=a+(b-a)*(da/(da-db));inside.append(q);outside.append(q)
  return np.array(inside),np.array(outside)
 V=[];F=[];kept=0;touched=0;removed=0;zero=0
 for ids in I:
  tri=A[ids];xyz=tri[:,pos]
  if np.any(xyz.max(0)<lo)or np.any(xyz.min(0)>hi):
   start=len(V);V.extend(tri.tolist());F.append([start,start+1,start+2]);kept+=1;continue
  pending=tri;fragments=[]
  for axis,limit,sgn in planes:
   if len(pending)<3:break
   pending,outside=split(pending,axis,limit,sgn)
   if len(outside)>=3:fragments.append(outside)
  touched+=1
  if len(pending)>=3:removed+=1
  for poly in fragments:
   for j in range(1,len(poly)-1):
    t=poly[[0,j,j+1]].copy();xyz=t[:,pos]
    if np.linalg.norm(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]))<1e-12:zero+=1;continue
    for q in t:
     if not any(np.array_equal(q,original)for original in tri):
      n=q[offsets['NORMAL']];n/=np.linalg.norm(n)
      tv=q[offsets['TANGENT']];tv[:3]-=n*np.dot(n,tv[:3]);tv[:3]/=np.linalg.norm(tv[:3]);tv[3]=1 if tv[3]>=0 else -1
    start=len(V);V.extend(t.tolist());F.append([start,start+1,start+2])
 V=np.array(V);F=np.array(F,dtype='<u4');outattrs={}
 for k in keys:
  a=V[:,offsets[k]].astype('<f4');outattrs[k]=append(a,'VEC'+str(a.shape[1]),5126,34962,k=='POSITION')
 ind=append(F.reshape(-1,1),'SCALAR',5125,34963);mi=len(meshes)
 meshes.append({'primitives':[{'attributes':outattrs,'indices':ind,'material':0}]})
 for level in range(3):
  name=f'Cave_Entry_Clearance_{tile}_LOD{level}'
  nodes.append({'mesh':mi,'name':name});runtime.append(name);targets.append(f'Foundation_Terrain_{tile}_LOD{level}')
 stats.append({'tile':tile,'inputTriangles':len(I),'unchangedOutsideTriangles':kept,'candidateIntersectingTriangles':touched,'trianglesClippedByVolume':removed,'zeroAreaIntersectionFragmentsDiscarded':zero,'outputTriangles':len(F)})
out={'asset':{'version':'2.0','generator':'Gullyverse private mouth-only attributed surface clip'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':[{'name':'Borrow_Original_Terrain_Material','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':1}}],'buffers':[{'byteLength':len(buffer)}],'bufferViews':views,'accessors':accessors}
enc=json.dumps(out,separators=(',',':')).encode();enc+=b' '*((-len(enc))%4);buffer+=b'\0'*((-len(buffer))%4)
packed=struct.pack('<III',0x46546c67,2,28+len(enc)+len(buffer))+struct.pack('<II',len(enc),0x4e4f534a)+enc+struct.pack('<II',len(buffer),0x004e4942)+buffer
path=O/'entry-clearance.glb';path.write_bytes(packed)
result={'status':'GENERATED_PENDING_BROWSER_VALIDATION','originalSHA256':hashlib.sha256(raw).hexdigest(),'runtimeSHA256':hashlib.sha256(packed).hexdigest(),'runtimeBytes':len(packed),'boundsOfOnlyRemovedVolume':[lo.tolist(),hi.tolist()],'tiles':stats,'targetNodes':targets,'runtimeNodes':runtime,'originalGroundRegistryAndC9RockAssetsChanged':False}
(R/'entry-clearance.json').write_text(json.dumps(result,indent=2)+'\n');(O/'entry-clearance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
