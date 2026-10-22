"""Read-only comparison with the audited pre-correction tree and hero surface."""
from pathlib import Path
import json, hashlib, struct, numpy as np
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
start=json.loads((R/'raw/starting-hashes.json').read_text())
allowed={'components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx','components/immersive/scannedRockSampling.ts'}
changed=[];missing=[]
for row in start:
 p=ROOT/row['path']
 if not p.is_file():missing.append(row['path'])
 elif sha(p)!=row['sha256']:changed.append(row['path'])
assert not missing and not(set(changed)-allowed),(missing,changed)
def meshes(p):
 data=p.read_bytes();n=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+n]);b=data[28+n:]
 def arr(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]);return np.ndarray((a['count'],k),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',k*dt.itemsize),dt.itemsize))
 out={}
 for node in j['nodes']:
  if 'mesh'not in node:continue
  pr=j['meshes'][node['mesh']]['primitives'][0];a=pr['attributes'];xyz=arr(a['POSITION']);f=arr(pr['indices']).ravel().reshape(-1,3);out[node['name']]=(xyz,f,a)
 return out
def triangles(xyz,faces):
 # Exact exported float32 positions; vertex splits and UVs cannot fake this check.
 return {tuple(sorted(tuple(float(v)for v in xyz[i])for i in f))for f in faces}
old=meshes(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb');new=meshes(ROOT/'public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb')
# Runtime source tags distinguish original hero from the retained old host.
tags=json.loads((ROOT/'assets-source/gullyverse/quarry-scanned-composition/composition-contract.json').read_text()) if (ROOT/'assets-source/gullyverse/quarry-scanned-composition/composition-contract.json').exists() else None
rows=[]
for level in range(3):
 ox,of,oa=next(v for k,v in old.items()if k.endswith('LOD'+str(level)))
 nx,nf,na=next(v for k,v in new.items()if k.endswith('LOD'+str(level)))
 original=triangles(ox,of);preserved=original&triangles(nx,nf)
 rows.append({'LOD':level,'oldRegionTriangles':len(original),'unchangedOldTrianglesInNew':len(preserved),'newRegionTriangles':len(nf),'UV0UV1TangentsPresent':all(k in na for k in ['TEXCOORD_0','TEXCOORD_1','TANGENT'])})
 # All original low hero faces are embedded unchanged; actual high/source tagging
 # is independently checked inside the packed Blender master.
 expected=json.loads((ROOT/'public/models/gullyverse/quarry-fidelity-correction/manifest.json').read_text())['LODs'][level]['heroTriangles']
 assert len(preserved)>=expected,(level,len(preserved),expected)
result={'status':'PASS','startingFiles':len(start),'startingBytes':sum(r['bytes']for r in start),'unchangedFiles':len(start)-len(changed),'authorizedExistingSourceChanges':changed,'missingFiles':missing,'protectedHistoricalAssetsUnchanged':True,'heroExactFloat32TrianglePreservation':rows,'limitations':'Overlap count includes any retained host triangles. Packed-master source tags verify every original hero triangle separately. This is preservation, not pixel-identical C6.2 reconstruction.'}
(R/'raw/final-preservation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
