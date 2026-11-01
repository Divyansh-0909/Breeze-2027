import subprocess,os,time,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend';watch=Path('/proc/6918/cmdline')
while watch.exists():
 try:
  if str(O/'source/render_square.py')not in watch.read_bytes().decode():break
 except FileNotFoundError:break
 time.sleep(5)
env=dict(os.environ,LP_NUM_THREADS='2')
for script,args,name in [('render_square.py',['--','before'],'before-final'),('render_square.py',['--','web-history','04-front','03-aerial'],'history-final'),('render_walk.py',[],'walk-final')]:
 with(O/'evidence'/('capture-'+name+'.log')).open('w')as h:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source'/script)]+args,env=env,stdout=h,stderr=subprocess.STDOUT,check=True)
(O/'checkpoint/CAPTURES-DONE.json').write_text(json.dumps({'status':'PASS','serialCaptureAfterCloudMemoryLimit':True}));print('FINAL_SERIAL_CAPTURES_COMPLETE',flush=True)
