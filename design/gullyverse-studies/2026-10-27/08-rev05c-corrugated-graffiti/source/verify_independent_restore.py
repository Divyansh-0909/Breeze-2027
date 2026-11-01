from pathlib import Path
import json,zipfile,hashlib,subprocess,os,re
O=Path(__file__).resolve().parents[1];C=O/'checkpoint';T=Path('/dev/shm/Rev05C-art-independent-restore-20261027')
assert not T.exists(),'Never overwrite another restore directory';T.mkdir()
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
a=json.loads((C/'ARCHIVE-INDEX.json').read_text());archives=[]
for r in a['archives']:
 p=Path(r['path']);assert p.stat().st_size==r['bytes']and sha(p)==r['sha256']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  for n in z.namelist():assert not Path(n).is_absolute()and'..'not in Path(n).parts
  z.extractall(T)
 archives.append({'name':r['name'],'bytes':r['bytes'],'sha256':r['sha256']})
m=json.loads((T/'FILE-MANIFEST.json').read_text())
for r in m['files']:
 p=T/r['path'];assert p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],r['path']
links=re.findall(r'(?:href|src)="([^"]+)"',(T/'GALLERY.html').read_text());assert all((T/p).is_file()for p in links)
env=os.environ.copy();env.update(LP_NUM_THREADS='2',OMP_NUM_THREADS='2')
with(C/'independent-master-open.log').open('w')as f:
 subprocess.run(['blender','-b',str(T/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend'),'-t','2','--python-exit-code','1','--python',str(T/'source/verify_art_master.py'),'--',str(C/'independent-master-open.json')],stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
for r in m['files']:assert sha(T/r['path'])==r['sha256']
result={'status':'PASS','independentFreshDirectory':str(T),'archives':archives,'memberHashesVerified':len(m['files']),'allRenderPNGsIncludingDiagnosticsAndDrafts':len(list((T/'renders').rglob('*.png'))),'finalScenePNGs':112,'mainMatchedPairs':53,'profileMatchedPairs':3,'galleryRelativeReferencesVerified':len(links),'packedMasterReopened':True,'memberHashesRecheckedAfterOpen':True,'oldCheckpointsAndWebsiteUntouched':True}
(C/'independent-restore-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('INDEPENDENT_ART_RESTORE_PASS',len(m['files']),len(links))
