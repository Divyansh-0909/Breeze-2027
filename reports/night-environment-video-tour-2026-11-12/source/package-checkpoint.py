from pathlib import Path
import json, hashlib, zipfile, subprocess, datetime

R=Path(__file__).resolve().parents[1];repo=R.parents[1];C=R/'checkpoint'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for name in ['native-preservation.json','movement-preservation.json']:
 d=json.loads((R/'evidence'/name).read_text())
 for row in d['files']:
  p=repo/row['path'];assert sha(p)==row['sha256'],row['path']
  rows.append({'path':row['path'],'sha256':row['sha256'],'unchanged':True})
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
assert head=='0e1e23dd2f5181df202d862d147067249bc55a41'
tracked=subprocess.check_output(['git','diff','--name-only'],cwd=repo,text=True).splitlines()
assert set(tracked)<= {'README.md'},tracked
v=json.loads((R/'evidence/video-validation.json').read_text());assert v['status']=='PASS' and v['fullDecode']=='PASS'
assert sha(R/'video/Breeze-Night-Environment-Full-Tour-2026-11-12.mp4')==v['sha256']
assert (R/'evidence/video-full-decode.log').read_bytes()==b''
pdf=json.loads((R/'evidence/pdf-verification.json').read_text());assert pdf['pages']==8
assert sha(R/'review/Breeze-Night-Environment-Tour-Companion.pdf')==pdf['sha256']
receipts=json.loads((C/'upload-receipts.json').read_text());assert all(p['status']=='PASS' for p in receipts)
proof={'status':'PASS','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'branch':subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip(),'existingTrackedDiff':tracked,'preservedFiles':rows,'video':{k:v[k] for k in ['duration','frames','width','height','deliveryFPS','sourceRenderFPS','sha256','bytes','fullDecode']},'pdf':pdf,'checkedUploadCount':len(receipts),'websiteImplemented':False,'nativeFileSaved':False,'videoVisualReview':'Four decoded delivery frames inspected; chapter labels, scene coverage and mural visible','pdfVisualReview':'Cover and final page inspected; eight pages and clickable video link verified'}
(R/'evidence/final-local-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
files=[R/'REPORT.md',R/'RESTORE.md',R/'tour-path.json',R/'review/Breeze-Night-Environment-Tour-Companion.pdf',C/'source-video-parts-index.json',C/'upload-receipts.json']
files+=list((R/'source').glob('*'))+list((R/'viewer').rglob('*'))
files += [p for p in (R/'evidence').iterdir() if p.name not in ['server.log','encode.lock'] and p.suffix!='.mp4']
shots=json.loads((R/'tour-path.json').read_text())['shots']
files += [R/'renders'/f"{s['id']}.jpg" for s in shots]+[R/'renders/native-team-reference.png']
files=sorted(set(p for p in files if p.is_file()))
payload=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
archive=C/'Breeze-Full-Night-Tour-Capture-Sources-2026-11-12.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('CAPTURE-PAYLOAD-SHA256.json',json.dumps(payload,indent=2)+'\n')
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for p in payload:
  b=z.read(p['path']);assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256']
external=[json.loads((R/'evidence'/n).read_text()) for n in ['video-upload.json','pdf-upload.json']]
index={'status':'PASS','createdUTC':proof['timeUTC'],'archive':{'name':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'zipCRCAndEveryPayloadSHA256':'PASS','payloadCount':len(payload)},'payloads':payload,'externalPlayableOutputs':external,'sourceRecording':json.loads((C/'source-video-parts-index.json').read_text()),'nativeRebuildDependency':json.loads((R/'evidence/source-dependency.json').read_text()),'nativeBackupFolder':'https://drive.google.com/drive/folders/19lLbeomN6cqhASBobc3T2SvmUHoz8wKG','restore':'Extract archive into repository root; see reports/night-environment-video-tour-2026-11-12/RESTORE.md. Compiled viewer is standalone; native master is needed only to rebuild.','excluded':'Video bytes are independently verified Drive outputs; native masters reused from earlier verified backup; regenerable build intermediates, temporary visual checks and mutable server log omitted.'}
indexpath=C/'Night-Tour-Delivery-Index-2026-11-12.json';indexpath.write_text(json.dumps(index,indent=2)+'\n')
(C/'SHA256SUMS.txt').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in [archive,indexpath,C/'source-video-parts-index.json',R/'RESTORE.md'])+'\n')
print(json.dumps({'status':'PASS','archive':index['archive'],'preservationFiles':len(rows),'index':str(indexpath)}))
