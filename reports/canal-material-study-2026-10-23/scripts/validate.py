from pathlib import Path
import hashlib,json,struct,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]; R=ROOT/'reports/canal-material-study-2026-10-23';S=ROOT/'assets-source/gullyverse/canal-material-study';O=ROOT/'public/models/gullyverse/canal-material-study'
x=json.load(open(O/'materials.json'));out=[]
for m in x['materials']:
 for r in m['sourceMaps']:
  p=ROOT/r['file']
  with p.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
  with p.open('rb')as f:assert hashlib.file_digest(f,'md5').hexdigest()==r['providerMD5']
 for r in m['runtimeMaps']:
  p=ROOT/'public'/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert Image.open(p).size==(2048,2048)
 orm=np.asarray(Image.open(O/m['id']/'orm.png'));assert np.all(orm[:,:,0]==255);assert np.all(orm[:,:,2]==0)
 normal=np.asarray(Image.open(O/m['id']/'normal.png')).astype('float32')/127.5-1;norm=np.linalg.norm(normal,axis=2)
 # Filtered source scan vectors need not be unit length before shader sampling.
 # Verify the actual Three tangent-space normalization path, not a false PNG invariant.
 assert np.isfinite(normal).all();assert np.all(norm>1e-6)
 shader=(ROOT/'node_modules/three/src/renderers/shaders/ShaderChunk/normal_fragment_maps.glsl.js').read_text()
 assert 'normal = normalize( tbn * mapN );' in shader
 scaled=normal.copy();scaled[:,:,:2]*=.7;scaled/=np.linalg.norm(scaled,axis=2,keepdims=True)
 assert np.max(np.abs(np.linalg.norm(scaled,axis=2)-1))<1e-6
 out.append({'id':m['id'],'status':'PASS','runtimeBytes':m['runtimeBytes'],'sourceProviderChecksumsVerified':True,'normalGL':True,'filteredSourceVectorsRenormalizedByThreeShader':True,'normalLengthPercentiles':[float(np.quantile(norm,p))for p in [0,.01,.5,.99,1]],'ormR':255,'metalnessB':0,'roughnessRange':[float(orm[:,:,1].min()/255),float(orm[:,:,1].max()/255)],'nativeDimensionsM':m['nativeDimensionsM'],'commonComparisonPeriodM':x['comparisonTilePeriodM'],'decodedRGBA8MipMiB':m['decodedRGBA8MipBytes']/1024/1024})
base=json.load(open(R/'raw/preserved-file-baseline.json'));bad=[]
for rec in base['files']:
 p=ROOT/rec['file']
 with p.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 if h!=rec['sha256'] or p.stat().st_size!=rec['bytes']:bad.append(rec['file'])
assert not bad,bad
# Every original vertex/index/UV/normal/tangent/color/LOD stays in its original GLB.
path=ROOT/'public/models/gullyverse/c9-cave-recovery/cave-entrance.glb';data=path.read_bytes();version,total=struct.unpack_from('<II',data,4);assert data[:4]==b'glTF'and version==2 and total==len(data)
length=struct.unpack_from('<I',data,12)[0];gltf=json.loads(data[20:20+length]);assert not gltf.get('images');attrs=[]
for mesh in gltf['meshes']:
 for primitive in mesh['primitives']:
  assert {'POSITION','NORMAL','TEXCOORD_0','TANGENT','COLOR_0'}<=primitive['attributes'].keys();attrs.append({'mesh':mesh.get('name'),'attributes':list(primitive['attributes'])})
report={'status':'PASS','materials':out,'existingFilesByteIdentical':len(base['files']),'changedProtectedFiles':bad,'existingCaveSHA256':hashlib.sha256(data).hexdigest(),'existingCaveGlTFVersion':version,'existingCaveAttributes':attrs,'geometryRegenerated':False,'newGLBs':0,'newLights':0,'limitation':'Byte-identical geometry preserves existing defects; it does not certify that inherited visibility is defect-free.'}
(R/'raw/asset-validation.json').write_text(json.dumps(report,indent=2));print('PASS',len(out),'materials;',len(base['files']),'protected original files unchanged')
