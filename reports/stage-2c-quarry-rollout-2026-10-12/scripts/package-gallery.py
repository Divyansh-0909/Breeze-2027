from pathlib import Path
import json,zipfile
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'reports/stage-2c-quarry-rollout-2026-10-12'
target=ROOT/'gullyverse-stage-2c-comparison-gallery.zip'
gallery=(R/'gallery.html').read_text().replace('<a href="../../docs/gullyverse-stage-2c-full-quarry-rollout.md">Implementation report</a>','<span>Implementation report supplied separately.</span>')
files=[p for d in ['before','after']for p in (R/d).glob('*.png')if not p.name.startswith('quick-')]
raw=['before-captures.json','after-captures.json','capture-comparison-metadata.json','before-performance.json','after-performance.json','hardware-profile.json','asset-inventory.json','test-summary.json','lifecycle.json','navigation-cycles.json','video-with-wall.json','recovery.json','network.json','material-lock-validation.json','perimeter-coverage.json','glTF-validator.json','shape-validation.json','exported-topology-validation.json','loading-access-before.png','loading-access-after.png','loading-access-before.json','loading-access-after.json']
assert len(files)==28
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 z.writestr('index.html',gallery)
 z.writestr('README.md','# Gullyverse Stage 2C comparison gallery\n\nOpen index.html. Contains 28 original quarry PNGs in 14 matched before/after pairs, two delayed-loading access captures, camera/quality metadata and measured runtime evidence. The implementation report, editable Blender source and GLBs are delivered separately in the project. No credentials or unrelated application data are included. Physical GPU/mobile acceptance is pending.\n')
 for p in files:z.write(p,str(p.relative_to(R)))
 for name in raw:z.write(R/'raw'/name,'raw/'+name)
with zipfile.ZipFile(target)as z:
 assert z.testzip()is None
 count=len(z.namelist())
(R/'raw/gallery-package.json').write_text(json.dumps({'file':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'entries':count,'quarryScreenshots':28,'loadingAccessScreenshots':2,'integrity':'PASS','includesCredentials':False},indent=2))
print('Created',target.name,target.stat().st_size,'bytes;',count,'entries, integrity PASS.')
