import json,hashlib,zipfile
from pathlib import Path
O=Path(__file__).resolve().parents[1];groups={'Rev12-01-Packed-Editable-Master.zip':[O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend'],'Rev12-03-Authentic-Rev11-Input.zip':[O/'inputs/Rev11-original.blend'],'Rev12-04-Art-Validator-and-Baselines.zip':[p for pp in[O/'source/prior-pilot',O/'baseline']for p in pp.rglob('*')if p.is_file()and '__pycache__'not in str(p)]};chunks=[];current=[];size=0
for p in sorted((O/'references').glob('*')):
 if current and size+p.stat().st_size>27_500_000:chunks.append(current);current=[];size=0
 current.append(p);size+=p.stat().st_size
if current:chunks.append(current)
for i,files in enumerate(chunks,5):groups[f'Rev12-{i:02}-Original-Photo-References.zip']=files
items=[]
for name,files in groups.items():
 path=O/'delivery'/name
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
  for p in files:z.write(p,p.relative_to(O))
 assert path.stat().st_size<28_000_000,(name,path.stat().st_size())
 items.append({'name':name,'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'folder':'checkpoint','save':str(O/'download-back'/name)})
(O/'checkpoint/static-archive-items.json').write_text(json.dumps(items,indent=2));print('STATIC_PACKAGED',[(r['name'],r['bytes'])for r in items])
