"""Complementary bounded ZIPs; every file is an actual payload, no symlink pointers."""
from pathlib import Path
import json,hashlib,zipfile,fitz,shutil
O=Path(__file__).resolve().parents[1];D=Path('/dev/shm/rev10/delivery');D.mkdir(exist_ok=True);groups=[{}for _ in range(12)]
def add(k,p,name=None):
 p=Path(p);assert p.is_file(),p;name=name or str(p.relative_to(O));assert name not in groups[k];groups[k][name]=p
for p in (O/'source').rglob('*'):
 if p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts and 'baseline'not in p.parts and 'prior-pilot'not in p.parts:add(0,p)
add(0,O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend')
for p in (O/'evidence').rglob('*'):
 if p.is_file()and p.name not in ['motion-runner.log']:add(0,p)
for n in ['REPORT.md','REFERENCE-ANALYSIS.md','PHOTO-TO-RENDER-MATRIX.csv','FURNITURE-SOURCE-STATUS.md','RESTORE.md','GALLERY.html','DELIVERY-COMPLETION-R1.md']:add(0,O/n)
add(1,O/'source/Rev09-Original.blend')
for p in (O/'source/prior-pilot/baseline').glob('*'):
 if p.is_file():add(1,p,'source/prior-pilot/baseline/'+p.name)
for p in (O/'references').glob('*.jpg'):
 if 'inspection'in p.name:continue
 k=3 if p.stem=='R3'else 4 if p.stem in['R5','R6']else 2;add(k,p)
for k,ed in enumerate(['before','A','B'],5):
 for p in (O/'renders'/ed).glob('*.png'):add(k,p)
for k,ed in enumerate(['A','B'],8):
 for p in (O/('renders/walk-'+ed)).glob('*.png'):add(k,p)
 add(k,O/('review/Rev10-'+ed+'-40s-Offline-Walk.mp4'))
for p in (O/'review').glob('*.pdf'):add(10,p)
add(11,Path('/dev/shm/rev10/Rev09-Phone-Review.pdf'),'references/Rev09-Original-24-page-Review.pdf')
for n in ['03-aerial','04-front','08-left-house']:add(11,Path('/dev/shm/rev10/rev09-images/renders/after')/(n+'.png'),'references/Rev09-original-stills/'+n+'.png')
manifest=[];seen=set()
for k,g in enumerate(groups):
 for name,p in sorted(g.items()):
  assert name not in seen,name;seen.add(name);manifest.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archiveNumber':k+1})
master=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';sha=hashlib.sha256(master.read_bytes()).hexdigest();assert sha==json.loads((O/'evidence/authoring.json').read_text())['masterSHA256']
(O/'FILE-MANIFEST.json').write_text(json.dumps({'version':1,'masterSHA256':sha,'payloadFiles':manifest,'selfHashExcluded':True,'allAssetsActualPayloadsNotLFSPointers':True,'allPhotosPrivateReferenceOnly':True},indent=2));add(0,O/'FILE-MANIFEST.json')
names=['Source-and-Technical-Evidence','Protected-Original-Masters','Real-Photos-R1-R2-R4','Real-Photo-R3','Real-Photos-R5-R6','Before-PNGs','Proposal-A-PNGs','Proposal-B-PNGs','Proposal-A-Actual-Walk','Proposal-B-Actual-Walk','Review-PDFs','Historical-Rev09-Review'];items=[]
for k,(g,label)in enumerate(zip(groups,names)):
 oldItems=json.loads((O/'checkpoint/INITIAL-OCT29-ARCHIVE-ITEMS.json').read_text())
 reused=k in [1,2,3,4,5,11]
 name=(f'Rev10-{k+1:02d}-{label}.zip' if reused else f'Rev10-R1-{k+1:02d}-{label}.zip');dest=D/name
 if reused:
  original=next(r for r in oldItems if r['archiveNumber']==k+1);download=D/('downloaded-'+original['name'])
  assert download.stat().st_size==original['bytes'] and hashlib.sha256(download.read_bytes()).hexdigest()==original['sha256']
  with zipfile.ZipFile(download)as z:
   assert set(z.namelist())==set(g),name
   for target,p in g.items():assert hashlib.sha256(z.read(target)).digest()==hashlib.sha256(p.read_bytes()).digest(),target
  shutil.copyfile(download,dest)
 else:
  with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3)as z:
   for target,p in sorted(g.items()):z.write(p,target)
 assert dest.stat().st_size<32_000_000,(name,dest.stat().st_size)
 item={'name':name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'folder':('checkpoint' if reused else 'completion'),'save':str(D/('downloaded-'+name)),'payloadFiles':len(g),'archiveNumber':k+1};items.append(item);print('ARCHIVE',json.dumps(item),flush=True)
(O/'checkpoint/final-archive-items.json').write_text(json.dumps(items,indent=2));pdfs=[]
for p in (O/'review').glob('*.pdf'):
 d=fitz.open(p);assert all(len(page.get_text().strip())>25 for page in d);pdfs.append({'name':p.name,'pages':len(d),'bytes':p.stat().st_size})
(O/'checkpoint/LOCAL-PACKAGE-INDEX.json').write_text(json.dumps({'allNumberedArchivesRequired':True,'archives':items,'manifestPayloadFiles':len(manifest),'rawPayloadBytes':sum(r['bytes']for r in manifest),'pdfs':pdfs},indent=2));(O/'checkpoint/PACKAGES-DONE.json').write_text(json.dumps({'status':'PASS','payloadFiles':len(manifest),'archives':len(items),'pdfs':pdfs}));print('PACKAGED',len(manifest),flush=True)
