from pathlib import Path
import json,hashlib,struct,numpy as np
from PIL import Image
ROOT=Path.cwd();RAW=ROOT/'reports/recovery-phase3-c9-2026-10-19/raw'
def sha(path):
 with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def arrays(doc,binary,index):
 a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 dtype={5126:'<f4',5122:'<i2',5123:'<u2',5125:'<u4'}[a['componentType']]
 x=np.frombuffer(binary,dtype=dtype,count=a['count']*components,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],components).astype(float)
 if a.get('normalized'):x/=32767 if a['componentType']==5122 else 65535
 return x
source=ROOT/'assets-source/gullyverse/quarry-scanned-composition';directory=ROOT/'public/models/gullyverse/recovered-c9-composition'
manifest=json.loads((directory/'manifest.json').read_text());provenance=json.loads((source/'source-provenance.json').read_text());originals=[]
for row in provenance['files']:
 p=ROOT/row['path'];assert p.stat().st_size==row['bytes'];assert sha(p)==row['sha256'];assert hashlib.md5(p.read_bytes()).hexdigest()==row['providerMD5'];originals.append({'path':row['path'],'bytes':row['bytes'],'sha256':sha(p)})
assert manifest['uniformScale']==.9 and all(abs(v-.9)<1e-12 for v in manifest['singularValues'])
assert sha(directory/'composition-region.glb')==manifest['runtimeSHA256'];assert sha(directory/'composition-bake.glb')==manifest['normalBake']['sha256']
doc,binary=read(directory/'composition-region.glb');assert not doc.get('images')and not doc.get('textures');rows=[]
for node in doc['nodes']:
 if 'mesh'not in node:continue
 p=doc['meshes'][node['mesh']]['primitives'][0];attrs=p['attributes'];assert {'POSITION','NORMAL','TANGENT','TEXCOORD_0','TEXCOORD_1'}<=attrs.keys()
 values={k:arrays(doc,binary,i)for k,i in attrs.items()};assert all(np.isfinite(v).all()for v in values.values())
 n,t=values['NORMAL'],values['TANGENT'];length=np.linalg.norm(t[:,:3],axis=1);normal_length=np.linalg.norm(n,axis=1);dot=abs((n*t[:,:3]).sum(1))
 assert length.min()>.99 and length.max()<1.01 and normal_length.min()>.99 and dot.max()<.001 and set(t[:,3])<={-1.,1.}
 if not node['name'].endswith('LOD0'):assert values['TEXCOORD_1'].min()>=0 and values['TEXCOORD_1'].max()<=1
 rows.append({'node':node['name'],'vertices':len(n),'minimumTangentLength':float(length.min()),'maximumTangentLength':float(length.max()),'maximumAbsNormalDotTangent':float(dot.max()),'UV0Finite':True,'UV1Finite':True,'normalChannel':0 if node['name'].endswith('LOD0')else 1})
bake,_=read(directory/'composition-bake.glb');assert len(bake['images'])==1 and bake['materials'][0]['normalTexture']['texCoord']==1
image=Image.open(source/'geometry-normal-1024.png');assert image.size==(1024,1024)
base=json.loads((ROOT/'public/models/gullyverse/recovered-c8-material/manifest.json').read_text());assert base['approvedDefaultScale']==3
assert sha(ROOT/'public/models/gullyverse/recovered-c8-material/scanned-materials.glb')=='ff330dcfe418436d324535675472b7e10ca34e8f4cb924faf40e7748bea5feee'
result={'status':'PASS','sourceOriginals':originals,'sourceDimensionsM':manifest['sourceNativeDimensionsM'],'cropDimensionsM':manifest['cropDimensionsM'],'transformSingularValues':manifest['singularValues'],'runtimeMeshes':rows,'geometryBytes':manifest['runtimeBytes'],'bakeBytes':manifest['normalBake']['bytes'],'normalImage':{'width':1024,'height':1024,'channels':image.mode,'UV':1,'estimatedRGBA8MipBytes':1024*1024*4*4/3},'approvedC8TextureScale':3,'C8MaterialBytesUnchanged':True,'geometryContainsPBRImages':False}
(RAW/'asset-contract-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('ASSET_CONTRACT PASS',manifest['runtimeBytes']+manifest['normalBake']['bytes'])
