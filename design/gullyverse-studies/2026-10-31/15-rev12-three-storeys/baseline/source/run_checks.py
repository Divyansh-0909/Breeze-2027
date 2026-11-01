import subprocess,os,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend';tasks=[('validate_preservation.py',None),('validate_shutters.py',None),('validate_layout.py',None),('validate_sightlines.py',None),('measure_floor_attribution.py',None)]+[('validate_bodies_and_shops.py',v)for v in['REV11','REV11 H00','REV11 H06','REV11 H09']]+[('validate_wall_placements.py','REV11')];rows=[]
for name,variant in tasks:
 label=name[:-3]+('-'+variant.replace(' ','-')if variant else'');start=time.monotonic()
 with (O/'evidence'/('test-'+label+'.log')).open('w')as f:r=subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2',**({'REV11_TEST_VARIANT':variant}if variant else{})),stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':label,'exitCode':r.returncode,'seconds':time.monotonic()-start});(O/'evidence/tests.json').write_text(json.dumps(rows,indent=2));print('TEST',label,r.returncode,flush=True)
print('CHECKS_COMPLETE',all(r['exitCode']==0 for r in rows),flush=True)
