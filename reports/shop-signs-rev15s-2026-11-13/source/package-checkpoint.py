from pathlib import Path
import hashlib,json,zipfile,datetime,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();idx=json.loads((R/'delivery/Native-Master-Parts.json').read_text());assert idx['status']=='PASS';b=json.loads((R/'evidence/build-verification.json').read_text());assert sha(Path(b['editedMaster']))==idx['sha256'];assert json.loads((R/'evidence/fresh-open.json').read_text())['editedSHA256']==idx['sha256']
with Path(b['editedMaster']).open('rb') as f:
 for row in idx['parts']:
  assert f.tell()==row['offset'];data=f.read(row['bytes']);assert hashlib.sha256(data).hexdigest()==row['sha256']
 assert not f.read()
captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures)==12
for row in captures:assert row['masterSHA256']==idx['sha256'] and sha(R/'renders'/f"{row['key']}.png")==row['sha256']
pdf=json.loads((R/'evidence/pdf-verification.json').read_text());up=json.loads((R/'evidence/pdf-upload.json').read_text());assert sha(R/'review/Breeze-Realistic-Shop-Boards-Review.pdf')==pdf['sha256']==up['sha256']
mov=json.loads((repo/'reports/open-shops-rev15r-2026-11-13/evidence/movement-preservation.json').read_text());assert all(sha(repo/x['path'])==x['sha256'] for x in mov['files']);(R/'evidence/movement-preservation.json').write_text(json.dumps(mov,indent=2))
assert subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()==''
proof={'status':'PASS','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSHA256':idx['sha256'],'masterSourceSlicesAndWholeHash':'PASS','nativeFreshOpen':'PASS','viewCount':12,'pdf':pdf,'originalQuarryFiles':'UNCHANGED','productionSourceDiffEmpty':True,'destinationAccount':'losersamurai09@gmail.com'};(R/'evidence/final-verification.json').write_text(json.dumps(proof,indent=2))
files=[R/'REPORT.md',R/'RESTORE.md',R/'review/Breeze-Realistic-Shop-Boards-Review.pdf',repo/'AGENTS.md',repo/'docs/gullyverse-shop-signs-current.md']
exclude={'Rev15S-Shop-Board-Additions.blend','Breeze-Rev15S-Shop-Boards-Source-Checkpoint.zip','Delivery-Index.json','SHA256SUMS.txt'}
for folder in ['source','references','renders','evidence','delivery']:
 files += [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in exclude]
files=sorted(set(files));payload=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];out=R/'delivery/Breeze-Rev15S-Shop-Boards-Source-Checkpoint.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for p in payload:
  data=z.read(p['path']);assert len(data)==p['bytes'] and hashlib.sha256(data).hexdigest()==p['sha256']
library=json.loads((R/'evidence/library-upload.json').read_text());index={'status':'PASS','archive':{'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'payloadCount':len(payload)},'nativeMaster':idx,'assetLibrary':library,'pdf':up,'payload':payload,'restore':'Extract checkpoint into checkout root; see reports/shop-signs-rev15s-2026-11-13/RESTORE.md. Full native master and optional additions library are separate verified outputs, not duplicated in the source ZIP.'};p=R/'delivery/Delivery-Index.json';p.write_text(json.dumps(index,indent=2)+'\n');(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(x)+'  '+x.name for x in [out,p,R/'delivery/Native-Master-Parts.json'])+'\n');print(json.dumps(index['archive']))
