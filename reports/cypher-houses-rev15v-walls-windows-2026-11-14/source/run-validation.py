from pathlib import Path
import subprocess,json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);a=ap.parse_args();jobs=[('fresh-open',[]),('build',['--restore','--base','/dev/shm/Gullyverse-Rev15U3-Restore-Test.blend','--output','/dev/shm/Gullyverse-Rev15V-Restore-Test.blend']),('fresh-open',['--restored']),('render',[]),('render',['--before']),('render-neutral',[])]
for i,(name,args) in enumerate(jobs):
 if i<a.start:continue
 key={0:'fresh-open',1:'restore-check',2:'restored-fresh-open',3:'lighting-verification',4:'before-lighting',5:'neutral-captures'}[i];p=R/f'evidence/{key}.json'
 if p.exists():p.unlink()
 print('START',name,args,flush=True)
 with (R/f'evidence/validation-{i}-{name}.log').open('w') as log:subprocess.run(['blender','-b','--python',str(R/'source'/f'{name}.py'),'--',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
 assert p.exists() and json.loads(p.read_text())['status']=='PASS',key
 if i in [0,2]:
  p=json.loads(p.read_text());want=json.loads((R/f'evidence/{"restore-check" if i==2 else "build-verification"}.json').read_text());assert p['sourceSHA256']==want['restoredSHA256' if i==2 else 'editedSHA256']
 print('PASS',name,args,flush=True)
print('ALL_NATIVE_CHECKS_AND_CAPTURES_PASS',flush=True)
