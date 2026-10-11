from pathlib import Path
import subprocess,os,json,time,signal,urllib.request
root=Path('/workspace/Breeze-2027-navigation');out=root/'reports/verification-2026-10-10';results=[]
def run(name,args,log,env=None,cwd=None,timeout=360):
 print('START',name,flush=True);settings=os.environ.copy();settings.update(env or {})
 with (out/log).open('w')as stream:
  p=subprocess.Popen(args,cwd=cwd or root,env=settings,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   code=124
 results.append({'name':name,'args':args,'exitCode':code,'log':log,'cwd':str(cwd or root),'envOverrides':env or {}});(out/'raw/final-checks-results.json').write_text(json.dumps(results,indent=2));print('END',name,code,flush=True);return code
run('playback-restoration-observed-activation',['node','reports/verification-2026-10-10/scripts/playback-restoration.mjs'],'raw/playback-restoration.log',timeout=180)
run('repeated-movie-resources',['node','reports/verification-2026-10-10/scripts/edges-and-media.mjs'],'raw/media-cycles.log',{'AUDIT_MEDIA_ONLY':'1'},timeout=300)
run('native-DPR1-profile',['node','reports/verification-2026-10-10/scripts/native-profile.mjs'],'raw/native-profile.log',timeout=250)
run('existing-revision2-navigation-assertions',['node','reports/verification-2026-10-10/scripts/run-existing.mjs','reports/verification-2026-10-10/scripts/existing-navigation-relocated.mjs'],'raw/existing-navigation.log',{'AUDIT_DPR':'.25','AUDIT_MOBILE_DPR':'.5'},timeout=300)
run('payment-browser-portable',['node','--import','tsx','reports/verification-2026-10-10/scripts/run-existing.mjs','tests/payments/browser.ts'],'raw/payment-browser-portable.log',{'PAYMENT_TEST_ARTIFACT_DIR':'reports/verification-2026-10-10/raw/payment-browser-portable'},timeout=90)
fixture=Path('/tmp/breeze-verification-2026-10-10-reference');env={'NEXT_PUBLIC_SUPABASE_URL':'http://127.0.0.1:9','NEXT_PUBLIC_SUPABASE_ANON_KEY':'audit-placeholder'}
code=run('historical-reference-build',['npm','run','build'],'raw/reference-build.log',env,cwd=fixture,timeout=300)
if code==0:
 with(out/'raw/reference-server.log').open('w')as f:
  settings=os.environ.copy();settings.update(env);server=subprocess.Popen(['node',str(root/'node_modules/next/dist/bin/next'),'start','--hostname','127.0.0.1','--port','3001'],cwd=fixture,env=settings,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   ready=False
   for i in range(40):
    try:
     with urllib.request.urlopen('http://127.0.0.1:3001/aftermovie',timeout=2)as resp:ready=resp.status==200
    except Exception:pass
    if ready:break
    time.sleep(.25)
   (out/'raw/reference-server-readiness.json').write_text(json.dumps({'pid':server.pid,'ready':ready,'temporaryServer':'127.0.0.1:3001','terminatedAfterComparison':True},indent=2))
   if ready:run('matched-reference-comparison',['node','reports/verification-2026-10-10/scripts/reference-compare.mjs'],'raw/reference-comparison.log',timeout=200)
  finally:
   os.killpg(server.pid,signal.SIGTERM)
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(server.pid,signal.SIGKILL);server.wait()
print('SEQUENTIAL_CHECKS_COMPLETE',flush=True)
