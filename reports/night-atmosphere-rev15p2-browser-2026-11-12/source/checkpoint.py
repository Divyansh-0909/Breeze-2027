from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];BASE=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11';C=R/'checkpoint';C.mkdir(exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
base_index=json.loads((BASE/'checkpoint/INDEX.json').read_text());base=BASE/'checkpoint'/base_index['archive'];assert sha(base)==base_index['archiveSHA256']
files=[R/'PLAN.md',R/'REPORT.md',R/'RESTORE.md']+list((R/'source').glob('*.py'))+list((R/'source').glob('*.mjs'))+[p for p in (R/'viewer').rglob('*') if p.is_file()]+list((R/'evidence').glob('*.json'))+list((R/'evidence').glob('*.f32'))+[p for p in (R/'renders').glob('*.png') if p.name.startswith(('desktop-','mobile-emulated-'))]+[R/'review/Gullyverse-Rev15P2-Browser-Night-Review.pdf']
files=sorted(set(files));rows=[{'path':str(p.relative_to(R.parent.parent)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];archive=C/'Rev15P2-Browser-Lighting-Local-Checkpoint-20261112.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p,row in zip(files,rows):z.write(p,row['path'])
index={'phase':'Rev15P2 browser lighting/optimization','storage':'Local source checkpoint; Drive permission used only for the review PDF','archive':archive.name,'archiveBytes':archive.stat().st_size,'archiveSHA256':sha(archive),'dependency':{'path':str(base.relative_to(R.parent.parent)),'bytes':base.stat().st_size,'sha256':base_index['archiveSHA256'],'contains':'Complete packed Rev15P native master, exact baseline GLB, prior source and reviews'},'standaloneViewer':True,'payloads':rows}
(C/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n');(C/'SHA256SUMS.txt').write_text(index['archiveSHA256']+'  '+archive.name+'\n')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in rows:
  h=hashlib.sha256();size=0
  with z.open(row['path']) as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
  assert size==row['bytes'] and h.hexdigest()==row['sha256']
proof={'status':'PASS','method':'Every local archive payload streamed and checked by ZIP CRC, byte count and SHA256; complete dependency archive independently rehashed; live standalone viewer test uses bundled runtime','payloads':len(rows),'archiveSHA256':index['archiveSHA256'],'dependencySHA256':base_index['archiveSHA256'],'externalSourceUpload':False,'reviewPDFUpload':'verified separately after upload'}
(C/'LOCAL-VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':'PASS','payloads':len(rows),'archiveBytes':archive.stat().st_size}),flush=True)
