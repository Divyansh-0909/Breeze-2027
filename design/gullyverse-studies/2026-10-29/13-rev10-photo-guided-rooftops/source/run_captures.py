import os,subprocess,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend'
poses=['01-plan','02-entry-square','03-aerial','04-front','05-back','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','10-team','11-events','12-elevation','13-return-left','14-return-right','15-mobile','16-mobile-lateral','20-roof-utility','21-roof-gallery','22-street-entry','23-screen-side']
for ed in ['before','A','B']:
 with (O/'evidence'/('capture-'+ed+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source/render_studies.py'),'--',ed]+poses,env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
(O/'checkpoint/CAPTURES-DONE.json').write_text(json.dumps({'status':'PASS','actualOfflineBlender':True,'editions':['before','A','B'],'poses':poses}));print('CAPTURES_COMPLETE',flush=True)
