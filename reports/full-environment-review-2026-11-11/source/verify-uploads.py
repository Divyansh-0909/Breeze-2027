import json,hashlib,sys,datetime
from pathlib import Path

O=Path(__file__).resolve().parents[1]
receipts=O/'checkpoint/remote';receipts.mkdir(parents=True,exist_ok=True)
results=[]
for p in sorted(receipts.glob('*.json')):
    r=json.loads(p.read_text())
    local=Path(r['localPath']);download=Path(r['downloadPath'])
    a=hashlib.sha256(local.read_bytes()).hexdigest();b=hashlib.sha256(download.read_bytes()).hexdigest()
    assert a==b,(local.name,'SHA-256 mismatch')
    assert local.stat().st_size==download.stat().st_size==r['remoteBytes'],local.name
    assert r['parent'] in r['remoteParents'],local.name
    results.append(dict(name=local.name,path=str(local),bytes=local.stat().st_size,sha256=a,id=r['id'],url=r['url'],parent=r['parent'],verified=True,downloadPath=str(download),method='Full authenticated Drive download-back SHA-256; remote parent and size checked'))
out={'version':'FULL-ENVIRONMENT-REVIEW-20261111','verifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','count':len(results),'files':results}
(O/'checkpoint/UPLOADED.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'status':'PASS','verifiedFiles':len(results)}))
