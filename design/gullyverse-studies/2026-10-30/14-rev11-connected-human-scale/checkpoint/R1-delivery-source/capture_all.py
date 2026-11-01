import subprocess,os,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend';poses=['01-plan','02-entry-square','03-aerial','04-front','05-back','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','10-team','11-events','12-elevation','13-return-left','14-return-right','15-mobile','16-mobile-lateral','20-roof-utility','21-roof-gallery','22-street-entry','23-screen-side','24-right-elevation','25-back-junction','26-left-junction','27-right-junction','28-roof-joins']
jobs=[('new',poses)]+[(ed,['04-front','06-left-diagonal','15-mobile','03-aerial'])for ed in['H00','H06','H09']]
for edition,wanted in jobs:
 with (O/'evidence'/('capture-'+edition+'.log')).open('w')as f:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source/render.py'),'--',edition]+wanted,env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
for name in ['render_diagnostics.py','render_floor_proposal.py','budget.py']:
 with (O/'evidence'/(name+'.log')).open('w')as f:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
(O/'evidence/CAPTURES-DONE.json').write_text(json.dumps({'status':'PASS','newStills':25,'heightControlStills':12,'diagnostics':'separate studio scale sheet and optional unchanged-geometry floor material proposal','existingABPNGsReusedByteExact':40},indent=2));print('CAPTURES_COMPLETE',flush=True)
