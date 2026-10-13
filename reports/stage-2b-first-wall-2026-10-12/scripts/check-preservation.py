import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd();r=root/'reports/stage-2b-first-wall-2026-10-12'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
allowed={'components/immersive/AftermovieScene.tsx','components/immersive/HubScene.tsx','components/immersive/ImmersiveShell.tsx','components/immersive/rendering.tsx'}
results=[]
for name in ['source-hashes-before','pre-existing-untracked-hashes']:
 before=json.loads((r/'raw'/f'{name}.json').read_text());changed=[];missing=[]
 for file,hash in before.items():
  p=root/file
  if not p.is_file():missing.append(file)
  elif sha(p)!=hash:changed.append(file)
 permitted=allowed if name=='source-hashes-before' else set()
 results.append({'inventory':name,'files':len(before),'unchanged':len(before)-len(changed)-len(missing),'changed':changed,'missing':missing,'status':'PASS' if not missing and set(changed)<=permitted else 'FAIL'})
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip();diff=subprocess.check_output(['git','diff'],text=True);(r/'raw/source-changes.patch').write_text(diff)
status=subprocess.check_output(['git','status','--short'],text=True);(r/'raw/ending-git-status.txt').write_text(status)
output={'branch':branch,'HEAD':head,'stagedDiffEmpty':not subprocess.check_output(['git','diff','--cached'],text=True),'inventories':results,'status':'PASS' if all(x['status']=='PASS' for x in results) and head=='e3dbbc233f1f12f5e4d96333db3b797e75da4760' else 'FAIL'};(r/'raw/preservation-results.json').write_text(json.dumps(output,indent=2));print(json.dumps(output,indent=2));assert output['status']=='PASS'
