import json,sys,urllib.request,hashlib,pathlib
for line in sys.stdin:
 try:
  x=json.loads(line);h=hashlib.sha256();size=0;p=pathlib.Path(x['save']);p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('wb')as f,urllib.request.urlopen(x['url'],timeout=120)as r:
   while b:=r.read(1048576):h.update(b);size+=len(b);f.write(b)
  q={'id':x['id'],'name':x['name'],'bytes':size,'sha256':h.hexdigest(),'expectedSHA256Provided':bool(x.get('sha256')),'verified':size==x['bytes']and(not x.get('sha256')or h.hexdigest()==x['sha256'])}
  pathlib.Path(x['receipt']).write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
 except Exception as e:print(json.dumps({'verified':False,'errorType':type(e).__name__}),flush=True)
