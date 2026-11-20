from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((R/'evidence/build-verification.json').read_text());assert sha(Path(b['editedMaster']))==b['editedSHA256']
for key in ['fresh-open','restored-fresh-open','restore-check','browser','pdf-verification','lighting-verification','before-lighting','neutral-captures']:
 assert json.loads((R/f'evidence/{key}.json').read_text())['status']=='PASS',key
assert json.loads((R/'evidence/fresh-open.json').read_text())['sourceSHA256']==b['editedSHA256']
for key in ['library','runtime','pdf']:
 row=json.loads((R/f'evidence/{key}-upload.json').read_text());assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256']
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
files=[]
for group in ['source','renders','evidence','review','textures','references','dependencies']:
 files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.lock','.log','.tmp'] and not p.name.startswith('check-'))
files.extend(R/'viewer'/f for f in ['index.html','main.js','vendor/LICENSE-three','vendor/three.module.min.js','vendor/addons/loaders/GLTFLoader.js','vendor/addons/utils/BufferGeometryUtils.js'])
files.extend(R/f for f in ['REPORT.md','RESTORE.md','delivery/Dependency-Index.json','delivery/Base-Rev15T2-Native-Parts.json'])
files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-cypher-houses-current.md','docs/gullyverse-events-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-navigation-board-current.md','docs/gullyverse-ground-current.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15V-Cypher-Houses-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for row in rows:
  data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
parts=[]
with out.open('rb') as f:
 while data:=f.read(12*1024*1024):
  i=len(parts)+1;p=R/'delivery'/f'{out.name}.part{i:02d}';p.write_bytes(data);parts.append({'index':i,'file':p.name,'bytes':len(data),'sha256':sha(p),'status':'LOCAL_VERIFIED'})
index={'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':parts,'payloads':rows,'sourceRestoreVerification':'PASS: ZIP CRC and every payload SHA256. Verified U3 source checkpoint is embedded, including all earlier T3/U1/U2/U3 reconstruction modules.','nativeRecovery':'Complete verified T2 base plus T3/U1 packed deltas; U2/U3/V source reconstruction. The V rebuild from restored U3 and independent fresh open passed.','runtimeAndNativeComponent':'Separate verified Drive artifacts indexed in delivery/Dependency-Index.json'}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(index,indent=2)+'\n')
checks=[out,R/'delivery/Rev15V-Cypher-Houses-Architecture-Update.blend',R/'delivery/Rev15V-Cypher-Houses-Architecture.glb',R/'delivery/Dependency-Index.json',R/'delivery/Base-Rev15T2-Native-Parts.json',R/'review/Breeze-Cypher-Houses-Walls-Windows-Review.pdf',R/'REPORT.md',R/'RESTORE.md']+[R/'delivery'/p['file'] for p in parts]
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+str(p.relative_to(R)) for p in checks)+'\n');print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'parts':len(parts),'payloads':len(rows)}))
