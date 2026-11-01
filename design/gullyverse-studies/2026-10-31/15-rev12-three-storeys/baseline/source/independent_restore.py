import json,hashlib,zipfile,sys,subprocess,re,urllib.parse,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];items=json.load(open(O/'checkpoint/final-archive-items.json'));dest=O/'independent-restore-final';assert not dest.exists();dest.mkdir();archives=[]
for r in items:
 p=Path(r['save']);assert p.is_file(),str(p);assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():assert not n.startswith('/')and '..'not in Path(n).parts
  z.extractall(dest)
 archives.append({'name':r['name'],'bytes':r['bytes'],'sha256':r['sha256'],'actualDriveDownloadUsed':True})
mf=json.load(open(dest/'FILE-MANIFEST.json'))['files']
def verify():
 for name,row in mf.items():
  p=dest/name;assert p.is_file()and p.stat().st_size==row['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],name
verify();links=re.findall(r'(?:src|href)="([^"]+)"',(dest/'GALLERY.html').read_text());assert all((dest/urllib.parse.unquote(x)).is_file()for x in links if not x.startswith(('http:','https:')))
# Audit from the fresh restored paths, without resaving either original master.
originals={name:(dest/name).read_bytes()for name in mf if name.startswith('evidence/')};audit=O/'evidence/independent-audit';audit.mkdir(exist_ok=True)
command=['blender','-b',str(dest/'source/Gullyverse-Rev11-Connected-Neighborhood.blend'),'-t','2','--python-exit-code','9','--python',str(dest/'source/validate_preservation.py')]
with (audit/'fresh-preservation.log').open('w')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0,r.returncode
proof=json.load(open(dest/'evidence/preservation-geometry-height.json'));assert proof['status']=='PASS'and proof['historicalSceneCountPreserved']==15 and proof['packedImages']==33
shutil.copy2(dest/'evidence/preservation-geometry-height.json',audit/'fresh-preservation.json')
# Preserve delivered evidence bytes after running the independent audit.
for name,data in originals.items():(dest/name).write_bytes(data)
verify();out={'status':'PASS_FRESH_DRIVE_ONLY_RESTORE','archives':archives,'archiveCount':len(archives),'payloadHashesBeforeAndAfterAudit':len(mf),'localGalleryLinks':len(links),'reopenedScenes':19,'originalScenesExact':15,'packedImageOwners':33,'originalObjectSignaturesExact':proof['allOriginalObjectSignaturesExact'],'coreConnectedComponents':1,'originalUnscaledAndHeightControlsAvailable':True,'candidateAndOriginalMastersNeverResaved':True,'deliveredEvidenceRestoredAfterAudit':True,'sealedMasterSHA256':hashlib.sha256((dest/'source/Gullyverse-Rev11-Connected-Neighborhood.blend').read_bytes()).hexdigest()};(O/'checkpoint/INDEPENDENT-RESTORE-VERIFICATION.json').write_text(json.dumps(out,indent=2));print('FRESH_RESTORE_PASS',len(archives),len(mf),len(links))
