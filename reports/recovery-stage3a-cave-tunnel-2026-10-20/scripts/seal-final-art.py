"""Protect the final art independently while slower browser tests finish."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path.cwd();W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=[]
for rel in ['assets-source/gullyverse/c9-cave-recovery','public/models/gullyverse/c9-cave-recovery']:
 files.extend(p for p in (ROOT/rel).rglob('*')if p.is_file()and not p.name.endswith(('.blend1','.blend2'))and'__pycache__'not in p.parts)
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(files)]
name='Gullyverse-Stage3A-FINAL-B-editable-art-runtime.zip';archive=W/name;assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for row in rows:z.write(ROOT/row['path'],'project/'+row['path'])
 assert z.testzip()is None
d={'name':name,'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'group':'B','files':rows,'parent_id':'1y-fLFkJthsB9gMOr5fZNseZXSg_2B24a'}
(W/'B-final-assets.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k!='files'}))
