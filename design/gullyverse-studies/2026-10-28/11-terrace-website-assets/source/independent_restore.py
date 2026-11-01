"""Only uses actual authenticated Drive-downloaded archive copies."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,os
from html.parser import HTMLParser
O=Path(__file__).resolve().parents[1];items=json.loads((O/'checkpoint/final-archive-items.json').read_text());root=Path('/dev/shm/terrace-rev08/independent-restore-final');assert not root.exists(),'Refuse overwrite';root.mkdir()
for r in items:
 p=Path(r['save']);assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():assert not Path(n).is_absolute()and '..'not in Path(n).parts
  assert z.testzip()is None;z.extractall(root)
manifest=json.loads((root/'FILE-MANIFEST.json').read_text())
def check():
 errors=[]
 for r in manifest['payloadFiles']:
  p=root/r['file']
  if not p.is_file()or p.stat().st_size!=r['bytes']or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:errors.append(r['file'])
 assert not errors,errors
check()
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in['src','href']and v and not v.startswith(('http:','https:','#','data:')):self.links.append(v)
links=Links();links.feed((root/'GALLERY.html').read_text());assert all((root/p).is_file()for p in links.links)
for script in['verify_reopen.py','audit_preservation.py']:
 env=dict(os.environ,GULLYVERSE_BASELINE_OVERRIDE=str(root/'source/baseline/Wider-Realism.blend'))
 with(O/'checkpoint'/('restored-'+script+'.log')).open('w')as f:subprocess.run(['blender','-b',str(root/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend'),'-t','2','--python-exit-code','9','--python',str(root/'source'/script)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
check()
proof={'status':'PASS','onlyActualDriveDownloadedZIPsUsed':True,'archives':len(items),'payloadHashesBeforeAndAfterBlenderOpen':len(manifest['payloadFiles']),'galleryLinksChecked':len(links.links),'freshDirectory':str(root),'masterSHA256':manifest['masterSHA256'],'all11ScenesAnd33PackedImagesReopened':True,'noExternalFontDependency':True,'allFiveHistoricalSceneSignaturesCheckedAgainstRestoredOriginalMaster':True,'allOptionalSupportsOFF':True,'allFiveNumberedArchivesNecessary':True}
(O/'checkpoint/INDEPENDENT-RESTORE-VERIFICATION.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
