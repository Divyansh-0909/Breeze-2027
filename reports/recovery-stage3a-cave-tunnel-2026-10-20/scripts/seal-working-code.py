from pathlib import Path
import json,hashlib,zipfile,datetime
ROOT=Path.cwd();W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint');P=Path('/workspace/recovery-fidelity/2026-10-19/checkpoint/restoration-test/project')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
rels=['components/immersive/'+f for f in ['AftermovieScene.tsx','HubScene.tsx','ImmersiveShell.tsx','CaveEntrance.tsx','CaveEntranceSession.ts','caveLegacyInterface.ts','caveLightResponse.ts','caveReview.ts']]+['tests/immersive/cave-review.test.ts']+['scripts/blender/'+f for f in ['author_cave_recovery.py','cave_scan_surface.py','cave_mikktspace.mjs','clip_cave_entry_terrain.py']]
rels+= [str(p.relative_to(ROOT))for p in (ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/scripts').glob('*')if p.is_file()]
rows=[{'path':r,'bytes':(ROOT/r).stat().st_size,'sha256':sha(ROOT/r),'beforeSHA256':sha(P/r)if(P/r).is_file()else None}for r in sorted(set(rels))]
required=['public/models/gullyverse/blockout.layout.json','public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb','public/models/gullyverse/recovered-c8-material/scanned-materials.glb','package-lock.json']
manifest={'status':'WORKING_CODE_CHECKPOINT_NOT_PHASE_COMPLETION','branch':'codex/navigation-board','HEAD':'14f36da1a9b79a3b4926f7445bf0cde6c6c8f767','files':rows,'requiredBaselineFiles':[{'path':r,'sha256':sha(P/r)}for r in required]}
name='Gullyverse-Stage3A-Working-Code-2026-10-20.zip';path=W/name;assert not path.exists()
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for r in rows:z.write(ROOT/r['path'],'project/'+r['path'])
 z.writestr('recovery-stage3a/stage3a-file-manifest.json',json.dumps(manifest,indent=2)+'\n');z.write(ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/scripts/apply-stage3a.py','apply-stage3a.py')
 z.writestr('WORKING-CHECKPOINT-README.md','# Working source checkpoint, not final phase completion\n\nRestore protected Phases1/2/3 then quarry-fidelity checkpoint https://drive.google.com/drive/folders/1doGUar6hMGWhFuqn0jlkcG4sl2nE2MXw into a NEW directory. Extract this ZIP into a separate overlay; run python3 apply-stage3a.py --base /path/to/restored-fidelity/project. Conflicting user edits are refused before any write.\n\nThe independently verified 70MB editable master/runtime archive is https://drive.google.com/file/d/1kW78RW6maDuzgLnDqiltCWRCso3N1J4y/view . Merge its project/ assets too, verifying its checksums. This WORKING code checkpoint has97 passing immersive units and build/type/lint; browser/art/performance review remains in progress. It is superseded by the final02 Complete Cave Candidate checkpoint index when delivered.\n\nPrivate preview only: /?diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave . C9 and3x are preserved. No public promotion, commit or deployment. Exact artist images are pending.\n')
 assert z.testzip()is None
record={'name':name,'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'parent_id':'12Tr1E8K2P4Ry3TEh0uTZ5g6NJxCpBkSe'};(W/'working-code-record.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
