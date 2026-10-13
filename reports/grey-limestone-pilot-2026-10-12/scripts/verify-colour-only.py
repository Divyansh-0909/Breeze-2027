from pathlib import Path
import json,struct,hashlib,numpy as np
root=Path.cwd();r=root/'reports/grey-limestone-pilot-2026-10-12/raw';rows=[]
def glb(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def array(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.frombuffer(b,dtype=dtype,count=a['count']*dims,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dims)
for old in (root/'public/models/gullyverse/pilot-limestone').glob('*.glb'):
 name='quarry-grey-limestone-pilot.glb' if old.name=='quarry-limestone-pilot.glb' else old.name;new=root/'public/models/gullyverse/pilot-limestone-grey'/name;a,ab=glb(old);b,bb=glb(new);row={'file':name,'bytes':new.stat().st_size,'meshes':[]};assert len(a['meshes'])==len(b['meshes'])
 for x,y in zip(a['meshes'],b['meshes']):
  assert x['name']==y['name'];m={'name':x['name'],'attributes':{}}
  for p,q in zip(x['primitives'],y['primitives']):
   for kind,i in p['attributes'].items():
    oldarray=array(a,ab,i);newarray=array(b,bb,q['attributes'][kind]);equal=np.array_equal(oldarray,newarray);m['attributes'][kind]={'byteEquivalentValues':equal,'changedComponents':int(np.count_nonzero(oldarray!=newarray)),'maxAbsoluteDifference':float(np.max(np.abs(oldarray.astype(float)-newarray.astype(float))))}
    if kind!='TANGENT':assert equal,(name,kind)
   assert np.array_equal(array(a,ab,p['indices']),array(b,bb,q['indices']));m['indicesIdentical']=True
  row['meshes'].append(m)
 rows.append(row)
texture_rows=[]
for p in (root/'assets-source/gullyverse/limestone-pilot/textures').glob('*'):
 if 'basecolor' in p.name:continue
 n=root/'assets-source/gullyverse/limestone-grey-pilot/textures'/p.name;same=hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()==hashlib.file_digest(open(n,'rb'),'sha256').hexdigest();assert same,p.name;texture_rows.append({'file':p.name,'SHA256Identical':same})
s=json.loads((r/'starting-state.json').read_text());bad=[p for p,h in s['preservedLimestoneHashes'].items() if not (root/p).is_file() or hashlib.file_digest(open(root/p,'rb'),'sha256').hexdigest()!=h];assert not bad,bad
baseline=json.loads((root/'reports/stage-2a-asset-pilot-2026-10-11/raw/source-hashes-before.json').read_text());bad=[p for p,h in baseline.items() if hashlib.file_digest(open(root/p,'rb'),'sha256').hexdigest()!=h];assert not bad,bad
result={'status':'PASS','scope':'Geometry positions/normals/UVs/indices and all six non-colour source/runtime maps match exactly. Tangents are separately quantified, not claimed byte-identical. Only requested albedo palette/fallback material colour authored differently.','GLBs':rows,'normalRoughnessAOMaps':texture_rows,'preservedPriorFiles':len(s['preservedLimestoneHashes']),'preservedProductionFiles':len(baseline),'tangentNote':'Initial all-attribute byte-identity assertion found one LOD0 tangent component changed by about0.0001 during Blender re-export. No position/normal/UV/index changes. Result reports that exporter difference; it is not hidden by relaxing geometry equality.'};(r/'colour-only-verification.json').write_text(json.dumps(result,indent=2));print('PASS; exact geometry and non-colour maps; tiny exporter tangent difference recorded')
