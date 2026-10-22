"""Freeze an incremental, conflict-checked Phase3 checkpoint. Never overwrites
archives; requires final reports/evidence. Run only after the browser cohort.
"""
from pathlib import Path
import json,hashlib,zipfile,shutil
ROOT=Path.cwd();R=ROOT/'reports/recovery-phase3-c9-2026-10-19';W=Path('/workspace/recovery-phase3/2026-10-19/checkpoint');W.mkdir(parents=True,exist_ok=True)
def sha(path):
 with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
start={r['path']:r for r in json.loads((R/'raw/starting-hashes.json').read_text())}
files={ROOT/name for name in ['components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx','components/immersive/scannedRockSampling.ts','components/immersive/ScannedCompositionSession.ts','tests/immersive/scanned-composition.test.ts','scripts/blender/recover_c9_source.py','scripts/blender/author_recovered_c9.py','scripts/blender/bake_recovered_c9.py','docs/gullyverse-recovery-phase3-c9-composition.md']}
for directory in ['assets-source/gullyverse/quarry-scanned-composition','public/models/gullyverse/recovered-c9-composition',str(R.relative_to(ROOT))]:
 for path in (ROOT/directory).rglob('*'):
  rel=path.relative_to(ROOT)
  if not path.is_file()or any(p in ['.authoring-cache','.pdf-cache','__pycache__']for p in rel.parts)or path.name.endswith(('.blend1','.blend2')):continue
  files.add(path)
for needed in [R/'gallery.html',R/'review-package.json',R/'videos/visitor-journey.mp4',R/'videos/automatic-lod-inspection.mp4',R/'raw/matched-performance.json',R/'raw/composition-browser-checks.json']:
 assert needed in files and needed.is_file(),str(needed)
rows=[];groups={c:[]for c in 'ABCD'}
for path in sorted(files):
 rel=str(path.relative_to(ROOT));assert not path.name.startswith('.env')and '/node_modules/'not in rel and '/.next/'not in rel
 if '/licensed-source/'in rel:group='B'
 elif path.is_relative_to(R):
  part=path.relative_to(R).parts[0]
  group='A'if part=='scripts'else'C'if part in ['screenshots','references','videos']or path.suffix in ['.pdf','.html']or path.name in ['matched-pose-verification.json','review-package.json']else'D'
 else:group='A'
 row={'path':rel,'bytes':path.stat().st_size,'sha256':sha(path),'beforeSHA256':start.get(rel,{}).get('sha256'),'group':group};rows.append(row);groups[group].append(row)
# Cap raw members conservatively below Drive's 100MiB upload limit. Each ZIP is
# independently extractable; review parts merge into one project/ tree.
archives=[];chunks=[]
for group in groups:
 parts=[];part=[];size=0
 for row in groups[group]:
  if part and size+row['bytes']>82*1024*1024:parts.append(part);part=[];size=0
  part.append(row);size+=row['bytes']
 if part:parts.append(part)
 for i,part in enumerate(parts):
  suffix=group+(str(i+1)if len(parts)>1 else'');label={'A':'code-master-runtime','B':'licensed-originals','C':'review-gallery','D':'technical-evidence'}[group]
  name=f'Gullyverse-Recovery-Phase3-C9-{suffix}-{label}.zip'
  for row in part:row['archive']=name
  chunks.append((name,group,part))
required=['public/models/gullyverse/blockout.layout.json','public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb','public/models/gullyverse/quarry-foundation-refined/foundation-materials.glb','public/models/gullyverse/quarry-foundation-refined/manifest.json','public/models/gullyverse/recovered-c8-material/scanned-materials.glb','public/models/gullyverse/recovered-c8-material/manifest.json','assets-source/gullyverse/recovered-c8-material/recovered-c8-material.blend','assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend','assets-source/gullyverse/quarry-foundation/quarry-foundation.blend','assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend','components/immersive/QuarryFoundationSession.ts','components/immersive/ScannedRockMaterialSession.ts','package.json','package-lock.json']
manifest={'version':'Recovery-Phase3-C9','branch':'codex/navigation-board','HEAD':'14f36da1a9b79a3b4926f7445bf0cde6c6c8f767','requiredBaselineFiles':[{'path':p,'sha256':start[p]['sha256']}for p in required],'files':rows}
(W/'phase3-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p1=json.loads(Path('/workspace/recovery-phase2/2026-10-19/checkpoint/PHASE1-DEPENDENCY.json').read_text());p2=json.loads(Path('/workspace/recovery-phase2/2026-10-19/checkpoint/checkpoint-index.json').read_text())
dependency={'phase1':p1,'phase2':{'folder':'https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-','checkpointIndexSHA256':sha(Path('/workspace/recovery-phase2/2026-10-19/checkpoint/checkpoint-index.json')),'archives':p2['archives'],'externalReceiptSHA256':sha(Path('/workspace/recovery-phase2/2026-10-19/checkpoint/DRIVE-BACKUP-RECEIPT.json'))},'historicalEvidence':{'folder':'https://drive.google.com/drive/folders/1LsbsSDSiZZ8qai0MuB-_cTReU5cj8Bk6','C8':{'id':'1YJplmjx7cBGrRg-8D4Sz1_bLz5AeVmOu','sha256':'e9b67adf3ab5656fdec7599ab56e33218d3202c36feec07cbc051faf812a5815'},'C9':{'id':'12xi4iOo887gOc5yUembJN9r5RE3P0Dim','sha256':'24d37c280844e7f5a30fef700f205955255d5323ddb564286dfefd370af664eb'}},'note':'Restore actual Phase1 LFS/stage/media payloads, then all Phase2 archives, before Phase3. Historical packages remain protected externally and are not redundantly repackaged. Phase3 includes original licensed new scan/maps, full packed master and runtime; it is not a Git-bundle-only backup.'}
(W/'DEPENDENCIES.json').write_text(json.dumps(dependency,indent=2)+'\n');shutil.copyfile(R/'scripts/apply-phase3.py',W/'apply-phase3.py')
readme='''# Restore Recovery Phase3 — selected C9

This is an incremental source/asset checkpoint on protected Phase1 + Phase2, branch codex/navigation-board, HEAD14f36da1a9b79a3b4926f7445bf0cde6c6c8f767. It is not a complete website by itself.

Phase1: https://drive.google.com/drive/folders/1OdGXZvpfHCdYpWesgya3x_lTupKsB_HI
Phase2: https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-
New Phase3: https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A

1. Restore Phase1 into a NEW directory using its index, binary-part reassembler and original SHA manifests. Its actual LFS payloads, stage and media are required. Apply the Phase1 backup-policy addendum.
2. Restore ALL FOUR Phase2 ZIPs with its apply-phase2.py and exact baseline checks. Do not reset/clean an existing user checkout. DEPENDENCIES.json identifies every required previous archive and checksum.
3. Download EVERY Phase3 archive listed in checkpoint-index.json, plus SHA256SUMS.txt, phase3-file-manifest.json, this README, DEPENDENCIES.json and apply-phase3.py. Verify sha256sum -c SHA256SUMS.txt (macOS: shasum -a256 -c SHA256SUMS.txt). Each labelled ZIP is standalone under100MiB; no binary reassembly is required. Review parts still must be extracted together.
4. Extract all Phase3 ZIPs into one SEPARATE EMPTY overlay directory. Their project/ children merge. Do not extract straight over user work.
5. From that overlay run: python3 apply-phase3.py --base /path/to/restored-phase2/project
   Windows may use py. Preflight checks all payloads and baseline hashes before any write, rejects unrelated source changes/symlinks, uses atomic replacements, verifies every final file, and is idempotent. A conflict stops recovery for inspection; it is not permission to reset or overwrite it.
6. Keep these archives, checksums and the final Drive download-back verification receipt outside Codex too. The Drive backup is established only by complete byte/hash verification, not by an upload-success message.

## Run the private candidate

Use npm ci with the existing package-lock.json. Supply normal backend environment separately; credentials/live.env are excluded. Build with NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1 NEXT_PUBLIC_GULLYVERSE_INSPECTION=1 npm run build, then npm run start. The verification build used clearly non-secret local Supabase placeholders; this is not backend-service certification.

Open /?arrival=hub&diagnostics&quarryReview=scanned-composition. Native geometry0.9× and C8 material3× are locked. The private C8 comparison remains scanned-material-multi; ordinary URLs remain public C5.1. No public promotion/deployment is authorized. The preview gate is configuration, not authentication.

## Editable art / reproducibility

The final quarry-scanned-composition.blend packs its required source images and includes native licensed meshes, cropped high geometry, optimized LODs and baked normal. Authentic provider originals/maps and API/license provenance are included separately. Restoring shipped files needs no new scan download or Blender execution.

To reproduce the method with Blender4.3.2: run recover_c9_source.py, then author_recovered_c9.py, then bake_recovered_c9.py from scripts/blender/. The first downloads authentic sources only when needed; actual preserved sources are already supplied. The authoring scripts use the surviving C5.1 GLB and Phase2 material/master; they do not recreate C6.2 stretching. Intermediate caches are regenerated. Cross-version decimator/bake bytes are not promised identical.

The technical report documents historical differences, seven inherited visibility hits, sample-based validation limits and pending physical hardware performance. Historical C8/C9 packages remain in their protected evidence folder with exact hashes in DEPENDENCIES.json; selected embedded PDF images/report text are included in the review. No Stage3A reconstruction is included.

## Review without starting the site

Extract ALL C-review parts together. Open REVIEW-START.html, or the gallery.html/phone/full PDFs under project/reports/recovery-phase3-c9-2026-10-19/. All current art evidence is actual-browser imagery, with original full-resolution PNGs and matched metadata. Video is software-rendered browser recording, not physical-device FPS.

For the next prompt give ChatGPT the WHOLE Phase3 folder link plus the two protected baseline links. Start with the technical report, checkpoint-index.json, DEPENDENCIES.json, SHA256SUMS.txt and final Drive receipt. Review the reconstructed C9 before requesting Stage3A.
'''
(W/'RESTORE-PHASE3.md').write_text(readme)
(W/'REVIEW-START.html').write_text('<!doctype html><meta name="viewport" content="width=device-width"><h1>BREEZE2027 / recovered C9</h1><p>Extract all C-review parts together.</p><p><a href="project/reports/recovery-phase3-c9-2026-10-19/gallery.html">Full-resolution gallery</a></p><p><a href="project/reports/recovery-phase3-c9-2026-10-19/Gullyverse-Recovery-Phase3-C9-Review.pdf">Phone review PDF</a></p>')
for name,group,part in chunks:
 p=W/name;assert not p.exists(),'Never overwrite a checkpoint archive'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for row in part:z.write(ROOT/row['path'],'project/'+row['path'])
  if group=='A':
   for n in ['phase3-file-manifest.json','DEPENDENCIES.json']:z.write(W/n,'recovery-phase3/'+n)
   for n in ['RESTORE-PHASE3.md','apply-phase3.py']:z.write(W/n,n)
  if group=='C'and not any(a['group']=='C'for a in archives):z.write(W/'REVIEW-START.html','REVIEW-START.html')
 with zipfile.ZipFile(p)as z:assert z.testzip()is None;members=len(z.infolist())
 assert p.stat().st_size<100*1024*1024
 archives.append({'name':name,'group':group,'bytes':p.stat().st_size,'sha256':sha(p),'members':members})
index={'version':'Recovery-Phase3-C9','branch':manifest['branch'],'HEAD':manifest['HEAD'],'phase3Folder':'https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A','dependencies':dependency,'archives':archives,'projectFiles':len(rows),'projectBytes':sum(r['bytes']for r in rows),'perFileManifestSHA256':sha(W/'phase3-file-manifest.json'),'restore':'Apply Phase3 overlay to a separately restored Phase1+2 project. All C-review parts must be extracted together.','externalVerification':'See separate full download-back SHA-256 Drive receipt/completion index; upload success alone is insufficient.'}
(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2)+'\n');(W/'SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['name']+'\n'for r in archives))
print(json.dumps({'archives':archives,'projectFiles':len(rows),'projectBytes':index['projectBytes']},indent=2))
