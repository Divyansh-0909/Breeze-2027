"""Lossless positions/images; native glTF NORMAL/TANGENT/UV0 quantization.
No Draco/Meshopt/KTX2 decoder. Keep accepted pilot's attributes float32.
"""
from pathlib import Path
import json,struct,shutil,numpy as np,hashlib
ROOT=Path(__file__).resolve().parents[2];directory=ROOT/'public/models/gullyverse/quarry-rollout';backup=ROOT/'assets-source/gullyverse/quarry-rollout/uncompressed';backup.mkdir(exist_ok=True);results=[]
for path in sorted(directory.glob('*.glb')):
 data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);binary=data[28+length:];newViews={};updated=[];before=len(data)
 if 'KHR_mesh_quantization'in doc.get('extensionsUsed',[]):continue
 shutil.copy2(path,backup/path.name)
 for mesh in doc['meshes']:
  if mesh.get('name','').startswith('Quarry_Rock_04')or mesh.get('name','').startswith('Wall_Collision'):continue
  for primitive in mesh['primitives']:
   normalAccessor=doc['accessors'][primitive['attributes']['NORMAL']];normalView=doc['bufferViews'][normalAccessor['bufferView']];sourceNormals=np.frombuffer(binary,dtype='<f4',count=normalAccessor['count']*3,offset=normalView.get('byteOffset',0)+normalAccessor.get('byteOffset',0)).reshape(-1,3)
   for key in ['NORMAL','TANGENT','TEXCOORD_0']:
    if key not in primitive['attributes']:continue
    ai=primitive['attributes'][key];a=doc['accessors'][ai]
    if ai in updated:continue
    dim={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and not v.get('byteStride')
    values=np.frombuffer(binary,dtype='<f4',count=a['count']*dim,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dim).copy()
    if key=='TANGENT':
     # Blender can emit a zero tangent at a decimated reflected-UV boundary.
     # Derive the missing basis from the actual fine-normal UV triangle.
     def attr(index,dims,dt='<f4'):
      x=doc['accessors'][index];view=doc['bufferViews'][x['bufferView']];return np.frombuffer(binary,dtype=dt,count=x['count']*dims,offset=view.get('byteOffset',0)+x.get('byteOffset',0)).reshape(x['count'],dims)
     zero=np.flatnonzero(np.linalg.norm(values[:,:3],axis=1)<1e-6)
     if len(zero):
      positions=attr(primitive['attributes']['POSITION'],3);fine=attr(primitive['attributes']['TEXCOORD_1'],2);indexAccessor=doc['accessors'][primitive['indices']];indices=attr(primitive['indices'],1,{5123:'<u2',5125:'<u4'}[indexAccessor['componentType']]).reshape(-1,3)
      for i in zero:
       normal=sourceNormals[i].astype(float);candidate=None
       for f in indices[np.any(indices==i,axis=1)]:
        d1=positions[f[1]]-positions[f[0]];d2=positions[f[2]]-positions[f[0]];aUV=fine[f[1]]-fine[f[0]];bUV=fine[f[2]]-fine[f[0]];det=aUV[0]*bUV[1]-aUV[1]*bUV[0]
        if abs(det)>1e-12:
         t=(d1*bUV[1]-d2*aUV[1])/det;t-=normal*np.dot(normal,t)
         if np.linalg.norm(t)>1e-9:candidate=t/np.linalg.norm(t);break
       if candidate is None:
        axis=np.array([1.,0,0])if abs(normal[0])<.9 else np.array([0.,1,0]);candidate=np.cross(normal,axis);candidate/=np.linalg.norm(candidate)
       values[i,:3]=candidate
      print('TANGENT_REPAIR',path.name,mesh['name'],len(zero))
    if key=='TEXCOORD_0':
     if values.min()<0 or values.max()>1:continue
     q=np.round(values*65535).astype('<u2');component=5123;stride=None
    else:
     q=np.round(np.clip(values,-1,1)*32767).astype('<i2');component=5122;stride=8
    encoded=np.pad(q,((0,0),(0,1))).astype('<i2').tobytes()if dim==3 else q.tobytes();vi=len(doc['bufferViews']);view={'buffer':0,'byteLength':len(encoded),'target':34962}
    if stride:view['byteStride']=stride
    doc['bufferViews'].append(view);newViews[vi]=encoded;a['bufferView']=vi;a['byteOffset']=0;a['componentType']=component;a['normalized']=True
    if 'min'in a:a['min']=q.min(axis=0).astype(int).tolist()
    if 'max'in a:a['max']=q.max(axis=0).astype(int).tolist()
    updated.append(ai)
 if updated:
  doc.setdefault('extensionsUsed',[]).append('KHR_mesh_quantization');doc.setdefault('extensionsRequired',[]).append('KHR_mesh_quantization')
 used={a['bufferView']for a in doc['accessors']if'bufferView'in a}|{i['bufferView']for i in doc.get('images',[])if'bufferView'in i};views=[];mapping={};output=bytearray()
 for i,v in enumerate(doc['bufferViews']):
  if i not in used:continue
  output.extend(b'\0'*((-len(output))%4));payload=newViews[i]if i in newViews else binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];mapping[i]=len(views);views.append({**v,'byteOffset':len(output)});output.extend(payload)
 for a in doc['accessors']:
  if'bufferView'in a:a['bufferView']=mapping[a['bufferView']]
 for i in doc.get('images',[]):
  if'bufferView'in i:i['bufferView']=mapping[i['bufferView']]
 doc['bufferViews']=views;doc['buffers'][0]['byteLength']=len(output);jsonbytes=json.dumps(doc,separators=(',',':')).encode();jsonbytes+=b' '*((-len(jsonbytes))%4);output.extend(b'\0'*((-len(output))%4));result=struct.pack('<III',0x46546c67,2,12+8+len(jsonbytes)+8+len(output))+struct.pack('<II',len(jsonbytes),0x4e4f534a)+jsonbytes+struct.pack('<II',len(output),0x004e4942)+output;path.write_bytes(result)
 results.append({'file':str(path.relative_to(ROOT)),'beforeBytes':before,'afterBytes':len(result),'savedBytes':before-len(result),'quantizedAccessors':len(updated),'positionPolicy':'float32 exact; approved pilot attributes exact','normalTangentUVPolicy':'normalized signed16/unsigned16 on new parts only','images':'byte-exact','requiredExtension':'KHR_mesh_quantization (native current GLTFLoader)','sha256':hashlib.sha256(result).hexdigest()})
(ROOT/'reports/stage-2c-quarry-rollout-2026-10-12/raw/attribute-quantization.json').write_text(json.dumps(results,indent=2));print([(Path(r['file']).name,r['beforeBytes'],r['afterBytes'])for r in results])
