from pathlib import Path
import hashlib,json,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];T=R.parent/'ground-rev15t2-wet-grain-asphalt-2026-11-13'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for key in ['fresh-open','restored-fresh-open','restore-check','browser-check','pdf-verification','lighting-verification']:
    assert json.loads((R/f'evidence/{key}.json').read_text())['status']=='PASS',key
for key in ['library','runtime','pdf']:
    row=json.loads((R/f'evidence/{key}-upload.json').read_text())
    assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256'],key
base=json.loads((R/'delivery/Base-Rev15T2-Native-Parts.json').read_text())
assert base['status']=='PASS' and len(base['parts'])==13 and all(p['status']=='PASS' for p in base['parts'])
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
files=[]
for folder in [R,T]:
    for group in ['source','textures','renders','evidence','review','viewer']:
        files.extend(p for p in (folder/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.lock','.tmp'])
    files.extend(folder/x for x in ['REPORT.md','RESTORE.md'])
    files.extend(p for p in (folder/'source/fonts').glob('*') if p.is_file())
    vendor=folder/'viewer/vendor'
    if vendor.exists():
        files.extend(vendor/x for x in ['three/build/three.module.js','three/examples/jsm/loaders/GLTFLoader.js','three/examples/jsm/utils/BufferGeometryUtils.js','three/LICENSE'])
files.extend([T/'delivery/Native-Master-Parts.json',R/'delivery/Base-Rev15T2-Native-Parts.json'])
files.extend(repo/x for x in ['AGENTS.md','docs/gullyverse-ground-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json'])
files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15T3-Rebuilt-Potholes-Checkpoint.zip'
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
        i=len(parts)+1;p=out.with_name(out.name+f'.part{i:02d}');p.write_bytes(data)
        parts.append({'index':i,'file':p.name,'bytes':len(data),'sha256':sha(p),'status':'LOCAL_VERIFIED'})
joined=hashlib.sha256()
for p in parts:joined.update((R/'delivery'/p['file']).read_bytes())
assert joined.hexdigest()==sha(out)
index={'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':parts,'payloads':rows,
       'nativeRecovery':'Complete verified T2 master plus current packed T3 native delta; actual semantic restoration and fresh-open checks passed'}
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps(index,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(R/'delivery'/x)+'  '+x for x in [out.name,'Rev15T3-Rebuilt-Potholes-Additions.blend','Rev15T3-Rebuilt-Potholes-Ground.glb','Base-Rev15T2-Native-Parts.json'])+'\n')
print(json.dumps({'status':'PASS','zipBytes':out.stat().st_size,'zipSHA256':sha(out),'parts':len(parts),'payloads':len(rows)}))
