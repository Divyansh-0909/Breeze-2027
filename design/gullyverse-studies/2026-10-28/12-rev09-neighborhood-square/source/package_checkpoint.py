"""Five complementary ZIPs with actual packed masters and all review payloads."""
from pathlib import Path
import json,hashlib,zipfile
O=Path(__file__).resolve().parents[1];D=Path('/dev/shm/rev09/delivery');D.mkdir(exist_ok=True);cfg=json.loads((O/'source/BASELINE.json').read_text());groups=[{}, {}, {}, {}, {}]
def add(k,p,name=None):
 p=Path(p);assert p.is_file(),p;name=name or str(p.relative_to(O));assert name not in groups[k];groups[k][name]=p
for p in (O/'source').rglob('*'):
 if p.is_file()and not p.is_symlink()and 'prior-pilot'not in p.parts and '__pycache__'not in p.parts:add(0,p)
for p in (O/'evidence').rglob('*'):
 if p.is_file()and 'furniture-inventory'not in p.parts and p.name!='review-finish-runner.log':add(0,p)
for name in ['REPORT.md','FURNITURE-SOURCE-STATUS.md','RESTORE.md','GALLERY.html']:add(0,O/name)
add(1,Path(cfg['path']),'source/baseline/Rev08-Protected-Original.blend')
for p in (O/'source/prior-pilot/baseline').glob('*'):
 if p.is_file():add(1,p,'source/prior-pilot/baseline/'+p.name)
for p in (Path(cfg['priorPhase'])/'source/website').glob('*'):
 if p.is_file():add(1,p,'source/historical-website-source/'+p.name)
for p in (O/'renders/before').glob('*.png'):add(2,p)
for edition in ['after','web-history']:
 for p in (O/'renders'/edition).glob('*.png'):add(3,p)
for p in (O/'evidence/furniture-inventory').glob('*.png'):add(3,p)
for p in (O/'review').glob('*'):
 if p.is_file():add(4,p)
for p in (O/'renders/walk').glob('*.png'):add(4,p)
manifest=[];seen=set()
for k,g in enumerate(groups):
 for name,p in sorted(g.items()):
  assert name not in seen,name;seen.add(name);manifest.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archiveNumber':k+1})
master=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();assert sha=='3f637b223aff0fd4eb397ae6e51d821ed5de5675cf9707643a1cdf955821ab78'
(O/'FILE-MANIFEST.json').write_text(json.dumps({'version':1,'masterSHA256':sha,'payloadFiles':manifest,'selfHashExcluded':True,'allSourceAndAssetsAreActualPayloads':True},indent=2));add(0,O/'FILE-MANIFEST.json')
names=['Rev09-01-Source-and-Evidence.zip','Rev09-02-Protected-Baseline-Masters.zip','Rev09-03-Before-PNGs.zip','Rev09-04-Square-and-Historical-PNGs.zip','Rev09-05-Reviews-and-Walk.zip'];items=[]
for k,(g,name) in enumerate(zip(groups,names)):
 dest=D/name
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3)as z:
  for target,p in sorted(g.items()):z.write(p,target)
 item={'name':name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'folder':'checkpoint','save':str(D/('downloaded-'+name)),'payloadFiles':len(g),'archiveNumber':k+1};items.append(item);print('ARCHIVE',json.dumps(item),flush=True)
(O/'checkpoint/final-archive-items.json').write_text(json.dumps(items,indent=2));(O/'checkpoint/LOCAL-ARCHIVE-INDEX.json').write_text(json.dumps({'allFiveArchivesRequired':True,'archives':items,'manifestPayloadFiles':len(manifest),'rawPayloadBytes':sum(r['bytes']for r in manifest),'noCredentialsOrBuildOutputs':True},indent=2));print('PACKAGED',len(manifest),flush=True)
