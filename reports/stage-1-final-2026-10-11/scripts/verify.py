from pathlib import Path
import subprocess,os,time,json,urllib.request
root=Path.cwd();raw=root/'reports/stage-1-final-2026-10-11/raw';results=[];env=os.environ.copy();env.update(NEXT_PUBLIC_SUPABASE_URL='http://127.0.0.1:9',NEXT_PUBLIC_SUPABASE_ANON_KEY='audit-placeholder')
with (raw/'server.log').open('w') as log:server=subprocess.Popen(['node','node_modules/next/dist/bin/next','start','--hostname','0.0.0.0','--port','3000'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(raw/'server-pid.txt').write_text(str(server.pid))
for i in range(60):
 try:urllib.request.urlopen('http://127.0.0.1:3000/',timeout=1).close();break
 except Exception:time.sleep(.5)
else:raise RuntimeError('Server not ready')
jobs=[('browser',['npm','run','test:immersive:browser'],{}),('resources',['node','reports/stage-1-final-2026-10-11/scripts/resources.mjs'],{}),('navigation',['node','scripts/check-gullyverse-stage-1-revision-2.mjs'],{'CHROME_PATH':'/usr/bin/chromium','GULLYVERSE_BASE_URL':'http://127.0.0.1:3000','GULLYVERSE_ARTIFACT_DIR':'reports/stage-1-final-2026-10-11/raw/navigation','GULLYVERSE_TEST_DPR':'.25','GULLYVERSE_MOBILE_DPR':'.25','GULLYVERSE_MOVEMENT_TIMEOUT':'60000','GULLYVERSE_EXPECT_CATALOG_UNAVAILABLE':'1'}),('captures',['node','reports/stage-1-final-2026-10-11/scripts/captures.mjs'],{'CAPTURE_MODE':'acceptance'}),('blender-browser',['node','reports/stage-1-final-2026-10-11/scripts/blender-browser.mjs'],{}),('performance',['node','reports/stage-1-final-2026-10-11/scripts/performance.mjs'],{'PERF_LABEL':'after'}),('native-profile',['node','reports/stage-1-final-2026-10-11/scripts/native-profile.mjs'],{})]
for name,cmd,extra in jobs:
 e=env.copy();e.update(extra);t=time.time()
 with (raw/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=e,stdout=log,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'environmentOverrides':extra,'exitCode':code,'elapsedSeconds':time.time()-t});(raw/'commands.json').write_text(json.dumps(results,indent=2));print(name,'exit',code,flush=True)
