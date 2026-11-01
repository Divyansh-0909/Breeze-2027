from pathlib import Path
import json,hashlib,re,urllib.parse
O=Path(__file__).resolve().parents[1];a=json.load(open(O/'evidence/render-new.json'));fields=[('position','cameraPosition'),('rotationEuler','rotationEuler'),('lens','lens'),('sensorWidth','sensorWidth'),('cameraType','type'),('orthoScale','orthoScale'),('resolution','viewport'),('exposure','exposure'),('world','world'),('samples','samples')];rows=[]
for e in ['A','B']:
 old=json.load(open(O/'evidence'/('render-'+e+'.json')))
 for x in a:
  y=next((r for r in old if r['pose']==x['pose']),None)
  if not y:continue
  assert all(y[k]==x[v]for k,v in fields),(e,x['pose'])
  assert hashlib.sha256((O/y['file']).read_bytes()).hexdigest()==y['sha256'];rows.append([e,x['pose']])
assert len(rows)==40
for e in ['new','H00','H06','H09']:
 rr=json.load(open(O/'evidence'/('render-'+e+'.json')));assert len(rr)==(25 if e=='new' else 4)
 for r in rr:assert r['masterSHA256'].startswith('b149a04a')and hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
links=re.findall(r'(?:src|href)="([^"]+)"',(O/'GALLERY.html').read_text());bad=[x for x in links if not x.startswith(('http:','https:'))and not (O/urllib.parse.unquote(x)).is_file()];assert not bad,bad
out={'status':'PASS','ABMatchedPairs':40,'newStills':25,'heightControlStills':12,'originalABBytesExact':True,'cameraSettingsLightingQualityMatch':True,'galleryLinksChecked':len(links),'missingLocalLinks':0,'sealedMasterSHA256':hashlib.sha256((O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend').read_bytes()).hexdigest()};(O/'evidence/capture-final-validation.json').write_text(json.dumps(out,indent=2));print(out)
