from pathlib import Path
import json,struct,hashlib,copy,math
import numpy as np
R=Path(__file__).resolve().parents[1];B=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11'
raw=(B/'viewer/pilot.glb').read_bytes();jl=struct.unpack_from('<I',raw,12)[0];source=json.loads(raw[20:20+jl]);binary=raw[28+jl:];out=copy.deepcopy(source)
mapping=json.loads((R/'evidence/bake-mapping.json').read_text());lookup={r['object']:r for r in mapping};light=np.fromfile(R/'evidence/native-lightfield.f32',dtype='<f4').reshape(-1,3);positions=np.fromfile(R/'evidence/native-positions.f32',dtype='<f4').reshape(-1,3)
atlas={r['node']:r for r in json.loads((R/'evidence/ground-atlas.json').read_text())['objects']}
def sha(b):return hashlib.sha256(b).hexdigest()
def accessor(i):
 a=source['accessors'][i];v=source['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);start=v.get('byteOffset',0)+a.get('byteOffset',0)
 data=np.ndarray((a['count'],n),dtype=dt,buffer=binary,offset=start,strides=(v.get('byteStride',n*dt.itemsize),dt.itemsize)).copy();return data
chunks=[];views=[];accessors=[];length=0;view_cache={};accessor_cache={}
def view(data):
 global length
 digest=sha(data)
 if digest in view_cache:return view_cache[digest]
 pad=(-length)%4;chunks.append(bytes(pad));length+=pad;idx=len(views);views.append({'buffer':0,'byteOffset':length,'byteLength':len(data)});chunks.append(data);length+=len(data);view_cache[digest]=idx;return idx
def copy_accessor(i):
 if i in accessor_cache:return accessor_cache[i]
 a=copy.deepcopy(source['accessors'][i]);a['bufferView']=view(accessor(i).tobytes());a['byteOffset']=0;idx=len(accessors);accessors.append(a);accessor_cache[i]=idx;return idx

scale=32.0;checks=[];primitive_count=0;emission_notes=[]
for node in out['nodes']:
 if 'mesh' not in node:continue
 m=lookup[node['name']];cursor=m['offset'];mesh=out['meshes'][node['mesh']]
 for p in mesh['primitives']:
  old=copy.deepcopy(p);points=accessor(old['attributes']['POSITION']);count=len(points);coords=np.c_[points[:,0],-points[:,2],points[:,1]]
  error=float(np.max(np.abs(positions[cursor:cursor+count]-coords)));assert error<.0002,(node['name'],error)
  material=source['materials'][old['material']];irradiance=light[cursor:cursor+count].copy();cursor+=count
  if material.get('extras',{}).get('groundLightmap'):irradiance[:]=1
  emission=np.array(material.get('emissiveFactor',[0,0,0]),dtype=np.float32)*material.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
  if np.any(emission):
   base=np.array(material.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1])[:3],dtype=np.float32)
   et=material.get('emissiveTexture',{}).get('index');bt=material.get('pbrMetallicRoughness',{}).get('baseColorTexture',{}).get('index')
   same_image=et is None or bt is not None and source['textures'][et]['source']==source['textures'][bt]['source']
   assert same_image,(material['name'],'emissive image differs from albedo; separate shader needed')
   irradiance+=emission/np.maximum(base,.02)
   emission_notes.append(material['name'])
  if 'COLOR_0' in old['attributes']:
   col=accessor(old['attributes']['COLOR_0']).astype(np.float32)
   if source['accessors'][old['attributes']['COLOR_0']].get('normalized'):col/=np.iinfo(accessor(old['attributes']['COLOR_0']).dtype).max
   irradiance*=col[:,:3]
  assert np.isfinite(irradiance).all();packed=np.round(np.clip(irradiance/scale,0,1)*65535).astype('<u2')
  ai=len(accessors);accessors.append({'bufferView':view(packed.tobytes()),'byteOffset':0,'componentType':5123,'normalized':True,'count':count,'type':'VEC3'})
  attrs={'POSITION':copy_accessor(old['attributes']['POSITION']),'COLOR_0':ai}
  if 'TEXCOORD_0' in old['attributes']:attrs['TEXCOORD_0']=copy_accessor(old['attributes']['TEXCOORD_0'])
  if material.get('extras',{}).get('groundLightmap'):
   tile=atlas[node['name']]['tileBlenderUV'];lo,hi=np.array(atlas[node['name']]['bounds']);uv=np.c_[tile[0]+(coords[:,0]-lo[0])/(hi[0]-lo[0])*(tile[2]-tile[0]),tile[1]+(coords[:,1]-lo[1])/(hi[1]-lo[1])*(tile[3]-tile[1])]
   normals=accessor(old['attributes']['NORMAL']);uv[normals[:,1]<=.5]=[.002,.002];uv[:,1]=1-uv[:,1];assert uv.min()>=0 and uv.max()<=1
   attrs['TEXCOORD_1']=len(accessors);accessors.append({'bufferView':view(uv.astype('<f4').tobytes()),'byteOffset':0,'componentType':5126,'count':count,'type':'VEC2'})
  p['attributes']=attrs;p['indices']=copy_accessor(old['indices']);p.pop('extensions',None)
  checks.append({'node':node['name'],'primitive':primitive_count,'positionSHA256':sha(points.tobytes()),'indexSHA256':sha(accessor(old['indices']).tobytes()),'UV0SHA256':sha(accessor(old['attributes']['TEXCOORD_0']).tobytes()) if 'TEXCOORD_0' in old['attributes'] else None,'positionMatchError':error,'points':count,'lightingPeak':float(irradiance.max()),'clippedComponents':int((irradiance>scale).sum())});primitive_count+=1
 assert cursor==m['offset']+m['count'],(node['name'],cursor,m)

used_textures=set()
for mat in out['materials']:
 pbr=mat.get('pbrMetallicRoughness',{});mat['pbrMetallicRoughness']={k:v for k,v in pbr.items() if k in ['baseColorFactor','baseColorTexture']}
 if 'baseColorTexture' in pbr:used_textures.add(pbr['baseColorTexture']['index'])
 for k in ['normalTexture','occlusionTexture','emissiveTexture','emissiveFactor']:mat.pop(k,None)
 mat['extensions']={'KHR_materials_unlit':{}};mat.setdefault('extras',{})['nativeLightfieldScale']=scale
texture_map={old:new for new,old in enumerate(sorted(used_textures))};textures=[copy.deepcopy(source['textures'][i]) for i in sorted(used_textures)]
image_map={};images=[];image_checks=[]
for texture in textures:
 old=texture['source']
 if old not in image_map:
  im=copy.deepcopy(source['images'][old]);v=source['bufferViews'][im['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];image_checks.append({'name':im.get('name'),'sha256':sha(data),'bytes':len(data)});im['bufferView']=view(data);image_map[old]=len(images);images.append(im)
 texture['source']=image_map[old]
for mat in out['materials']:
 if 'baseColorTexture' in mat['pbrMetallicRoughness']:mat['pbrMetallicRoughness']['baseColorTexture']['index']=texture_map[mat['pbrMetallicRoughness']['baseColorTexture']['index']]
out['textures']=textures;out['images']=images;out['accessors']=accessors;out['bufferViews']=views;out['buffers']=[{'byteLength':length}];out['extensionsUsed']=['KHR_materials_unlit'];out['extensionsRequired']=['KHR_materials_unlit'];out.setdefault('extras',{})['lightingContract']='Apply material.extras.nativeLightfieldScale to MeshBasicMaterial.color. Bind groundLightmap explicitly on UV1. No runtime lights required.'
text=json.dumps(out,separators=(',',':')).encode();text+=b' '*((-len(text))%4);data=b''.join(chunks);data+=bytes((-len(data))%4);blob=struct.pack('<III',0x46546c67,2,28+len(text)+len(data))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(data),0x004e4942)+data
(R/'viewer/pilot.glb').write_bytes(blob)
report={'status':'PASS','baselineGLBSHA256':sha(raw),'compiledGLBSHA256':sha(blob),'baselineBytes':len(raw),'compiledBytes':len(blob),'triangles':sum(source['accessors'][p['indices']]['count']//3 for m in source['meshes'] for p in m['primitives']),'primitiveCount':primitive_count,'allSourcePositionsIndicesAndUV0CopiedExactly':True,'allNodeTransformsUnchanged':out['nodes']==source['nodes'],'allAlbedoImageBytesUnchanged':True,'retainedImageCount':len(images),'oldImageCount':len(source['images']),'droppedRuntimeAttributes':['NORMAL','TANGENT','unused second UVs'],'lightfieldScale':scale,'colourEncoding':'normalized unsigned short RGB, linear illuminance + matching source emissive contribution','clippedComponents':sum(c['clippedComponents'] for c in checks),'emissiveMaterialsRetained':sorted(set(emission_notes)),'geometry':checks,'images':image_checks}
(R/'evidence/compile.json').write_text(json.dumps(report,indent=2));print('COMPILED',len(blob),'bytes;',len(images),'images;',report['triangles'],'triangles; source geometry and artwork exact',flush=True)
