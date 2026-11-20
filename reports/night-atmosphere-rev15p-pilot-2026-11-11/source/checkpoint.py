from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1];C=R/'checkpoint';C.mkdir(exist_ok=True)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
files=sorted(p for p in R.rglob('*') if p.is_file() and 'checkpoint' not in p.relative_to(R).parts and p.suffix not in ['.log'] and p.name!='server.log')
rows=[{'path':str(p.relative_to(R.parent.parent)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
z=C/'Rev15P-Night-Pilot-Local-Checkpoint-20261111.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as out:
 for p,row in zip(files,rows):out.write(p,row['path'])
index={'phase':'Rev15P isolated pilot','storage':'LOCAL ONLY — active prompt prohibits Drive writes','archive':z.name,'archiveBytes':z.stat().st_size,'archiveSHA256':sha(z),'payloads':rows,'sourceMasterReused':'Full original content is included as 45 preserved scenes inside the packed pilot; the separate authoritative O file is not duplicated','restoration':'See included RESTORE.md; bundled Three.js runtime allows standalone viewer'}
(C/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n');(C/'SHA256SUMS.txt').write_text(index['archiveSHA256']+'  '+z.name+'\n')
with zipfile.ZipFile(z) as archive:
 assert archive.testzip() is None
 for row in rows:
  h=hashlib.sha256();size=0
  with archive.open(row['path']) as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
  assert size==row['bytes'] and h.hexdigest()==row['sha256']
 # Extract the packed master for a truly independent Blender reopen, without
 # consuming another full environment directory on this small workspace disk.
 master=next(r for r in rows if r['path'].endswith('.blend'));dest=C/'restore-verification';dest.mkdir(exist_ok=True)
 restored=dest/'Gullyverse-Rev15P-RESTORED.blend'
 with archive.open(master['path']) as a,restored.open('wb') as b:
  for chunk in iter(lambda:a.read(1048576),b''):b.write(chunk)
 assert sha(restored)==master['sha256']
(C/'LOCAL-VERIFICATION.json').write_text(json.dumps({'status':'PASS','method':'Every ZIP payload streamed and verified by CRC, size and SHA256; packed Blender master extracted independently and hash matched; fresh Blender reopen in separate proof','payloads':len(rows),'archiveSHA256':index['archiveSHA256'],'restoredMaster':str(restored),'externalUpload':'NOT PERFORMED — prompt prohibits Drive writes'},indent=2)+'\n')
print(json.dumps({'status':'PASS','archiveBytes':z.stat().st_size,'payloads':len(rows),'restoredMaster':str(restored)}),flush=True)
