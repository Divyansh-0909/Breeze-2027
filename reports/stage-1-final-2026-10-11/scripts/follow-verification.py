import os,time,json,subprocess
from pathlib import Path
r=Path('reports/stage-1-final-2026-10-11/raw'); env=os.environ.copy(); results=[]
# Await the owned serial verification process, never overlap GPU browsers.
while True:
 try:os.kill(9087,0)
 except ProcessLookupError:break
 time.sleep(5)
jobs=[('edges-and-media','edges-and-media.mjs',{'AUDIT_EDGES_ONLY':'1'}),('interruption','interruption.mjs',{}),('journey','journey.mjs',{}),('loading-check','loading-check.mjs',{})]
for name,script,overrides in jobs:
 e=env.copy();e.update(overrides);start=time.time()
 cmd=['node','reports/stage-1-final-2026-10-11/scripts/'+script]
 with (r/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=e,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'environmentOverrides':overrides,'exitCode':code,'elapsedSeconds':time.time()-start})
 (r/'follow-commands.json').write_text(json.dumps(results,indent=2));print(name,code,flush=True)
