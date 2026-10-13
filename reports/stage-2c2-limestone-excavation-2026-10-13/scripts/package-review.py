from pathlib import Path
import hashlib,json,zipfile,re

PROJECT=Path.cwd();ROOT=PROJECT/'reports/stage-2c2-limestone-excavation-2026-10-13'
TARGET=PROJECT/'gullyverse-stage-2c2-limestone-excavation-review.zip'
files={}
def add(p):
    p=Path(p)
    if p.is_file():files[str(p.relative_to(PROJECT))]=p
for folder in['before','macro','after','reference','lod','recordings','diagnostics','raw','scripts']:
    for p in(ROOT/folder).rglob('*'):
        if p.is_file()and p.suffix not in['.pyc']and'__pycache__'not in p.parts:add(p)
add(ROOT/'gallery.html');add(PROJECT/'docs/gullyverse-stage-2c2-limestone-excavation.md')
for folder in['assets-source/gullyverse/limestone-excavation','public/models/gullyverse/limestone-excavation']:
    for p in(PROJECT/folder).glob('*'):
        if p.is_file()and p.suffix in['.blend','.glb','.json','.md']:add(p)
for name in[
 'assets-source/gullyverse/limestone-grey-pilot/quarry-grey-limestone-pilot.blend',
 'assets-source/gullyverse/limestone-grey-pilot/asset-manifest.json',
 'public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb',
 'public/models/gullyverse/quarry-rollout/quarry-limestone.glb',
 'assets-source/gullyverse/quarry-rollout/source-topology.json',
 'public/models/gullyverse/blockout.layout.json',
 'components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx',
 'components/immersive/LimestoneExcavationSession.ts','components/immersive/wallSection.ts',
 'scripts/blender/limestone_excavation_geometry.py','scripts/blender/author_limestone_excavation.py',
 'scripts/blender/pack_limestone_excavation.py','tests/immersive/limestone-excavation.test.ts',
]:add(PROJECT/name)
assert not any('/backup/'in p or '/trials/'in p or '.env'in Path(p).name for p in files)
report=PROJECT/'docs/gullyverse-stage-2c2-limestone-excavation.md'
for ref in re.findall(r'\]\(([^)]+)\)',report.read_text()):
    target=(report.parent/ref).resolve()
    assert str(target.relative_to(PROJECT))in files,ref
manifest={'scope':'Stage2C2 self-contained visual/technical review; no secrets, broad baseline backup or unrelated application data',
          'files':[{'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for name,p in sorted(files.items())]}
readme='''GULLYVERSE STAGE2C.2 REVIEW

Open reports/stage-2c2-limestone-excavation-2026-10-13/gallery.html for the visual
gallery, or inspect the original PNG files in before/macro/after directly.
The MP4 walkthrough opens in iPhone Files/Photos as well as desktop players.
Report: docs/gullyverse-stage-2c2-limestone-excavation.md
Editable sources: assets-source/gullyverse/limestone-excavation/*.blend
Runtime exports: public/models/gullyverse/limestone-excavation/

This package contains the current macro + three detailed examples. Production
default remains unchanged. Hardware GPU/mobile acceptance is pending.
Blender sources are for desktop authoring, not native iPhone model editing.

The original Grey pilot and source-topology/layout inputs are included so the
author/export scripts can reproduce this candidate. App fragments are review
context, not an entire independently runnable website. Full repository is
required to run the browser journey tests. Install the pinned Khronos validator
in an isolated tools directory as described by the source workflow.

No commit, push, deployment or full-quarry detail rollout was performed.
'''
with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as archive:
    for name,p in sorted(files.items()):archive.write(p,name)
    archive.writestr('REVIEW-MANIFEST.json',json.dumps(manifest,indent=2))
    archive.writestr('START-HERE.txt',readme)
with zipfile.ZipFile(TARGET)as archive:
    assert archive.testzip()is None
    for row in manifest['files']:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest()==row['sha256'],row['path']
result={'status':'PASS','zip':str(TARGET),'bytes':TARGET.stat().st_size,
        'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'entries':len(files)+2,
        'allReportLinksResolveInArchive':True,'CRCAndAllFileHashes':'PASS'}
(ROOT/'raw/package-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
