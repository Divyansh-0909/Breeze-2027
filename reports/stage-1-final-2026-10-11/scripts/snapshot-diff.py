from pathlib import Path
import json,hashlib,subprocess,tarfile,difflib,re
root=Path.cwd();out=root/'reports/stage-1-final-2026-10-11/raw';base=json.loads((out/'baseline-hashes.json').read_text());changes=[];same=[];patch=[];preserved={}
for p,h in base.items():
 data=(root/p).read_bytes();new=hashlib.sha256(data).hexdigest()
 if h==new:same.append(p)
 else:changes.append({'path':p,'beforeSha256':h,'afterSha256':new})
with tarfile.open(out/'current-approved-baseline.tar.gz','r:gz') as archive:
 for member in archive:
  if member.name not in {c['path'] for c in changes}:continue
  old=archive.extractfile(member).read();new=Path(member.name).read_bytes()
  if member.name.endswith('LEDScreens.tsx'):
   for name in ['VERT','FRAG']:
    pattern=rf'const {name} = /\* glsl \*/ `(.*?)`;'
    preserved['LED_'+name]=re.search(pattern,old.decode(),re.S).group(1)==re.search(pattern,new.decode(),re.S).group(1)
   for name in ['CENTER_W','CENTER_H','SIDE_W','SIDE_H','GAP']:
    pattern=rf'const {name} = (.*?);'
    preserved['LED_'+name]=re.search(pattern,old.decode()).group(1)==re.search(pattern,new.decode()).group(1)
  patch.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='approved-baseline/'+member.name,tofile='current/'+member.name))
new=[p for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines() if p not in base and not p.startswith('reports/')]
new += [p for p in ['docs/gullyverse-current-user-approved-baseline.md','docs/gullyverse-stage-1-final-acceptance.md'] if Path(p).exists() and p not in base and p not in new]
for p in new:patch.extend(difflib.unified_diff([],Path(p).read_text().splitlines(True),fromfile='/dev/null',tofile='current/'+p))
(out/'source-diff.json').write_text(json.dumps({'changesAgainstApprovedBaseline':changes,'newSourceFiles':new,'unchangedCount':len(same),'unchangedFiles':same,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'status':subprocess.check_output(['git','status','--short'],text=True)},indent=2));(out/'changes-against-approved-baseline.patch').write_text(''.join(patch));print(len(changes),'changed baseline files;',len(same),'unchanged;',len(new),'new source/test files')

assets=[p for p in base if p.startswith(('public/','Assets/'))]
locked=['components/immersive/HubScene.tsx','components/immersive/AftermovieEnvironment.tsx','components/immersive/aerial.ts','components/immersive/blockoutGeometry.ts','public/models/gullyverse/blockout.layout.json','package-lock.json','pnpm-lock.yaml']
for p in locked:
 if p in base:preserved[p]=p in same
preserved['all_public_and_Assets_files']=all(p in same for p in assets)
preserved['historical_report_files']=all(p in same for p in base if p.startswith('reports/verification-2026-10-10/'))
preserved['payment_and_admin_files']=all(p in same for p in base if any(k in p.lower() for k in ['/payments/','/admin/']))
(out/'locked-preservation.json').write_text(json.dumps({'checks':preserved,'assetCount':len(assets),'allChecksPass':all(preserved.values())},indent=2))
