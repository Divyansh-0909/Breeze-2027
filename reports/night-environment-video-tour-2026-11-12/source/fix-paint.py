from pathlib import Path
import struct,json,numpy as np
R=Path(__file__).resolve().parents[1];p=R/'viewer/pilot.glb';raw=p.read_bytes();jl=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jl]);binary=raw[28+jl:];views=g['bufferViews'];chunks=[];offset=0;newviews=[]
def add(data):
 global offset
 pad=(-offset)%4;chunks.append(bytes(pad));offset+=pad;idx=len(newviews);newviews.append({'buffer':0,'byteOffset':offset,'byteLength':len(data)});chunks.append(data);offset+=len(data);return idx
def data(v):return binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
for v in views:add(data(v))
def access(index):
 a=g['accessors'][index];v=views[a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC2':2,'VEC3':3,'VEC4':4,'SCALAR':1}[a['type']];return np.frombuffer(data(v),dtype=dtype,offset=a.get('byteOffset',0),count=a['count']*n).reshape((-1,n))
records=json.loads((R/'evidence/paint-projections.json').read_text());byname={r['webMaterial']:r for r in records};fixed=[]
for mesh in g['meshes']:
 for prim in mesh['primitives']:
  mat=g['materials'][prim['material']];r=byname.get(mat['name'])
  if not r:continue
  pos=access(prim['attributes']['POSITION']);normal=access(prim['attributes']['NORMAL']);xyz=np.c_[pos[:,0],-pos[:,2],pos[:,1],np.ones(len(pos))];uv=xyz@np.array(r['UVMatrixWorldBlender']).T;uv[:,1]=1-uv[:,1]
  norm=np.c_[normal[:,0],-normal[:,2],normal[:,1]];axis=np.argmax(abs(norm),axis=1);mask=np.array([r['normalMasks'][('+' if norm[i,j]>=0 else '-')+'XYZ'[j]] for i,j in enumerate(axis)]);uv[mask<.01]=[-1,-1]
  ai=prim['attributes']['TEXCOORD_0'];new=dict(g['accessors'][ai]);new['bufferView']=add(uv.astype('<f4').tobytes());new['byteOffset']=0;new.pop('min',None);new.pop('max',None);g['accessors'].append(new);prim['attributes']['TEXCOORD_0']=len(g['accessors'])-1
  # Give this material its own image/sampler; preserve source wrap as CLIP.
  ii=len(g['images']);g['images'].append({'name':'Exact original paint '+r['sourceMaterial'],'mimeType':'image/png','bufferView':add((R/r['compositeFile']).read_bytes())});si=len(g.setdefault('samplers',[]));g['samplers'].append({'wrapS':33071,'wrapT':33071,'magFilter':9729,'minFilter':9987});ti=len(g['textures']);g['textures'].append({'source':ii,'sampler':si});mat['pbrMetallicRoughness']['baseColorTexture']={'index':ti};mat['pbrMetallicRoughness']['baseColorFactor']=[1,1,1,1];fixed.append({'mesh':mesh.get('name'),'material':mat['name'],'vertices':len(pos)})
g['bufferViews']=newviews;g['buffers']=[{'byteLength':offset}];j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b=b''.join(chunks);b+=bytes((-len(b))%4);out=struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b;p.write_bytes(out)
(R/'evidence/paint-fix.json').write_text(json.dumps({'status':'APPLIED; visual verification required','primitives':fixed,'sourceArtUnchanged':True},indent=2));print('PAINT FIXED',len(fixed))
