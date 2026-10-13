from pathlib import Path
import subprocess,json,time,os
r=Path('reports/stage-2c-quarry-rollout-2026-10-12');commands=[('after-captures',['node',str(r/'scripts/capture.mjs'),'after']),('after-performance',['node',str(r/'scripts/measure.mjs'),'after']),('ten-toggle-cycles',['node',str(r/'scripts/lifecycle.mjs')]),('default-browser',['npm','run','test:immersive:browser']),('ten-navigation-cycles',['node',str(r/'scripts/navigation-cycles.mjs')]),('ten-video-cycles',['node',str(r/'scripts/video-cycles.mjs')]),('recovery-failure',['node',str(r/'scripts/recovery.mjs')])];rows=[]
for name,args in commands:
 at=time.time()
 with(r/'raw'/(name+'.log')).open('w')as f:
  try:code=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'GULLYVERSE_ARTIFACT_DIR':str(r/'raw/default-regressions')},timeout=900).returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-at});(r/'raw/verification-commands.json').write_text(json.dumps(rows,indent=2));print(name,code,flush=True)
