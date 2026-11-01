from pathlib import Path
import json,subprocess,os,time
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';env=dict(os.environ,LP_NUM_THREADS='2')
while not (O/'checkpoint/MOTION-DONE.json').exists():time.sleep(5)
# Matched final plan shows the ENTIRE enlarged roof depth, not just the old floor.
# Render-time camera changes never resave or alter the sealed historical master.
for ed,poses in [('before',['01-plan','20-roof-utility','08-left-house','21-roof-gallery','22-street-entry']),('A',['01-plan','20-roof-utility','08-left-house','21-roof-gallery','22-street-entry']),('B',['01-plan','20-roof-utility','08-left-house','21-roof-gallery','22-street-entry'])]:
 with (O/'evidence'/('final-framing-'+ed+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source/render_studies.py'),'--',ed]+poses,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
for script in ['validate_captures.py','build_report.py','build_reviews.py','package_checkpoint.py']:
 subprocess.run(['python',str(O/'source'/script)],check=True)
print('FINAL_REVIEW_AND_PACKAGES_COMPLETE',flush=True)
