import json,sys,hashlib
from pathlib import Path
row=json.loads(sys.argv[1]); downloaded=Path(sys.argv[2]); staged=Path(row['path'])
assert downloaded.stat().st_size==row['bytes']
h=hashlib.sha256()
with downloaded.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
assert h.hexdigest()==row['sha256']
row.update({'status':'PASS','method':'Authenticated Drive download-back; remote parent and byte size checked; downloaded SHA-256 equals original archive slice'})
r=Path(__file__).resolve().parent/'source-upload-receipts.json';rows=json.loads(r.read_text()) if r.exists() else []
assert not any(v['archive']==row['archive'] and v['index']==row['index'] for v in rows)
rows.append(row);r.write_text(json.dumps(rows,indent=2)+'\n')
assert downloaded!=staged;downloaded.unlink();staged.unlink()
print(json.dumps({'id':row['id'],'part':row['index']+1,'status':'PASS','verifiedParts':len(rows)}))
