from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
jobs=[('fresh-open',[],'fresh-open'),('export',[],'export'),('build',['--restore','--base','/dev/shm/Gullyverse-Rev15V-Restore-Test.blend','--output','/dev/shm/Gullyverse-Rev15V1-Restore-Test.blend'],'restore-check'),('fresh-open',['--restored'],'restored-fresh-open'),('render',[],'captures')]
for name,args,key in jobs:
 print('START',name,args,flush=True);p=R/f'evidence/{key}.json'
 if p.exists():p.unlink()
 with (R/f'evidence/check-{key}.log').open('w') as log:subprocess.run(['blender','-b','--python',str(R/'source'/f'{name}.py'),'--',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
 assert p.exists() and json.loads(p.read_text())['status']=='PASS',key;print('PASS',key,flush=True)
 if key=='restored-fresh-open':Path('/dev/shm/Gullyverse-Rev15V1-Restore-Test.blend').unlink()
