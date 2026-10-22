"""Open the editable master without saving; verify native hero and packed sources."""
from pathlib import Path
import bpy,json,hashlib,struct,numpy as np
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19'
master=ROOT/'assets-source/gullyverse/quarry-fidelity-correction/quarry-fidelity-correction.blend'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(master);bpy.ops.wm.open_mainfile(filepath=str(master))
contract=json.loads(bpy.data.texts['QUARRY_FIDELITY_CONTRACT'].as_string());tags=json.loads(bpy.data.texts['ALL_LOD_FACE_SOURCE_TAGS'].as_string())
images=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)}for i in bpy.data.images if i.source=='FILE']
assert images and all(i['packed']for i in images)
data=(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb').read_bytes();n=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+n]);binary=data[28+n:]
def arr(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]);return np.ndarray((a['count'],k),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',k*dt.itemsize),dt.itemsize))
def key(tri):return tuple(sorted(tuple(float(x)for x in np.float32(p))for p in tri))
oldspec=json.loads((ROOT/'public/models/gullyverse/recovered-c9-composition/manifest.json').read_text());rows=[]
for level in range(3):
 node=next(o for o in j['nodes']if o.get('name','').endswith('LOD'+str(level)));pr=j['meshes'][node['mesh']]['primitives'][0];xyz=arr(pr['attributes']['POSITION']);faces=arr(pr['indices']).reshape(-1,3)
 start=oldspec['LODs'][level]['retainedHostTriangles'];count=oldspec['LODs'][level]['sourceTriangles'];old={key(xyz[f])for f in faces[start:start+count]}
 ob=bpy.data.objects[f'Fidelity_Wall_15_LOD{level}'];points=np.array([[v.co.x,v.co.z,-v.co.y]for v in ob.data.vertices]);assert len(tags[level])==len(ob.data.polygons)
 new={key(points[list(p.vertices)])for p,tag in zip(ob.data.polygons,tags[level])if tag=='hero'}
 assert old==new,(level,len(old),len(new),len(old-new))
 rows.append({'LOD':level,'exactOriginalHeroTriangles':len(new),'sourceUniformScale':.9,'positionsUnchanged':True,'UVSideProjectionMayChange':True})
assert sha(master)==before
result={'status':'PASS','masterBytes':master.stat().st_size,'masterSHA256':before,'openedReadOnly':True,'packedFileImages':images,'hero':rows,'sourceTransformsUniform':all(max(s['singularValues'])-min(s['singularValues'])<1e-10 for s in contract['sourceModels']),'highSourceObjects':[{'name':o.name,'triangles':len(o.data.polygons)}for o in bpy.data.objects if o.type=='MESH'and ('High'in o.name or o.name.startswith('Native_Coastal04'))]}
(R/'raw/editable-master-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('EDITABLE_MASTER_PASS',len(images),rows,flush=True)
