from pathlib import Path
import os,time,subprocess,json
raw=Path('reports/stage-1-final-2026-10-11/raw');results=[]
while Path('/proc/11010/stat').exists() and Path('/proc/11010/stat').read_text().split()[2]!='Z':time.sleep(3)
jobs=[('gap-browser',['node','reports/stage-1-final-2026-10-11/scripts/gap-browser.mjs'],{}),('project-perf',['npm','run','perf:immersive'],{'CHROME_PATH':'/usr/bin/chromium','GULLYVERSE_BASE_URL':'http://127.0.0.1:3000','GULLYVERSE_MODE':'production','GULLYVERSE_PROFILES':'desktop','GULLYVERSE_ARTIFACT_DIR':'reports/stage-1-final-2026-10-11/raw/project-performance'})]
for name,cmd,extra in jobs:
 env=os.environ.copy();env.update(extra);start=time.time()
 with (raw/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'environmentOverrides':extra,'exitCode':code,'elapsedSeconds':time.time()-start})
 (raw/'post-commands.json').write_text(json.dumps(results,indent=2));print(name,code,flush=True)
