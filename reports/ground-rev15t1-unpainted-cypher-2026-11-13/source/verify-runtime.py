from pathlib import Path
import struct,json,hashlib,io
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];old=R.parent/'ground-rev15t-continuous-asphalt-2026-11-13'
def load(p):
 b=p.read_bytes();n,kind=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);start=20+n;size,kind=struct.unpack_from('<II',b,start);return g,b[start+8:start+8+size]
def accessor(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)+a.get('byteOffset',0);components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];bytesPer={5126:4,5125:4,5123:2,5121:1}[a['componentType']];assert 'byteStride' not in v;return b[start:start+a['count']*components*bytesPer]
def fingerprint(g,b):
 rows=[]
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   row={k:hashlib.sha256(accessor(g,b,v)).hexdigest() for k,v in p['attributes'].items()};row['indices']=hashlib.sha256(accessor(g,b,p['indices'])).hexdigest();rows.append(json.dumps(row,sort_keys=True))
 return sorted(rows)
g,b=load(old/'delivery/Rev15T-Continuous-Asphalt-Ground.glb');n,nb=load(R/'delivery/Rev15T1-Unpainted-Asphalt-Ground.glb');assert fingerprint(g,b)==fingerprint(n,nb)
assert len(g['nodes'])==len(n['nodes'])==13
def nodeTransforms(g):return sorted(json.dumps({k:n[k] for k in ['translation','rotation','scale','matrix'] if k in n},sort_keys=True) for n in g['nodes'])
assert nodeTransforms(g)==nodeTransforms(n)
mat=next(m for m in n['materials'] if m['name'].startswith('REV15T1 /'));assert mat['normalTexture'].get('texCoord',0)==1
tex=n['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']];image=n['images'][tex['source']];v=n['bufferViews'][image['bufferView']];data=nb[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
pixels=np.array(Image.open(io.BytesIO(data)).convert('RGB'));expected=np.array(Image.open(R/'textures/road-world-color.png').convert('RGB'));assert np.array_equal(pixels,expected)
out={'status':'PASS','allPrimitiveGeometryNormalsUVsAndIndicesUnchanged':True,'allNodeTransformsUnchanged':True,'nodes':13,'normalUVChannel':1,'runtimeColorPixelsMatchUnpaintedSource':True,'sha256':hashlib.sha256((R/'delivery/Rev15T1-Unpainted-Asphalt-Ground.glb').read_bytes()).hexdigest()}
(R/'evidence/runtime-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
