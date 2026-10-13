from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
root=Path.cwd();r=root/'reports/stage-2b-first-wall-2026-10-12'
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
old=json.loads((root/'reports/stage-2a-asset-pilot-2026-10-11/raw/source-hashes-before.json').read_text());paths=set(old)
for folder in ['assets-source','scripts/blender']:
 for p in (root/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.blend1':paths.add(str(p.relative_to(root)))
for p in (root/'public/models/gullyverse').rglob('*'):
 if p.is_file():paths.add(str(p.relative_to(root)))
for n in ['docs/gullyverse-stage-2a-asset-pilot.md','docs/gullyverse-current-final-review.md','docs/gullyverse-current-visual-baseline.md','docs/gullyverse-environment-pipeline.md','design/references/README.md']:paths.add(n)
paths={p for p in paths if not any(x.startswith('.env') or x in ['.vercel','credentials'] for x in Path(p).parts)}
hashes={p:sha(root/p) for p in sorted(paths)}
(r/'raw/source-hashes-before.json').write_text(json.dumps(hashes,indent=2))
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0');uh={p:sha(root/p) for p in untracked if p and (root/p).is_file() and not p.startswith('reports/stage-2b-first-wall-2026-10-12/') and '__pycache__' not in Path(p).parts and not Path(p).name.startswith('.env')}
(r/'raw/pre-existing-untracked-hashes.json').write_text(json.dumps(uh,indent=2))
state={'dateUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'staged':subprocess.check_output(['git','diff','--cached'],text=True),'unstaged':subprocess.check_output(['git','diff'],text=True),'status':subprocess.check_output(['git','status','--short','--untracked-files=normal'],text=True),'sourceFiles':len(hashes),'preExistingUntrackedFiles':len(uh),'secretsExcluded':True,'approvedMaterial':'assets-source/gullyverse/limestone-grey-pilot/textures; actual default Hub quarry still vertex-coloured; grey pilot is approved material reference, not active in default application'}
(r/'raw/starting-state.json').write_text(json.dumps(state,indent=2));print('Starting hashes complete',len(hashes),len(uh),flush=True)
with tarfile.open(r/'backup/current-source-assets.tar.gz','w:gz',compresslevel=2) as t:
 for p in hashes:t.add(root/p,arcname=p,recursive=False)
print('Recoverable snapshot complete',flush=True)
