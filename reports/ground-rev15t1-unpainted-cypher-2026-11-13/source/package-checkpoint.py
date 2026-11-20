from pathlib import Path
import json,hashlib,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for file in ['paint-only-check.json','runtime-verification.json','restore-check.json']:
 assert json.loads((R/'evidence'/file).read_text())['status']=='PASS'
assert json.loads((R/'delivery/Base-Rev15T-Native-Parts.json').read_text())['status']=='PASS'
for name in ['library','runtime','pdf']:
 row=json.loads((R/f'evidence/{name}-upload.json').read_text());assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256']
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
files=[]
for group in ['source','textures','renders','evidence','review']:files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(R/x for x in ['REPORT.md','RESTORE.md','delivery/Base-Rev15T-Native-Parts.json','delivery/Dependency-Index.json'])
files.extend(repo/x for x in ['AGENTS.md','docs/gullyverse-ground-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-ground-direction-study-current.md'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15T1-Unpainted-Cypher-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for x in rows:
  d=z.read(x['path']);assert len(d)==x['bytes'] and hashlib.sha256(d).hexdigest()==x['sha256']
assert out.stat().st_size<32*1024*1024
index={'status':'PASS','checkpoint':{'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out)},'payloads':rows,'dependencyIndex':'Dependency-Index.json','baseSHA256':'8c0745fcb068ba8039a8196742e0b500e905026e842e09788e565d3c34a459fc','nativeRecovery':'Fresh-process restoration from verified base and native material delta passed'}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(index,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(R/'delivery'/f)+'  '+f for f in [out.name,'Rev15T1-Unpainted-Asphalt-Material.blend','Rev15T1-Unpainted-Asphalt-Ground.glb','Base-Rev15T-Native-Parts.json'])+'\n')
print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'payloads':len(rows)}))
