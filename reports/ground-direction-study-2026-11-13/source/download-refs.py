from pathlib import Path
import urllib.request,json,concurrent.futures
from PIL import Image
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'references/sources.json').read_text())
def fetch(x):
 try:
  req=urllib.request.Request(x['imageUrl'],headers={'User-Agent':'Mozilla/5.0'});r=urllib.request.urlopen(req,timeout=35)
  p=R/x['local'];p.write_bytes(r.read())
  with Image.open(p) as im:im.verify()
  with Image.open(p) as im:x.update(local=str(p.relative_to(R)),dimensions=list(im.size),format=im.format)
  x['status']='DOWNLOADED'
 except Exception as e:x.update(status='FAILED',error=str(e)[:250])
 return x
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:out=list(pool.map(fetch,rows))
(R/'references/downloads.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{k:x.get(k) for k in ['key','status','dimensions','error']} for x in out],indent=2))
