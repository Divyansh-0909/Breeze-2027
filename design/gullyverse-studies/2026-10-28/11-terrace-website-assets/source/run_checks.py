import subprocess,json,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend';rows=[]
for name in ['audit_preservation','validate_terrace','validate_layout','validate_shutters','validate_wall_placements','validate_bodies_and_shops','validate_sightlines']:
 start=time.monotonic()
 with(O/'evidence'/('test-'+name+'.log')).open('w')as f:r=subprocess.run(['blender','-b',str(master),'-t','3','--python-exit-code','9','--python',str(O/'source'/(name+'.py'))],stdout=f,stderr=subprocess.STDOUT)
 rows.append({'test':name,'exitCode':r.returncode,'seconds':time.monotonic()-start});(O/'evidence/test-summary.json').write_text(json.dumps(rows,indent=2));print(name,r.returncode,flush=True)
