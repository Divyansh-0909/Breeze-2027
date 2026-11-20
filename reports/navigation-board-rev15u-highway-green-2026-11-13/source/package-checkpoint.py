from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];T=R.parent/'ground-rev15t3-rebuilt-potholes-2026-11-13';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for key in ['fresh-open','restored-fresh-open','restore-check','browser','pdf-verification','lighting-verification','hindi-artwork']:
    assert json.loads((R/f'evidence/{key}.json').read_text())['status']=='PASS',key
for key in ['library','runtime','pdf']:
    row=json.loads((R/f'evidence/{key}-upload.json').read_text());assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256']
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
base=json.loads((R/'delivery/Base-Rev15T2-Native-Parts.json').read_text());assert base['status']=='PASS' and len(base['parts'])==13 and all(x['status']=='PASS' for x in base['parts'])
files=[]
for group in ['source','textures','renders','evidence','review','viewer','history']:
    files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.lock','.tmp'])
files.extend(p for p in (R/'source/review-fonts').glob('*') if p.is_file())
files.extend(R/'viewer/vendor'/f for f in ['LICENSE-three','three.module.min.js','addons/loaders/GLTFLoader.js','addons/utils/BufferGeometryUtils.js'])
files.extend(R/f for f in ['REPORT.md','RESTORE.md','delivery/Base-Rev15T2-Native-Parts.json','delivery/Dependency-Index.json'])
files.extend(T/f for f in ['source/restore-master.py','source/restore-native.py','source/scene-fingerprint.py','evidence/native-scene-fingerprint.json','evidence/build-verification.json','evidence/library-upload.json','evidence/restore-check.json','evidence/restored-fresh-open.json','REPORT.md','RESTORE.md'])
files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-navigation-board-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-ground-current.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15U1-Bilingual-Navigation-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,str(p.relative_to(repo)))
    z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for row in rows:
        data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert out.stat().st_size<18*1024*1024
index={'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':[{'index':1,'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'status':'LOCAL_VERIFIED'}],
       'payloads':rows,'sourceRestoreVerification':'PASS: ZIP CRC and every included payload SHA256; required T3/U1 helpers, fonts, viewer and native dependency index included',
       'nativeRecovery':'Complete verified T2 master plus packed T3 ground and U1 bilingual style deltas; actual reconstruction and independent fresh-open checks passed'}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(R/f)+'  '+f for f in ['delivery/'+out.name,'delivery/Rev15U1-Bilingual-Highway-Sign-Styling.blend','delivery/Rev15U1-Bilingual-Highway-Navigation-Board.glb','delivery/Base-Rev15T2-Native-Parts.json','delivery/Dependency-Index.json','review/Breeze-Bilingual-Highway-Navigation-Review.pdf','REPORT.md','RESTORE.md'])+'\n')
print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'payloads':len(rows)}))
