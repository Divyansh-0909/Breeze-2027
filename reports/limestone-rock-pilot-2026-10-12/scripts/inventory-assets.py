from pathlib import Path
import struct,json,hashlib,io
import numpy as np
from PIL import Image
root=Path.cwd();out=root/'reports/limestone-rock-pilot-2026-10-12/raw';files=[]
for p in (root/'public/models/gullyverse/pilot-limestone').glob('*.glb'):
 b=p.read_bytes();n,typ=struct.unpack_from('<II',b,12);doc=json.loads(b[20:20+n]);binary=b[28+n:];item={'file':str(p.relative_to(root)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'extensionsUsed':doc.get('extensionsUsed',[]),'materials':doc.get('materials',[]),'nodes':doc.get('nodes',[]),'meshes':[],'images':[]}
 for image in doc.get('images',[]):
  view=doc['bufferViews'][image['bufferView']];im=Image.open(io.BytesIO(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]))
  item['images'].append({'mime':image['mimeType'],'dimensions':[im.width,im.height],'embeddedBytes':view['byteLength'],'format':im.format,'mode':im.mode})
 def array(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];dtypes={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4};return np.frombuffer(binary,dtype=dtypes[a['componentType']],count=a['count']*dims[a['type']],offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dims[a['type']])
 for m in doc['meshes']:
  for primitive in m['primitives']:
   attrs=primitive['attributes'];pos=array(attrs['POSITION']);norm=array(attrs['NORMAL']);uv=array(attrs['TEXCOORD_0']) if 'TEXCOORD_0' in attrs else None;tan=array(attrs['TANGENT']) if 'TANGENT' in attrs else None
   row={'name':m.get('name'),'vertices':len(pos),'triangles':doc['accessors'][primitive['indices']]['count']//3,'glTFBounds':[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()],'finiteAttributes':bool(np.isfinite(pos).all() and np.isfinite(norm).all()),'normalLengthRange':[float(np.linalg.norm(norm,axis=1).min()),float(np.linalg.norm(norm,axis=1).max())],'UVRange':[uv.min(axis=0).tolist(),uv.max(axis=0).tolist()] if uv is not None else None,'tangents':tan is not None,'maxNormalTangentDot':float(np.abs((tan[:,:3]*norm).sum(axis=1)).max()) if tan is not None else None};item['meshes'].append(row)
 files.append(item)
tex=[]
for p in (root/'assets-source/gullyverse/limestone-pilot/textures').iterdir():
 im=Image.open(p);tex.append({'file':str(p.relative_to(root)),'bytes':p.stat().st_size,'resolution':[im.width,im.height],'format':im.format,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'asset-inventory.json').write_text(json.dumps({'GLBs':files,'textures':tex,'master':{'file':'assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend','bytes':(root/'assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend').stat().st_size},'provenance':'All pilot surfaces/materials original, no reference-photo texels.'},indent=2))
print([(Path(x['file']).name,x['bytes']) for x in files])
