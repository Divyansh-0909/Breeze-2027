from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['build-verification','fresh-open','restore-check','restored-fresh-open','export','glb-structure','pdf','document-verification']:
 assert json.loads((R/'evidence'/(name+'.json')).read_text())['status']=='PASS',name
b=json.loads((R/'evidence/build-verification.json').read_text());rs=json.loads((R/'evidence/restore-check.json').read_text());assert rs['sceneFingerprintSHA256']==b['sceneFingerprintSHA256'];assert sha(Path(b['editedMaster']).read_bytes())==b['editedSHA256'];rows=[]
for folder in ['source','evidence','renders','document-snapshots']:
 for p in sorted((R/folder).rglob('*')):
  if p.is_file()and p.suffix not in ['.lock','.pyc']:rows.append((str(p.relative_to(repo)),p.read_bytes()))
for p in sorted((R/'delivery').iterdir()):
 if p.suffix in ['.blend','.glb']or p.name=='component-manifest.json':rows.append((str(p.relative_to(repo)),p.read_bytes()))
for name in ['REPORT.md','RESTORE.md']:rows.append((str((R/name).relative_to(repo)),(R/name).read_bytes()))
p=R/'review/Breeze-Clean-Accommodation-and-Gully-Contact-Rev15X1.pdf';rows.append((str(p.relative_to(repo)),p.read_bytes()))
for name in ['AGENTS.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json','docs/gullyverse-accommodation-current.md','docs/gullyverse-contact-theme-current.md','docs/gullyverse-destination-design-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-shared-document-current.md']:
 rows.append((name,(repo/name).read_bytes()))
payload=[{'path':name,'bytes':len(data),'sha256':sha(data)}for name,data in rows];out=R/'delivery/Breeze-Rev15X1-Clean-Accommodation-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8)as z:
 for name,data in rows:z.writestr(name,data)
 z.writestr('PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(out)as z:
 assert z.testzip()is None
 for row in payload:
  data=z.read(row['path']);assert len(data)==row['bytes']and sha(data)==row['sha256']
parts=[]
with out.open('rb')as f:
 i=1
 while data:=f.read(3*1024*1024):
  p=out.with_name(out.name+'.part%02d'%i);p.write_bytes(data);parts.append({'index':i,'file':p.name,'bytes':len(data),'sha256':sha(data)});i+=1
assert sha(b''.join((R/'delivery'/r['file']).read_bytes()for r in parts))==sha(out.read_bytes())
result={'status':'PASS','filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'payloadFiles':len(payload),'zipCRCAndEveryPayloadHash':'PASS','parts':parts};(R/'evidence/checkpoint-package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
