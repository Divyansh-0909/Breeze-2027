from pathlib import Path
import json,subprocess,sys,os,time,hashlib,shutil,datetime
O=Path(__file__).resolve().parents[1];env=os.environ.copy();env.update(LP_NUM_THREADS='2',OMP_NUM_THREADS='2')
def state(stage,**kw):
 d={'stage':stage,'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw};(O/'checkpoint/progress.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d),flush=True)
def wait_finished(path,marker):
 end=time.monotonic()+7200
 while True:
  t=path.read_text()
  if 'Traceback'in t or'Error: script failed'in t:raise RuntimeError(str(path))
  if marker in t and'Blender quit'in t:return
  if time.monotonic()>end:raise RuntimeError('Capture deadline exceeded')
  time.sleep(3)
state('VERIFY_FINAL_PREVIEW_AND_WAIT_BASELINE_C')
wait_finished(O/'evidence/render-preview-v2.log','ART_CAPTURES_COMPLETE preview C 6')
sha=hashlib.sha256((O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend').read_bytes()).hexdigest();preview=json.loads((O/'evidence/render-preview-C.json').read_text());dest=[]
for r in preview:
 assert r['masterSHA256']==sha
 src=O/r['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['sha256']
 target=O/'renders/after/C'/(r['camera']+'.png');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
 dest.append({**r,'edition':'after','file':str(target.relative_to(O)),'provenance':'Exact final-candidate preview promoted after master/PNG hash checks'})
(O/'evidence/render-after-C.json').write_text(json.dumps(dest,indent=2)+'\n')
wait_finished(O/'evidence/render-before-C.log','ART_CAPTURES_COMPLETE before C 27')
tasks=[('after','C'),('before','A'),('after','A'),('before','B'),('after','B'),('profile-before','C'),('profile-after','C')]
for ed,v in tasks:
 state('RENDER_'+ed.upper()+'_'+v)
 master=O/('source/baseline/Rev05C-Support-Off.blend'if ed in ['before','profile-before']else'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend')
 with(O/f'evidence/render-{ed}-{v}.log').open('w')as h:
  subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','1','--python',str(O/'source/render_art.py'),'--',ed,v],env=env,stdout=h,stderr=subprocess.STDOUT,check=True)
state('ALL_FINAL_CAPTURES_COMPLETE')
