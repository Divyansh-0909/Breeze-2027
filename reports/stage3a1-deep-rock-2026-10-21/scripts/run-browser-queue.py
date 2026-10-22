from pathlib import Path
import subprocess,json,time,os,signal,datetime
R=Path('reports/stage3a1-deep-rock-2026-10-21');checks=[]
# All GPU comparisons run sequentially after the matched still session closes.
while True:
 try:os.kill(5068,0)
 except ProcessLookupError:break
 time.sleep(2)
for name,limit in [('direct-stage-cave-gate.mjs',400),('candidate-regressions-cave.mjs',900),('record-cave-walkthroughs.mjs',600),('cave-ownership-recovery.mjs',900),('preview-persistence.mjs',600),('directional-travel-cave.mjs',400),('profile-cave-comparison.mjs',700)]:
 at=time.time();log=R/'raw'/('run-'+name+'.log');env=os.environ.copy();env['GULLYVERSE_ARTIFACT_DIR']=str(R/'raw/regressions');status='DONE'
 with log.open('w')as output:
  p=subprocess.Popen(['node',str(R/'scripts'/name)],stdout=output,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:code=p.wait(timeout=limit)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);p.wait();code=124;status='TIMEOUT'
 checks.append({'script':name,'exitCode':code,'status':status,'seconds':time.time()-at,'log':str(log)});(R/'raw/browser-queue.json').write_text(json.dumps(checks,indent=2)+'\n');print(name,code,flush=True)
