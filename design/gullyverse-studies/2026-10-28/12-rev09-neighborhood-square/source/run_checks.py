import subprocess,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend';rows=[]
for name in ['audit_preservation','validate_houses','validate_layout','validate_shutters','validate_wall_placements','validate_bodies_and_shops','validate_sightlines']:
 t=time.monotonic()
 with(O/'evidence'/('test-'+name+'.log')).open('w')as f:r=subprocess.run(['blender','-b',str(m),'-t','3','--python-exit-code','9','--python',str(O/'source'/(name+'.py'))],stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':name,'exitCode':r.returncode,'seconds':time.monotonic()-t});(O/'evidence/test-summary.json').write_text(json.dumps(rows,indent=2));print(name,r.returncode,flush=True)
