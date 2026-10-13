import subprocess,time,json
from pathlib import Path
r=Path('reports/stage-2c1-geological-refinement-2026-10-13');rows=[]
for name in ['lod-walkthrough','capture-stage-lighting','directional-travel']:
 start=time.time()
 with(r/'raw'/(name+'-final.log')).open('w')as f:code=subprocess.run(['node',str(r/'scripts'/(name+'.mjs'))],stdout=f,stderr=subprocess.STDOUT).returncode
 rows.append({'name':name,'command':['node',str(r/'scripts'/(name+'.mjs'))],'exitCode':code,'seconds':time.time()-start});(r/'raw/extra-browser-commands.json').write_text(json.dumps(rows,indent=2));print(name,code,flush=True)
