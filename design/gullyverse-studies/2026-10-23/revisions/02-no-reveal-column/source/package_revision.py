from pathlib import Path
import hashlib,json,zipfile
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';C.mkdir(exist_ok=True)
files=[]
for folder in ['source','evidence','review','renders']:
    files.extend(p for p in (O/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.blend1'))
files.extend([O/'REPORT.md',O/'RESTORE.md'])
files=sorted(set(files))
rows=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(O/'FILE-SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['file']+'\n'for r in rows))
files.append(O/'FILE-SHA256SUMS.txt')
archive=C/'Gullyverse-No-Reveal-Column-Source-Review.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for p in files:z.write(p,str(p.relative_to(O)))
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    for r in rows:assert hashlib.sha256(z.read(r['file'])).hexdigest()==r['sha256']
index={'handoff':'WORLD-LANE-ROOFTOP-NO-COLUMN-20261023-02','archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':rows,'sourceMasterSelfContained':True,'websiteFilesChanged':False,'externalBackupStatus':'PENDING_UPLOAD_AND_DOWNLOAD_BACK_VERIFICATION'}
(C/'CHECKPOINT-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVE_READY',archive.stat().st_size,'bytes',len(files),'members',flush=True)
