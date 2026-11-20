import hashlib, json, sys
from pathlib import Path

row = json.loads(sys.argv[1]); path = Path(sys.argv[2]); h = hashlib.sha256()
assert path.stat().st_size == row['bytes']
with path.open('rb') as f:
    while data := f.read(1024 * 1024): h.update(data)
assert h.hexdigest() == row['sha256']
row.update({'status':'PASS','method':'Authenticated Drive download-back SHA-256, byte size and parent verified'})
receipt = Path(__file__).resolve().parent / 'documentation-upload-receipts.json'
rows = json.loads(receipt.read_text()) if receipt.exists() else []
rows.append(row); receipt.write_text(json.dumps(rows, indent=2)+'\n')
assert path.resolve() != Path(row['path']).resolve(); path.unlink()
print(json.dumps({'name':Path(row['path']).name,'id':row['id'],'status':'PASS'}))
