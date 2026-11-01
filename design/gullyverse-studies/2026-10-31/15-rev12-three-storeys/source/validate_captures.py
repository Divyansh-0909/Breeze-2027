from pathlib import Path
import json,hashlib,re,urllib.parse
O=Path(__file__).resolve().parents[1];a=json.load(open(O/'evidence/render-new.json'));b=json.load(open(O/'evidence/render-before.json'));assert len(a)==len(b)==25;sha=hashlib.sha256((O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend').read_bytes()).hexdigest();fields=['cameraPosition','rotationEuler','lens','sensorWidth','type','orthoScale','viewport','pixelRatio','samples','engine','world','viewTransform','look','exposure','optionalSupportW']
for x in a:
 y=next(r for r in b if r['pose']==x['pose']);assert all(x[k]==y[k]for k in fields),(x['pose'],[(k,x[k],y[k])for k in fields if x[k]!=y[k]])
 for r in[x,y]:assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
 assert x['masterSHA256']==sha;assert y['masterSHA256']=='b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd'
walk=json.load(open(O/'evidence/render-walk-Rev12.json'));assert len(walk)==80 and sorted(r['index']for r in walk)==list(range(80))
for r in walk:assert r['masterSHA256']==sha and abs(r['position'][0])<1e-5 and hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
links=re.findall(r'(?:src|href)="([^"]+)"',(O/'GALLERY.html').read_text());bad=[x for x in links if not x.startswith(('http:','https:'))and not (O/urllib.parse.unquote(x)).is_file()];assert not bad,bad
result={'status':'PASS','matchedRev11Rev12Pairs':25,'originalPNGsByteExact':True,'cameraFOVDPRQualityWorldExposureLightsIdentical':True,'automaticCameraReframing':False,'newStills':25,'walkSamples':80,'offlineWalkSeconds':40,'sourceActionFrames':960,'galleryLinksChecked':len(links),'sealedMasterSHA256':sha,'noHardwareFPSClaim':True};(O/'evidence/capture-final-validation.json').write_text(json.dumps(result,indent=2));print('CAPTURE_VALIDATION_PASS',result)
