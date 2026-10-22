"""Apply an extracted, hash-verified overlay after a complete conflict preflight.
Never reset/checkout Git. Existing independent user edits are never overwritten.
"""
from pathlib import Path
import argparse,json,hashlib,tempfile,shutil,os
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--manifest',default='recovery-stage3a/stage3a-file-manifest.json');a=p.parse_args();base=Path(a.base).resolve();overlay=Path.cwd();manifest=json.loads((overlay/a.manifest).read_text())
def sha(f):return hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
def target(rel):
 r=Path(rel)
 if r.is_absolute()or'..'in r.parts:raise SystemExit('Unsafe path')
 t=base/r
 if not t.resolve().is_relative_to(base):raise SystemExit('Path escapes target')
 for q in [t,*t.parents]:
  if q==base:break
  if q.is_symlink():raise SystemExit('Refusing symlink target')
 return t
for row in manifest.get('requiredBaselineFiles',[]):
 t=target(row['path'])
 if not t.is_file()or sha(t)!=row['sha256']:raise SystemExit('Protected baseline dependency mismatch: '+row['path'])
plan=[];unchanged=0
for row in manifest['files']:
 src=overlay/'project'/row['path'];assert src.is_file()and src.stat().st_size==row['bytes']and sha(src)==row['sha256'],row['path'];t=target(row['path']);current=sha(t)if t.is_file()else None
 if current==row['sha256']:unchanged+=1;continue
 if t.exists()and(current!=row.get('beforeSHA256')or not t.is_file()):raise SystemExit('Refusing to overwrite unrelated user changes: '+row['path'])
 if current is None and row.get('beforeSHA256')is not None:raise SystemExit('Missing required previous source: '+row['path'])
 plan.append((src,t,row))
# All conflicts and source hashes are checked before the first write.
for src,t,row in plan:
 t.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(dir=t.parent,prefix='.stage3a-restore-',delete=False)as f:
  tmp=Path(f.name)
  with src.open('rb')as input:shutil.copyfileobj(input,f)
 shutil.copystat(src,tmp);tmp.replace(t);assert sha(t)==row['sha256']
for row in manifest['files']:assert sha(target(row['path']))==row['sha256']
print(json.dumps({'status':'PASS','restored':len(plan),'alreadyIdentical':unchanged,'filesVerified':len(manifest['files']),'unrelatedFilesUntouched':True}))
