import json,sys,urllib.request,pathlib,hashlib
for line in sys.stdin:
 try:
  a=json.loads(line);p=pathlib.Path(a['path']);p.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();size=0
  with urllib.request.urlopen(a['url'],timeout=90)as r,p.open('wb')as f:
   while True:
    b=r.read(1048576)
    if not b:break
    f.write(b);h.update(b);size+=len(b)
  result={'key':a['key'],'bytes':size,'sha256':h.hexdigest(),'verified':size==a['bytes']and h.hexdigest()==a['sha256']}
  if a.get('receipt'):pathlib.Path(a['receipt']).write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result),flush=True)
 except Exception as e:print(json.dumps({'error':type(e).__name__}),flush=True)
