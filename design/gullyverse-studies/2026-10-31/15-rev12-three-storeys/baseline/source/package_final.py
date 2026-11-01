import json,hashlib,zipfile,re
from pathlib import Path
O=Path(__file__).resolve().parents[1];D=O/'delivery';D.mkdir(exist_ok=True);items=[];manifest={}
def record(p,relative,sha=None,size=None):
 data=p.read_bytes()if sha is None else None;row={'sha256':sha or hashlib.sha256(data).hexdigest(),'bytes':size if size is not None else len(data)}
 if relative in manifest:assert manifest[relative]==row,relative
 manifest[relative]=row
def existing(p):
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():
   if n.endswith('/'):continue
   assert not n.startswith('/')and '..'not in Path(n).parts
   data=z.read(n);record(None,n,hashlib.sha256(data).hexdigest(),len(data))
def item(p):return {'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'folder':'completion','save':str(O/'download-back'/p.name)}
# Parts already uploaded/verified are reused byte-for-byte, not repackaged.
base=O/'inputs/Rev11-02-Authentic-Rev10-Input-and-History.zip';existing(base);items.append(dict(item(base),id='1TN7maUGM8qBaZO7LTaMq-F7IXtra9l2S',folder='checkpoint'))
for row in json.load(open(O/'checkpoint/early-archive-items.json'))+json.load(open(O/'checkpoint/media-archive-items.json')):
 p=Path(row['path']);existing(p);items.append(row)
groups={
 'Rev11-R1-10-Height-Control-PNGs.zip':[p for e in['H00','H06','H09']for p in sorted((O/'renders'/e).glob('*.png'))],
 'Rev11-R1-12-Review-PDFs-Diagnostics.zip':sorted(p for p in (O/'review').glob('*')if p.is_file()and p.suffix in['.pdf','.png'])}
source=[p for p in (O/'source').rglob('*')if p.is_file()and '__pycache__'not in str(p)and p.suffix!='.pyc'and(p.suffix!='.blend'or p.name=='Gullyverse-Rev11-Connected-Neighborhood.blend')]
source+=sorted(p for p in (O/'evidence').rglob('*')if p.is_file());source+=[O/n for n in['REPORT.md','RESTORE.md','REFERENCE-ANALYSIS.md','DELIVERY-COMPLETION-R1.md','GALLERY.html']]
groups['Rev11-R1-01-Master-Source-Technical-Evidence.zip']=source
for files in groups.values():
 for p in files:record(p,str(p.relative_to(O)))
payload={'status':'PAYLOAD_MANIFEST','sealedMasterSHA256':'b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd','files':manifest,'selfNotHashed':'Manifest is protected by its containing archive SHA; final index/receipts are sidecars to avoid circular hashes.'};(O/'FILE-MANIFEST.json').write_text(json.dumps(payload,indent=2)+'\n')
groups['Rev11-R1-01-Master-Source-Technical-Evidence.zip'].append(O/'FILE-MANIFEST.json')
for name,files in groups.items():
 p=D/name
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
  for f in files:z.write(f,f.relative_to(O))
 assert p.stat().st_size<28_000_000,(name,p.stat().st_size());items.append(item(p))
items.sort(key=lambda r:int(re.search(r'(?:R1-|Rev11-)(\d\d)-',r['name']).group(1)));assert len(items)==12
(O/'checkpoint/final-archive-items.json').write_text(json.dumps(items,indent=2));print('FINAL_PACKAGE',len(items),len(manifest),[(r['name'],r['bytes'])for r in items])
