import os,time,json,subprocess
from pathlib import Path
r=Path('reports/current-final-review-2026-10-11');results=[]
while Path('/proc/25204').exists():time.sleep(3)
for name,cmd in [('navigation-followup',['node',str(r/'scripts/navigation-followup.mjs')]),('supplementary-performance',['node',str(r/'scripts/extra-performance.mjs')]),('blender-browser',['node',str(r/'scripts/blender-browser.mjs')])]:
 print('START',name,flush=True);at=time.time()
 with (r/'raw'/f'{name}.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'exitCode':p.returncode,'elapsedSeconds':time.time()-at});(r/'raw/followup-commands.json').write_text(json.dumps(results,indent=2));print('END',name,p.returncode,flush=True)
