from pathlib import Path
import hashlib,json,zipfile,datetime
ROOT=Path.cwd();W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint');W.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=[]
for rel in ['assets-source/gullyverse/c9-cave-recovery','public/models/gullyverse/c9-cave-recovery']:
 for p in (ROOT/rel).rglob('*'):
  if p.is_file()and not p.name.endswith(('.blend1','.blend2'))and '__pycache__'not in p.parts:files.append(p)
rows=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(files)]
name='Gullyverse-Stage3A-B-editable-cave-and-runtime.zip';archive=W/name;assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for row in rows:z.write(ROOT/row['path'],'project/'+row['path'])
 z.writestr('ASSET-ONLY-README.md','# Stage3A private cave assets\n\nEditable full entrance/passage master, trial master, source provenance, five reference images and validated local GLBs. This is NOT a complete website backup by itself. Use the FINAL checkpoint-index.json, source archive and protected Phase1/2/3/quarry-fidelity dependencies. Public C5.1 and selected C9 remain protected. Exact artist PNGs are missing; no replacement artwork was invented. User visual approval is pending. No commit/deploy.\n')
 assert z.testzip()is None
record={'name':name,'bytes':archive.stat().st_size,'sha256':sha(archive),'group':'B','files':rows,'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'STATIC_SOURCE_ART_SEALED_PENDING_EXTERNAL_VERIFICATION','parent_id':'1y-fLFkJthsB9gMOr5fZNseZXSg_2B24a'}
(W/'B-static-assets.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k]for k in ['name','bytes','sha256','status']}))
