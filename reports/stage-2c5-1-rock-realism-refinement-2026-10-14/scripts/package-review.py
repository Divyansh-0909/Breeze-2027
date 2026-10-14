"""Credential-free self-contained review ZIP, with link/integrity verification."""
from pathlib import Path
import json,zipfile,hashlib,re
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-1-rock-realism-refinement-2026-10-14'
report=ROOT/'docs/gullyverse-stage-2c5-1-rock-realism-refinement.md'
zip_path=ROOT/'gullyverse-stage-2c5-1-rock-realism-refinement-review.zip'
files={report}
for directory in['before','after','diagnostics','raw','scripts','source-before','source-after']:
    files.update(p for p in(OUT/directory).rglob('*')if p.is_file()and'__pycache__'not in p.parts)
files.update([OUT/'gallery.html',OUT/'screenshot-metadata.json',OUT/'trials/build-artifact-naming.log'])
for name in['visitor-walk-and-aerial.mp4','near-wall-inspection.mp4','map-ascent.png','map-descent.png']:
    files.add(OUT/'recordings'/name)
for directory in['assets-source/gullyverse/quarry-foundation-refined','public/models/gullyverse/quarry-foundation-refined']:
    files.update(p for p in(ROOT/directory).rglob('*')if p.is_file()and p.suffix!='.blend1')
for name in['source-provenance.json','material-manifest.json','licensed-source/polyhaven-license.html']:
    files.add(ROOT/'assets-source/gullyverse/quarry-foundation'/name)
for name in['foundation-geometry.glb','foundation-materials.glb','foundation-lod0.glb','manifest.json']:
    files.add(ROOT/'public/models/gullyverse/quarry-foundation'/name)
files.add(ROOT/'assets-source/gullyverse/quarry-foundation/quarry-foundation.blend')
files.update(p for p in(ROOT/'assets-source/gullyverse/quarry-foundation/textures').rglob('*')if p.is_file())
# Original licensed inputs and metadata preserve reproducible provenance.
files.update(p for p in(ROOT/'assets-source/gullyverse/quarry-foundation/licensed-source').rglob('*')if p.is_file())
for name in['foundation_geometry.py','limestone_excavation_geometry.py','refined_foundation_geometry.py','refined_foundation_terrain_material.py','author_refined_quarry_foundation.py']:
    files.add(ROOT/'scripts/blender'/name)
for name in['ImmersiveShell.tsx','QuarryFoundationSession.ts']:
    files.add(ROOT/'components/immersive'/name)
files.add(ROOT/'tests/immersive/quarry-foundation-refinement.test.ts')
files.add(ROOT/'public/models/gullyverse/blockout.layout.json')
files.add(ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json')
files.add(ROOT/'design/references/03-open-roof-quarry/quarry-open-sky-geometry.jpeg')
files.add(ROOT/'design/references/03-open-roof-quarry/quarry-warm-dappled-light.jpeg')
files={p for p in files if p.name not in['package-verification.json','package-files.json','package.log']}
for p in files:
    assert p.exists(),p
    assert not any(part.startswith('.env')or part in['.git','node_modules','.next','secrets','credentials','backup']for part in p.relative_to(ROOT).parts),p
    assert p.suffix not in['.webm','.zip'],p
links=[]
for target in re.findall(r'\]\(([^)]+)\)',report.read_text()):
    if target.startswith(('http:','https:','#')):continue
    path=(report.parent/target.split('#')[0]).resolve();assert path.exists(),('missing report link',target)
    assert path in files,('report link absent from package',target)
    links.append(target)
# Gallery references all final PNGs and phone-playable videos.
for target in re.findall(r'(?:src|href)="([^"]+)"',(OUT/'gallery.html').read_text()):
    if target.startswith(('http:','https:','#')):continue
    path=(OUT/target).resolve();assert path in files,('gallery artifact absent',target)
inventory=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(files)]
start='''GULLYVERSE STAGE2C.5.1 — REVIEW PACKAGE

Open reports/stage-2c5-1-rock-realism-refinement-2026-10-14/gallery.html.
For iPhone Files/Quick Look, individual before/after PNGs are provided directly.
Recordings are H.264 MP4; software-renderer pauses are preserved.
Read docs/gullyverse-stage-2c5-1-rock-realism-refinement.md.
Source master: assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend.
Runtime GLBs: public/models/gullyverse/quarry-foundation-refined/.

Production/default website unchanged. Candidate requires opt-in preview.
Close wall recordings are explicitly labeled inspection cameras. Physical GPU/
mobile performance is unverified. No photorealistic/final-art approval claimed.
No credentials, user data, full-site backups or unrelated source are packaged.
'''
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    z.writestr('START-HERE.txt',start);z.writestr('package-files.json',json.dumps(inventory,indent=2))
    for p in sorted(files):z.write(p,str(p.relative_to(ROOT)))
with zipfile.ZipFile(zip_path)as z:
    assert z.testzip()is None
    count=len(z.infolist())
result={'status':'PASS','zip':zip_path.name,'bytes':zip_path.stat().st_size,
 'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'entries':count,
 'reportLinksVerified':len(links),'pngFilesIncludingPBR':len([p for p in files if p.suffix=='.png']),
 'screenshotRecords':len(json.loads((OUT/'screenshot-metadata.json').read_text())),
 'archiveIntegrity':'PASS','credentialsExcluded':True,'snapshotExcluded':True}
(OUT/'raw/package-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
