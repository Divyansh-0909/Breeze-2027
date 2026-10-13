import subprocess,os,time,json
from pathlib import Path
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');rows=[]
commands=[('after-captures',['node',str(r/'scripts/after-evidence.mjs')]),('extra-captures',['node',str(r/'scripts/extra-evidence.mjs')]),('after-performance',['node',str(r/'scripts/measure.mjs'),'after']),('ten-preview-cycles',['node',str(r/'scripts/lifecycle.mjs')]),('default-browser',['npm','run','test:immersive:browser']),('opt-in-browser',['node',str(r/'scripts/opt-in-regressions.mjs')]),('touch-opt-in',['node',str(r/'scripts/touch-optin.mjs')]),('video-with-wall',['node',str(r/'scripts/video-with-wall.mjs')]),('walkthrough',['node',str(r/'scripts/walkthrough.mjs')]),('critical-fallback',['node',str(r/'scripts/production-smoke.mjs')]),('loading-interruption',['node',str(r/'scripts/interruption.mjs')])]
for name,args in commands:
 start=time.time()
 with (r/'raw'/f'{name}.log').open('w') as f:
  try:code=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'GULLYVERSE_ARTIFACT_DIR':str(r/'raw/default-regressions')},timeout=720).returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-start});(r/'raw/browser-command-results.json').write_text(json.dumps(rows,indent=2));print(name,code,flush=True)
