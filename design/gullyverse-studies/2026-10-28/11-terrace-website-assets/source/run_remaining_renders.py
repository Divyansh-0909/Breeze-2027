import os,time,subprocess
from pathlib import Path
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend'
# Wait for this task's two initial still batches; no website process is inspected/stopped.
for pid in [3904,4001]:
 while Path(f'/proc/{pid}').exists():time.sleep(5)
env=dict(os.environ,LP_NUM_THREADS='2');poses=['01-approach','02-screen-wide','03-crowd-eye','04-left-diagonal','05-right-diagonal','06-reverse','07-team','08-events','09-perimeter','10-roof-elevated','11-top-plan','12-cross-section','13-rear-terrace','14-return-art','15-mobile-approach','16-mobile-crowd']
for edition,wanted in [('crowd',poses),('props-a',['17-furniture-A','13-rear-terrace']),('props-b',['18-furniture-B','13-rear-terrace'])]:
 with(O/'evidence'/('capture-'+edition+'.log')).open('w')as h:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source/render_terrace.py'),'--',edition]+wanted,env=env,stdout=h,stderr=subprocess.STDOUT,check=True)
print('REMAINING_RENDERS_DONE',flush=True)
