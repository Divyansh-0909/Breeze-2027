import json,hashlib,zipfile
from pathlib import Path
O=Path(__file__).resolve().parents[1];items=json.loads((O/'checkpoint/static-archive-items.json').read_text())+json.loads((O/'checkpoint/media-archive-items.json').read_text());manifest={}
def record(n,data):
 r={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 if n in manifest:assert manifest[n]==r,n
 manifest[n]=r
for row in items:
 with zipfile.ZipFile(row['path'])as z:
  for n in z.namelist():
   if not n.endswith('/'):record(n,z.read(n))
def chunks(files,prefix):
 groups=[];part=[];size=0
 for p in files:
  if part and size+p.stat().st_size>26_000_000:groups.append(part);part=[];size=0
  part.append(p);size+=p.stat().st_size
 if part:groups.append(part)
 return {prefix+('-'+str(i+1)if len(groups)>1 else'')+'.zip':pp for i,pp in enumerate(groups)}
groups=chunks(sorted((O/'renders/new').glob('*.png')),'Rev12-11-New-Matched-PNGs');groups.update(chunks(sorted(p for p in(O/'review').glob('*')if p.is_file()and p.suffix in['.pdf','.png']),'Rev12-12-Review-PDFs-and-Diagnostics'))
source=list((O/'source').glob('*.py'))+list((O/'source').glob('*.json'))+[p for p in(O/'evidence').rglob('*')if p.is_file()and '__pycache__'not in str(p)and 'independent-audit'not in str(p)]+[O/n for n in['REPORT.md','RESTORE.md','REFERENCE-ANALYSIS.md','APPROVED-PROMPT.txt','GALLERY.html']]
groups['Rev12-02-Source-and-Technical-Evidence.zip']=source
for files in groups.values():
 for p in files:record(str(p.relative_to(O)),p.read_bytes())
(O/'FILE-MANIFEST.json').write_text(json.dumps({'status':'COMPLETE_PAYLOAD_MANIFEST','masterSHA256':'101447553e9c487b860198465880fa21471908828b923da4e465c654d9ad51fc','files':manifest,'selfNotHashed':'Containing archive SHA protects this manifest; final Drive/restore receipts are external sidecars to avoid circular hashes.'},indent=2));groups['Rev12-02-Source-and-Technical-Evidence.zip'].append(O/'FILE-MANIFEST.json')
new=[]
for name,files in groups.items():
 p=O/'delivery'/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
  for f in files:z.write(f,f.relative_to(O))
 assert p.stat().st_size<28_000_000,(name,p.stat().st_size())
 new.append({'name':name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'folder':'checkpoint','save':str(O/'download-back'/name)})
items+=new;items.sort(key=lambda x:x['name']);(O/'checkpoint/final-archive-items.json').write_text(json.dumps(items,indent=2));(O/'checkpoint/remaining-archive-items.json').write_text(json.dumps(new,indent=2));print('FINAL_PACKAGED',len(items),len(manifest),[(x['name'],x['bytes'])for x in new])
