"""Stream an authenticated connector file reference into scratch, verify, discard.
Used when the attachment helper cannot create its root-filesystem cache.
Temporary signed reference is consumed once and never included in receipts.
"""
import json,hashlib,sys,urllib.request,urllib.parse,datetime,fcntl
from pathlib import Path
descriptor=Path(sys.argv[1]);d=json.loads(descriptor.read_text());row=d['expected'];url=d['downloadURL'];host=urllib.parse.urlparse(url).hostname;assert host and host.endswith('.oaiusercontent.com');target=descriptor.with_suffix('.bytes');h=hashlib.sha256();total=0
try:
 with urllib.request.urlopen(url,timeout=120)as response,target.open('wb')as f:
  while data:=response.read(1024*1024):f.write(data);h.update(data);total+=len(data)
 assert total==row['bytes']and h.hexdigest()==row['sha256']
 row.update(status='PASS',verificationMethod='Authenticated connector file-reference download streamed into tmpfs; SHA-256 and byte size exact',verifiedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());receipt=Path(d['receipt'])
 with receipt.with_suffix('.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);rows=json.loads(receipt.read_text())if receipt.exists()else[];rows.append(row);receipt.write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps({'status':'PASS','name':row['name'],'bytes':total,'sha256':h.hexdigest()}))
finally:
 if target.exists():target.unlink()
 descriptor.unlink(missing_ok=True)
