"""Validate GLB structure, original art bytes and complete source accounting."""
from pathlib import Path
import json,struct,hashlib,argparse
ap=argparse.ArgumentParser();ap.add_argument('output');ap.add_argument('inventory');ap.add_argument('evidence');ap.add_argument('--ground',action='store_true');a=ap.parse_args();out=Path(a.output);evidence=Path(a.evidence);evidence.mkdir(parents=True,exist_ok=True);m=json.loads((out/'manifest.json').read_text());inventory=json.loads(Path(a.inventory).read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
def glb(path):
 b=path.read_bytes();assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
rows=[]
for name in ['contact-frontage.png.glb','contact-frontage.optimized.glb','contact-frontage.mobile.glb']+([]if a.ground else['contact-frontage.collision.glb']):
 g,b=glb(out/name);triangles=sum(g['accessors'][p['indices']]['count']//3 if 'indices'in p else g['accessors'][p['attributes']['POSITION']]['count']//3 for mesh in g.get('meshes',[])for p in mesh['primitives']);bindings=[]
 if 'collision'not in name:
  assert triangles==m['counts']['triangles']
  for mesh in g['meshes']:
   for p in mesh['primitives']:
    mat=g['materials'][p['material']];channel=mat['extras']['runtimeLightmapChannel'];assert f'TEXCOORD_{channel}'in p['attributes'];bindings.append(channel)
  if name!='contact-frontage.png.glb':
   assert 'EXT_meshopt_compression'in g['extensionsUsed']
   if g.get('images'):assert 'KHR_texture_basisu'in g['extensionsUsed']
 rows.append({'file':name,'bytes':(out/name).stat().st_size,'sha256':sha((out/name).read_bytes()),'triangles':triangles,'meshObjects':len(g.get('meshes',[])),'materialBindings':len(g.get('materials',[])),'textures':len(g.get('textures',[])),'images':len(g.get('images',[])),'extensions':g.get('extensionsUsed',[]),'lightmapUVBindings':bindings})
g,b=glb(out/'contact-frontage.png.glb');embedded=[]
for image in g.get('images',[]):
 v=g['bufferViews'][image['bufferView']];start=v.get('byteOffset',0);embedded.append({'image':image.get('name'),'sha256':sha(b[start:start+v['byteLength']])})
expected={v['name']:v['sha256']for mat in m['materials']for v in mat['sourceImages']};preserved=[{'sourceImage':name,**row}for name,digest in expected.items()for row in embedded if row['sha256']==digest]
if not a.ground:assert any('graffiti'in r['sourceImage'].lower()for r in preserved),'Source heading image must survive byte-exact in baseline'
exported={name for r in m['objects'] for name in [r['sourceObject'],*r.get('batchedSourceObjects',[])]};excluded={r['object']for r in m['intentionalSourceExclusions']};contexts=set(m['bakeOnlyContextObjects']);allNames={r['name']for r in inventory['objects']};missing=allNames-exported-excluded-contexts;assert not missing,sorted(missing);assert len(allNames)==3230
proof={'status':'PASS','sourceSHA256':m['source']['sha256'],'sourceObjects':len(allNames),'accountedObjects':len(allNames& (exported|excluded|contexts)),'exportedSourceObjects':len(exported),'bakeOnlyContextObjects':len(contexts),'explicitExclusions':len(excluded),'partialMeshesMayAlsoSupplyBakeContext':True,'missingObjects':sorted(missing),'baselineSourceImagesPreservedByteExact':preserved,'runtimeFiles':rows,'artAcceptance':'Lighting comparison remains a separate visual gate; structural correctness is not visual approval'};(evidence/'runtime-validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':'PASS','accountedObjects':len(allNames),'byteExactSourceImages':len(preserved),'files':[{k:r[k]for k in ['file','bytes','triangles']}for r in rows]}))
