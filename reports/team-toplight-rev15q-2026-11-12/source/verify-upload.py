from pathlib import Path
import json,hashlib,sys,datetime
row=json.loads(sys.argv[1]);p=Path(sys.argv[2]);assert p.stat().st_size==row['bytes'];h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==row['sha256'];row.update(status='PASS',verifiedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Authenticated Drive download-back SHA-256, byte size and parent verified')
R=Path(__file__).resolve().parents[1];proof=R/'checkpoint/upload-receipts.json';rows=json.loads(proof.read_text()) if proof.exists() else [];assert not any(v['id']==row['id'] for v in rows);rows.append(row);proof.write_text(json.dumps(rows,indent=2)+'\n');assert p.resolve()!=Path(row['path']).resolve();p.unlink()
if row.get('temporaryPart'):Path(row['path']).unlink()
print(json.dumps({'name':row['name'],'id':row['id'],'status':'PASS'}))
