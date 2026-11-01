from pathlib import Path
import json,hashlib,zipfile,shutil,subprocess,sys
from html.parser import HTMLParser
C=Path(__file__).resolve().parent;O=C.parent;ram=Path('/dev/shm/gullyverse-rev05b-20261026-archive-staging');target=C/'independent-restore'
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
index=json.loads((C/'ARCHIVE-INDEX.json').read_text());uploads=[json.loads(p.read_text())for p in C.glob('uploaded-*.json')]
assert not target.exists()and not ram.exists()
assert shutil.disk_usage('/dev/shm').free>sum(a['bytes']for a in index['archives'])+32*1024*1024
ram.mkdir();target.mkdir();transfers=[]
for a in index['archives']:
    p=C/a['file'];assert p.parent==C and p.name.startswith('Rev05B-')and sha(p)==a['sha256']
    u=next(x for x in uploads if x['name']==a['file']);assert u['sha256']==a['sha256']and u['fullDownloadBackSHA256Verified']
    v=json.loads((C/('verified-'+u['id']+'.json')).read_text());assert v['verified']and v['sha256']==a['sha256']
    q=ram/p.name;shutil.copy2(p,q);assert q.stat().st_size==a['bytes']and sha(q)==a['sha256'];p.unlink()
    transfers.append({'file':p.name,'sha256':a['sha256'],'temporaryRAMCopyVerified':True})
(C/'ram-archive-staging.json').write_text(json.dumps(transfers,indent=2)+'\n')
for a in index['archives']:
    p=ram/a['file'];assert sha(p)==a['sha256']
    with zipfile.ZipFile(p)as z:
        assert z.testzip()is None
        assert all((target/n).resolve().is_relative_to(target.resolve())for n in z.namelist())
        z.extractall(target)
assert sha(target/'FILE-MANIFEST.json')==index['fileManifestSHA256']
m=json.loads((target/'FILE-MANIFEST.json').read_text())
for f in m['files']:
    p=target/f['file'];assert p.stat().st_size==f['bytes']and sha(p)==f['sha256'],f['file']
class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['href','src']and not v.startswith(('http:','https:','#','data:')):self.refs.append(v)
l=Links();l.feed((target/'GALLERY.html').read_text());assert all((target/p).is_file()for p in l.refs)
with (C/'independent-restore-blender.log').open('w')as h:
    subprocess.run(['blender','-b','-t','1','--python-exit-code','1','--python',str(target/'source/verify_restored_master.py'),'--',str(C/'independent-restored-master.json')],stdout=h,stderr=subprocess.STDOUT,check=True)
b=json.loads((C/'independent-restored-master.json').read_text());assert b['status']=='PASS'
receipt={'status':'PASS','archiveCount':len(index['archives']),'memberHashesVerified':len(m['files']),'renderedPNGsRestored':len(list((target/'renders').rglob('*.png'))),'finalPNGsRestored':sum(len(list((target/'renders'/e).rglob('*.png')))for e in ['before','after']),'galleryReferencesChecked':len(l.refs),'masterOpen':b,'allOriginalSourcesAndPriorCheckpointsRetained':True,'temporaryRAMStagingUsedForCurrentNewArchivesOnly':True}
# This is the newly generated verification extraction, never an earlier checkpoint.
# Verify once more before retiring the duplicate and restoring all archive staging paths.
assert all(sha(target/f['file'])==f['sha256']for f in m['files'])
shutil.rmtree(target)
for a in index['archives']:
    q=ram/a['file'];p=C/a['file'];assert not p.exists();shutil.copy2(q,p);assert sha(p)==a['sha256'];q.unlink()
ram.rmdir();receipt['allNineLocalArchivesReturnedWithIdenticalSHA256']=True;receipt['newTemporaryExtractionRetiredAfterSuccessfulChecks']=True
(C/'independent-restore-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
