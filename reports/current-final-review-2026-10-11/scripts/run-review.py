import subprocess,os,time,json
from pathlib import Path
root=Path('reports/current-final-review-2026-10-11'); results=[]
while Path('/proc/24524').exists():time.sleep(3)
commands=[('captures',['node',str(root/'scripts/captures.mjs')],{}),('resources',['node',str(root/'scripts/resources.mjs')],{}),('performance',['node',str(root/'scripts/performance.mjs')],{'PERF_LABEL':'current'}),('visitor',['node',str(root/'scripts/visitor.mjs')],{}),('edges',['node',str(root/'scripts/edges-and-media.mjs')],{'AUDIT_EDGES_ONLY':'1'}),('interruption',['node',str(root/'scripts/interruption.mjs')],{}),('project-performance',['npm','run','perf:immersive'],{'CHROME_PATH':'/usr/bin/chromium','GULLYVERSE_PROFILES':'desktop','GULLYVERSE_MODE':'production','GULLYVERSE_ARTIFACT_DIR':str(root/'raw/project-performance')})]
for name,cmd,env in commands:
 print('START',name,flush=True);at=time.time()
 with (root/'raw'/f'{name}.log').open('w') as f:
  p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,**env})
 results.append({'name':name,'command':cmd,'environment':env,'exitCode':p.returncode,'elapsedSeconds':time.time()-at});(root/'raw/browser-commands.json').write_text(json.dumps(results,indent=2));print('END',name,p.returncode,flush=True)
