from pathlib import Path
import subprocess,time,json,sys
R=Path(__file__).resolve().parents[1];repo=R.parents[1]
steps=[('paint-projection',['blender','-b','-t','6','--python',str(R/'source/paint-projection.py')]),('paint-fix',[sys.executable,str(R/'source/fix-paint.py')]),('textures',['node',str(R/'source/optimize-full.mjs')]),('lightfield',['blender','-b','-t','6','--python',str(R/'source/bake-lightfield.py')]),('ground',['blender','-b','-t','6','--python',str(R/'source/bake-ground.py')]),('roughness',['blender','-b','-t','6','--python',str(R/'source/bake-roughness.py')]),('compile',[sys.executable,str(R/'source/compile.py')]),('mural-lightmap',['blender','-b','-t','2','--python',str(R/'source/bake-mural-lightmap.py')])]
rows=[]
for name,cmd in steps:
 print('START',name,flush=True);t=time.monotonic()
 with (R/f'evidence/{name}.log').open('w') as f:result=subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'step':name,'exit':result.returncode,'seconds':round(time.monotonic()-t,2)})
 (R/'evidence/rebuild-steps.json').write_text(json.dumps(rows,indent=2)+'\n')
 if result.returncode:raise SystemExit('FAILED '+name)
 print('DONE',name,rows[-1]['seconds'],flush=True)
