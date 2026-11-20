from pathlib import Path
import hashlib,json,zipfile,subprocess
R=Path(__file__).resolve().parents[1];repo=R.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for file in ['build-verification','fresh-open','restore-check','restored-fresh-open','browser','export','pdf','document-final-verification']:
 assert json.loads((R/'evidence'/(file+'.json')).read_text())['status']=='PASS',file
assert json.loads((R/'evidence/movement-recheck.json').read_text())['status']=='UNCHANGED'
def zip_files(out,rows):
 payload=[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in rows];payloadbytes=(json.dumps(payload,indent=2)+'\n').encode()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for n,b in rows:z.writestr(n,b)
  z.writestr('PAYLOAD-SHA256.json',payloadbytes)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
  for row in payload:
   data=z.read(row['path']);assert len(data)==row['bytes'] and sha(data)==row['sha256']
 return {'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'payloadFiles':len(payload),'zipCRCAndEveryPayloadHash':'PASS'}
runtime=[]
for p in sorted((R/'viewer').rglob('*')):
 if p.is_file():runtime.append((str(p.relative_to(R/'viewer')),p.read_bytes()))
runtime.append(('README.txt',b'Isolated Rev15W fixture component. Serve this directory over local HTTP. Diagnostic floor/lights are not the native environment. Full-world website integration remains pending.'))
rp=R/'delivery/Breeze-Rev15W-Streetlights-Runtime-Review.zip';runtimeProof=zip_files(rp,runtime)
(R/'evidence/git-state.txt').write_text(subprocess.check_output(['git','status','--porcelain=v1'],cwd=repo,text=True))
rows=[]
for folder in ['source','evidence','references','renders','viewer']:
 for p in sorted((R/folder).rglob('*')):
  if p.is_file() and p.suffix not in ['.lock','.pyc']:rows.append((str(p.relative_to(repo)),p.read_bytes()))
for p in sorted((R/'delivery').iterdir()):
 if p.is_file() and p.suffix in ['.blend','.glb','.json']:rows.append((str(p.relative_to(repo)),p.read_bytes()))
for name in ['REPORT.md','RESTORE.md']:rows.append((str((R/name).relative_to(repo)),(R/name).read_bytes()))
pdf=R/'review/Breeze-Gully-Only-Streetlights-and-Wires-Rev15W.pdf';rows.append((str(pdf.relative_to(repo)),pdf.read_bytes()))
for file in ['document-before-final-handoff.json','document-after-format.json']:
 rows.append((str(R.relative_to(repo)/'document-snapshots'/file),(R/'restore'/file).read_bytes()))
for file in ['AGENTS.md','docs/gullyverse-backup-policy.md','docs/gullyverse-backup-target.json','docs/gullyverse-streetlights-current.md','docs/gullyverse-shared-document-current.md','docs/gullyverse-consolidated-handoff-current.md']:
 p=repo/file;rows.append((file,p.read_bytes()))
out=R/'delivery/Breeze-Rev15W-Gully-Streetlights-Checkpoint.zip';proof=zip_files(out,rows);result={'status':'PASS','source':proof,'runtime':runtimeProof,'nativeRecovery':'Verified original T2 complete native plus authenticated incremental chain to V2 and W source reconstruction; all dependency IDs/hashes in source/restore-manifest.json','nativeRecoveryTest':'PASS','allChecksPassedBeforePackaging':True};(R/'evidence/checkpoint-package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
