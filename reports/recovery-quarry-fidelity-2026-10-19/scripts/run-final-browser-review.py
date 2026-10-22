"""One browser job at a time; performance runs last without competing rendering."""
from pathlib import Path
import os,json,subprocess,time
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19';S=R/'scripts';rows=[]
env=os.environ.copy();env.update(CHROME_PATH='/usr/bin/chromium',GULLYVERSE_ARTIFACT_ROOT=str(R))
jobs=[('browser-suite',['python3',str(S/'run-browser-suite.py')])]
jobs += [('capture-'+k,['node',str(S/'capture-comparisons.mjs'),k])for k in ['c51','c8','recovered','material','corrected']]
jobs += [('diagnostics',['node',str(S/'capture-diagnostics.mjs')]),('walkthroughs',['node',str(S/'record-walkthroughs.mjs')]),('matched-performance',['node',str(S/'profile-comparison.mjs')])]
for name,cmd in jobs:
 start=time.monotonic()
 with (R/'raw'/('final-'+name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'name':name,'exitCode':p.returncode,'seconds':round(time.monotonic()-start,3),'build':(ROOT/'.next/BUILD_ID').read_text().strip()})
 (R/'raw/final-browser-review-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
for stem in ['visitor-journey','automatic-lod-inspection']:
 src=R/'videos'/(stem+'.webm')
 if src.exists():
  p=subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(src),'-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(src.with_suffix('.mp4'))],cwd=ROOT)
  assert p.returncode==0
raise SystemExit(1 if any(r['exitCode']for r in rows)else 0)
