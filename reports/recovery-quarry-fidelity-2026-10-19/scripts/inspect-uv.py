import json,struct,numpy as np
from pathlib import Path
p=Path('public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb');data=p.read_bytes();n=struct.unpack_from('<I',data,12)[0];j=json.loads(data[20:20+n]);binary=data[28+n:]
def arr(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4',5122:'<i2'}[a['componentType']];return np.frombuffer(binary,dtype=dtype,count=a['count']*cols,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,cols)
rows=[]
for node in j['nodes']:
 if node.get('name')not in ['Foundation_Wall_'+str(i)+'_LOD0'for i in [13,14,15,16,17]]:continue
 a=j['meshes'][node['mesh']]['primitives'][0]['attributes'];xyz,uv=arr(a['POSITION']),arr(a['TEXCOORD_0']);fit=np.polyfit(xyz[:,1],uv[:,1],1);print(node['name'],'uv ranges',uv.min(0),uv.max(0),'V per metre',fit)
 rows.append({'name':node['name'],'UVMin':uv.min(0).tolist(),'UVMax':uv.max(0).tolist(),'VPerMetre':fit.tolist()})
Path('/workspace/recovery-fidelity/2026-10-19/host-uv-inspection.json').write_text(json.dumps(rows,indent=2)+'\n')
