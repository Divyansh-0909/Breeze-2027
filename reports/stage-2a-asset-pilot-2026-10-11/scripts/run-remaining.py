import subprocess,json,time
from pathlib import Path
r=Path('reports/stage-2a-asset-pilot-2026-10-11');results=[]
for name in ['resources','interruption','production-smoke']:
 cmd=['node',str(r/'scripts'/f'{name}.mjs')];at=time.time()
 with open(r/'raw'/f'{name}.log','w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 results.append({'command':cmd,'exitCode':p.returncode,'elapsedSeconds':time.time()-at,'log':f'raw/{name}.log'});(r/'raw/remaining-commands.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,flush=True)
