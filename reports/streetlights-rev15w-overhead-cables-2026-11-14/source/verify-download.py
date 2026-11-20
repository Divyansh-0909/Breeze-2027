from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];row=json.loads(sys.argv[1]);dest=R/'restore/downloads'/row['file'];dest.parent.mkdir(parents=True,exist_ok=True)
if len(sys.argv)>2:
 src=Path(sys.argv[2])
 if src.resolve()!=dest.resolve():
  assert not dest.exists();shutil.move(str(src),str(dest))
assert dest.stat().st_size==row['bytes'] and hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256'];(R/'evidence/restore-downloads').mkdir(exist_ok=True);row['status']='PASS';(R/'evidence/restore-downloads'/(row['kind']+'-'+row['file']+'.json')).write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'kind':row['kind'],'file':row['file'],'status':'PASS'}))
