from pathlib import Path
import json,struct,math
O=Path(__file__).resolve().parents[1];raw=(O/'viewer/house-context.glb').read_bytes();magic,v,length=struct.unpack_from('<4sII',raw);assert(magic,v,length)==(b'glTF',2,len(raw));n,kind=struct.unpack_from('<I4s',raw,12);assert kind==b'JSON';j=json.loads(raw[20:20+n]);bn,bkind=struct.unpack_from('<I4s',raw,20+n);assert bkind==b'BIN\0';binary=raw[28+n:28+n+bn];checks={'singleLocalExportScene':len(j['scenes'])==1,'sevenHouseContextNodes':len(j['scenes'][0]['nodes'])==7,'bufferViewsInsideBuffer':all(x.get('byteOffset',0)+x['byteLength']<=len(binary)for x in j['bufferViews']),'trianglesOnly':all(p.get('mode',4)==4 for me in j['meshes']for p in me['primitives']),'positionsNormalsUVsPresent':all(all(k in p['attributes']for k in ['POSITION','NORMAL','TEXCOORD_0'])for me in j['meshes']for p in me['primitives'])}
attrs=[]
for me in j['meshes']:
 for p in me['primitives']:
  for key in ['NORMAL','TANGENT']:
   if key not in p['attributes']:continue
   a=j['accessors'][p['attributes'][key]];bv=j['bufferViews'][a['bufferView']];count=3 if key=='NORMAL'else 4;offset=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',count*4);vals=[struct.unpack_from('<'+'f'*count,binary,offset+i*stride)for i in range(a['count'])];attrs.append({'kind':key,'finite':all(math.isfinite(v)for x in vals for v in x),'unit':all(abs(sum(v*v for v in x[:3])-1)<.002 for x in vals)})
checks['finiteUnitNormalTangentAttributes']=all(r['finite']and r['unit']for r in attrs);result={'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'normalTangentAccessors':len(attrs),'bytes':len(raw),'note':'Structural and attribute validation of the local review GLB; master paint UV/tangent validation is separate.'};(O/'evidence/gltf.json').write_text(json.dumps(result,indent=2));print(result);assert result['status']=='PASS'
