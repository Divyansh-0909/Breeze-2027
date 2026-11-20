from pathlib import Path
import json,sys,hashlib,datetime,fcntl
R=Path(__file__).resolve().parents[1]
r=json.loads(sys.argv[1]);p=Path(sys.argv[2])
assert p.stat().st_size==r['bytes']
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
r.update(status='PASS',verifiedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
f=R/'evidence/upload-receipts.json';f.parent.mkdir(exist_ok=True)
with (R/'evidence/upload-receipts.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 rows=json.loads(f.read_text()) if f.exists() else [];rows.append(r)
 f.write_text(json.dumps(rows,indent=2)+'\n')
assert p.resolve()!=Path(r['path']).resolve()
p.unlink()
print(json.dumps({'name':r['name'],'id':r['id'],'status':'PASS'}))
