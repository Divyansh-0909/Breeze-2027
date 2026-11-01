import time,subprocess
from pathlib import Path
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Selected-C-Wider-Realism.blend'
while not(O/'checkpoint/VALIDATION-DONE.json').exists():time.sleep(1)
for script,args,log in[('measure_visibility.py',[],'coverage.log'),('render_world.py',['--','after'],'capture-after.log'),('render_walk.py',[],'capture-walk.log')]:
 with(O/'evidence'/log).open('w')as h:subprocess.run(['blender','-b',str(m),'-t','4','--python-exit-code','9','--python',str(O/'source'/script)]+args,stdout=h,stderr=subprocess.STDOUT,check=True)
(O/'checkpoint/CAPTURES-DONE.json').write_text('{"status":"PASS"}\n')
