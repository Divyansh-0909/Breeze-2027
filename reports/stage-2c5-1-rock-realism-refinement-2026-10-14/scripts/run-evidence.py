"""Serial software-renderer captures/profile windows; no concurrent browsers."""
from pathlib import Path
import subprocess,json,os,time
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-1-rock-realism-refinement-2026-10-14'
jobs=[('capture-supplement.mjs',['after']),('capture-detail.mjs',['after']),('capture-baseline.mjs',['after']),
      ('lighting-diagnostics.mjs',['after']),
      ('measure.mjs',['before']),('measure.mjs',['after']),('network-loading.mjs',[]),('capture-stage-lighting.mjs',[])]
file=OUT/'raw/evidence-run-summary.json';rows=json.loads(file.read_text())if file.exists()else[]
env=os.environ.copy();env['GULLYVERSE_ARTIFACT_ROOT']=str(OUT)
for name,args in jobs:
    key='-'.join([name.removesuffix('.mjs')]+args)
    if any(r['job']==key and r['exitCode']==0 for r in rows):continue
    started=time.time()
    with (OUT/'raw'/f'{key}.log').open('w')as log:
        p=subprocess.run(['node',str(OUT/'scripts'/name)]+args,env=env,stdout=log,stderr=subprocess.STDOUT)
    row={'job':key,'command':['node',str(OUT/'scripts'/name)]+args,'exitCode':p.returncode,'seconds':time.time()-started}
    rows.append(row);file.write_text(json.dumps(rows,indent=2));print(key,p.returncode,round(row['seconds'],1),flush=True)
    if p.returncode:raise SystemExit(p.returncode)
