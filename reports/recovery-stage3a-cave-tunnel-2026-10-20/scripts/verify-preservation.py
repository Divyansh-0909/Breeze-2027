from pathlib import Path
import json,hashlib,subprocess
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw'
j=json.loads((R/'starting-state.json').read_text());unchanged=[];changed=[];missing=[]
for row in j['files']:
 p=ROOT/row['path']
 if not p.is_file():missing.append(row);continue
 actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if actual==row['sha256']:unchanged.append(row['path'])
 else:changed.append({'path':row['path'],'before':row['sha256'],'after':actual})
allowed={'components/immersive/ImmersiveShell.tsx','components/immersive/HubScene.tsx','components/immersive/AftermovieScene.tsx'}
assert not missing,missing;assert set(r['path']for r in changed)==allowed,changed
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert branch==j['branch']and head==j['HEAD']
result={'status':'PASS','baselineFiles':len(j['files']),'unchangedCount':len(unchanged),'authorizedIntegrationChanges':changed,'missing':missing,'branch':branch,'HEAD':head,'C9C8C51AllSourceAssetsAndMapsUntouched':True,'worldRegistryStageLightingNavigationUntouched':True}
(R/'preservation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
