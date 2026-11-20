import bpy,json,struct,numpy as np,os
from pathlib import Path
out=Path(os.environ.get('GULLYVERSE_OUT',str(Path(__file__).resolve().parents[2]/'public/models/gullyverse/locked-rev15z-clean-v2')));raw=(out/'contact-frontage.png.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);bin=raw[28+n:]
def accessor(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];typ={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];count={'VEC2':2,'VEC3':3,'SCALAR':1}[a['type']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',np.dtype(typ).itemsize*count);return np.ndarray((a['count'],count),dtype=typ,buffer=bin,offset=start,strides=(stride,np.dtype(typ).itemsize)).copy()
with bpy.data.libraries.load(str(out/'contact-frontage-baked.blend'))as(a,b):b.collections=['Runtime / contact-frontage']
objects={o.get('runtimeOriginalSource'):o for o in b.collections[0].objects};rows=[]
uv_name=json.loads((out/'manifest.json').read_text())['bake']['uvName']
for node in g['nodes']:
 source=node.get('extras',{}).get('runtimeOriginalSource')
 if source not in objects or 'mesh'not in node:continue
 ob=objects[source];expected={};lightmap_uv=ob.data.uv_layers[uv_name]
 for p in ob.data.polygons:
  for li in p.loop_indices:
   pos=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv=lightmap_uv.data[li].uv;k=(pos.x,pos.z,-pos.y);expected.setdefault(k,set()).add((uv.x,1-uv.y))
 for prim in g['meshes'][node['mesh']]['primitives']:
  pos=accessor(prim['attributes']['POSITION']);matches={}
  for k,idx in prim['attributes'].items():
   if not k.startswith('TEXCOORD_'):continue
   uv=accessor(idx)
   # A float32 round-trip of 1 - V may differ by one ULP. Compare the
   # bound coordinates directly without rounding across a decimal boundary.
   n=sum(any(max(abs(float(q[0])-u),abs(float(q[1])-v))<=1e-6 for u,v in expected.get(tuple(map(float,p)),()))for p,q in zip(pos,uv));matches[k]=[n,len(pos)]
  rows.append({'source':source,'materialChannel':g['materials'][prim['material']].get('extras',{}).get('runtimeLightmapChannel'),'matches':matches})
expectedBindings=sum(len({p.material_index for p in ob.data.polygons})for ob in objects.values())
assert len(rows)==expectedBindings,(len(rows),expectedBindings)
for row in rows:
 matched,total=row['matches']['TEXCOORD_'+str(row['materialChannel'])];assert matched==total,row
(out/'uv-roundtrip-verification.json').write_text(json.dumps({'status':'PASS','bindings':rows,'allExpectedChannelsMatchBlenderWithinFloatTolerance':True,'uvAbsoluteTolerance':1e-6},indent=2)+'\n');print('UV_ROUNDTRIP_PASS',len(rows))
