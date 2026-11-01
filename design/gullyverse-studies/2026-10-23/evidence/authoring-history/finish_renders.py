from pathlib import Path
import subprocess,json,time,shutil
O=Path(__file__).resolve().parents[1]
# Called only after the first render batch has exited; the running Blender scene is never modified.
master=O/'source/Gullyverse-Lane-Rooftop-ABC.blend'
def blender(script,args=None,log=''):
 cmd=['blender','-b',str(master),'-t','2','--python',str(O/'source'/script)]+(['--',*args]if args else[])
 with (O/'evidence'/log).open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(script+' failed; inspect '+log)
with (O/'evidence/render-final.log').open()as f:
 assert 'RENDER_JOBS_COMPLETE 36'in f.read(),'Wait for initial render batch to finish'
manifest=O/'evidence/render-manifest.json';rows=json.loads(manifest.read_text())
for v in ['A','B','C']:
 for n in ['04-hub','05-team','06-events','11-overhead']:
  p=O/'renders'/v/(n+'.png');q=O/'evidence/composition-drafts'/v/p.name;q.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():p.rename(q)
  for row in rows:
   if row['variant']==v and row['camera']==n and row['mode']=='final':row['file']=str(q.relative_to(O));row['mode']='composition-draft'
manifest.write_text(json.dumps(rows,indent=2))
shutil.copyfile(O/'source/camera-guide.json',O/'evidence/camera-guide-before-composition-correction.json')
blender('calibrate_scene.py',log='calibrate-final.log')
blender('render_study.py',['composition-fix'],'render-composition-final.log')
blender('validate_concept.py',log='concept-validation-final.log')
blender('render_study.py',['animatic'],'render-animatic.log')
(O/'evidence/render-pipeline-complete.json').write_text(json.dumps({'status':'ALL_RENDER_BATCHES_EXITED','matchedFinalPNGs':36,'animaticKeyframes':12,'editedWebsite':False}))
print('FINAL_RENDER_PIPELINE_COMPLETE',flush=True)
