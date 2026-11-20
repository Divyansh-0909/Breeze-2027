from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();verification=json.loads((R/'evidence/document-readback-verification.json').read_text());snapshots=json.loads((R/'evidence/native-snapshot-index.json').read_text());initial=json.loads((R/'evidence/initial-state-and-backups.json').read_text());pdf=json.loads((R/'evidence/pdf-verification-final.json').read_text());doc=verification['url'];phase=initial['phase']['url'];native=json.loads((R/'evidence/final-native-snapshot-verification.json').read_text())
assert verification['status']=='PASS' and native['status']=='PASS' and pdf['status']=='PASS';assert json.loads((R/'evidence/movement-recheck.json').read_text())['status']=='PASS'
(R/'REPORT.md').write_text(f'''# Project document sync through Rev15V2 / 14 November 2026

Updated the existing destination-owned [shared recovery-control document]({doc}) in place. The previous dated handoff was 12 November / P-P2, while its old current-state fields still pointed to the 45-scene O master. The current header, latest-handoff pointer and shared state now identify the 58-scene V2 environment and handoff {verification['handoffId']}.

The appended consolidated record covers the night tour; Team top light and detailed crowd retained through R; five reference-informed open shops and S fascia boards; the verified Drive migration excluding CSD361; continuous asphalt, circle removal, wet shoulders and rebuilt potholes; final English highway navigation, Accommodation, larger centred lettering and the unchanged LED; house/window details; terracotta Events plaster with all posters retained; and the narrow outward-open see-through steel gate beyond the navigation stand. The user's “great” is recorded as acceptance of the latest Events/gate direction. Full-world website/walkable/collision integration remains pending.

Readback exactly matched the planned scoped edits and two subsequent line-wrap repairs. All {verification['preservedHistoricalParagraphs']:,} unedited historical paragraphs retain their text, native formatting and links, including {verification['preservedHistoricalGreenParagraphs']:,} green ChatGPT paragraphs. All five embedded images, tabs, global styles and the last independent ChatGPT review marker are preserved. Twenty-five new linked labels were verified. All eight original movement/rendering files still match the 12 November hashes.

The full original and final native copies are preserved, destination owner and parent verified. Their bodies, native structure, styles and image counts match their respective live-document states. Complete before/final PDF exports have {pdf['beforePages']} and {pdf['afterPages']} pages. A ten-page unchanged native-PDF excerpt shows the updated current header, handoff pointer, shared-state pages and appended record. PDF layout was inspected; long master filename/directory values were separated so they fit the page.

The execution environment restarted after the first readback. Temporary exports were recovered from the native snapshots and authenticated file references; live document content still matched the saved after copy. This phase did not reconstruct or change any 3D asset. Temporary native world caches must be restored from their already verified Drive dependency chain before further asset work.

[Documentation phase]({phase}) contains the native copies and this independently restorable documentation checkpoint. The checkpoint contains exact original/final native JSON records, full before/final PDFs, the excerpt, source/edit requests, readback evidence, reports and local pointers. Native document restoration uses the complete native backup copies to retain editable images/formatting; see RESTORE.md. Earlier backups and sharing are unchanged. No commit, push, merge or deployment occurred.
''')
(R/'RESTORE.md').write_text(f'''# Restore the project-document checkpoint

This phase updates documentation only. The current shared document is {doc}. The versioned phase is {phase}.

Download every ordered checkpoint ZIP part and Checkpoint-Index.json. Run source/restore-checkpoint.py with the download folder, a new output ZIP filename and --index pointing at that index. It verifies each part's size/SHA-256, the complete ZIP, ZIP CRCs and every payload hash. Extract into a new empty directory. Source paths are relative to the repository root. Do not apply the fixed-index edit requests to an already updated or concurrently changed document.

Complete native BEFORE snapshot: {snapshots['before']['url']}
Complete native final AFTER snapshot: {snapshots['finalAfter']['url']}

For an editable native restoration, copy the appropriate verified native snapshot with Google Drive's native copy action into a new recovery folder, then read back its body, styles and image count. Preserve the live document and original snapshots. These native copies retain all five embedded images and their editable native layout. The JSON records and full PDF exports supply an independent content/structure and offline-readable record; rebuilding a Doc from PDF alone would lose native editing structure.

The archive includes snapshots/before-document.json (read from the verified BEFORE native copy after a runtime restart), snapshots/final-after-document.json (final live readback), full before/final PDF exports, the exact initially guarded requests, the two scoped layout repairs and complete readback evidence. The BEFORE native copy had been verified byte-for-byte in native body/style structure against the live original before editing. The final native copy likewise matches the final live body/structure/styles/image count, with destination parent/owner verification recorded.

NativeDoc indexes are UTF-16 units. compose-edit.js and planned-edit.json describe the original scoped update; layout-repair.json records the final filename/directory line-wrap adjustment. Replaying edits is optional and must start from the matching BEFORE state with a fresh requiredRevisionId. The tested and simplest restoration is a new native copy of the preserved complete document.

This archive is not a full 3D world backup. Current V2 art/native/runtime dependencies remain in their separately verified phase indexes and the source links in CONSOLIDATED-HANDOFF.md. The environment restart cleared temporary local 3D caches; recover the master through that existing chain before any further world editing. Website/walkable integration remains pending.
''')
pointer=f'''# Current shared project document

Updated **14 November 2026 through Rev15V2** in the existing migrated destination-owned document:

{doc}

Handoff: `{verification['handoffId']}`. The current header, latest-handoff pointer and shared state now identify the 58-scene V2 master. The dated record covers all changes since the 12 November P/P2 handoff, current review PDFs, complete native recovery links, the resolved Accommodation/English-only navigation choice and pending website integration. The user accepted the latest presented Events-plaster/open-gate direction with “great”.

Earlier history, green review notes, all five embedded images and the last independent ChatGPT review marker are preserved. Native before/final document copies and an independently verified documentation checkpoint are stored at {phase}. See [the sync report](../reports/{R.name}/REPORT.md) and [restore instructions](../reports/{R.name}/RESTORE.md).

Temporary local 3D caches were cleared by the execution-environment restart; the complete current world remains recoverable from its verified V2 native/source dependency chain. No new art or website implementation was performed in this documentation phase.
''';(repo/'docs/gullyverse-shared-document-current.md').write_text(pointer)
p=repo/'docs/gullyverse-consolidated-handoff-current.md';t=p.read_text();intro=f'''The shared recovery-control document is synchronized **14 November 2026 through Rev15V2**, with the 58-scene master, latest review/source links and all changes since the 12 November handoff. The user's “great” records acceptance of the latest Events wall and open-gate direction. [Open the updated document]({doc}) or see [document status and recovery](gullyverse-shared-document-current.md). History, images and independent review markers are preserved.\n\n'''
if intro not in t:t=t.replace('# Current consolidated handoff\n\n','# Current consolidated handoff\n\n'+intro,1)
t=t.replace('The latest full native scene is **Rev15V1','The preceding full native scene was **Rev15V1').replace('The latest shared-document handoff is **12 November','The preceding shared-document handoff was **12 November');t=t.replace('The navigation replacement remains undecided. Schedule is still visible in the asset but was rejected as redundant with Events; Graffiti Yard was also rejected. Festival Guide was suggested only and has not been selected or implemented. Website integration awaits further direction. No new art phase, commit, push or deployment occurred in this documentation task.','Historical Rev15O navigation note: Schedule was then undecided; the later U1–U3 user requests resolved it to Accommodation, with final English-only lettering. No website destination integration is implied.');p.write_text(t)
p=repo/'docs/gullyverse-cypher-entry-current.md';t=p.read_text().replace('User visual review is pending.','The user accepted the latest presented Events-plaster/open-gate direction with “great” on 14 November 2026.');p.write_text(t)
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
files=[]
for group in ['source','evidence']:
 files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.log','.lock'])
files.extend(R/f for f in ['snapshots/before-document.json','snapshots/final-after-document.json','snapshots/before-document.pdf','snapshots/final-after-document.pdf','review/Gullyverse-Project-Document-Update-Rev15V2-Final.pdf','REPORT.md','RESTORE.md','CONSOLIDATED-HANDOFF.md'])
files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-shared-document-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-cypher-entry-current.md']);files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];out=R/'delivery/Breeze-Project-Document-Sync-Rev15V2-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for row in rows:
  data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
parts=[]
with out.open('rb') as src:
 while data:=src.read(12*1024*1024):
  n=len(parts)+1;p=R/'delivery'/f'{out.name}.part{n:02d}';p.write_bytes(data);parts.append({'index':n,'file':p.name,'bytes':len(data),'sha256':sha(p),'status':'LOCAL_VERIFIED'})
idx={'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':parts,'payloads':rows,'nativeSnapshots':snapshots,'documentReadback':'PASS','sourceRestoreVerification':'Every ZIP CRC and payload SHA256 passed','scope':'Complete before/final native document copies plus exact structure JSON, full original/final PDFs, edit source/evidence and local pointers; 3D art remains in its separately indexed checkpoints.'};(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(idx,indent=2)+'\n');(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+str(p.relative_to(R)) for p in [out,R/'REPORT.md',R/'RESTORE.md',R/'review/Gullyverse-Project-Document-Update-Rev15V2-Final.pdf'])+'\n');print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'parts':len(parts),'payloads':len(rows)}))
