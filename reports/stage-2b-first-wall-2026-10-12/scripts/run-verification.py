import subprocess,json,time,os
from pathlib import Path
root=Path('reports/stage-2b-first-wall-2026-10-12');rows=[]
commands=[('matched-performance-lifecycle',['node',str(root/'scripts/benchmark-and-lifecycle.mjs')]),('browser-walkthrough',['node',str(root/'scripts/walkthrough.mjs')]),('default-runtime-browser',['npm','run','test:immersive:browser']),('opt-in-runtime-regressions',['node',str(root/'scripts/opt-in-regressions.mjs')]),('default-smoke-failure',['node',str(root/'scripts/production-smoke.mjs')]),('loading-playback-interruption',['node',str(root/'scripts/interruption.mjs')])]
for name,args in commands:
 start=time.time();env={**os.environ,'GULLYVERSE_ARTIFACT_DIR':str(root/'raw/default-regressions')}
 with (root/'raw'/f'{name}.log').open('w') as f:
  try:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=720);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-start});(root/'raw/verification-commands.json').write_text(json.dumps(rows,indent=2));print(name,code,flush=True)
