from pathlib import Path
import json,hashlib,subprocess,tarfile,difflib
root=Path.cwd();r=root/'reports/stage-2c1-geological-refinement-2026-10-13';original=json.loads((r/'raw/baseline-hashes.json').read_text());changes=[];missing=[]
for name,entry in original.items():
 p=root/name
 if not p.exists():missing.append(name);continue
 now=hashlib.sha256(p.read_bytes()).hexdigest()
 if now!=entry['sha256']:changes.append({'path':name,'before':entry['sha256'],'after':now})
expected={'components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx','components/immersive/wallSection.ts'}
assert not missing and {c['path']for c in changes}==expected,(missing,changes)
state={'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'status':subprocess.check_output(['git','status','--short'],text=True)}
assert state['HEAD']==json.loads((r/'raw/starting-state.json').read_text())['HEAD']
(r/'raw/preservation.json').write_text(json.dumps({'protectedFiles':len(original),'byteIdenticalFiles':len(original)-len(changes),'changedExistingFiles':changes,'missing':missing,'state':state,'materialAndStageAssetsPreserved':True},indent=2))
patch=[]
with tarfile.open(r/'backup/current-stage-2c-baseline.tar.gz')as tar:
 for name in sorted(expected):
  before=tar.extractfile(name).read().decode();after=(root/name).read_text();patch.extend(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='starting-worktree/'+name,tofile='current/'+name))
(r/'raw/source-changes.patch').write_text(''.join(patch))
# Match every primary screenshot by actual camera/viewport/quality, not label.
a=json.loads((r/'raw/before-captures.json').read_text());b=json.loads((r/'raw/after-captures.json').read_text());pairs=[]
for before in a['captures']:
 name=Path(before['file']).name;after=next(x for x in b['captures']if Path(x['file']).name==name)
 fields=['camera','viewport'];checks={k:before['data'][k]==after['data'][k]for k in fields};checks['dpr']=before['data']['stats']['dpr']==after['data']['stats']['dpr'];checks['quality']=before['data']['snapshot']['quality']==after['data']['snapshot']['quality'];assert all(checks.values()),(name,checks)
 pairs.append({'file':name,'checks':checks,'before':before['file'],'after':after['file']})
stage=json.loads((r/'raw/stage-lighting-comparison.json').read_text());left,right=stage;checks={k:left['details'][k]==right['details'][k]for k in ['camera','viewport']};checks['dpr']=left['details']['stats']['dpr']==right['details']['stats']['dpr'];checks['quality']=left['details']['snapshot']['quality']==right['details']['snapshot']['quality'];assert all(checks.values());pairs.append({'file':'desktop-11-stage-lighting.png','checks':checks,'before':left['file'],'after':right['file']})
(r/'raw/capture-pair-validation.json').write_text(json.dumps({'status':'PASS','pairs':pairs,'method':'Exact metadata equality, original browser PNG resolutions retained; visual differences are authorized rock geometry/UV changes, not a pixel-identical claim.'},indent=2))
print('Preserved',len(original)-len(changes),'files; changed',len(changes),'matched pairs',len(pairs))
