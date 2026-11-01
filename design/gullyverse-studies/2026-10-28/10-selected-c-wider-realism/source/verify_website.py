from pathlib import Path
import json,hashlib,subprocess
O=Path(__file__).resolve().parents[1];b=json.loads((O/'source/prior-pilot/baseline/website-baseline.json').read_text());repo=Path('/workspace/Breeze-2027-wip-push')
errors=[]
for row in b['files']:
 f=repo/row['file']
 if not f.is_file()or hashlib.sha256(f.read_bytes()).hexdigest()!=row['sha256']:errors.append(row['file'])
assert not errors,errors
start=json.loads((O/'evidence/Breeze-2027-wip-push-start.json').read_text())
current=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=repo,text=True)
assert current==start['status']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==start['head']
nav=json.loads((O/'evidence/Breeze-2027-navigation-start.json').read_text())
assert subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=nav['repo'],text=True)==nav['status']
proof={'status':'PASS','protectedFiles':len(b['files']),'allSHA256Unchanged':True,'branch':start['branch'],'HEAD':start['head'],'exactStartingFullGitDirtyStateUnchanged':True,'otherNavigationCheckoutGitStateUnchanged':True,'legacyStatusDisplayNote':'Old Phase 8 status collapsed untracked directories; compare Phase 9 start/end with identical --untracked-files=all options.'}
(O/'evidence/website-preservation.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)
