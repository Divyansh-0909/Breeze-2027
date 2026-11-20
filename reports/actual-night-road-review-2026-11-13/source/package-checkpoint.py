from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((R/'evidence/lighting-verification.json').read_text());assert proof['status']=='PASS' and proof['sourceMasterUnchanged']
assert sha(Path(proof['sourceMaster']))==proof['sourceSHA256']
up=json.loads((R/'evidence/pdf-upload.json').read_text());assert up['status']=='PASS' and sha(Path(up['path']))==up['sha256']
files=[]
for group in ['source','renders','evidence','review']:files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend([R/'README.md',R/'delivery/Source-Scene-Dependencies.json',repo/'AGENTS.md',repo/'docs/gullyverse-ground-current.md'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Actual-Night-Road-Review-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for row in rows:
  b=z.read(row['path']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
idx={'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'payloadCount':len(rows),'files':rows,'sourceMasterUnchanged':True}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(idx,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text(sha(out)+'  '+out.name+'\n')
print(json.dumps({k:idx[k] for k in ['status','bytes','sha256','payloadCount']}))
