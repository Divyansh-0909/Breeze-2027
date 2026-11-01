from pathlib import Path
import subprocess,json,time
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Selected-C-Wider-Realism.blend';rows=[]
for name in ['audit_world.py','validate_details.py','validate_shutters.py','validate_wall_placements.py','validate_bodies_and_shops.py','validate_layout.py','audit_budget.py']:
 start=time.monotonic()
 with(O/'evidence'/('run-'+name+'.log')).open('w')as h:r=subprocess.run(['blender','-b',str(master),'-t','4','--python-exit-code','9','--python',str(O/'source'/name)],stdout=h,stderr=subprocess.STDOUT)
 rows.append({'script':name,'exitCode':r.returncode,'seconds':time.monotonic()-start});(O/'evidence/validation-runs.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
 if r.returncode:raise SystemExit(9)
subprocess.run(['python',str(O/'source/verify_website.py')],check=True)
(O/'checkpoint/VALIDATION-DONE.json').write_text(json.dumps({'status':'PASS','runs':rows},indent=2)+'\n')
