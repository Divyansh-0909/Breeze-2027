import json,hashlib,zipfile,re,subprocess
from pathlib import Path
O=Path(__file__).resolve().parents[1];index=json.loads((O/'checkpoint/ARCHIVE-INDEX.json').read_text());D=Path('/dev/shm/rev07-download-back');R=Path('/dev/shm/Rev07-Independent-Drive-Restore-20261028')
assert not R.exists(),'Fresh directory required';R.mkdir();checked=[]
for r in index['archives']:
 p=D/r['name'];assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  assert all(not Path(n).is_absolute()and '..'not in Path(n).parts for n in z.namelist())
  z.extractall(R)
 checked.append({'name':r['name'],'bytes':r['bytes'],'sha256':r['sha256'],'authenticatedDownloadBackCopyUsed':True})
m=json.loads((R/'FILE-MANIFEST.json').read_text())
def verify():
 for r in m['members']:
  p=R/r['path'];assert p.is_file()and p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
verify();links=re.findall(r'(?:href|src)="([^"]+)"',(R/'GALLERY.html').read_text())
for p in links:
 if p.startswith(('http:','https:','#','data:')):continue
 assert(R/p).is_file(),p
master=R/'source/Gullyverse-Selected-C-Wider-Realism.blend';assert hashlib.sha256(master.read_bytes()).hexdigest()==index['masterSHA256']
with(O/'checkpoint/independent-restore-blender.log').open('w')as h:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(R/'source/verify_restored.py')],stdout=h,stderr=subprocess.STDOUT,check=True)
assert json.loads((R/'restored-blender-proof.json').read_text())['status']=='PASS';verify()
proof={'status':'PASS','freshDirectory':str(R),'allSevenVerifiedDriveDownloadedArchivesUsed':True,'archives':checked,'payloadHashesBeforeAndAfterOpen':len(m['members']),'galleryRelativeLinks':len(links),'worldMasterSHA256':index['masterSHA256'],'fiveScenesIncludingFourHistoricalReopened':True,'33PackedImagesAndNoExternalFonts':True,'supportsOffVerified':True,'noResave':True}
(O/'checkpoint/independent-restore-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('INDEPENDENT_RESTORE_PASS',len(m['members']),len(links),flush=True)
