"""Apply this diagnostic overlay to an independently restored Stage3A parent.
All conflicts are checked before writes. Existing unrelated files are retained.
"""
from pathlib import Path
import argparse,json,hashlib,os,tempfile,shutil
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--overlay',type=Path,default=Path(__file__).resolve().parent);args=ap.parse_args()
root=args.base.resolve();overlay=args.overlay.resolve();meta=json.loads((overlay/'pilot-file-manifest.json').read_text())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def safe(rel):
 p=Path(rel)
 if p.is_absolute()or'..'in p.parts:raise ValueError('Unsafe checkpoint path')
 return p
pending=[];conflicts=[]
for row in meta['files']:
 rel=safe(row['path']);source=overlay/'project'/rel;target=root/rel
 if not source.is_file()or sha(source)!=row['sha256']:raise SystemExit('Missing or changed overlay: '+str(rel))
 actual=sha(target)if target.is_file()else None
 if actual==row['sha256']:continue
 if actual!=row['beforeSHA256']:conflicts.append(str(rel))
 else:pending.append((source,target))
for row in meta['protectedParentFiles']:
 target=root/safe(row['path'])
 if not target.is_file()or sha(target)!=row['sha256']:conflicts.append(row['path'])
if conflicts:raise SystemExit('Refusing conflicts before any write: '+str(conflicts))
for source,target in pending:
 target.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix='.pilot-restore-',dir=target.parent);os.close(fd)
 try:shutil.copyfile(source,name);os.replace(name,target)
 finally:
  if Path(name).exists():Path(name).unlink()
print(json.dumps({'status':'PASS','applied':len(pending),'idempotent':not pending,'unrelatedFilesPreserved':True}))
