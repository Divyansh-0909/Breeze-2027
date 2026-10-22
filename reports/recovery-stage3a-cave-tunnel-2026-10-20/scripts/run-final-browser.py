from pathlib import Path
import os,subprocess,json,time
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20';jobs=[('direct-stage-gate','direct-stage-cave-gate.mjs'),('review-captures','capture-review.mjs'),('cave-diagnostics','capture-cave-diagnostics.mjs'),('private-regressions','candidate-regressions-cave.mjs'),('directional-travel','directional-travel-cave.mjs'),('ownership-recovery','cave-ownership-recovery.mjs'),('preview-persistence','preview-persistence.mjs'),('walkthroughs','record-cave-walkthroughs.mjs'),('matched-performance','profile-cave-comparison.mjs')];rows=[]
for name,script in jobs:
 out=R/'raw'/name;out.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update(CHROME_PATH='/usr/bin/chromium',GULLYVERSE_ARTIFACT_ROOT=str(R),GULLYVERSE_ARTIFACT_DIR=str(out))
 if name=='review-captures':env['GULLYVERSE_REVIEW_RESUME']='1'
 t=time.monotonic()
 with (R/'raw'/('final-browser-'+name+'.log')).open('w')as log:p=subprocess.run(['node',str(R/'scripts'/script)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 row={'name':name,'script':script,'exitCode':p.returncode,'seconds':round(time.monotonic()-t,3),'build':(ROOT/'.next/BUILD_ID').read_text().strip()};rows.append(row);print(json.dumps(row),flush=True);(R/'raw/final-browser-suite.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(1 if any(r['exitCode']for r in rows)else 0)
