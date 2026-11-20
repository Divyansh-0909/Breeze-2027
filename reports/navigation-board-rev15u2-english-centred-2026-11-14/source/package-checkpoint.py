from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];U1=R.parent/'navigation-board-rev15u-highway-green-2026-11-13';T=R.parent/'ground-rev15t3-rebuilt-potholes-2026-11-13';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for key in ['fresh-open','restored-fresh-open','restore-check','browser','pdf-verification','lighting-verification']:
    assert json.loads((R/f'evidence/{key}.json').read_text())['status']=='PASS',key
for key in ['library','runtime','pdf']:
    row=json.loads((R/f'evidence/{key}-upload.json').read_text());assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256']
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
files=[]
for group in ['source','renders','evidence','review','viewer']:
    files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.lock','.tmp'])
files.extend(p for p in (R/'source/review-fonts').glob('*') if p.is_file())
files.extend(R/'viewer/vendor'/f for f in ['LICENSE-three','three.module.min.js','addons/loaders/GLTFLoader.js','addons/utils/BufferGeometryUtils.js'])
files.extend(R/f for f in ['REPORT.md','RESTORE.md','delivery/Dependency-Index.json','delivery/Base-Rev15T2-Native-Parts.json'])
files.extend(U1/f for f in ['source/restore-native.py','source/scene-fingerprint.py','source/fonts/OFL.txt','source/fonts/AUTHORS.txt','evidence/build-verification.json','evidence/native-scene-fingerprint.json','evidence/library-upload.json','evidence/restore-check.json','evidence/restored-fresh-open.json','delivery/Dependency-Index.json','REPORT.md','RESTORE.md'])
files.extend(T/f for f in ['source/restore-master.py','source/restore-native.py','source/scene-fingerprint.py','evidence/native-scene-fingerprint.json','evidence/library-upload.json'])
files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-navigation-board-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-ground-current.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15U2-English-Centred-Navigation-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,str(p.relative_to(repo)))
    z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for row in rows:
        data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert out.stat().st_size<16*1024*1024
index={'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':[{'index':1,'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'status':'LOCAL_VERIFIED'}],'payloads':rows,'sourceRestoreVerification':'PASS: ZIP CRC and every payload SHA256; all required T3/U1/U2 reconstruction modules included','nativeRecovery':'Complete verified T2 base plus T3/U1 deltas, then U2 label centring source; actual reconstruction and independent fresh-open checks passed'}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(index,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(R/f)+'  '+f for f in ['delivery/'+out.name,'delivery/Rev15U2-English-Centred-Labels.blend','delivery/Rev15U2-English-Centred-Navigation-Board.glb','delivery/Dependency-Index.json','delivery/Base-Rev15T2-Native-Parts.json','review/Breeze-English-Centred-Navigation-Review.pdf','REPORT.md','RESTORE.md'])+'\n')
print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'payloads':len(rows)}))
