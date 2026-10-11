from pathlib import Path
import subprocess,os,time,json
raw=Path('reports/stage-1-final-2026-10-11/raw');results=[];env=os.environ.copy();env.update(NEXT_PUBLIC_SUPABASE_URL='http://127.0.0.1:9',NEXT_PUBLIC_SUPABASE_ANON_KEY='audit-placeholder')
jobs=[('navigation',['node','scripts/check-gullyverse-stage-1-revision-2.mjs'],{'CHROME_PATH':'/usr/bin/chromium','GULLYVERSE_BASE_URL':'http://127.0.0.1:3000','GULLYVERSE_ARTIFACT_DIR':'reports/stage-1-final-2026-10-11/raw/navigation','GULLYVERSE_TEST_DPR':'.25','GULLYVERSE_MOBILE_DPR':'.25','GULLYVERSE_MOVEMENT_TIMEOUT':'60000','GULLYVERSE_EXPECT_CATALOG_UNAVAILABLE':'1'}),('captures',['node','reports/stage-1-final-2026-10-11/scripts/captures.mjs'],{'CAPTURE_MODE':'acceptance'}),('blender-browser',['node','reports/stage-1-final-2026-10-11/scripts/blender-browser.mjs'],{}),('performance',['node','reports/stage-1-final-2026-10-11/scripts/performance.mjs'],{'PERF_LABEL':'after'}),('native-profile',['node','reports/stage-1-final-2026-10-11/scripts/native-profile.mjs'],{})]
more=[('edges-and-media','edges-and-media.mjs',{'AUDIT_EDGES_ONLY':'1'}),('interruption','interruption.mjs',{}),('journey','journey.mjs',{}),('loading-check','loading-check.mjs',{})]
jobs += [(name,['node','reports/stage-1-final-2026-10-11/scripts/'+script],overrides) for name,script,overrides in more]
for name,cmd,extra in jobs:
 e=env.copy();e.update(extra);t=time.time()
 try:
  with (raw/(name+'.log')).open('w') as log:code=subprocess.call(cmd,env=e,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 except subprocess.TimeoutExpired:code=124
 results.append({'name':name,'command':cmd,'environmentOverrides':extra,'exitCode':code,'elapsedSeconds':time.time()-t});(raw/'remaining-commands.json').write_text(json.dumps(results,indent=2));print(name,'exit',code,flush=True)
