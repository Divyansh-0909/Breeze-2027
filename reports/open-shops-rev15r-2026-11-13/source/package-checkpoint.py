from pathlib import Path
import json,hashlib,zipfile,datetime,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();idx=json.loads((R/'delivery/Native-Master-Parts.json').read_text());assert idx['status']=='PASS'
proof=json.loads((R/'evidence/build-verification.json').read_text());master=Path(proof['editedMaster']);assert sha(master)==idx['sha256']
with master.open('rb') as f:
 for p in idx['parts']:
  assert f.tell()==p['offset'];b=f.read(p['bytes']);assert hashlib.sha256(b).hexdigest()==p['sha256']
 assert f.read()==b''
fresh=json.loads((R/'evidence/fresh-open.json').read_text());assert fresh['masterSHA256']==idx['sha256'] and fresh['status']=='PASS'
captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures)==13
for row in captures:assert sha(R/'renders'/f"{row['key']}.png")==row['sha256']
pdf=json.loads((R/'evidence/pdf-verification.json').read_text());assert pdf['pages']==10 and sha(R/'review/Breeze-Open-Shops-Indian-Market-Review.pdf')==pdf['sha256']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();assert head=='0e1e23dd2f5181df202d862d147067249bc55a41'
assert subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()==''
summary={'status':'PASS','verifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSourceSlicesAndWholeSHA256':'PASS','masterSHA256':idx['sha256'],'nativeFreshOpen':fresh,'capturedViews':13,'pdf':pdf,'productionSourceDiffEmpty':True,'gitHEAD':head,'destinationOwner':'losersamurai09@gmail.com','olderDriveMigration':'PENDING; CSD361 excluded'};(R/'evidence/final-verification.json').write_text(json.dumps(summary,indent=2)+'\n')
files=[R/'REPORT.md',R/'RESTORE.md',R/'review/Breeze-Open-Shops-Indian-Market-Review.pdf',repo/'AGENTS.md',repo/'docs/gullyverse-open-shops-current.md']
for folder in ['source','references','renders','delivery','evidence']:
 files += [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['bounds-debug.json','PAUSE-UPLOAD','Breeze-Rev15R-Open-Shops-Source-Checkpoint.zip','Delivery-Index.json','SHA256SUMS.txt']]
files=sorted(set(files));payload=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15R-Open-Shops-Source-Checkpoint.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for p in payload:
  b=z.read(p['path']);assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256']
index={'status':'PASS','archive':{'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'payloads':len(payload)},'nativeMasterParts':idx,'pdfUpload':json.loads((R/'evidence/pdf-upload.json').read_text()),'payload':payload,'restore':'Extract source checkpoint into checkout root; see reports/open-shops-rev15r-2026-11-13/RESTORE.md. Complete master is in seven separately verified final native parts. Ignore superseded pre-UV draft parts.','scope':'Native authoring only; public website and old-account folder migration pending.'};p=R/'delivery/Delivery-Index.json';p.write_text(json.dumps(index,indent=2)+'\n');(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+p.name for p in [out,p,R/'delivery/Native-Master-Parts.json'])+'\n');print(json.dumps(index['archive']))
