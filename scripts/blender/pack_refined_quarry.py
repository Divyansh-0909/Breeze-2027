"""Geometry-only review exports borrow approved material at runtime.
Original Blender export retained. Native attribute quantization is identical to
Stage2C and does not alter positions or UV1; no new compression loaders.
"""
from pathlib import Path
import json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2];directory=ROOT/'public/models/gullyverse/quarry-refinement';backup=ROOT/'assets-source/gullyverse/quarry-refinement/with-approved-material';backup.mkdir(parents=True,exist_ok=True)
rows=[]
for path in sorted(directory.glob('*.glb')):
 data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+n]);binary=data[28+n:]
 if not doc.get('images'):continue
 (backup/path.name).write_bytes(data)
 images={i['bufferView']for i in doc['images']};used={a['bufferView']for a in doc['accessors']};views=[];mapping={};output=bytearray()
 for i,v in enumerate(doc['bufferViews']):
  if i not in used:continue
  output.extend(b'\0'*((-len(output))%4));payload=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];mapping[i]=len(views);views.append({**v,'byteOffset':len(output)});output.extend(payload)
 for a in doc['accessors']:a['bufferView']=mapping[a['bufferView']]
 for k in ['images','textures','samplers']:doc.pop(k,None)
 doc['materials']=[{'name':'BORROW_APPROVED_LIMESTONE_RUNTIME','pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':1}}]
 for m in doc['meshes']:
  for p in m['primitives']:p['material']=0
 # Geometry exports retain no material extensions; mesh attributes are untouched.
 doc.pop('extensionsUsed',None);doc.pop('extensionsRequired',None);doc['bufferViews']=views;doc['buffers'][0]['byteLength']=len(output)
 js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);output.extend(b'\0'*((-len(output))%4));result=struct.pack('<III',0x46546c67,2,28+len(js)+len(output))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(output),0x004e4942)+output;path.write_bytes(result)
 rows.append({'file':path.name,'withMapsBytes':len(data),'geometryOnlyBytes':len(result),'removedImagePayloadBytes':sum(docv['byteLength'] for i,docv in enumerate(json.loads(data[20:20+n])['bufferViews'])if i in images),'materialPolicy':'Exact original maps borrowed from live Stage2C owner, zero image download in this GLB'})
# Existing validated quantization process, redirected ONLY to the new directory.
source=(ROOT/'scripts/blender/quantize_quarry_attributes.py').read_text().replace("directory=ROOT/'public/models/gullyverse/quarry-rollout'","directory=ROOT/'public/models/gullyverse/quarry-refinement'").replace("backup=ROOT/'assets-source/gullyverse/quarry-rollout/uncompressed'","backup=ROOT/'assets-source/gullyverse/quarry-refinement/uncompressed-geometry'").replace("reports/stage-2c-quarry-rollout-2026-10-12/raw/attribute-quantization.json","reports/stage-2c1-geological-refinement-2026-10-13/raw/attribute-quantization.json")
exec(compile(source,str(ROOT/'scripts/blender/quantize_quarry_attributes.py'),'exec'))
(ROOT/'reports/stage-2c1-geological-refinement-2026-10-13/raw/geometry-only-pack.json').write_text(json.dumps(rows,indent=2))
