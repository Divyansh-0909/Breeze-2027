from pathlib import Path
import json,hashlib,zipfile,subprocess,os,re
O=Path(__file__).resolve().parents[1];C=O/'checkpoint'
T=Path('/dev/shm/Rev05C-independent-restore-20261026')
assert not T.exists(),'Never overwrite a pre-existing restoration directory.'
T.mkdir()
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
index=json.loads((C/'ARCHIVE-INDEX.json').read_text())
archives=[]
for a in index['archives']:
 p=Path(a['path']);assert p.stat().st_size==a['bytes']and sha(p)==a['sha256']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  for n in z.namelist():assert not Path(n).is_absolute()and'..'not in Path(n).parts
  z.extractall(T)
 archives.append({'name':a['name'],'bytes':a['bytes'],'sha256':a['sha256']})
m=json.loads((T/'FILE-MANIFEST.json').read_text())
for r in m['files']:
 p=T/r['path'];assert p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],r['path']
gallery=(T/'GALLERY.html').read_text();links=re.findall(r'(?:href|src)="([^"]+)"',gallery)
assert all((T/x).is_file()for x in links)
master=T/'source/Gullyverse-Rev05C-Interior-Support-Off.blend'
env=os.environ.copy();env.update(LP_NUM_THREADS='2',OMP_NUM_THREADS='2')
with(C/'independent-master-open.log').open('w')as h:
 subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','1','--python',str(T/'source/verify_restored_master.py'),'--',str(C/'independent-master-open.json')],stdout=h,stderr=subprocess.STDOUT,env=env,check=True)
for r in m['files']:assert sha(T/r['path'])==r['sha256'],r['path']
result={'status':'PASS','scope':'Partial lighting checkpoint only; graffiti source gate unresolved','independentFreshDirectory':str(T),'archives':archives,'memberHashesVerified':len(m['files']),'originalPNGs':len(list((T/'renders').rglob('*.png'))),'galleryRelativeReferences':len(links),'packedMasterOpened':True,'membersUnchangedAfterOpen':True}
(C/'independent-restore-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('INDEPENDENT_PARTIAL_RESTORE_PASS',len(m['files']),len(links),flush=True)
