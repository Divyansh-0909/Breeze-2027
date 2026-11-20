from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for name in ['build-verification','fresh-open','export','restore-check','restored-fresh-open','pdf','document-verification']:
 assert json.loads((R/'evidence'/(name+'.json')).read_text())['status']=='PASS',name
rows=[]
for folder in ['source','evidence','assets','renders','document-snapshots']:
 for p in sorted((R/folder).rglob('*')):
  if p.is_file()and p.suffix not in ['.lock','.pyc']:rows.append((str(p.relative_to(repo)),p.read_bytes()))
for p in sorted((R/'delivery').iterdir()):
 if p.suffix in ['.blend','.glb']:rows.append((str(p.relative_to(repo)),p.read_bytes()))
for name in ['REPORT.md','RESTORE.md']:rows.append((str((R/name).relative_to(repo)),(R/name).read_bytes()))
pdf=R/'review/Breeze-Events-Accommodation-and-Contact-Proposal-Rev15X.pdf';rows.append((str(pdf.relative_to(repo)),pdf.read_bytes()))
for name in ['AGENTS.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json','docs/gullyverse-accommodation-current.md','docs/gullyverse-destination-design-current.md','docs/gullyverse-events-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-shared-document-current.md']:
 rows.append((name,(repo/name).read_bytes()))
payload=[{'path':n,'bytes':len(data),'sha256':sha(data)}for n,data in rows];out=R/'delivery/Breeze-Rev15X-Accommodation-and-Destination-Proposal-Checkpoint.zip'
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
 while data:=f.read(4*1024*1024):
  p=out.with_name(out.name+'.part%02d'%i);p.write_bytes(data);parts.append({'index':i,'file':p.name,'bytes':len(data),'sha256':sha(data)});i+=1
assert sha(b''.join((R/'delivery'/r['file']).read_bytes()for r in parts))==sha(out.read_bytes())
result={'status':'PASS','filename':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'payloadFiles':len(payload),'zipCRCAndAllPayloadHashes':'PASS','parts':parts,'nativeRecovery':'Reuse the verified complete W recovery chain, then X source rebuild; actual X rebuild and separate fresh-open passed.'};(R/'evidence/checkpoint-package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
