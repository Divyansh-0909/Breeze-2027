import subprocess,os,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend';tasks=['validate_preservation.py','validate_storeys.py','validate_layout.py','validate_shutters.py','validate_wall_placements.py','validate_bodies_and_shops.py','validate_sightlines.py','measure_floor_attribution.py','survey_peripheral_setbacks.py','budget.py'];rows=[]
for name in tasks:
 start=time.monotonic()
 with (O/'evidence'/('test-'+name+'.log')).open('w')as f:r=subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':name,'exitCode':r.returncode,'seconds':time.monotonic()-start});(O/'evidence/tests.json').write_text(json.dumps(rows,indent=2));print('TEST',name,r.returncode,flush=True)
 if r.returncode:break
print('CHECKS_COMPLETE',len(rows)==len(tasks)and all(r['exitCode']==0 for r in rows),flush=True)
