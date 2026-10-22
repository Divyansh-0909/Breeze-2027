"""Read one JSON instruction from stdin; never print a raw signed fetch URL.
Used after archive freeze; upload success is not external verification.
"""
from pathlib import Path
import sys,json,hashlib,datetime,urllib.request
W=Path('/workspace/recovery-fidelity/2026-10-19/checkpoint');M=W/'upload-manifest.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(data):
 data['updatedUTC']=now();data['verificationStatus']='verified'if data.get('sealed')and all(r['status']=='verified'for r in data['files'])else'pending'
 t=M.with_suffix('.tmp');t.write_text(json.dumps(data,indent=2)+'\n');t.replace(M)
def main():
 operation=sys.argv[1];request=json.loads(sys.stdin.readline());data=json.loads(M.read_text())
 if operation=='register':
  assert not data.get('sealed')
  assert not any(r['name']==request['name']for r in data['files']);request['status']='pending';data['files'].append(request);save(data);print(json.dumps({'registered':request['name']}));return
 if operation=='seal':data['sealed']=True;save(data);print(json.dumps({'status':data['verificationStatus'],'files':len(data['files'])}));return
 item=next(r for r in data['files']if r['name']==request['name'])
 if operation=='uploaded':
  assert request['parent_id']==item['parent_id'],'Unexpected upload parent'
  item.update(status='uploaded-verification-pending',drive_id=request['id'],drive_url=request['url'],uploadedUTC=now());save(data);print(json.dumps({'name':item['name'],'status':item['status']}));return
 assert operation=='verify';meta=request['metadata']
 assert meta['id']==item['drive_id']and meta['name']==item['name']and int(meta['size'])==item['bytes']and meta['parents']==[item['parent_id']],'Remote identity/name/size/parent mismatch'
 digest=hashlib.sha256();length=0
 with urllib.request.urlopen(request['download_url'],timeout=60)as stream:
  while True:
   chunk=stream.read(4*1024*1024)
   if not chunk:break
   digest.update(chunk);length+=len(chunk)
 assert length==item['bytes']and digest.hexdigest()==item['sha256'],'Full download-back bytes/SHA mismatch'
 item.update(status='verified',verifiedUTC=now(),remoteContentBytes=length,remoteContentSHA256=digest.hexdigest(),verificationMethod='Authenticated raw Drive fetch; full content downloaded back and SHA-256 hashed; metadata ID/name/parent/size checked')
 save(data);print(json.dumps({'name':item['name'],'status':'verified','bytes':length,'verifiedFiles':sum(r['status']=='verified'for r in data['files']),'totalFiles':len(data['files'])}))
if __name__=='__main__':
 try:main()
 except Exception as error:
  print(json.dumps({'status':'failed','errorType':type(error).__name__,'message':str(error)if isinstance(error,AssertionError)else'Remote verification failed; signed URL omitted'}));sys.exit(1)
