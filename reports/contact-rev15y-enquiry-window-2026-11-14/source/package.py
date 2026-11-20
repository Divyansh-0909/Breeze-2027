from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['build-verification','fresh-open','restore-check','restored-fresh-open','export','glb-structure','browser','pdf','document-verification']:
 assert json.loads((R/'evidence'/(name+'.json')).read_text())['status']=='PASS',name
assert json.loads((R/'evidence/movement-recheck.json').read_text())['status']=='UNCHANGED'
b=json.loads((R/'evidence/build-verification.json').read_text());rs=json.loads((R/'evidence/restore-check.json').read_text());assert rs['sceneFingerprintSHA256']==b['sceneFingerprintSHA256'];assert sha(Path(b['editedMaster']).read_bytes())==b['editedSHA256'];rows={}
def add(p):rows[str(p.relative_to(repo))]=p.read_bytes()
for folder in ['source','evidence','renders','document-snapshots','assets','viewer']:
 for p in sorted((R/folder).rglob('*')):
  if p.is_file()and p.suffix not in ['.lock','.pyc']and p.name not in ['upload-receipts.json','checkpoint-package.json']:add(p)
for p in sorted((R/'source/review-fonts').iterdir()):
 if p.is_file():add(p)
for p in sorted((R/'delivery').iterdir()):
 if p.suffix in ['.blend','.glb']or p.name=='window-manifest.json':add(p)
for name in ['REPORT.md','RESTORE.md']:add(R/name)
add(R/'review/Breeze-Contact-Window-and-Clean-Accommodation-Rev15Y.pdf')
for name in ['AGENTS.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json','docs/gullyverse-accommodation-current.md','docs/gullyverse-contact-theme-current.md','docs/gullyverse-destination-design-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-shared-document-current.md']:add(repo/name)
payload=[{'path':name,'bytes':len(data),'sha256':sha(data)}for name,data in sorted(rows.items())];out=R/'delivery/Breeze-Rev15Y-Enquiry-Window-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8)as z:
 for name,data in sorted(rows.items()):z.writestr(name,data)
 z.writestr('PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(out)as z:
 assert z.testzip()is None
 for row in payload:
  data=z.read(row['path']);assert len(data)==row['bytes']and sha(data)==row['sha256']
parts=[]
with out.open('rb')as f:
 i=1
 while data:=f.read(2*1024*1024):
  p=out.with_name(out.name+'.part%02d'%i);p.write_bytes(data);parts.append({'index':i,'file':p.name,'bytes':len(data),'sha256':sha(data)});i+=1
assert sha(b''.join((R/'delivery'/r['file']).read_bytes()for r in parts))==sha(out.read_bytes())
result={'status':'PASS','filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'payloadFiles':len(payload),'zipCRCAndEveryPayloadHash':'PASS','parts':parts};(R/'evidence/checkpoint-package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
