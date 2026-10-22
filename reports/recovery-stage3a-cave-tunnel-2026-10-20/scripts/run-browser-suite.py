from pathlib import Path
import argparse,json,os,subprocess,time
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20';p=argparse.ArgumentParser();p.add_argument('jobs',nargs='*');a=p.parse_args()
jobs={'private-regressions':R/'scripts/candidate-regressions-cave.mjs','directional-travel':R/'scripts/directional-travel-cave.mjs','ownership-recovery':R/'scripts/cave-ownership-recovery.mjs','preview-persistence':R/'scripts/preview-persistence.mjs','review-captures':R/'scripts/capture-review.mjs','cave-diagnostics':R/'scripts/capture-cave-diagnostics.mjs'}
rows=[]
for name in a.jobs or jobs:
 out=R/'raw'/name;out.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env.update(CHROME_PATH='/usr/bin/chromium',GULLYVERSE_ARTIFACT_ROOT=str(R),GULLYVERSE_ARTIFACT_DIR=str(out));at=time.monotonic()
 with (R/'raw'/('browser-'+name+'.log')).open('w')as log:r=subprocess.run(['node',str(jobs[name])],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 row={'name':name,'script':str(jobs[name].relative_to(ROOT)),'exitCode':r.returncode,'seconds':round(time.monotonic()-at,3),'build':(ROOT/'.next/BUILD_ID').read_text().strip()};rows.append(row)
 (R/'raw/browser-suite-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
raise SystemExit(1 if any(r['exitCode']for r in rows)else 0)
