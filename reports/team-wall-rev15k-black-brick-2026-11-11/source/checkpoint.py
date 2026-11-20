import json,hashlib,zipfile,datetime,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';C.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in ['blender-validation','fresh-open','browser','review-validation','visual-review']:
 assert json.loads((O/'evidence'/f'{f}.json').read_text())['status']=='PASS',f
v=json.loads((O/'evidence/blender-validation.json').read_text());master=O/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend';assert sha(master)==v['masterSHA256']
files=[p for p in sorted(O.rglob('*')) if p.is_file() and not p.is_relative_to(C) and '__pycache__' not in p.parts and p.suffix!='.log' and p.name!='FILE-MANIFEST.json']
payloads=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
f=O/'FILE-MANIFEST.json';f.write_text(json.dumps({'version':'REV15K','files':payloads},indent=2));payloads.append({'path':f.name,'bytes':f.stat().st_size,'sha256':sha(f)})
archive=C/'Rev15K-Complete-Checkpoint.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for row in payloads:z.write(O/row['path'],row['path'])
parts=[]
with archive.open('rb') as src:
 i=1
 while block:=src.read(25000000):
  p=C/(archive.name+f'.{i:03d}');p.write_bytes(block);parts.append({'name':p.name,'bytes':len(block),'sha256':sha(p)});i+=1
index={'version':'REV15K','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archiveSHA256':sha(archive),'archiveBytes':archive.stat().st_size,'parts':parts,'payloads':payloads,'sourceMaster':{'path':'delivery/'+master.name,'bytes':master.stat().st_size,'sha256':sha(master)},'originalBaseReference':'evidence/base-reference.json'}
(C/'INDEX.json').write_text(json.dumps(index,indent=2));(C/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['name']+'\n' for x in parts));shutil.copy2(O/'source/restore.py',C/'restore.py')
archive.unlink() # The verified numbered parts retain the complete archive bytes.
print(json.dumps({'parts':len(parts),'payloads':len(payloads),'archiveBytes':index['archiveBytes'],'masterBytes':master.stat().st_size}))
