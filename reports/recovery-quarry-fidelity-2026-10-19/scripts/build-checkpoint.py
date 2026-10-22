"""Freeze a NEW incremental checkpoint; never overwrite prior archives."""
from pathlib import Path
import json,hashlib,zipfile,shutil
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19';W=Path('/workspace/recovery-fidelity/2026-10-19/checkpoint');W.mkdir(parents=True,exist_ok=True)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
start={x['path']:x for x in json.loads((R/'raw/starting-hashes.json').read_text())}
paths=['components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx','components/immersive/scannedRockSampling.ts','components/immersive/ScannedMaterialFidelitySession.ts','components/immersive/GeologyFidelitySession.ts','tests/immersive/quarry-fidelity.test.ts','docs/gullyverse-recovery-quarry-fidelity-correction.md']
paths+=['scripts/blender/'+s for s in ['author_quarry_fidelity.py','compose_quarry_fidelity_volume.py','bake_quarry_fidelity.py','fidelity_runtime_border.py','fidelity_mikktspace.mjs']]
files={ROOT/s for s in paths}
# Do not assume the old protected checkpoint contains every audited user file.
# Preserve any surviving pre-task work absent/different in its independent restore.
baseline=Path('/workspace/recovery-phase3/2026-10-19/checkpoint/restoration-test/project');baseline_hashes={};extra=[]
for rel,row in start.items():
 p=baseline/rel;digest=sha(p)if p.is_file()else None;baseline_hashes[rel]=digest
 if digest!=row['sha256']:
  files.add(ROOT/rel);extra.append({'path':rel,'protectedPhase3SHA256':digest,'auditedStartingSHA256':row['sha256']})
for directory in ['assets-source/gullyverse/quarry-fidelity-correction','public/models/gullyverse/quarry-fidelity-correction',str(R.relative_to(ROOT))]:
 for p in (ROOT/directory).rglob('*'):
  if not p.is_file()or any(x in p.parts for x in ['.authoring-cache','.pdf-cache','__pycache__'])or p.name.endswith(('.blend1','.blend2','.webm'))or p.suffix=='.zip':continue
  files.add(p)
for p in [R/'gallery.html',R/'review-package.json',R/'videos/visitor-journey.mp4',R/'videos/automatic-lod-inspection.mp4',R/'raw/matched-performance.json',R/'raw/composition-browser-checks.json',R/'raw/targeted-ray-cones.json']:
 assert p in files and p.is_file(),p
assert json.loads((R/'raw/fidelity-geometry-validation.json').read_text())['status']=='PASS'
assert json.loads((R/'raw/targeted-ray-cones.json').read_text())['status']=='PASS'
groups={k:[]for k in 'ABCD'};rows=[]
for p in sorted(files):
 rel=str(p.relative_to(ROOT));assert not p.name.startswith('.env')and '/node_modules/'not in rel and '/.next/'not in rel
 if '/licensed-source/'in rel:g='B'
 elif p.is_relative_to(R):
  part=p.relative_to(R).parts[0];g='A'if part=='scripts'else'C'if part in ['screenshots','references','videos','contact-sheets']or p.suffix in ['.pdf','.html']or p.name in ['matched-pose-verification.json','comparison-index.json','review-package.json','stage-fidelity-matrix.csv']else'D'
 else:g='A'
 row={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'beforeSHA256':baseline_hashes.get(rel),'auditedStartingSHA256':start.get(rel,{}).get('sha256'),'group':g};rows.append(row);groups[g].append(row)
chunks=[]
for g,items in groups.items():
 parts=[];part=[];size=0
 for row in items:
  if part and size+row['bytes']>82*1024*1024:parts.append(part);part=[];size=0
  part.append(row);size+=row['bytes']
 if part:parts.append(part)
 for i,part in enumerate(parts):
  suffix=g+(str(i+1)if len(parts)>1 else'');name=f'Gullyverse-Quarry-Fidelity-{suffix}-'+{'A':'code-master-runtime','B':'licensed-originals','C':'review-gallery','D':'technical-evidence'}[g]+'.zip'
  for row in part:row['archive']=name
  chunks.append((name,g,part))
required=['public/models/gullyverse/blockout.layout.json','public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb','public/models/gullyverse/quarry-foundation-refined/foundation-materials.glb','public/models/gullyverse/recovered-c8-material/scanned-materials.glb','public/models/gullyverse/recovered-c8-material/manifest.json','public/models/gullyverse/recovered-c9-composition/composition-region.glb','public/models/gullyverse/recovered-c9-composition/manifest.json','assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend','assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend','assets-source/gullyverse/quarry-foundation/quarry-foundation.blend','assets-source/gullyverse/quarry-foundation-refined/quarry-foundation-refined.blend','components/immersive/QuarryFoundationSession.ts','components/immersive/ScannedRockMaterialSession.ts','components/immersive/ScannedCompositionSession.ts','package.json','package-lock.json']
manifest={'version':'Recovery-Quarry-Fidelity-Correction','branch':'codex/navigation-board','HEAD':'14f36da1a9b79a3b4926f7445bf0cde6c6c8f767','requiredBaselineFiles':[{'path':s,'sha256':start[s]['sha256']}for s in required],'files':rows}
(W/'fidelity-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
p3=Path('/workspace/recovery-phase3/2026-10-19/checkpoint');old=json.loads((p3/'checkpoint-index.json').read_text())
dependencies={'phase1AndPhase2':old['dependencies'],'phase3':{'folder':'https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A','checkpointIndexSHA256':sha(p3/'checkpoint-index.json'),'archives':old['archives'],'verificationReceiptSHA256':sha(p3/'DRIVE-BACKUP-RECEIPT.json')},'historicalReferences':{'preC9':{'id':'1M7Np5ywCzOvIdMgCn95MQVij7O4I3TS8','sha256':'e7edb115190a2fa1050541b1c7cc064871d69e7e116e352364d0aedb4451e2bb'},'visualPack':{'id':'1rkl9Np7SatwA24sKjnFavO2nTAAJQJAL','sha256':'a82e6336490858d1d68f387f298e0060c68a0d6c9f07a97b033183d4b0a91274'}},'note':'Incremental on full protected Phase1 + Phase2 + Phase3. Real required LFS/stage/media payloads live in Phase1, shared C8 textures in Phase2, original hero scan/master in Phase3. New CC04 provider source/maps and packed editable master are supplied here. No pointer-only substitutes.'}
(W/'DEPENDENCIES.json').write_text(json.dumps(dependencies,indent=2)+'\n');shutil.copyfile(R/'scripts/apply-fidelity.py',W/'apply-fidelity.py')
readme='''# Restore the quarry-fidelity correction

This is a new PRIVATE incremental checkpoint on protected Recovery Phases1+2+3. It is not a replacement for those checkpoints and does not approve the art. Branch codex/navigation-board, HEAD14f36da1a9b79a3b4926f7445bf0cde6c6c8f767.

Protected Phase1: https://drive.google.com/drive/folders/1OdGXZvpfHCdYpWesgya3x_lTupKsB_HI
Protected Phase2: https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-
Protected Phase3: https://drive.google.com/drive/folders/1fdmtNcQ68aJQJj1-UEZ5yDapTW4NGR4A
New correction: https://drive.google.com/drive/folders/1doGUar6hMGWhFuqn0jlkcG4sl2nE2MXw

1. Restore Phase1 into a NEW directory, including actual LFS payloads, original Blender masters, stage/media and backup-policy addendum. Apply all Phase2 and Phase3 archives using their exact hash-checked restoration instructions. DEPENDENCIES.json identifies exact prior archives/checksums.
2. Download EVERY archive in checkpoint-index.json plus fidelity-file-manifest.json, DEPENDENCIES.json, SHA256SUMS.txt, this README, apply-fidelity.py and the final Drive verification receipt. Verify sha256sum -c SHA256SUMS.txt (macOS: shasum -a256 -c SHA256SUMS.txt).
3. Extract all NEW ZIPs into one separate EMPTY overlay directory. Each ZIP is independently extractable under100MiB; no binary concatenation is needed. Their project/ children merge. Extract all C-review parts together for the complete gallery.
4. From the overlay run: python3 apply-fidelity.py --base /path/to/restored-phase3/project
   Preflight validates every source/baseline hash before writing, rejects unrelated edits/symlinks, replaces atomically and verifies final hashes. Reapplying is idempotent. A conflict is not permission to reset or overwrite work.
5. Keep these archives/checksums outside Codex too. Full remote download-back verification is recorded separately; upload success alone is insufficient. The interim authoring snapshot is NOT a complete restore checkpoint.

## Run

Use npm ci with the preserved lockfile. Supply private backend configuration separately; .env/credentials are excluded. Build with NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1 NEXT_PUBLIC_GULLYVERSE_INSPECTION=1 npm run build, then npm run start. The validation build used non-secret invalid Supabase placeholders; backend functionality is not certified.

Private modes:
/?arrival=hub&diagnostics&quarryReview=material-fidelity — corrected35.557m material coverage, unchanged C5.1 meshes, locked3x.
/?arrival=hub&diagnostics&quarryReview=geology-fidelity — corrected native-source physical geology + same3x materials.
Historical recovered comparisons remain scanned-material-multi and scanned-composition. Ordinary URLs remain unchanged public C5.1. Preview configuration is not authentication. No deployment or promotion is authorized.

## Editable master / source reproduction

assets-source/gullyverse/quarry-fidelity-correction/quarry-fidelity-correction.blend is the packed editable high/runtime master. Authentic CC0 Coastal Cliff04 provider Blender/model/maps and provenance are in licensed-source/. The original0.9hero source/master remains a Phase3 dependency, not another full-world download.

With Blender4.3.2 run scripts/blender/compose_quarry_fidelity_volume.py, then bake_quarry_fidelity.py from the repository root. The final entry point is compose_quarry_fidelity_volume.py; the earlier direct-entry author_quarry_fidelity.py is a retained failed trial plus shared utility library, not the final method. Do not use --resume on first reproduction: it needs a regenerated authoring cache. Offline MikkTSpace production uses the already installed Three dependency, not a new runtime loader. Cross-version remesh/decimation/bake bytes are not promised identical. Restoring shipped assets requires no Blender regeneration or new downloads.

## Review / limitations

Open REVIEW-START.html after extracting ALL C-review parts, or project/reports/recovery-quarry-fidelity-2026-10-19/gallery.html. Exact current PNGs, historical original PDF panels, phone/full/technical PDFs, browser videos, pose metadata and failure/validation evidence are included. Historical camera matches are reference-aligned, not pixel-identical. C6/C6.1/C6.2 are historical comparisons, C7 rejected, C8.1 optional. The lost C6.2 host is not falsely restored.

No Stage3A is included. No lighting, footprint, collision, stage, crowd, map or navigation redesign. Whole-scene inherited visibility limitations and physical-device performance remain explicitly pending in the report. Visual approval is required before any next phase.
'''
(W/'RESTORE-FIDELITY.md').write_text(readme);(W/'REVIEW-START.html').write_text('<!doctype html><meta name="viewport" content="width=device-width"><h1>Quarry fidelity correction</h1><p>Extract all C-review ZIPs together.</p><a href="project/reports/recovery-quarry-fidelity-2026-10-19/gallery.html">Full-resolution gallery and PDFs</a>')
archives=[]
for name,g,part in chunks:
 p=W/name;assert not p.exists(),'Never overwrite a checkpoint archive'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for row in part:z.write(ROOT/row['path'],'project/'+row['path'])
  if g=='A':
   for s in ['fidelity-file-manifest.json','DEPENDENCIES.json']:z.write(W/s,'recovery-fidelity/'+s)
   for s in ['RESTORE-FIDELITY.md','apply-fidelity.py']:z.write(W/s,s)
  if g=='C'and not any(a['group']=='C'for a in archives):z.write(W/'REVIEW-START.html','REVIEW-START.html')
 with zipfile.ZipFile(p)as z:assert z.testzip()is None;members=len(z.infolist())
 assert p.stat().st_size<100*1024*1024
 archives.append({'name':name,'group':g,'bytes':p.stat().st_size,'sha256':sha(p),'members':members})
index={'version':manifest['version'],'branch':manifest['branch'],'HEAD':manifest['HEAD'],'folder':'https://drive.google.com/drive/folders/1doGUar6hMGWhFuqn0jlkcG4sl2nE2MXw','dependencies':dependencies,'archives':archives,'projectFiles':len(rows),'projectBytes':sum(r['bytes']for r in rows),'auditedStartingFiles':len(start),'preexistingUserFilesAddedBeyondProtectedPhase3':extra,'perFileManifestSHA256':sha(W/'fidelity-file-manifest.json'),'externalVerification':'See separate full download-back SHA256 receipt; upload success alone is insufficient.'}
(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2)+'\n');(W/'SHA256SUMS.txt').write_text(''.join(a['sha256']+'  '+a['name']+'\n'for a in archives));print(json.dumps({k:index[k]for k in ['archives','projectFiles','projectBytes']},indent=2))
