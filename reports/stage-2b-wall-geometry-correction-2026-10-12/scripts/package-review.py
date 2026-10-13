from pathlib import Path
import zipfile,json,hashlib,re,html,subprocess,tarfile
root=Path.cwd();r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');report=Path('docs/gullyverse-stage-2b-wall-geometry-correction.md');target=Path('gullyverse-stage-2b-wall-geometry-correction-review.zip')
assert report.exists()and (r/'gallery.html').exists()
files=set()
for folder in [r/'before',r/'after',r/'raw',r/'scripts',r/'recordings',r/'backup',r/'trials',Path('assets-source/gullyverse/first-wall-corrected'),Path('public/models/gullyverse/first-wall-corrected')]:
 for p in folder.rglob('*'):
  if p.is_file()and '__pycache__'not in p.parts and p.suffix not in ['.blend1','.pyc']:files.add(p)
# The review is self-contained for the gallery/export workflow, not a new whole application checkout.
files.add(report);files.add(r/'gallery.html')
for p in Path('components/immersive').glob('*'):
 if p.is_file()and p.suffix in ['.ts','.tsx']:files.add(p)
files.update([Path('tests/immersive/wall-section.test.ts'),Path('scripts/blender/author_corrected_wall_section.py'),Path('scripts/blender/corrected_wall_geometry.py'),Path('scripts/blender/corrected_wall_joins.py'),Path('scripts/blender/rock_pilot_surface.py'),Path('assets-source/gullyverse/first-wall-section/anchor.json'),Path('public/models/gullyverse/first-wall-section/manifest.json'),Path('public/models/gullyverse/first-wall-section/first-wall-section.glb')])
files.update(p for p in Path('assets-source/gullyverse/first-wall-section/textures').iterdir()if p.is_file())
for p in files:
 assert p.exists(),p
 assert not any(part.startswith('.env')or part in ['node_modules','.git','credentials']for part in p.parts),p
with tarfile.open(r/'backup/current-wall-candidate.tar.gz')as t:
 assert not any(any(part.startswith('.env')or part in ['.git','node_modules','credentials']for part in Path(n).parts)for n in t.getnames())
# Check report/gallery local links against the actual filesystem before packaging.
links=re.findall(r'\]\(([^)]+)\)',report.read_text());bad=[]
for href in links:
 if href.startswith(('https:','http:','#','mailto:')):continue
 p=(report.parent/href).resolve()
 if not p.is_file():bad.append(href)
assert not bad,bad
for href in re.findall(r'(?:href|src)="([^"]+)"',(r/'gallery.html').read_text()):
 if href.startswith(('http:','https:','#','data:')):continue
 assert (r/html.unescape(href)).is_file(),href
# All main report/gallery file links must also be included in the ZIP.
for href in links:
 if href.startswith(('https:','http:','#','mailto:')):continue
 p=(report.parent/href).resolve().relative_to(root);assert p in files,(href,p)
manifest=[{'file':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(files)]
(r/'raw/review-package-manifest.json').write_text(json.dumps(manifest,indent=2));files.add(r/'raw/review-package-manifest.json')
readme='''Gullyverse — Stage 2B geometry correction review\n\nOpen reports/stage-2b-wall-geometry-correction-2026-10-12/gallery.html locally.\nRead docs/gullyverse-stage-2b-wall-geometry-correction.md.\nAll final screenshots, metadata, recordings, raw results and final Blender source/exports are included.\nThe original candidate/locked source maps and a recoverable source/asset backup are included.\nIntermediate trial screenshots are preserved under trials and are not final acceptance evidence.\nThe source/export directory README gives Blender 4.3.2 reproduction commands.\nA base Breeze-2027 checkout and its dependencies are required to run the website; this is an offline review/asset-authoring package, not an application deployment.\nNo credentials or environment files are packaged. No commit, push or deployment occurred.\nVisual approval and physical-GPU profiling remain pending.\n'''
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 z.writestr('REVIEW-README.txt',readme)
 for p in sorted(files):z.write(p,str(p))
with zipfile.ZipFile(target)as z:assert z.testzip()is None
result={'file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':len(files)+1,'CRC':'PASS','mainReportAndGalleryLinks':'PASS','credentialsEnvironmentFiles':'excluded'}
(r/'raw/review-package-validation.json').write_text(json.dumps(result,indent=2));print(result)
