import subprocess,os,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend';poses=['03-aerial','04-front','01-plan','02-entry-square','05-back','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','10-team','11-events','12-elevation','13-return-left','14-return-right','15-mobile','16-mobile-lateral','20-roof-utility','21-roof-gallery','22-street-entry','23-screen-side','24-right-elevation','25-back-junction','26-left-junction','27-right-junction','28-roof-joins']
with (O/'evidence/capture-new.log').open('w')as f:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source/render.py'),'--','new']+poses,env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
for name in ['render_screen_diagnostic.py','render_diagnostics.py','render_storey_diagnostics.py']:
 with (O/'evidence'/(name+'.log')).open('w')as f:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
print('CAPTURES_COMPLETE',flush=True)
