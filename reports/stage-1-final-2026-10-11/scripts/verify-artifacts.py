from pathlib import Path
import re,json,hashlib,subprocess
from html.parser import HTMLParser
root=Path.cwd();out=root/'reports/stage-1-final-2026-10-11';references=[];missing=[]
docs=[root/'docs/gullyverse-current-user-approved-baseline.md',root/'docs/gullyverse-stage-1-final-acceptance.md',out/'PHYSICAL-DEVICE-PROCEDURE.md',out/'README.md']
for p in docs:
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):references.append((p,target))
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src']:references.append((out/'gallery.html',v))
Links().feed((out/'gallery.html').read_text())
for p,target in references:
 if target.startswith(('http:','https:','#','app:','mailto:')):continue
 target=target.split('#')[0].strip('<>')
 if not (p.parent/target).resolve().exists():missing.append({'file':str(p.relative_to(root)),'target':target})
assert not missing,missing
preserved=json.loads((out/'raw/locked-preservation.json').read_text());assert preserved['allChecksPass']
before=json.loads((out/'baseline/captures.json').read_text());after=json.loads((out/'acceptance/captures.json').read_text());assert len(before['captures'])==len(after['captures'])==23;assert not before['errors'] and not after['errors']
for p in [out/'baseline',out/'acceptance']:
 for c in json.loads((p/'captures.json').read_text())['captures']:assert (p/c['file']).exists()
current={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'status':subprocess.check_output(['git','status','--short'],text=True),'stagedStat':subprocess.check_output(['git','diff','--cached','--stat'],text=True)}
assert current['head']=='8919589d47385efd674ca91b52376f1ad310b797';assert current['stagedStat']==''
check={'localReferencesChecked':len(references),'missing':missing,'baselineAndAcceptanceCaptures':23,'lockedPreservation':True,'git':current}
(out/'raw/artifact-validation.json').write_text(json.dumps(check,indent=2))
manifest=[]
for p in sorted(out.rglob('*')):
 if not p.is_file() or p.name in ['manifest.json','artifact-validation.json','artifact-validation.log'] or p.suffix=='.pyc' or p.name.startswith('server'):continue
 data=p.read_bytes();manifest.append({'path':str(p.relative_to(out)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
for p in docs[:2]:manifest.append({'path':str(p.relative_to(out,walk_up=True)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps({'files':manifest,'mutableServerLogsExcluded':True,'validationOutputExcluded':True,'scope':'Current Stage1 evidence only; historical audit retained unchanged'},indent=2))
print(len(references),'resolved references;',len(manifest),'manifest files; starting HEAD and empty index preserved.')
