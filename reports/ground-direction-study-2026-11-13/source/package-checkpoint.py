from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];D=R/'delivery';D.mkdir(exist_ok=True)
refs=json.loads((R/'references/sources.json').read_text())
files={str(p.relative_to(R)):p for p in (R/'source').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for group in ['evidence','review']:
 files.update({str(p.relative_to(R)):p for p in (R/group).rglob('*') if p.is_file()})
for x in refs:files[x['local']]=R/x['local']
for name in ['references/sources.json','REPORT.md','RESTORE.md']:files[name]=R/name
for name in ['AGENTS.md','docs/gullyverse-ground-direction-study-current.md','docs/gullyverse-backup-target.json']:files['workspace-docs/'+name]=R.parents[1]/name
index={name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for name,p in sorted(files.items())}
z=D/'Breeze-Ground-Direction-Study-Source-Checkpoint.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,p in sorted(files.items()):out.write(p,name)
 out.writestr('CHECKPOINT-SHA256.json',json.dumps(index,indent=2)+'\n')
with zipfile.ZipFile(z) as check:
 assert check.testzip() is None
 for name,row in index.items():
  b=check.read(name);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
receipt={'status':'PASS','payloadCount':len(index),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'verification':'ZIP CRC and every payload size/SHA256 checked','scope':'Research-only checkpoint; no native or website implementation'}
(D/'Checkpoint-Index.json').write_text(json.dumps({'checkpoint':receipt,'payloads':index},indent=2)+'\n')
(D/'SHA256SUMS.txt').write_text(receipt['sha256']+'  '+z.name+'\n')
print(json.dumps(receipt))
