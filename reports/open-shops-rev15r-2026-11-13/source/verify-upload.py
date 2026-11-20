from pathlib import Path
import json,hashlib,sys,datetime
r=json.loads(sys.argv[1]);p=Path(sys.argv[2]);assert p.stat().st_size==r['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];r.update(status='PASS',verifiedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());R=Path(__file__).resolve().parents[1];f=R/'evidence/upload-receipts.json';rows=json.loads(f.read_text()) if f.exists() else [];rows.append(r);f.write_text(json.dumps(rows,indent=2)+'\n');assert p.resolve()!=Path(r['path']).resolve();p.unlink();print(json.dumps({'id':r['id'],'name':r['name'],'status':'PASS'}))
if (R/'evidence/PAUSE-UPLOAD').exists():raise SystemExit('Upload batch paused after verified file boundary for the final visual correction.')
