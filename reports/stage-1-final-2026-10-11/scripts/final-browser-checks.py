from pathlib import Path
import subprocess,json,time,os
raw=Path('reports/stage-1-final-2026-10-11/raw');results=[]
while Path('/proc/11463/stat').exists() and Path('/proc/11463/stat').read_text().split()[2]!='Z':time.sleep(2)
jobs=[('gap-browser-final',['node','reports/stage-1-final-2026-10-11/scripts/gap-browser.mjs'],{}),('camera-final',['npm','run','test:immersive:browser'],{'GULLYVERSE_CAMERA_ONLY':'1','GULLYVERSE_ARTIFACT_DIR':'reports/stage-1-final-2026-10-11/raw/camera-final'}),('additional-captures',['node','reports/stage-1-final-2026-10-11/scripts/additional-captures.mjs'],{})]
for name,cmd,extra in jobs:
 env=os.environ.copy();env.update(extra);start=time.time()
 with (raw/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'environmentOverrides':extra,'exitCode':code,'elapsedSeconds':time.time()-start});(raw/'final-browser-commands.json').write_text(json.dumps(results,indent=2));print(name,code,flush=True)
