from pathlib import Path
import zipfile,json,hashlib,shutil,time
root=Path.cwd();r=root/'reports/current-final-review-2026-10-11';manifest=r/'raw/evidence-manifest.json'
files=[root/'docs/gullyverse-current-final-review.md',root/'docs/gullyverse-current-visual-baseline.md']+sorted(p for p in r.rglob('*') if p.is_file() and p!=manifest and '__pycache__' not in p.parts)
items=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest.write_text(json.dumps({'manifestExcludesItself':True,'files':items,'artifactCount':len(items),'totalIndexedBytes':sum(i['bytes'] for i in items)},indent=2))
files.append(manifest);out=root/'gullyverse-final-review-evidence.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 z.writestr('index.html','<!doctype html><html><meta charset="utf-8"><title>Gullyverse review</title><p><a href="reports/current-final-review-2026-10-11/START-HERE.html">Open the evidence package</a></p></html>')
 for p in files:z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(out) as z:
 bad=z.testzip();names=z.namelist();assert not bad
 for i in items:assert hashlib.sha256(z.read(i['path'])).hexdigest()==i['sha256']
 assert len(names)==len(files)+1
 out.chmod(0o644)
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'entries':len(names),'CRCtest':'PASS','indexedSHA256tests':'PASS','archiveSHA256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
