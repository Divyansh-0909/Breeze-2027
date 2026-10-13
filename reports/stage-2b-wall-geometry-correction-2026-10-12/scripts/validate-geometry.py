from pathlib import Path
import json,struct,hashlib,io
import numpy as np
from PIL import Image
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');anchor=json.loads(Path('assets-source/gullyverse/first-wall-corrected/manifest.json').read_text());host=json.loads(Path('assets-source/gullyverse/first-wall-corrected/host.json').read_text());rotation=np.array([anchor['uAxis'],anchor['vAxis'],anchor['normal']]).T;origin=np.array(anchor['anchor']);original=np.array(host['vertices']);planes=[];solids=[(original,[f['indices'] for f in host['faces']])]+[(np.array(j['vertices']),j['faces'])for j in anchor['joiningContacts']]
unionplanes=[]
for vertices,faces in solids:
 group=[]
 for ids in faces:
  points=vertices[ids];normal=np.cross(points[1]-points[0],points[2]-points[0]);normal/=np.linalg.norm(normal);group.append((normal,points[0]))
 unionplanes.append(group)
requiredCorners=np.concatenate([original]+[np.array(j['vertices'])[list(set(sum([j['faces'][f]for f in j['selectedFaces']],[])))]for j in anchor['joiningContacts']])
for face in host['faces']:
 p=original[face['indices']];n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n);planes.append((n,p[0]))
def read(path):
 b=Path(path).read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def array(doc,binary,i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],count)
results=[]
for path in Path('public/models/gullyverse/first-wall-corrected').glob('*.glb'):
 doc,binary=read(path);meshes=[]
 for mesh in doc['meshes']:
  worldpoints=[]
  for prim in mesh['primitives']:
   pos=array(doc,binary,prim['attributes']['POSITION']);world=pos@rotation.T+origin;worldpoints.append(world);outside=float(np.min(np.stack([np.max(np.stack([(world-a)@n for n,a in group]),axis=0)for group in unionplanes]),axis=0).max());assert outside<2e-5,(path,mesh['name'],outside)
   finite=all(np.isfinite(array(doc,binary,i)).all()for i in prim['attributes'].values());assert finite
   mat=doc.get('materials',[])[prim['material']]if'material'in prim else {};isGray=mat.get('name','').startswith('Approved_');assert not isGray or 'TEXCOORD_1'in prim['attributes']
   meshes.append({'name':mesh['name'],'material':mat.get('name'),'triangles':len(array(doc,binary,prim['indices']))//3,'maxOutsideOriginalHullM':outside,'finite':finite,'uv1':'TEXCOORD_1'in prim['attributes']})
  world=np.concatenate(worldpoints);error=max(float(np.linalg.norm(world-v,axis=1).min())for v in requiredCorners);assert error<2e-5,(mesh['name'],error)
 results.append({'file':str(path),'bytes':path.stat().st_size,'primitives':meshes,'originalHostAndContactCornerMaxErrorM':error})
old,oldbin=read('public/models/gullyverse/first-wall-section/first-wall-section.glb');new,newbin=read('public/models/gullyverse/first-wall-corrected/first-wall-corrected.glb');oldmat=old['materials'][0];newmat=next(m for m in new['materials']if m['name'].startswith('Approved_'))
def images(doc,binary):
 rows=[]
 for i in doc['images']:
  v=doc['bufferViews'][i['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im=Image.open(io.BytesIO(b));rows.append({'encodedSHA256':hashlib.sha256(b).hexdigest(),'pixelSHA256':hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest(),'size':list(im.size),'mime':i['mimeType']})
 return rows
oldimgs=images(old,oldbin);newimgs=images(new,newbin);assert {i['pixelSHA256']for i in oldimgs}=={i['pixelSHA256']for i in newimgs};assert oldmat==newmat,(oldmat,newmat)
locks=json.loads((r/'raw/locked-material-hashes.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in locks.items())
(r/'raw/geometry-material-validation.json').write_text(json.dumps({'status':'PASS','GLBs':results,'materialJSONExactMatch':True,'allSourceMapsHashMatch':True,'embeddedImagesBefore':oldimgs,'embeddedImagesAfter':newimgs,'decodedPixelHashMatch':True,'encodedImageHashMatch':{i['encodedSHA256']for i in oldimgs}=={i['encodedSHA256']for i in newimgs}},indent=2));print('Hull, original20corners, finite attributes, UV1 and exact material/maps PASS')
