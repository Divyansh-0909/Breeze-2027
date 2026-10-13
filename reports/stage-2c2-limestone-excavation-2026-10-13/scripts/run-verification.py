"""Serial browser workloads; perf windows never compete with another test."""
import subprocess,os,json,time
from pathlib import Path
r=Path('reports/stage-2c2-limestone-excavation-2026-10-13');s=r/'scripts';rows=[]
commands=[
 ('macro-captures',['node',str(s/'capture.mjs'),'macro']),
 ('default-regressions',['npm','run','test:immersive:browser']),
 ('preview-regressions',['node',str(s/'candidate-regressions.mjs')]),
 ('ten-toggle-cycles',['node',str(s/'lifecycle.mjs')]),
 ('recovery-fallback',['node',str(s/'recovery.mjs')]),
 ('directional-travel',['node',str(s/'directional-travel.mjs')]),
 ('ten-navigation-cycles',['node',str(s/'navigation-cycles.mjs')]),
 ('ten-video-cycles',['node',str(s/'video-cycles.mjs')]),
 ('actual-walkthrough',['node',str(s/'walkthrough.mjs')]),
 ('before-performance',['node',str(s/'measure.mjs'),'before']),
 ('after-performance',['node',str(s/'measure.mjs'),'after']),
 ('cold-network',['node',str(s/'network.mjs')]),
]
for name,args in commands:
 print('START',name,flush=True);start=time.time()
 env={**os.environ,'GULLYVERSE_ARTIFACT_DIR':str(r/'raw'/name)}
 with(r/'raw'/(name+'.log')).open('w')as log:
  try:code=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1300).returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-start})
 (r/'raw/browser-commands.json').write_text(json.dumps(rows,indent=2))
 print('END',name,code,flush=True)
