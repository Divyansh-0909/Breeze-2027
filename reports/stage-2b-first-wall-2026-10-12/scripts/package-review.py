from pathlib import Path
import zipfile,json,hashlib,re,html,os
root=Path.cwd();r=root/'reports/stage-2b-first-wall-2026-10-12';zipPath=root/'gullyverse-stage-2b-first-wall-review.zip'
readme=root/'reports/stage-2b-first-wall-2026-10-12/REVIEW-PACKAGE.md';readme.write_text('''# Stage2B review package

This self-contained evidence/source package contains the report, actual browser PNGs/recordings, capture metadata, raw measured data, tests, source patch and original Blender authoring/exports. It is not a complete runnable application checkout or a deployment.

Open `gallery.html` beside this README, or serve the extracted package root with `python -m http.server 8000` and open `/reports/stage-2b-first-wall-2026-10-12/gallery.html`. Main report: `docs/gullyverse-stage-2b-first-wall-integration.md` at package root. Editable asset: `assets-source/gullyverse/first-wall-section/first-wall-section.blend`; runtime combined asset: `public/models/gullyverse/first-wall-section/first-wall-section.glb`. Other GLBs are alternatives and should not all be mounted visible or downloaded redundantly.

For interactive quarry preview use the existing application checkout at the recorded baseline plus these bounded source changes and assets, following the main report's opt-in local build instructions. Default production appearance is preserved. This package contains relevant source for review, not dependencies/private environment configuration or unrelated site data.

The large recoverable pre-edit source/assets snapshot remains in the workspace backup directory and is deliberately not packaged. Its hash inventories/preservation results are included. Source master/maps are original; provided reference photographs are comparison material only. No credentials, `.env`, `.vercel`, `.git`, application databases, payments/admin data or dependencies are included.

Acceptance images are under `acceptance/`; unchanged initial captures under `baseline/`; rejected trial screenshots under `exploratory/` are clearly labeled in the report. Individual PNG resolution is retained. SwiftShader performance is not physical GPU/mobile acceptance.
''')
paths=set()
def add(p):
 p=Path(p)
 if p.is_file():paths.add(p.relative_to(root).as_posix())
def folder(p):
 for f in Path(p).rglob('*'):
  if not f.is_file() or any(t in ['backup','__pycache__','.git','node_modules','.vercel'] or t.startswith('.env') for t in f.relative_to(root).parts) or f.suffix in ['.blend1','.pyc']:continue
  add(f)
for p in ['assets-source/gullyverse/first-wall-section','public/models/gullyverse/first-wall-section','components/immersive','tests/immersive','components/landing-page/stage3d']:
 folder(root/p)
folder(r)
for p in ['docs/gullyverse-stage-2b-first-wall-integration.md','scripts/blender/author_first_wall_section.py','scripts/blender/wall_section_surface.py','scripts/blender/wall_section_materials.py','scripts/blender/rock_pilot_surface.py']:add(root/p)
# Refresh our final new-source/asset/report inventory, not pre-existing inventories.
p=r/'raw/new-file-inventory.json';old=json.loads(p.read_text());rows=[]
for row in old:
 f=root/row['file'];rows.append({'file':row['file'],'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
p.write_text(json.dumps(rows,indent=2))
# Fail early on unresolved main-report/gallery file references.
missing=[]
for file,regex in [(root/'docs/gullyverse-stage-2b-first-wall-integration.md',r'\]\(([^)]+)\)'),(r/'gallery.html',r'(?:href|src)="([^"]+)"')]:
 for link in re.findall(regex,file.read_text()):
  if link.startswith(('http:','https:','#','data:')):continue
  target=(file.parent/html.unescape(link.split('#')[0])).resolve()
  if not target.exists() or str(target.relative_to(root)) not in paths:missing.append({'file':str(file.relative_to(root)),'link':link})
assert not missing,missing
ledger={p:{'bytes':(root/p).stat().st_size,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()}for p in sorted(paths)}
manifestPath=r/'raw/package-file-manifest.json';manifestPath.write_text(json.dumps(ledger,indent=2));add(manifestPath)
with zipfile.ZipFile(zipPath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(paths):z.write(root/p,p)
with zipfile.ZipFile(zipPath) as z:
 assert z.testzip() is None
 for p,row in ledger.items():assert hashlib.sha256(z.read(p)).hexdigest()==row['sha256'],p
out={'archive':zipPath.name,'bytes':zipPath.stat().st_size,'sha256':hashlib.sha256(zipPath.read_bytes()).hexdigest(),'files':len(paths),'CRC':'PASS','fileHashes':'PASS','mainReportAndGalleryLinks':'PASS','credentialsExcluded':True,'unrelatedProductionDataExcluded':True};(r/'raw/package-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
