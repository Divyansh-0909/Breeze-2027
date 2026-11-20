import json,hashlib,zipfile,shutil,datetime
from pathlib import Path
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';C.mkdir(exist_ok=True)
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):d.update(b)
 return d.hexdigest()
for name in ['blender-validation','fresh-open','browser','logo-coverage','viewer-export','review-validation','video','visual-review']:
 assert json.loads((O/'evidence'/f'{name}.json').read_text())['status']=='PASS',name
v=json.loads((O/'evidence/blender-validation.json').read_text());master=O/'delivery/Gullyverse-Rev15L-Navigation-LED.blend';assert sha(master)==v['masterSHA256']
files=[p for p in sorted(O.rglob('*')) if p.is_file() and not p.is_relative_to(C) and '__pycache__' not in p.parts and not p.is_relative_to(O/'review/video') and p.suffix not in ['.log','.webm'] and p.name!='FILE-MANIFEST.json']
rows=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
manifest=O/'FILE-MANIFEST.json';manifest.write_text(json.dumps({'version':'REV15L','files':rows},indent=2));rows.append({'path':manifest.name,'bytes':manifest.stat().st_size,'sha256':sha(manifest)})
archive=C/'Rev15L-Complete-Checkpoint.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for row in rows:z.write(O/row['path'],row['path'])
parts=[]
with archive.open('rb') as f:
 i=1
 while b:=f.read(25000000):
  p=C/(archive.name+f'.{i:03d}');p.write_bytes(b);parts.append({'name':p.name,'bytes':len(b),'sha256':sha(p)});i+=1
index={'version':'REV15L','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archiveSHA256':sha(archive),'archiveBytes':archive.stat().st_size,'parts':parts,'payloads':rows,'sourceMaster':{'path':'delivery/'+master.name,'sha256':sha(master),'bytes':master.stat().st_size},'originalBaseReference':'evidence/base-reference.json'}
(C/'INDEX.json').write_text(json.dumps(index,indent=2));(C/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['name']+'\n' for x in parts));shutil.copy2(O/'source/restore.py',C/'restore.py');archive.unlink()
print(json.dumps({'parts':len(parts),'payloads':len(rows),'archiveBytes':index['archiveBytes'],'masterBytes':master.stat().st_size}),flush=True)
