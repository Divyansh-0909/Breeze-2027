import io,bisect,hashlib,json,sys,zipfile,stat
from pathlib import Path,PurePosixPath

def sha(file):
 d=hashlib.sha256()
 with Path(file).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):d.update(block)
 return d.hexdigest()

class Parts(io.RawIOBase):
 def __init__(self,files):
  super().__init__();self.files=[p.open('rb') for p in files];self.starts=[0];self.position=0
  for p in files:self.starts.append(self.starts[-1]+p.stat().st_size)
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.position
 def seek(self,offset,whence=0):
  target=offset if whence==0 else self.position+offset if whence==1 else self.starts[-1]+offset
  if target<0:raise ValueError('Negative seek')
  self.position=target;return target
 def read(self,size=-1):
  remaining=self.starts[-1]-self.position
  size=remaining if size is None or size<0 else min(size,remaining)
  if size<=0:return b''
  chunks=[]
  while size>0:
   i=bisect.bisect_right(self.starts,self.position)-1
   count=min(size,self.starts[i+1]-self.position);f=self.files[i];f.seek(self.position-self.starts[i]);b=f.read(count)
   if len(b)!=count:raise IOError('Short archive part')
   chunks.append(b);self.position+=len(b);size-=len(b)
  return b''.join(chunks)
 def close(self):
  for f in self.files:f.close()
  super().close()

def restore(index_path,downloads,destination):
 index=json.loads(Path(index_path).read_text());downloads=Path(downloads);destination=Path(destination)
 if destination.exists() and any(destination.iterdir()):raise ValueError('Restore destination must be empty')
 files=[];combined=hashlib.sha256()
 for part in index['parts']:
  if Path(part['name']).name!=part['name']:raise ValueError('Invalid part path')
  p=downloads/part['name'];assert p.stat().st_size==part['bytes'] and sha(p)==part['sha256'],part['name'];files.append(p)
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):combined.update(block)
 assert combined.hexdigest()==index['archiveSHA256'],'Combined archive checksum mismatch'
 expected={r['path']:r for r in index['payloads']};destination.mkdir(parents=True,exist_ok=True)
 with Parts(files) as stream,zipfile.ZipFile(stream) as archive:
  assert set(archive.namelist())==set(expected),'Payload list mismatch'
  for item in archive.infolist():
   name=PurePosixPath(item.filename)
   if name.is_absolute() or '..' in name.parts or stat.S_ISLNK(item.external_attr>>16) or item.file_size!=expected[item.filename]['bytes']:raise ValueError('Unsafe archive entry: '+item.filename)
  archive.extractall(destination)
 for relative,r in expected.items():
  p=destination/relative;assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],relative
 print(json.dumps({'status':'PASS','payloads':len(expected),'destination':str(destination),'method':'Direct seekable stream across verified ZIP parts; no combined temporary archive'}))

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('Usage: python restore.py INDEX.json /downloads /empty/restore')
 restore(*sys.argv[1:])
