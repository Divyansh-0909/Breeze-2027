import sys,json,urllib.request,pathlib,hashlib
for line in sys.stdin:
 try:
  row=json.loads(line)
  with urllib.request.urlopen(row['url'],timeout=60)as response:data=response.read()
  p=pathlib.Path(row['path']);p.write_bytes(data);print(json.dumps({'status':'saved','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}),flush=True)
 except Exception as e:print(json.dumps({'status':'failed','error':type(e).__name__}),flush=True)
