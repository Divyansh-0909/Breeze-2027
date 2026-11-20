import io,json,hashlib,zipfile,shutil,datetime
from pathlib import Path
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';C.mkdir(exist_ok=True)
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
class SplitWriter(io.RawIOBase):
 def __init__(self):super().__init__();self.position=0;self.file=None;self.count=0;self.digest=hashlib.sha256();self.partDigest=None;self.parts=[];self.inPart=0
 def writable(self):return True
 def seekable(self):return False
 def tell(self):return self.position
 def finishPart(self):
  if self.file:
   self.file.close();self.parts.append({'name':self.file.name.split('/')[-1],'bytes':self.inPart,'sha256':self.partDigest.hexdigest()});self.file=None
 def write(self,data):
  total=len(data);self.digest.update(data);data=memoryview(data)
  while data:
   if self.file is None:self.count+=1;self.file=(C/f'Rev15O-Complete-Checkpoint.zip.{self.count:03d}').open('wb');self.partDigest=hashlib.sha256();self.inPart=0
   n=min(len(data),25000000-self.inPart);chunk=data[:n];self.file.write(chunk);self.partDigest.update(chunk);self.inPart+=n;self.position+=n;data=data[n:]
   if self.inPart==25000000:self.finishPart()
  return total
for name in ['blender-validation','fresh-open','review-validation','visual-review']:assert json.loads((O/'evidence'/f'{name}.json').read_text())['status']=='PASS',name
master=O/'delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend';assert sha(master)==json.loads((O/'evidence/blender-validation.json').read_text())['masterSHA256']
files=[p for p in sorted(O.rglob('*')) if p.is_file() and not p.is_relative_to(C) and not p.is_relative_to(O/'review/video') and '__pycache__' not in p.parts and p.suffix not in ['.log','.webm'] and p.name!='FILE-MANIFEST.json']
rows=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];manifest=O/'FILE-MANIFEST.json';manifest.write_text(json.dumps({'version':'REV15O','files':rows},indent=2));rows.append({'path':manifest.name,'bytes':manifest.stat().st_size,'sha256':sha(manifest)})
stream=SplitWriter()
with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for row in rows:archive.write(O/row['path'],row['path'])
stream.finishPart();index={'version':'REV15O','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archiveBytes':stream.position,'archiveSHA256':stream.digest.hexdigest(),'parts':stream.parts,'payloads':rows,'sourceMaster':next(r for r in rows if r['path'].startswith('delivery/')),'originalBaseReference':'evidence/base-reference.json'}
(C/'INDEX.json').write_text(json.dumps(index,indent=2));(C/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['name']+'\n' for r in stream.parts));shutil.copy2(O/'source/restore.py',C/'restore.py');print(json.dumps({'parts':len(stream.parts),'payloads':len(rows),'archiveBytes':stream.position}),flush=True)
