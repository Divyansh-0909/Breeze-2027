import os,subprocess,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';tasks=[('validate_architecture.py',None),('validate_shutters.py',None),('validate_layout.py',None),('validate_sightlines.py',None),('measure_floor.py',None)]+[(name,v)for v in ['PHOTO A','PHOTO B']for name in ['validate_bodies_and_shops.py','validate_wall_placements.py']];rows=[]
for name,v in tasks:
 label=name.removesuffix('.py')+('-'+v.replace(' ','-')if v else'');log=O/'evidence'/('test-'+label+'.log');start=time.monotonic()
 with log.open('w')as f:r=subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2',**({'REV10_TEST_VARIANT':v}if v else{})),stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':label,'exitCode':r.returncode,'seconds':time.monotonic()-start,'log':str(log.relative_to(O))});(O/'evidence/test-summary.json').write_text(json.dumps(rows,indent=2));print(label,r.returncode,flush=True)
print('VALIDATION_COMPLETE',all(r['exitCode']==0 for r in rows),flush=True)
