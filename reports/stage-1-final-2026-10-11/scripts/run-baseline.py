from pathlib import Path
import subprocess,os,time,json
root=Path.cwd();raw=root/'reports/stage-1-final-2026-10-11/raw';results=[]
while True:
 try:
  data=json.loads((root/'reports/stage-1-final-2026-10-11/baseline/captures.json').read_text())
  if len(data['captures'])>=23:break
  if data['errors']:raise RuntimeError(data['errors'])
 except FileNotFoundError:pass
 time.sleep(1)
for name,args,extra in [('baseline-performance',['node','reports/stage-1-final-2026-10-11/scripts/performance.mjs'],{'PERF_LABEL':'baseline'}),('baseline-defects',['node','reports/stage-1-final-2026-10-11/scripts/baseline-defects.mjs'],{}),('baseline-media',['node','reports/stage-1-final-2026-10-11/scripts/edges-and-media.mjs'],{'AUDIT_MEDIA_ONLY':'1'})]:
 env=os.environ.copy();env.update(extra);started=time.time()
 with (raw/(name+'.log')).open('w') as log:code=subprocess.call(args,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':args,'exitCode':code,'elapsed':time.time()-started});(raw/'baseline-command-results.json').write_text(json.dumps(results,indent=2));print(name,code,flush=True)
 if name=='baseline-media' and (raw/'media-cycles.json').exists():(raw/'media-cycles.json').rename(raw/'baseline-media-cycles.json')
