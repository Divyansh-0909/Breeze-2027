from pathlib import Path
import os,json,subprocess,time
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20';rows=[]
jobs=[('typecheck',['npx','tsc','--noEmit']),('lint',['npm','run','lint']),('immersive-unit',['npm','run','test:immersive']),('production-build',['npm','run','build'])]
env=os.environ.copy();env.update(NEXT_PUBLIC_SUPABASE_URL='https://recovery-verification.invalid',NEXT_PUBLIC_SUPABASE_ANON_KEY='public-recovery-verification-placeholder',NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW='1',NEXT_PUBLIC_GULLYVERSE_INSPECTION='1')
for name,cmd in jobs:
 start=time.monotonic()
 with (R/'raw'/('final-'+name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'name':name,'command':cmd,'exitCode':p.returncode,'seconds':round(time.monotonic()-start,3)});print(rows[-1],flush=True)
 (R/'raw/source-validation-summary.json').write_text(json.dumps({'status':'FAIL'if any(x['exitCode']for x in rows)else'PASS','jobs':rows,'backendLimitation':'Invalid non-secret Supabase placeholders for local build; backend/payment/service integration not certified.'},indent=2)+'\n')
 if p.returncode:raise SystemExit(p.returncode)
