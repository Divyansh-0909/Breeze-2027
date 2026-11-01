"""Finish only the already-approved Rev05B evidence package after both capture jobs end."""
from pathlib import Path
import json,time,subprocess,sys,os,datetime
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';progress=C/'local-package-progress.json'
def state(stage,**kwargs):
    row={'stage':stage,'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),**kwargs};progress.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
previous=None;deadline=time.monotonic()+3600
while True:
    counts={ed:len(list((O/'renders'/ed).rglob('*.png')))for ed in ['before','after']}
    logs={ed:(O/f'evidence/render-{ed}-all.log').read_text()for ed in ['before','after']}
    if counts!=previous:state('WAITING_FOR_CAPTURE_JOBS',**counts);previous=counts.copy()
    if any('Traceback'in s or'Error: script failed'in s for s in logs.values()):raise RuntimeError('A capture job failed; inspect its log.')
    if all(counts[e]==75 and'CAPTURES_COMPLETE'in logs[e]and'Blender quit'in logs[e]for e in counts):break
    if time.monotonic()>deadline:raise RuntimeError('Capture wait exceeded one hour; inspect actual running processes.')
    time.sleep(5)
def run(stage,args,env=None):
    state(stage)
    with (C/(stage.lower()+'.log')).open('w')as h:subprocess.run(args,cwd=O,env=env,stdout=h,stderr=subprocess.STDOUT,check=True)
env=os.environ.copy();env.update(LP_NUM_THREADS='2',OMP_NUM_THREADS='2')
run('LIGHTING_ISOLATION',['blender','-b',str(O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend'),'-t','2','--python-exit-code','1','--python',str(O/'source/lighting_isolation.py')],env)
run('BUILD_REVIEW',[sys.executable,str(O/'source/build_review.py')])
run('BUILD_REPORT',[sys.executable,str(O/'source/build_report.py')])
run('PACKAGE_CHECKPOINT',[sys.executable,str(O/'source/package_checkpoint.py')])
state('LOCAL_PACKAGE_READY_FOR_INDEPENDENT_RESTORE_AND_DRIVE_VERIFICATION',noWebsiteChange=True,noCommitPushMergeDeploy=True)
