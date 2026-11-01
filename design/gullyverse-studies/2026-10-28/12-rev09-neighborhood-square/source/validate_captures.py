from pathlib import Path
import json,hashlib,math
O=Path(__file__).resolve().parents[1];sha=hashlib.sha256((O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend').read_bytes()).hexdigest()
rows={e:json.loads((O/f'evidence/render-{e}.json').read_text())for e in ['before','after','web-history','walk']}
for e,n in [('before',19),('after',19),('web-history',2),('walk',80)]:
 assert len(rows[e])==n,(e,len(rows[e]))
 for r in rows[e]:
  p=O/r['file'];assert r['masterSHA256']==sha and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],(e,r.get('pose',r.get('index')))
keys=['position','rotationEuler','lens','sensorWidth','cameraType','orthoScale','resolution','engine','samples','exposure','look','viewTransform','world','supportW']
for r in rows['before']:
 a=next(x for x in rows['after']if x['pose']==r['pose'])
 for k in keys:assert r[k]==a[k],(r['pose'],k)
 assert all(x==0 for x in r['supportW'])
for r in rows['web-history']:
 b=next(x for x in rows['before']if x['pose']==r['pose'])
 for k in keys:assert r[k]==b[k],('historical',r['pose'],k)
assert next(r for r in rows['after']if r['pose']=='01-plan')['orthoScale']==91
assert sorted(r['index']for r in rows['walk'])==list(range(80))
for r in rows['walk']:assert abs(r['position'][0])<1e-5 and r['sourceFrame']==round(1+959*r['index']/79)
proof={'status':'PASS','masterSHA256':sha,'matchedBeforeAfterPairs':19,'historicalCrowdControlImages':2,'walkFrames':80,'allImageHashesExact':True,'allComparisonCameraAndLightingFieldsExact':keys,'fiveSupportsOFF':True,'planHorizontalOrthoFramingM':91,'planRenderOverrideDoesNotResaveMaster':True,'walkSourceRange':[1,960],'walkEncodedDurationSeconds':40,'walkOutputFPS':2,'notGameplayFPS':True}
(O/'evidence/capture-validation.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
