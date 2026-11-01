from pathlib import Path
import subprocess,time,sys,json
O=Path(__file__).resolve().parents[1]
deadline=time.monotonic()+1800
while True:
 log=(O/'evidence/render-lighting.log').read_text()
 if 'Traceback'in log or'Error: script failed'in log:raise RuntimeError('Actual capture job failed; inspect render log.')
 if 'ALL_LIGHTING_COMPARISONS_COMPLETE 60'in log and 'Blender quit'in log:break
 if time.monotonic()>deadline:raise RuntimeError('Capture timeout')
 time.sleep(3)
for script in ['build_review.py','build_report.py','package_checkpoint.py']:
 print('RUN',script,flush=True)
 subprocess.run([sys.executable,str(O/'source'/script)],check=True,cwd=O)
print('LOCAL_PARTIAL_CHECKPOINT_READY',flush=True)
