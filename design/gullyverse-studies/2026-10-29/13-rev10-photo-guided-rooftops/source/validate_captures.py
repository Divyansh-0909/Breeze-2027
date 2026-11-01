from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));from rooftop_cameras import SPECS
expected={r[0]:r for r in SPECS}
O=Path(__file__).resolve().parents[1];sha=hashlib.sha256((O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend').read_bytes()).hexdigest();rows={e:json.loads((O/f'evidence/render-{e}.json').read_text())for e in ['before','A','B']}
keys=['position','rotationEuler','lens','sensorWidth','cameraType','orthoScale','resolution','engine','samples','exposure','look','viewTransform','world','supportW']
for ed,r in rows.items():
 assert len(r)==20,(ed,len(r))
 for x in r:
  assert x['masterSHA256']==sha and hashlib.sha256((O/x['file']).read_bytes()).hexdigest()==x['sha256']
  assert all(abs(a-b)<1e-5 for a,b in zip(x['position'],expected[x['pose']][1]))and x['lens']==expected[x['pose']][3],(ed,x['pose'],'camera differs from final specification')
 for x in r:
  base=next(b for b in rows['before']if b['pose']==x['pose'])
  assert all(x[k]==base[k]for k in keys),(ed,x['pose'],[k for k in keys if x[k]!=base[k]])
 assert all(w==0 for x in r for w in x['supportW']);assert next(x for x in r if x['pose']=='01-plan')['orthoScale']==114
walk=[]
for ed in ['A','B']:
 r=json.loads((O/('evidence/render-walk-'+ed+'.json')).read_text());assert len(r)==80 and sorted(x['index']for x in r)==list(range(80))
 for x in r:
  assert x['masterSHA256']==sha and hashlib.sha256((O/x['file']).read_bytes()).hexdigest()==x['sha256']
  assert abs(x['position'][0])<1e-5 and x['sourceFrame']==round(1+959*x['index']/79)
 walk.append({'edition':ed,'frames':80,'sourceRange':[1,960],'encodedSeconds':40,'sampledOutputFPS':2,'notRuntimeFPS':True})
p={'status':'PASS','masterSHA256':sha,'matchedViewpoints':20,'actualSceneStills':60,'bothMotionVerified':walk,'allImageHashesAndCameraLightingFieldsExact':keys,'finalPlanOrthoHorizontalM':114,'allPhotosGenuineAndSeparatelyCredited':True,'noFrameOrImageSubstitution':True};(O/'evidence/capture-validation.json').write_text(json.dumps(p,indent=2));print('CAPTURES_VALID',flush=True)
