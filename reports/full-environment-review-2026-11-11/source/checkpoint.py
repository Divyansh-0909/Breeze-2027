import hashlib, json, shutil, zipfile, datetime
from pathlib import Path

O=Path(__file__).resolve().parents[1];C=O/'checkpoint';C.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((O/'evidence/preservation.json').read_text())['status']=='PASS'
assert json.loads((O/'evidence/image-validation.json').read_text())['imageCount']==52
payloads=[]
for p in sorted(O.rglob('*')):
    if not p.is_file() or p.is_relative_to(C) or '__pycache__' in p.parts:continue
    if p.suffix=='.log':continue
    payloads.append({'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
archive=C/'Full-Environment-Review-2026-11-11.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in payloads:z.write(O/p['path'],p['path'])
parts=[]
with archive.open('rb') as src:
    i=1
    while block:=src.read(25000000):
        part=C/(archive.name+f'.{i:03d}');part.write_bytes(block)
        parts.append({'name':part.name,'bytes':len(block),'sha256':sha(part)});i+=1
index={'version':'FULL-ENVIRONMENT-REVIEW-20261111','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archiveSHA256':sha(archive),'parts':parts,'payloads':payloads,'sourceMasterReference':'evidence/base-master-reference.json','scope':'All review outputs self-contained; unchanged source master reused from the verified Rev15J1 base checkpoint.'}
(C/'INDEX.json').write_text(json.dumps(index,indent=2))
shutil.copy2(O/'source/restore.py',C/'restore.py')
(C/'SHA256SUMS.txt').write_text('\n'.join(x['sha256']+'  '+x['name'] for x in parts)+'\n')
print(json.dumps({'payloads':len(payloads),'parts':len(parts),'archiveBytes':archive.stat().st_size,'pdfBytes':(O/'review/Gullyverse-Full-3D-Environment-2026-11-11.pdf').stat().st_size}))
