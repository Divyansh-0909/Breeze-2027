import os,subprocess
from pathlib import Path
O=Path(__file__).resolve().parents[1]
with(O/'evidence/capture-web-history.log').open('w')as f:subprocess.run(['blender','-b',str(O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend'),'-t','2','--python-exit-code','9','--python',str(O/'source/render_square.py'),'--','web-history','04-front','03-aerial'],stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,LP_NUM_THREADS='2'),check=True)
