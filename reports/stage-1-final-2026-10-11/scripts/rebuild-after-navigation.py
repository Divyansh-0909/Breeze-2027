from pathlib import Path
import os,time,subprocess,json,urllib.request,signal
raw=Path('reports/stage-1-final-2026-10-11/raw')
while Path('/proc/11011/stat').exists() and Path('/proc/11011/stat').read_text().split()[2]!='Z':time.sleep(2)
os.kill(9088,signal.SIGTERM)
env=os.environ.copy();env.update(NEXT_PUBLIC_SUPABASE_URL='http://127.0.0.1:9',NEXT_PUBLIC_SUPABASE_ANON_KEY='audit-placeholder')
results=[]
for name,cmd in [('build-final',['npm','run','build']),('typecheck-final',['node','node_modules/typescript/bin/tsc','--noEmit'])]:
 with (raw/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'exitCode':code});print(name,code,flush=True)
 if code:raise RuntimeError(name+' failed; verification remains paused')
(raw/'final-build-checks.json').write_text(json.dumps(results,indent=2))
with (raw/'server-final.log').open('w') as log:server=subprocess.Popen(['node','node_modules/next/dist/bin/next','start','--hostname','0.0.0.0','--port','3000'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(raw/'server-pid.txt').write_text(str(server.pid))
for _ in range(60):
 try:urllib.request.urlopen('http://127.0.0.1:3000/',timeout=1).close();break
 except Exception:time.sleep(.5)
else:raise RuntimeError('Final server did not start')
os.kill(11010,signal.SIGCONT)
print('Resumed serial verification on final production build',flush=True)
