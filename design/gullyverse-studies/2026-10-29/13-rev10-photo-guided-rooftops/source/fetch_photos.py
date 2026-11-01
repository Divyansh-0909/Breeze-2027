from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures
from PIL import Image
O=Path(__file__).resolve().parents[1];refs=json.loads((O/'source/PHOTO-SOURCE-URLS.json').read_text())
def get(r):
 u=r['sourceUrl'];full=u
 if 'wikimedia.org/wikipedia/commons/thumb/' in u:full=u.replace('/thumb/','/').rsplit('/',1)[0]
 if 'prismic.io' in u:full=u.split('?')[0]
 attempts=[]
 for label,url in [('original',full),('providedImage',u)]:
  if attempts and full==u:break
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'GullyversePrivateReferenceStudy/1.0 (documented visual research)'})
   with urllib.request.urlopen(req,timeout=50)as response:raw=response.read();status=response.status
   p=O/'references'/(r['id']+'.image');p.write_bytes(raw);im=Image.open(p);im.load();fmt=im.format;ext={'JPEG':'jpg','PNG':'png','WEBP':'webp','AVIF':'avif'}.get(fmt,'image');q=p.with_suffix('.'+ext);p.rename(q)
   return {**r,'status':'AVAILABLE','used':label,'retrievedUrl':url,'file':str(q.relative_to(O)),'bytes':len(raw),'dimensions':list(im.size),'format':fmt,'sha256':hashlib.sha256(raw).hexdigest(),'attempts':attempts}
  except Exception as e:attempts.append({'url':url,'errorType':type(e).__name__,'detail':str(e)[:180]})
 return {**r,'status':'UNAVAILABLE','attempts':attempts}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(get,refs))
(O/'evidence/photo-availability.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
