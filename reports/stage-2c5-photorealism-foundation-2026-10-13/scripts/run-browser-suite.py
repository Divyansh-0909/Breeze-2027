"""Serial browser verification avoids competing software-renderer workloads."""
from pathlib import Path
import subprocess,json,os,time
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13'
summary=OUT/'raw/browser-suite-summary.json'
rows=json.loads(summary.read_text())if summary.exists()else[]
jobs=['candidate-regressions.mjs','directional-travel.mjs','lifecycle.mjs','video-cycles.mjs','navigation-cycles.mjs','recovery-foundation.mjs','walkthrough.mjs','near-wall-recording.mjs']
for name in jobs:
    if any(row['script']==name and row['exitCode']==0 for row in rows):continue
    env=os.environ.copy();env['GULLYVERSE_ARTIFACT_DIR']=str(OUT/'raw/regressions')
    start=time.time()
    with (OUT/'raw'/name.replace('.mjs','.log')).open('w')as f:
        result=subprocess.run(['node',str(OUT/'scripts'/name)],stdout=f,stderr=subprocess.STDOUT,env=env)
    rows.append({'script':name,'exitCode':result.returncode,'durationSeconds':time.time()-start})
    (OUT/'raw/browser-suite-summary.json').write_text(json.dumps(rows,indent=2))
    print(name,result.returncode,round(time.time()-start,2),flush=True)
