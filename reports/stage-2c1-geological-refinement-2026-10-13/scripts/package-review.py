from pathlib import Path
import zipfile,json,hashlib,re
root=Path.cwd();r=root/'reports/stage-2c1-geological-refinement-2026-10-13';out=root/'gullyverse-stage-2c1-geological-refinement-review.zip';files=[]
report=root/'docs/gullyverse-stage-2c1-geological-refinement.md';files.append(report)
for folder in ['before','after','diagnostics','lod','recordings','raw','scripts']:
 files.extend(p for p in (r/folder).rglob('*')if p.is_file()and '__pycache__'not in p.parts)
files.append(r/'gallery.html')
# Retain failed evidence relevant to claimed corrections, not unrelated backups.
for folder in ['decimation-boundary-failure','sparse-closure-failure','recording-missed-distant-lod']:
 files.extend(p for p in (r/'trials'/folder).rglob('*')if p.is_file())
for folder in ['public/models/gullyverse/quarry-refinement']:
 files.extend(p for p in (root/folder).rglob('*')if p.is_file())
for name in ['assets-source/gullyverse/quarry-refinement/refined-limestone-pair.blend','assets-source/gullyverse/quarry-refinement/README.md','assets-source/gullyverse/quarry-refinement/manifest.json','assets-source/gullyverse/quarry-rollout/source-topology.json','public/models/gullyverse/quarry-rollout/quarry-limestone.glb','scripts/blender/quantize_quarry_attributes.py','scripts/blender/refined_quarry_geology.py','scripts/blender/author_refined_quarry_pair.py','scripts/blender/prepare_refined_pair.py','scripts/blender/pack_refined_quarry.py','components/immersive/RefinedQuarrySession.ts','components/immersive/QuarryPerimeter.tsx','components/immersive/wallSection.ts','components/immersive/ImmersiveShell.tsx','tests/immersive/quarry-refinement.test.ts']:
 files.append(root/name)
files=[p for p in dict.fromkeys(files)if p.name!='package-validation.json'];assert all(p.exists()for p in files)
# Every report's clickable local target resolves in the package. The recoverable
# broad backup is deliberately workspace-only plain text, not a broken ZIP link.
selected={str(p.relative_to(root))for p in files};missing=[]
for target in re.findall(r'\]\(([^)]+)\)',report.read_text()):
 if target.startswith(('https://','http://','#')):continue
 full=(report.parent/target).resolve();rel=str(full.relative_to(root))
 if rel not in selected:missing.append(rel)
assert not missing,missing
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,str(p.relative_to(root)))
 z.writestr('REVIEW-MANIFEST.json',json.dumps({'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]},indent=2))
 z.writestr('README.txt','Open docs/gullyverse-stage-2c1-geological-refinement.md or reports/'+r.name+'/gallery.html. All screenshots are real browser captures. Source master and runtime exports are included. The original Stage2C GLB is unchanged. This ZIP excludes credentials, environment files, the broad worktree backup and unrelated application data. Source reproduction needs Blender4.3.2, Python NumPy/SciPy and the existing Node validation dependencies; it is not a full website deployment.\n')
with zipfile.ZipFile(out)as z:assert z.testzip()is None
metadata={'zip':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files)+2,'reportLinksResolved':True,'crcValidation':'PASS','gallery':str((r/'gallery.html').relative_to(root))}
(r/'raw/package-validation.json').write_text(json.dumps(metadata,indent=2));print(metadata)
