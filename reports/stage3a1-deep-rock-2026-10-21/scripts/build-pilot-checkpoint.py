"""Immutable diagnostic checkpoint over the verified Stage3A parent."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,shutil,datetime
ROOT=Path.cwd();R=ROOT/'reports/stage3a1-deep-rock-2026-10-21';W=Path('/workspace/stage3a1/2026-10-21/checkpoint');P=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint');BASE=P/'final-restoration-test/project';W.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
start=json.loads((R/'raw/starting-state.json').read_text());package=json.loads((R/'review-package.json').read_text());parent=json.loads((P/'checkpoint-index.json').read_text())
assert json.loads((R/'raw/preservation.json').read_text())['status']=='PASS'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==start['HEAD']
required=['gallery.html',package['phonePDF'],package['fullScreenshotPDF'],package['technicalPDF'],'technical-report.md']
for n in required:assert(R/n).is_file(),n
names=set(subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z']).decode().split('\0'))-{''};names.update(r['path']for r in start['files']);names.add(package['report'])
for folder in [ROOT/'assets-source/gullyverse/c9-cave-deep-relief',ROOT/'public/models/gullyverse/c9-cave-deep-relief',R]:names.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
files=[];same=[];overlay=[];excluded=[]
for rel in sorted(names):
 p=ROOT/rel
 if not p.is_file():continue
 if any(x in p.parts for x in ['node_modules','.next','.git','__pycache__','.authoring-cache','.pdf-cache','test-results','playwright-report'])or(p.name.startswith('.env')and p.name not in ['.env.example','.env.sample'])or p.name.endswith(('.blend1','.blend2','.pyc','.tsbuildinfo'))or p.suffix=='.zip':excluded.append(rel);continue
 assert not p.is_symlink(),rel
 row={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)};files.append(dict(row));before=sha(BASE/rel)if(BASE/rel).is_file()else None
 if row['sha256']==before:same.append(dict(row));continue
 row['beforeSHA256']=before
 if rel.startswith(('assets-source/gullyverse/c9-cave-deep-relief/','public/models/gullyverse/c9-cave-deep-relief/')):group='B'
 elif p.is_relative_to(R):
  item=p.relative_to(R).parts[0]
  group='A'if item=='scripts'else'C'if item in ['screenshots','videos']or p.suffix in ['.pdf','.html']else'D'
 else:group='A'
 row['group']=group;overlay.append(row)
protected=['public/models/gullyverse/blockout.layout.json','public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb','public/models/gullyverse/quarry-foundation-refined/foundation-materials.glb','public/models/gullyverse/recovered-c8-material/scanned-materials.glb','public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb','public/models/gullyverse/quarry-fidelity-correction/fidelity-bake.glb','public/models/gullyverse/c9-cave-recovery/cave-entrance.glb','public/models/gullyverse/c9-cave-recovery/entry-clearance.glb','assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend','package-lock.json']
chunks=[]
for group in 'ABCD':
 part=[];size=0;parts=[]
 for row in [r for r in overlay if r['group']==group]:
  if part and size+row['bytes']>64*1024*1024:parts.append(part);part=[];size=0
  part.append(row);size+=row['bytes']
 if part:parts.append(part)
 for i,part in enumerate(parts):
  name='Gullyverse-Stage3A1-PILOT-'+group+str(i+1)+'-'+{'A':'source','B':'editable-art-runtime','C':'review','D':'evidence'}[group]+'.zip';chunks.append((name,part))
  for row in part:row['archive']=name
manifest={'version':'STAGE3A1_FAILED_PILOT_DIAGNOSTIC','handoffID':package['handoffID'],'branch':start['branch'],'HEAD':start['HEAD'],'files':overlay,'protectedParentFiles':[{'path':p,'sha256':sha(BASE/p)}for p in protected]};(W/'pilot-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(W/'complete-current-tree.json').write_text(json.dumps({'files':files,'sameAsStage3AParent':same,'excluded':excluded},indent=2)+'\n')
deps={'requiredParentFolder':'https://drive.google.com/drive/folders/1zDrBmlXW1x8NQzgq022jNqS2JrDFdKej','parentHandoff':'STAGE3A-20261021T052321Z-1aa3fd6a','parentCheckpointIndexSHA256':sha(P/'checkpoint-index.json'),'parentIndex':parent,'parentReceiptSHA256':sha(P/'DRIVE-BACKUP-RECEIPT.json'),'note':'Restore every FINAL Stage3A archive and its complete acceptedC9/Phase1/2/3 dependency chain first, with authentic LFS payloads, stage/media and CC0 originals. This pilot is an incremental overlay; it is NOT a stand-alone replacement for those protected checkpoints.'};(W/'DEPENDENCIES.json').write_text(json.dumps(deps,indent=2)+'\n')
shutil.copy2(R/'scripts/apply-pilot-checkpoint.py',W/'apply-pilot-checkpoint.py')
readme='''# Restore the Stage3A.1 diagnostic pilot

NO-GO. Do not promote or extend the geometry. This checkpoint preserves a FAILED short pilot, the safe tunnel sampler implementation and its evidence; it does not claim a completed42m tunnel/entrance overhaul.

1. In a NEW directory restore the complete FINAL Stage3A parent (https://drive.google.com/drive/folders/1zDrBmlXW1x8NQzgq022jNqS2JrDFdKej), including its accepted-C9 and Phase1/2/3 chain. DEPENDENCIES.json contains exact parent indexes/archive hashes. Real LFS Blender masters, original stage/media and licensed scan payloads are required; pointers alone are insufficient. Earlier WORKING ZIPs are not required.
2. Download ALL ZIPs listed in checkpoint-index.json, pilot-file-manifest.json, complete-current-tree.json, DEPENDENCIES.json, SHA256SUMS.txt, this README, apply-pilot-checkpoint.py and the final DRIVE-BACKUP-RECEIPT.json. Keep prior checkpoints unchanged.
3. Verify sha256sum -c SHA256SUMS.txt (macOS shasum -a256 -c SHA256SUMS.txt). Extract every ZIP into the SAME new EMPTY overlay directory. They are independent ZIPs, not binary split parts. Merge the project/ trees. Do not concatenate ZIPs.
4. Run python3 apply-pilot-checkpoint.py --base /path/to/restored-stage3a/project --overlay /path/to/extracted-overlay. It checks source hashes and every conflict BEFORE writing, refuses changed user files and uses atomic replacements so hard-linked parent copies remain unchanged. Reapplication is idempotent.
5. complete-current-tree.json inventories the entire required project including inherited user work. Verify every file, not only new assets. Exclusions are credentials/private.env, dependencies/build output/caches and redundant archives/autosaves. Those excluded files were not deleted from the live project.

Use npm ci with the preserved lockfile. Supply private backend configuration separately; validation used explicitly invalid non-secret Supabase placeholders, which do not prove live services.
Build with NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1 NEXT_PUBLIC_GULLYVERSE_INSPECTION=1 npm run build, then npm run start.
Original Stage3A: /?diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave
FAILED PILOT ONLY: /?diagnostics&quarryReview=geology-fidelity&entranceReview=deep-rock
Quarry-only acceptedC9: /?diagnostics&quarryReview=geology-fidelity
Ordinary URLs remain publicC5.1. Review flags are development selectors, not an authentication barrier or permission to publish.

Master assets-source/gullyverse/c9-cave-deep-relief/cave-deep-pilot.blend opens with packed supporting images. Its embedded contract is pre-validation. Current manifest.json and VALIDATION-STATUS.json identify the final failed gate. The separate authoring.blend preserves the pre-unwrap source. True native source triangles remain editable at uniform1.0scale. Do not regenerate protected originals.

Open project/reports/stage3a1-deep-rock-2026-10-21/gallery.html. Full PNGs and phone/full/technical PDFs, browser videos, raw performance/regression results and failed geometry/Blender attempt logs are retained. The failure must not be concealed with DoubleSide, relaxed tolerances, illumination or another noise pass.

The final loose restore-verification.json records a clean independent restore; DRIVE-BACKUP-RECEIPT.json records full remote download-back hash/size/parent validation. This README does not itself certify external backup. Check the verified receipt and save copies outside Codex.
''';(W/'RESTORE-STAGE3A1-PILOT.md').write_text(readme)
archive_rows=[]
for name,part in chunks:
 p=W/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for row in part:z.write(ROOT/row['path'],'project/'+row['path'])
  for meta in ['pilot-file-manifest.json','complete-current-tree.json','DEPENDENCIES.json','RESTORE-STAGE3A1-PILOT.md','apply-pilot-checkpoint.py']:z.write(W/meta,meta)
 archive_rows.append({'name':name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(part)})
index={'handoffID':package['handoffID'],'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FAILED_PRIVATE_PILOT_PRESERVED','requiredParent':deps['requiredParentFolder'],'archives':archive_rows,'requiredCurrentFiles':len(files),'overlayFiles':len(overlay),'sameParentFiles':len(same),'sourceBlenderAndRuntimeIncluded':True,'externalVerification':'CONSULT_FINAL_RECEIPT','independentRestore':'CONSULT_RESTORE_VERIFICATION'};(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2)+'\n')
sums=[]
for name in sorted([r['name']for r in archive_rows]+['pilot-file-manifest.json','complete-current-tree.json','DEPENDENCIES.json','RESTORE-STAGE3A1-PILOT.md','apply-pilot-checkpoint.py','checkpoint-index.json']):
 p=W/name;sums.append(sha(p)+'  '+p.name)
(W/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n');print(json.dumps(index,indent=2))
