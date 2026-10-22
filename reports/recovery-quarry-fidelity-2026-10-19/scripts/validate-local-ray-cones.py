"""Denser follow-up around the actual failed trial sightlines; same .03 gate."""
from pathlib import Path
import json,math
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19'
# Run the complete survey first, so these checks use the identical actual GLBs,
# unchanged occluders and baseline BVHs, rather than hand-built approximations.
exec(compile((R/'scripts/validate-geometry.py').read_text(),'validate-geometry.py','exec'))
targets={}
for path in (R/'trials').rglob('*.json'):
 try:data=json.loads(path.read_text())
 except Exception:continue
 if not isinstance(data,dict):continue
 for row in data.get('newInvertedHits',[]):
  if all(k in row for k in ['eye','pitch','yaw']):targets[(tuple(row['eye']),row['pitch'],row['yaw'])]=row
targets[((0,1.72,-96),15,249)]={}
fail=[];count=0
for (eye,pitch,yaw)in targets:
 for dp in [-1,-.5,0,.5,1]:
  for dy in [-1,-.5,0,.5,1]:
   a,b=math.radians(pitch+dp),math.radians(yaw+dy);d=B([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)])
   for level in range(3):
    old=facing_cast(baseline[level],eye,d);hit=facing_cast(new[level],eye,d);count+=1
    if hit['mesh']and hit['mesh'].startswith('Fidelity_')and hit['normalDotRay']>.03:fail.append({'eye':eye,'pitch':pitch+dp,'yaw':yaw+dy,'LOD':level,'baseline':old,'candidate':hit})
result={'status':'PASS'if not fail else'FAIL','targetedFailedSightlines':len(targets),'additionalRaysPerVersion':count,'sameNormalDotGate':.03,'newInvertedHits':fail,'scope':'Denser cones around recorded trial failures; sample-based, not exhaustive geometry proof.'}
(R/'raw/targeted-ray-cones.json').write_text(json.dumps(result,indent=2)+'\n');print('TARGETED_RAY_CONES',result['status'],len(targets),count,len(fail));assert not fail
