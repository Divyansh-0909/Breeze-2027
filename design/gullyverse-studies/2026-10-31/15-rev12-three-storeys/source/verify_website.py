import json,hashlib,subprocess
from pathlib import Path
O=Path(__file__).resolve().parents[1];b=json.loads((O/'evidence/website-baseline.json').read_text());repo=Path('/workspace/Breeze-2027-wip-push');bad=[]
for r in b['files']:
 p=repo/r['file']
 if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:bad.append(r['file'])
assert not bad,bad
states=[]
for name in ['Breeze-2027-wip-push','Breeze-2027-navigation']:
 old=json.loads((O/'evidence'/(name+'-start.json')).read_text());p=Path(old['repo']);now=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=p,text=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=p,text=True).strip();assert now==old['status']and head==old['head']and branch==old['branch'];states.append({'repo':str(p),'branch':branch,'head':head,'exactDirtyAndUntrackedStateUnchanged':True})
(O/'evidence/website-preservation.json').write_text(json.dumps({'status':'PASS','protectedSHA256Files':len(b['files']),'allSourceHashesExact':True,'repositories':states,'noWebsiteBuildInstallServerOrGitMutation':True},indent=2));print('WEBSITE_PRESERVATION_PASS',len(b['files']))
