import subprocess,time,json
from pathlib import Path
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');rows=[]
commands=[('final-after-captures',['node',str(r/'scripts/after-evidence.mjs')]),('final-extra-captures',['node',str(r/'scripts/extra-evidence.mjs')]),('final-after-performance',['node',str(r/'scripts/measure.mjs'),'after']),('final-ten-preview-cycles',['node',str(r/'scripts/lifecycle.mjs')]),('final-public-walkthrough',['node',str(r/'scripts/walkthrough.mjs')]),('final-side-inspection',['node',str(r/'scripts/inspection-walkthrough.mjs')])]
for name,args in commands:
 start=time.time()
 with (r/'raw'/(name+'.log')).open('w')as f:
  try:code=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=420).returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'name':name,'command':args,'exitCode':code,'seconds':time.time()-start});(r/'raw/final-candidate-browser-commands.json').write_text(json.dumps(rows,indent=2));print(name,code,flush=True)
 assert code==0
subprocess.run(['python',str(r/'scripts/build-gallery.py')],check=True)
subprocess.run(['python',str(r/'scripts/build-report.py')],check=True)
