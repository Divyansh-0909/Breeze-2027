from pathlib import Path
import json,hashlib,zipfile,datetime,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
idx=json.loads((R/'delivery/Native-Master-Parts.json').read_text());assert idx['status']=='PASS'
b=json.loads((R/'evidence/build-verification.json').read_text());assert sha(Path(b['editedMaster']))==idx['sha256']==b['editedSHA256']
assert json.loads((R/'evidence/restore-check.json').read_text())['sha256']==idx['sha256']
assert json.loads((R/'evidence/fresh-open.json').read_text())['status']=='PASS'
assert json.loads((R/'evidence/browser-check.json').read_text())['status']=='PASS'
captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures)==10
for x in captures:assert x['masterSHA256']==idx['sha256'] and sha(R/x['file'])==x['sha256']
pdf=json.loads((R/'evidence/pdf-verification.json').read_text());up=json.loads((R/'evidence/pdf-upload.json').read_text());assert sha(R/'review/Breeze-Continuous-Asphalt-Implementation-Review.pdf')==pdf['sha256']==up['sha256']
for name,file in [('library','Rev15T-Asphalt-Ground-Additions.blend'),('runtime','Rev15T-Continuous-Asphalt-Ground.glb')]:
 r=json.loads((R/f'evidence/{name}-upload.json').read_text());assert r['status']=='PASS' and sha(R/'delivery'/file)==r['sha256']
mov=json.loads((R/'evidence/movement-preservation.json').read_text());assert all(sha(repo/x['path'])==x['sha256'] for x in mov['files'])
assert not subprocess.check_output(['git','diff','--name-only','--','app','components','lib'],cwd=repo,text=True).strip()
proof={'status':'PASS','verifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSHA256':idx['sha256'],'verifiedNativeParts':len(idx['parts']),'independentMasterRestore':'PASS','nativeFreshOpen':'PASS','nativeViewCount':10,'PDF':pdf['sha256'],'runtimeGLBBrowserCheck':'PASS / three views, UV bindings, eleven route raycasts, zero console or WebGL errors','originalQuarryFiles':'UNCHANGED','productionSourceDiffEmpty':True,'destinationAccount':'losersamurai09@gmail.com','publicIntegration':'Pending; native scene and separate runtime ground asset implemented'}
(R/'evidence/final-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
files=[]
for folder in ['source','renders','textures','viewer','evidence','review']:
 files.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(R/f for f in ['REPORT.md','RESTORE.md','delivery/Native-Master-Parts.json'])
files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-ground-current.md','docs/gullyverse-ground-direction-study-current.md','docs/gullyverse-consolidated-handoff-current.md','docs/gullyverse-backup-target.json'])
ref=repo/'reports/ground-direction-study-2026-11-13';sources=json.loads((ref/'references/sources.json').read_text());files.append(ref/'references/sources.json');files.extend(ref/x['local'] for x in sources)
files=sorted(set(files));payload=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
out=R/'delivery/Breeze-Rev15T-Continuous-Asphalt-Source-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for p in payload:
  d=z.read(p['path']);assert len(d)==p['bytes'] and hashlib.sha256(d).hexdigest()==p['sha256']
assert out.stat().st_size<32*1024*1024
delivery={'status':'PASS','sourceCheckpoint':{'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'payloadCount':len(payload)},'nativeMaster':idx,'additionsLibrary':json.loads((R/'evidence/library-upload.json').read_text()),'runtimeGround':json.loads((R/'evidence/runtime-upload.json').read_text()),'reviewPDF':up,'payloads':payload}
(R/'delivery/Delivery-Index.json').write_text(json.dumps(delivery,indent=2)+'\n')
(R/'delivery/SHA256SUMS.txt').write_text('\n'.join(sha(R/'delivery'/f)+'  '+f for f in [out.name,'Rev15T-Asphalt-Ground-Additions.blend','Rev15T-Continuous-Asphalt-Ground.glb','Native-Master-Parts.json'])+'\n')
print(json.dumps({'status':'PASS','sourceBytes':out.stat().st_size,'sourceSHA256':sha(out),'payloads':len(payload),'nativeParts':len(idx['parts'])}))
