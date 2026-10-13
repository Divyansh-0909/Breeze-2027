"""Losslessly split exact approved maps from geometry; no new decoder required."""
from pathlib import Path
import struct,json,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'public/models/gullyverse/limestone-excavation'
SOURCE=ROOT/'assets-source/gullyverse/limestone-excavation/unpacked'
SOURCE.mkdir(parents=True,exist_ok=True)
RAW=ROOT/'reports/stage-2c2-limestone-excavation-2026-10-13/raw'

def read(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,12)[0]
    return json.loads(data[20:20+n]),data[28+n:]
def write(path,doc,binary):
    doc['buffers']=[{'byteLength':len(binary)}]
    js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
    binary=bytes(binary)+b'\0'*((-len(binary))%4)
    data=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
    path.write_bytes(data)

rows=[]
for path in OUT.glob('*.glb'):
    if path.name=='grey-limestone-material.glb':continue
    doc,binary=read(path)
    if not doc.get('images'):continue
    (SOURCE/path.name).write_bytes(path.read_bytes())
    used={a['bufferView']for a in doc['accessors']};views=[];mapping={};payload=bytearray()
    for i,view in enumerate(doc['bufferViews']):
        if i not in used:continue
        payload.extend(b'\0'*((-len(payload))%4));mapping[i]=len(views)
        views.append({**view,'byteOffset':len(payload)})
        payload.extend(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])
    for a in doc['accessors']:a['bufferView']=mapping[a['bufferView']]
    for key in['images','textures','samplers']:doc.pop(key,None)
    doc['materials']=[{'name':'BORROW_APPROVED_GREY_LIMESTONE','pbrMetallicRoughness':{'metallicFactor':0,'roughnessFactor':1}}]
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:primitive['material']=0
    doc.pop('extensionsUsed',None);doc.pop('extensionsRequired',None);doc['bufferViews']=views
    write(path,doc,payload);rows.append({'file':path.name,'geometryOnlyBytes':path.stat().st_size})

# Material-only GLB reuses the exact image buffer bytes, samplers and material
# JSON from the approved pilot. Its tiny holder mesh is NEVER rendered.
src=ROOT/'public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb'
old,binary=read(src);image_indices={i['bufferView']for i in old['images']}
views=[];mapping={};payload=bytearray();images=[]
for i in sorted(image_indices):
    v=old['bufferViews'][i];payload.extend(b'\0'*((-len(payload))%4));mapping[i]=len(views)
    views.append({'buffer':0,'byteOffset':len(payload),'byteLength':v['byteLength']})
    payload.extend(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
for im in old['images']:images.append({**im,'bufferView':mapping[im['bufferView']]})
payload.extend(b'\0'*((-len(payload))%4));position_offset=len(payload)
payload.extend(struct.pack('<9f',0,0,0,.001,0,0,0,.001,0));views.append({'buffer':0,'byteOffset':position_offset,'byteLength':36,'target':34962})
normal_offset=len(payload);payload.extend(struct.pack('<9f',0,0,1,0,0,1,0,0,1));views.append({'buffer':0,'byteOffset':normal_offset,'byteLength':36,'target':34962})
uv_offset=len(payload);payload.extend(struct.pack('<6f',0,0,1,0,0,1));views.append({'buffer':0,'byteOffset':uv_offset,'byteLength':24,'target':34962})
tangent_offset=len(payload);payload.extend(struct.pack('<12f',1,0,0,1,1,0,0,1,1,0,0,1));views.append({'buffer':0,'byteOffset':tangent_offset,'byteLength':48,'target':34962})
material_doc={'asset':old['asset'],'scene':0,'scenes':[{'nodes':[0]}],
 'nodes':[{'name':'Approved_Material_Holder_Not_Rendered','mesh':0}],
 'meshes':[{'primitives':[{'attributes':{'POSITION':len(views)-3,'NORMAL':len(views)-2,'TEXCOORD_0':len(views)-1},'material':0}]}],
 'accessors':[{'bufferView':i,'componentType':5126,'count':3,'type':['VEC3','VEC3','VEC2','VEC4'][j],
               **({'min':[0,0,0],'max':[.001,.001,0]}if j==0 else{})}
              for j,i in enumerate(range(len(views)-4,len(views)))],
 'bufferViews':views,'materials':old['materials'],'textures':old['textures'],
 'samplers':old.get('samplers',[]),'images':images}
# Holder attribute indices refer to accessors, not bufferViews.
material_doc['meshes'][0]['primitives'][0]['attributes']={'POSITION':0,'NORMAL':1,'TEXCOORD_0':2,'TANGENT':3}
for k in['extensionsUsed','extensionsRequired']:
    if k in old:material_doc[k]=old[k]
write(OUT/'grey-limestone-material.glb',material_doc,payload)
evidence={'sourceGLBSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),
          'materialJSONUnchanged':material_doc['materials']==old['materials'],
          'images':[{'name':im.get('name'),'bytes':old['bufferViews'][im['bufferView']]['byteLength'],
                     'sha256':hashlib.sha256(binary[old['bufferViews'][im['bufferView']].get('byteOffset',0):old['bufferViews'][im['bufferView']].get('byteOffset',0)+old['bufferViews'][im['bufferView']]['byteLength']]).hexdigest()}
                    for im in old['images']],
          'materialHolderBytes':(OUT/'grey-limestone-material.glb').stat().st_size,
          'geometry':rows,'note':'Original image payload bytes and material factors unchanged. No Stage2C or Stage2C1 files rewritten.'}
(RAW/'material-and-pack.json').write_text(json.dumps(evidence,indent=2))
print(json.dumps(evidence,indent=2))
