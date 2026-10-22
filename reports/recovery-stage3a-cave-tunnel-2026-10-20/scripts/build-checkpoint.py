"""Create a fresh immutable final overlay on the verified complete parent.

Earlier working archives are preserved but are not prerequisites for this set.
The entire required current tree is inventoried, including surviving user work.
"""
from pathlib import Path
import hashlib,json,subprocess,zipfile,shutil,datetime

ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20';W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint');PARENT=Path('/workspace/recovery-fidelity/2026-10-19/checkpoint');BASE=PARENT/'restoration-test/project'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
package=json.loads((R/'review-package.json').read_text());start=json.loads((R/'raw/starting-state.json').read_text());previous=json.loads((PARENT/'checkpoint-index.json').read_text())
assert json.loads((R/'raw/preservation.json').read_text())['status']=='PASS'
for f in ['gallery.html',package['phonePDF'],package['fullScreenshotPDF'],package['technicalPDF'],'videos/visitor-journey.mp4','videos/automatic-lod-inspection.mp4']:assert(R/f).is_file(),f
names=set(subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z']).decode().split('\0'))-{''}
names.update(row['path']for row in start['files'])
# The repository ignores *.md. Required phase art direction and the new main
# report must be exported even though Git's untracked inventory hides them.
names.add('docs/gullyverse-stage-3a-c9-entrance-tunnel.md')
for folder in [ROOT/'assets-source/gullyverse/c9-cave-recovery',ROOT/'public/models/gullyverse/c9-cave-recovery',R]:
 names.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
excluded=[];current=[];overlay=[];same=[]
for rel in sorted(names):
 p=ROOT/rel
 if not p.is_file():continue
 reason=None
 if any(x in p.relative_to(ROOT).parts for x in ['.git','node_modules','.next','.authoring-cache','.pdf-cache','__pycache__','test-results','playwright-report']):reason='dependency/build/cache'
 if p.name.startswith('.env')and p.name not in ['.env.example','.env.sample']:reason='credentials/private environment excluded'
 if p.name.endswith(('.blend1','.blend2','.pyc','.tsbuildinfo')):reason='redundant automatic authoring/build cache'
 if p.suffix=='.zip':reason='redundant nested archive; checkpoints live outside project'
 if reason:excluded.append({'path':rel,'reason':reason});continue
 assert not p.is_symlink(),rel
 row={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)};current.append(row)
 before=sha(BASE/rel)if(BASE/rel).is_file()else None
 if row['sha256']==before:same.append(row);continue
 row.update(beforeSHA256=before)
 if rel.startswith(('assets-source/gullyverse/c9-cave-recovery/','public/models/gullyverse/c9-cave-recovery/')):g='B'
 elif p.is_relative_to(R):
  part=p.relative_to(R).parts[0]
  if part=='scripts':g='A'
  elif part in ['references','videos']or(part=='screenshots'and p.relative_to(R).parts[1]in ['review-before-desktop','review-before-mobile','review-after-desktop','review-after-mobile','diagnostics'])or p.suffix in ['.pdf','.html']or p.name in ['technical-report.md','review-package.json','comparison-index.json','matched-pose-verification.json']:g='C'
  else:g='D'
 else:g='A'if p.suffix in ['.tsx','.ts','.py','.mjs','.md','.json','.csv']or rel.startswith('scripts/')else'D'
 row['group']=g;overlay.append(row)
chunks=[]
for g in 'ABCD':
 part=[];size=0;parts=[]
 for row in (r for r in overlay if r['group']==g):
  if part and size+row['bytes']>82*1024*1024:parts.append(part);part=[];size=0
  part.append(row);size+=row['bytes']
 if part:parts.append(part)
 for i,part in enumerate(parts):
  suffix=g+(str(i+1)if len(parts)>1 else'')
  name=f'Gullyverse-Stage3A-FINAL-{suffix}-'+{'A':'source','B':'editable-art-runtime','C':'review-gallery','D':'technical-evidence'}[g]+'.zip'
  for row in part:row['archive']=name
  chunks.append((name,g,part))
protected=['public/models/gullyverse/blockout.layout.json','public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb','public/models/gullyverse/quarry-foundation-refined/foundation-materials.glb','public/models/gullyverse/recovered-c8-material/scanned-materials.glb','public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb','public/models/gullyverse/quarry-fidelity-correction/fidelity-bake.glb','assets-source/gullyverse/quarry-fidelity-correction/quarry-fidelity-correction.blend','assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend','package-lock.json']
manifest={'version':'STAGE3A_PRIVATE_CAVE_RECOVERY','handoffID':package['handoffID'],'branch':start['branch'],'HEAD':start['HEAD'],'requiredBaselineFiles':[{'path':p,'sha256':sha(BASE/p)}for p in protected],'files':overlay}
(W/'stage3a-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(W/'complete-current-tree.json').write_text(json.dumps({'files':current,'sameAsProtectedParent':same,'excluded':excluded},indent=2)+'\n')
dependencies={'requiredAcceptedQuarryCheckpoint':{'folder':previous['folder'],'checkpointIndexSHA256':sha(PARENT/'checkpoint-index.json'),'receiptSHA256':sha(PARENT/'DRIVE-BACKUP-RECEIPT.json'),'archives':previous['archives'],'dependencies':previous['dependencies']},'phase1Phase2Phase3Required':True,'note':'Restore the protected parent and its exact full prior chain first. This includes real LFS masters, original stage/media, both CC0 scan providers, approved C8 maps and selected C9 assets. Earlier report HOLD statements are historical; user approval on20October supersedes them. Never modify those protected backups. The two earlier Stage3A WORKING ZIPs are optional history, not part of the final restore set.'}
(W/'DEPENDENCIES.json').write_text(json.dumps(dependencies,indent=2)+'\n');shutil.copy2(R/'scripts/apply-stage3a.py',W/'apply-stage3a.py')
readme='''# Restore the FINAL Stage3A private cave candidate

No artwork is production-approved. Exact artist images remain pending. This checkpoint preserves selectedC9 and3×; publicC5.1 is unchanged. No commit, deployment or next phase.

## Required restore order
1. In a NEW directory restore the complete protected accepted-quarry checkpoint https://drive.google.com/drive/folders/1doGUar6hMGWhFuqn0jlkcG4sl2nE2MXw and its exact Phase1/2/3 chain. DEPENDENCIES.json records every required archive and hash. Include actual LFS/master/stage/media payloads. Git source or LFS pointers alone are insufficient.
2. From this folder download EVERY FINAL archive in checkpoint-index.json and the loose stage3a-file-manifest.json, complete-current-tree.json, DEPENDENCIES.json, SHA256SUMS.txt, this README, apply-stage3a.py and final DRIVE-BACKUP-RECEIPT.json. Earlier non-FINAL working ZIPs are optional historical snapshots; do not apply them on top of FINAL.
3. Verify sha256sum -c SHA256SUMS.txt (macOS: shasum -a256 -c SHA256SUMS.txt). Extract all FINAL ZIPs into one separate EMPTY overlay directory. ZIPs are independently extractable; do not concatenate them. All project/ trees merge. Extract all C-review parts together for the self-contained gallery.
4. From the overlay run python3 apply-stage3a.py --base /path/to/restored-quarry/project. All dependency and source hashes/conflicts are checked BEFORE any write. Atomic replacement avoids modifying hard-linked originals; reapplication is idempotent. Conflicting user work is refused, never reset.
5. complete-current-tree.json verifies the entire required current tree, including pre-task additions missing from the parent, not just this phase's new files. Exclusions are listed explicitly: credentials/.env, dependencies/build output, caches and redundant automatic Blender backups. They were not deleted from the live workspace.

## Run / preview
Use npm ci with the preserved lockfile. Supply private backend configuration separately. The verification build uses invalid non-secret Supabase placeholders; backend/payment acceptance is not implied.
Build with NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1 NEXT_PUBLIC_GULLYVERSE_INSPECTION=1 npm run build; start with npm run start.
Private cave: /?diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave
Selected quarry only: /?diagnostics&quarryReview=geology-fidelity
Original recovered C9: /?diagnostics&quarryReview=scanned-composition
Ordinary URLs remain publicC5.1. Preview flags are development selectors, not authentication or authorization to deploy.

## Source / evidence
The packed editable cave master is assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend. It contains native references, authored high mesh, runtime LODs and9packed source images. Source provenance and the protected parent identify the original CC0 scan files. scripts/blender/author_cave_recovery.py is the final reproduction entry with cave_scan_surface.py, cave_shared_frames.py and offline cave_mikktspace.mjs. clip_cave_entry_terrain.py reproduces the bounded private terrain overlay. Restoring shipped GLBs requires no regeneration; cross-version authoring bytes are not promised identical.
Open REVIEW-START.html, or project/reports/recovery-stage3a-cave-tunnel-2026-10-20/gallery.html after extracting every C part. Full-resolution images, phone/full screenshot/technical PDFs, exact camera metadata, actual-browser MP4/WebM and failed/final technical logs are retained.

## Limits and verification
The candidate is NOT production-ready. Smooth entrance collar, thin captured edges, regular vault/floor contacts and missing exact seven artworks remain. Seven inherited quarry visibility defects and physical-device acceptance remain unresolved. Raw browser deadline failures are retained. No lighting/layout/navigation/stage redesign occurred.
restore-verification.json proves independent restoration, unrelated-file preservation, conflict refusal and read-only Blender opening. DRIVE-BACKUP-RECEIPT.json proves actual full remote download-back SHA256/name/size/parent. Upload success alone is insufficient; consult the final verified receipt. Store these files outside Codex too.
'''
(W/'RESTORE-STAGE3A.md').write_text(readme)
(W/'REVIEW-START.html').write_text('<!doctype html><meta name="viewport" content="width=device-width"><h1>Stage3A private cave review</h1><p>Extract ALL FINAL C-review ZIPs together.</p><a href="project/reports/recovery-stage3a-cave-tunnel-2026-10-20/gallery.html">Open gallery, PDFs and browser videos</a>')
archives=[]
for name,g,part in chunks:
 p=W/name
 if p.exists():
  assert g=='B','Never overwrite a sealed checkpoint'
  sealed=json.loads((W/'B-final-assets.json').read_text());assert sealed['name']==name and sealed['sha256']==sha(p)
  assert {(r['path'],r['bytes'],r['sha256'])for r in part}=={(r['path'],r['bytes'],r['sha256'])for r in sealed['files']},'Final art changed after sealing'
 else:
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for row in part:z.write(ROOT/row['path'],'project/'+row['path'])
   if g=='A':
    for n in ['stage3a-file-manifest.json','complete-current-tree.json','DEPENDENCIES.json']:z.write(W/n,'recovery-stage3a/'+n)
    for n in ['RESTORE-STAGE3A.md','apply-stage3a.py']:z.write(W/n,n)
   if g=='C'and not any(a['group']=='C'for a in archives):z.write(W/'REVIEW-START.html','REVIEW-START.html')
 with zipfile.ZipFile(p)as z:assert z.testzip()is None;members=len(z.infolist())
 assert p.stat().st_size<100*1024*1024
 archives.append({'name':name,'group':g,'bytes':p.stat().st_size,'sha256':sha(p),'members':members,'parent_id':'1XkV6VnEIOAsmxVKxOpm9AbF_U0V_3VOf'if g=='C'else'1y-fLFkJthsB9gMOr5fZNseZXSg_2B24a'})
index={'version':manifest['version'],'handoffID':package['handoffID'],'branch':start['branch'],'HEAD':start['HEAD'],'folder':'https://drive.google.com/drive/folders/1y-fLFkJthsB9gMOr5fZNseZXSg_2B24a','dependencies':dependencies,'archives':archives,'projectOverlayFiles':len(overlay),'projectOverlayBytes':sum(r['bytes']for r in overlay),'completeCurrentRequiredFiles':len(current),'unchangedParentFiles':len(same),'perFileManifestSHA256':sha(W/'stage3a-file-manifest.json'),'wholeTreeManifestSHA256':sha(W/'complete-current-tree.json'),'excluded':excluded,'externalVerification':'Final separate DRIVE-BACKUP-RECEIPT.json; upload success alone is insufficient.'}
(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2)+'\n')
checksum_names=[a['name']for a in archives]+['stage3a-file-manifest.json','complete-current-tree.json','DEPENDENCIES.json','RESTORE-STAGE3A.md','apply-stage3a.py','REVIEW-START.html','checkpoint-index.json']
(W/'SHA256SUMS.txt').write_text(''.join(sha(W/n)+'  '+n+'\n'for n in checksum_names))
print(json.dumps({k:index[k]for k in ['archives','projectOverlayFiles','projectOverlayBytes','completeCurrentRequiredFiles','unchangedParentFiles']},indent=2))
