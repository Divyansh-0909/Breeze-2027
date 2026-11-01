from pathlib import Path
import json,subprocess,sys,time,os
O=Path(__file__).resolve().parents[1]
deadline=time.monotonic()+7200
while True:
 status=json.loads((O/'checkpoint/progress.json').read_text())
 log=(O/'checkpoint/capture-pipeline.log').read_text()
 if 'Traceback'in log:raise RuntimeError('Capture pipeline failed; inspect before proceeding.')
 if status['stage']=='ALL_FINAL_CAPTURES_COMPLETE':break
 if time.monotonic()>deadline:raise RuntimeError('Capture deadline exceeded')
 time.sleep(3)
for script in ['build_art_review.py','build_art_report.py','package_art_checkpoint.py','verify_independent_restore.py']:
 print('RUN',script,flush=True)
 with(O/'checkpoint'/('finish-'+script+'.log')).open('w')as f:subprocess.run([sys.executable,str(O/'source'/script)],cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True)
print('LOCAL_ART_DELIVERY_READY_FOR_DRIVE_VERIFICATION',flush=True)
