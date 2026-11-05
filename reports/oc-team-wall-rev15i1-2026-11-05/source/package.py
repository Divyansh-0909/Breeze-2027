from pathlib import Path
import hashlib,json,zipfile
O=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
files=[O/n for n in ['REPORT.md','RESTORE.md','GALLERY.html']]
for folder in ['source','inputs','evidence','renders','review','delivery','viewer']:
 for p in(O/folder).rglob('*'):
  if not p.is_file()or'__pycache__'in p.parts or p.suffix=='.log':continue
  if 'browser-recordings'in p.parts or p.name in ['lead-names-draft-unused.png','browser-first.png']:continue
  files.append(p)
rows=[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(set(files))];(O/'FILE-MANIFEST.json').write_text(json.dumps(rows,indent=2));plans=[]
for fn in ['inputs/Rev15I-authentic.blend','delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend']:
 p=O/fn
 with p.open('rb')as f:
  i=0
  while b:=f.read(25000000):
   i+=1;q=O/'archive'/f'{p.name}.part{i:03d}';q.write_bytes(b);plans.append({'name':q.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'part':i,'restorePath':fn,'local':str(q)})
for label,selection in [('Source-Art-Evidence',[p for p in files if p.relative_to(O).parts[0]not in['renders','review','delivery','viewer']and p.suffix!='.blend']+[O/'FILE-MANIFEST.json']),('Full-Screenshots',[p for p in files if p.relative_to(O).parts[0]=='renders']),('Review',[p for p in files if p.relative_to(O).parts[0]=='review']),('Interactive-Viewer',[p for p in files if p.relative_to(O).parts[0]=='viewer'])]:
 bins=[];current=[];size=0
 for p in sorted(set(selection)):
  assert p.stat().st_size<24000000,(p,p.stat().st_size)
  if current and size+p.stat().st_size>21000000:bins.append(current);current=[];size=0
  current.append(p);size+=p.stat().st_size
 if current:bins.append(current)
 for i,ps in enumerate(bins,1):
  q=O/'archive'/f'Rev15I1-{label}-{i:02d}.zip'
  with zipfile.ZipFile(q,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in ps:z.write(p,str(p.relative_to(O)))
  assert q.stat().st_size<25000000;plans.append({'name':q.name,'bytes':q.stat().st_size,'sha256':sha(q),'local':str(q)})
(O/'checkpoint/upload-plan.json').write_text(json.dumps(plans,indent=2));print(json.dumps({'payloadFiles':len(rows),'requiredComponents':len(plans),'bytes':sum(r['bytes']for r in plans),'archives':[(r['name'],r['bytes'])for r in plans]},indent=2))
