from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1]
jobs=[('export',[],'export'),('render',[],'captures'),('build',['--restore','--base','/dev/shm/Gullyverse-Rev15V1-Events-Coloured-Plaster.blend','--output','/dev/shm/Gullyverse-Rev15V2-Restore-Test.blend'],'restore-check'),('fresh-open',['--restored'],'restored-fresh-open')]
assert json.loads((R/'evidence/fresh-open.json').read_text())['status']=='PASS'
for name,args,key in jobs:
 print('START',name,args,flush=True);p=R/f'evidence/{key}.json'
 if p.exists():p.unlink()
 with (R/f'evidence/check-{key}.log').open('w') as log:subprocess.run(['blender','-b','--python',str(R/'source'/f'{name}.py'),'--',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
 assert p.exists() and json.loads(p.read_text())['status']=='PASS',key;print('PASS',key,flush=True)
 if key=='restored-fresh-open':Path('/dev/shm/Gullyverse-Rev15V2-Restore-Test.blend').unlink()
print('ALL_NATIVE_CHECKS_PASS',flush=True)
