import json,sys,urllib.request,hashlib,pathlib
for line in sys.stdin:
 try:
  x=json.loads(line);h=hashlib.sha256();size=0;p=pathlib.Path(x['save'])if x.get('save')else None
  f=p.open('wb')if p else None
  with urllib.request.urlopen(x['url'],timeout=120)as r:
   while True:
    b=r.read(1048576)
    if not b:break
    h.update(b);size+=len(b)
    if f:f.write(b)
  if f:f.close()
  r={'id':x['id'],'name':x['name'],'bytes':size,'sha256':h.hexdigest(),'verified':size==x['bytes']and h.hexdigest()==x['sha256']}
  pathlib.Path(x['receipt']).write_text(json.dumps(r,indent=2)+'\n')
  print(json.dumps(r),flush=True)
 except Exception as e:print(json.dumps({'verified':False,'errorType':type(e).__name__}),flush=True)
