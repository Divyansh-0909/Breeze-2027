from pathlib import Path
import json,hashlib,zipfile
O=Path(__file__).resolve().parents[1];C=O/'checkpoint'
groups={'Gullyverse-Straight-Walk-Source-Review.zip':[], 'Gullyverse-Walk-Original-Rendered-Frames.zip':[]}
for folder in ['source','evidence','review','renders']:
    groups['Gullyverse-Straight-Walk-Source-Review.zip'] += [p for p in (O/folder).rglob('*')if p.is_file()and '__pycache__'not in p.parts and not p.name.endswith('.blend1')]
groups['Gullyverse-Straight-Walk-Source-Review.zip'] += [O/'REPORT.md',O/'RESTORE.md']
groups['Gullyverse-Walk-Original-Rendered-Frames.zip']=[p for p in (O/'walk-frames').rglob('*.png')]
assert len(groups['Gullyverse-Walk-Original-Rendered-Frames.zip'])==120
rows=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for files in groups.values()for p in sorted(set(files))]
(O/'FILE-SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['file']+'\n'for r in rows))
groups['Gullyverse-Straight-Walk-Source-Review.zip'].append(O/'FILE-SHA256SUMS.txt')
archives=[]
for name,files in groups.items():
    path=C/name
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(set(files)):z.write(p,str(p.relative_to(O)))
    with zipfile.ZipFile(path)as z:assert z.testzip()is None
    archives.append({'file':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'members':len(set(files))})
index={'handoff':'WORLD-STRAIGHT-WALK-SEMICIRCLE-20261025-04','archives':archives,'files':rows,'restoreOrder':list(groups),'masterSelfContainedInMainArchive':True,'websiteFilesChanged':False,'externalBackupStatus':'PENDING_UPLOAD_AND_DOWNLOAD_BACK_VERIFICATION'}
(C/'CHECKPOINT-INDEX.json').write_text(json.dumps(index,indent=2)+'\n');print('CHECKPOINT_READY',json.dumps(archives),flush=True)
