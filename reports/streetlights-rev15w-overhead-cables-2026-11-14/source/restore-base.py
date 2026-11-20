from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];restore=R/'restore';repo=restore/'repo';downloads=restore/'downloads';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();manifest=json.loads((R/'source/restore-manifest.json').read_text());receipt=[]
for row in manifest:
 p=downloads/row['file'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
def extract(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  for row in json.loads(z.read('PAYLOAD-SHA256.json')):
   b=z.read(row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
  z.extractall(repo)
vrows=[r for r in manifest if r['kind']=='V'];vp=restore/'V-source.zip'
with vp.open('wb') as out:
 for row in sorted(vrows,key=lambda r:r['index']):out.write((downloads/row['file']).read_bytes())
assert sha(vp)=='2f4e5faca53c559068a711e4c86407f68b59ea34dd7068eaf9d71307a7db5a64';extract(vp);v=repo/'reports/cypher-houses-rev15v-walls-windows-2026-11-14';extract(v/'dependencies/Breeze-Rev15U3-Larger-English-Navigation-Checkpoint.zip');extract(downloads/next(r['file'] for r in manifest if r['kind']=='V1'));extract(downloads/next(r['file'] for r in manifest if r['kind']=='V2'))
masters=restore/'masters';masters.mkdir(exist_ok=True);index=repo/'reports/cypher-entry-rev15v2-open-steel-gate-2026-11-14/delivery/Base-Rev15T2-Native-Parts.json';T2=masters/'T2.blend'
if not T2.exists():
 with T2.open('wb') as out:
  for row in sorted([r for r in manifest if r['kind']=='T2'],key=lambda r:r['index']):out.write((downloads/row['file']).read_bytes())
assert T2.stat().st_size==214265912 and sha(T2)=='33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb';print('VERIFIED exact original complete T2 master',flush=True)
jobs=[
 ('T3','ground-rev15t3-rebuilt-potholes-2026-11-13','restore-native.py','T2',['--delta',str(downloads/'Rev15T3-Rebuilt-Potholes-Additions.blend')],'restore'),
 ('U1','navigation-board-rev15u-highway-green-2026-11-13','restore-native.py','T3',['--delta',str(downloads/'Rev15U1-Bilingual-Highway-Sign-Styling.blend')],'restore'),
 ('U2','navigation-board-rev15u2-english-centred-2026-11-14','build.py','U1',['--restore'],'restore-check'),
 ('U3','navigation-board-rev15u3-larger-english-text-2026-11-14','build.py','U2',['--restore'],'restore-check'),
 ('V','cypher-houses-rev15v-walls-windows-2026-11-14','build.py','U3',['--restore'],'restore-check'),
 ('V1','events-wall-rev15v1-coloured-plaster-2026-11-14','build.py','V',['--restore'],'restore-check'),
 ('V2','cypher-entry-rev15v2-open-steel-gate-2026-11-14','build.py','V1',['--restore'],'restore-check')]
for key,report,script,base,extra,proof in jobs:
 out=masters/(key+'.blend');work=repo/'reports'/report;print('RESTORE',key,flush=True)
 if not out.exists():
  with (R/'evidence'/('restore-'+key+'.log')).open('w') as log:subprocess.run(['blender','-b','--python-exit-code','1','--python',str(work/'source'/script),'--','--base',str(masters/(base+'.blend')),'--output',str(out),*extra],stdout=log,stderr=subprocess.STDOUT,check=True)
 assert out.exists(),key
 record={'stage':key,'file':str(out),'bytes':out.stat().st_size,'sha256':sha(out)};receipt.append(record);(R/'evidence/base-restoration-progress.json').write_text(json.dumps(receipt,indent=2)+'\n');print('RESTORED',key,out.stat().st_size,flush=True)
result={'status':'PASS','method':'Original complete T2 master byte hash verified; authenticated native deltas and source checkpoints applied in order with each builder fingerprint guard.','originalCompleteBaseSHA256':sha(T2),'originalV2WholeFileSHA256':'5fd74f84cd1c8d58ce99584045926288d0375eba95e6e1f9f0a5ea20714876bc','serializationNote':'The restored full V2 file can have a different serialization checksum; the exact active-scene content fingerprint is checked by the V2 restore builder.','stages':receipt,'restoredMaster':str(masters/'V2.blend'),'restoredSHA256':sha(masters/'V2.blend'),'expectedV2SceneFingerprint':'1b882cca849915c98c7df36fec1f38365b9166c325d541ee8fbaaaec749b4629'};(R/'evidence/base-restoration.json').write_text(json.dumps(result,indent=2)+'\n');print('V2_SOURCE_RESTORATION_PASS',flush=True)
