"""Five complete complementary archives. No credentials/dependencies/build outputs."""
from pathlib import Path
import json,hashlib,zipfile
O=Path(__file__).resolve().parents[1];D=Path('/dev/shm/terrace-rev08/final-delivery');D.mkdir(exist_ok=True);cfg=json.loads((O/'source/BASELINE.json').read_text());groups=[{}, {}, {}, {}, {}]
def add(k,p,name=None):
 p=Path(p);assert p.is_file(),p;name=name or str(p.relative_to(O));assert name not in groups[k];groups[k][name]=p
for p in(O/'source').rglob('*'):
 if p.is_file()and not p.is_symlink()and 'prior-pilot'not in p.parts and '__pycache__'not in p.parts:add(0,p)
for p in(O/'evidence').rglob('*'):
 if p.is_file():add(0,p)
for name in['REPORT.md','SOURCE-AUDIT.md','RESTORE.md','GALLERY.html']:add(0,O/name)
add(1,Path(cfg['path']),'source/baseline/Wider-Realism.blend')
for name in['Rev05C-Approved-Corrugated-Art.blend','website-baseline.json']:
 add(1,O/'source/prior-pilot/baseline'/name,'source/prior-pilot/baseline/'+name)
for edition in['before','architecture']:
 for p in(O/'renders'/edition).glob('*.png'):add(2,p)
for edition in['crowd','source-diagnostics','props-a','props-b']:
 for p in(O/'renders'/edition).glob('*.png'):add(3,p)
for p in(O/'review').glob('*'):
 if p.is_file():add(4,p)
for edition in['walk-final','walk','diagnostics']:
 for p in(O/'renders'/edition).glob('*.png'):add(4,p)
manifest=[];seen=set()
for k,g in enumerate(groups):
 for name,p in sorted(g.items()):
  assert name not in seen,name;seen.add(name);manifest.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archiveNumber':k+1})
(O/'FILE-MANIFEST.json').write_text(json.dumps({'version':1,'masterSHA256':'f130611ac54090baf6e25052c222b53a5a243414e1e49686bc1882dc3d6f7f50','payloadFiles':manifest,'selfHashExcluded':True,'allSourceAndAssetsAreActualPayloads':True},indent=2));add(0,O/'FILE-MANIFEST.json')
names=['Rev08-01-Source-and-Audit.zip','Rev08-02-Protected-Baseline-Masters.zip','Rev08-03-Architecture-Matched-PNGs.zip','Rev08-04-Crowd-and-Source-PNGs.zip','Rev08-05-Reviews-and-Walk.zip'];items=[]
for k,(g,name)in enumerate(zip(groups,names)):
 dest=D/name
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3)as z:
  for target,p in sorted(g.items()):z.write(p,target)
 item={'name':name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'folder':'checkpoint','save':str(D/('downloaded-'+name)),'payloadFiles':len(g),'archiveNumber':k+1};items.append(item)
 print('ARCHIVE',json.dumps(item),flush=True)
(O/'checkpoint/final-archive-items.json').write_text(json.dumps(items,indent=2));(O/'checkpoint/LOCAL-ARCHIVE-INDEX.json').write_text(json.dumps({'allFiveArchivesRequired':True,'archives':items,'manifestPayloadFiles':len(manifest),'rawPayloadBytes':sum(r['bytes']for r in manifest),'directMasterNotSubstituteForSourceEvidence':True},indent=2));print('PACKAGED',len(manifest),flush=True)
