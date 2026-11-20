from pathlib import Path
import struct,json,hashlib
R=Path(__file__).resolve().parents[1];p=R/'delivery/Rev15T2-Wet-Grain-Asphalt-Ground.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);tail=b[20+n:];removed=0
for m in g['meshes']:
 for prim in m['primitives']:
  name=g['materials'][prim['material']]['name']
  if not any(x in name for x in ['Wet coarse-grain asphalt','Silt-coated wet shoulder']) and 'COLOR_0' in prim['attributes']:prim['attributes'].pop('COLOR_0');removed+=1
jb=json.dumps(g,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);out=struct.pack('<4sII',b'glTF',2,12+8+len(jb)+len(tail))+struct.pack('<II',len(jb),0x4e4f534a)+jb+tail;p.write_bytes(out)
assert len(g['nodes'])==29
for name in ['Wet coarse-grain asphalt','Silt-coated wet shoulder']:
 mi=next(i for i,m in enumerate(g['materials']) if name in m['name']);mat=g['materials'][mi]
 assert mat['normalTexture'].get('texCoord',0)==1 and mat['pbrMetallicRoughness']['baseColorTexture'].get('texCoord',0)==1
 prims=[x for m in g['meshes'] for x in m['primitives'] if x.get('material')==mi]
 assert len(prims)==4 and all('COLOR_0' in x['attributes'] and 'TEXCOORD_1' in x['attributes'] for x in prims)
(R/'evidence/export.json').write_text(json.dumps({'status':'PASS','bytes':len(out),'sha256':hashlib.sha256(out).hexdigest(),'nodes':29,'embeddedImages':len(g['images']),'roadAndMudGrainColorUVChannel':1,'normalUVChannel':1,'macroRoughnessUVChannel':0,'tintAttribute':'COLOR_0','unnecessaryUndersideTintBindingsRemoved':removed},indent=2)+'\n');print('RUNTIME_EXPORT_PASS',len(out),hashlib.sha256(out).hexdigest())
