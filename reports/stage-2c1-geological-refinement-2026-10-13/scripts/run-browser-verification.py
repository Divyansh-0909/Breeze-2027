import subprocess,os,json,time
from pathlib import Path
r=Path('reports/stage-2c1-geological-refinement-2026-10-13');s=r/'scripts';rows=[]
commands=[('after-captures',['node',str(s/'capture.mjs'),'after']),('before-diagnostic',['node',str(s/'diagnostic.mjs'),'before']),('after-diagnostic',['node',str(s/'diagnostic.mjs'),'after']),('stage-lighting-comparison',['node',str(s/'capture-stage-lighting.mjs')]),('matched-performance',['node',str(s/'measure.mjs'),'after']),('lod-walkthrough',['node',str(s/'lod-walkthrough.mjs')]),('ten-toggle-cycles',['node',str(s/'lifecycle.mjs')]),('default-regressions',['npm','run','test:immersive:browser']),('candidate-regressions',['node',str(s/'candidate-regressions.mjs')]),('recovery-and-fallback',['node',str(s/'recovery.mjs')]),('ten-navigation-cycles',['node',str(s/'navigation-cycles.mjs')]),('ten-video-cycles',['node',str(s/'video-cycles.mjs')]),('cold-network',['node',str(s/'network.mjs')])]
for name,args in commands:
 print('START',name,flush=True);at=time.time();env={**os.environ,'GULLYVERSE_ARTIFACT_DIR':str(r/'raw'/name)}
 with(r/'raw'/(name+'.log')).open('w')as f:
  try:code=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1100).returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-at});(r/'raw/browser-commands.json').write_text(json.dumps(rows,indent=2));print('END',name,code,flush=True)
