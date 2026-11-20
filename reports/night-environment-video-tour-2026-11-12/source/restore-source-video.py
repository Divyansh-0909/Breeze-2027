from pathlib import Path
import argparse,json,hashlib,tempfile,os
p=argparse.ArgumentParser(description='Reassemble and verify the exact original 10 FPS camera-render video from its four Drive parts.');p.add_argument('downloads',type=Path);p.add_argument('output',type=Path);p.add_argument('--index',type=Path,default=Path(__file__).resolve().parents[1]/'checkpoint/source-video-parts-index.json');a=p.parse_args();d=json.loads(a.index.read_text());assert not a.output.exists(),'Choose a new output filename; existing files are preserved.';a.output.parent.mkdir(parents=True,exist_ok=True)
fd,tmpname=tempfile.mkstemp(prefix='breeze-source-video-',suffix='.partial',dir=a.output.parent);os.close(fd);tmp=Path(tmpname);whole=hashlib.sha256();total=0
try:
 with tmp.open('wb') as out:
  for row in sorted(d['parts'],key=lambda x:x['partIndex']):
   hits=list(a.downloads.rglob(row['name']));assert len(hits)==1,('Expected exactly one matching part',row['name']);h=hashlib.sha256();n=0
   with hits[0].open('rb') as src:
    while b:=src.read(1024*1024):h.update(b);whole.update(b);out.write(b);n+=len(b);total+=len(b)
   assert n==row['bytes'] and h.hexdigest()==row['sha256'],row['name']
 assert total==d['bytes'] and whole.hexdigest()==d['sha256'],'Complete video checksum failed';os.replace(tmp,a.output);print('PASS',a.output,total,whole.hexdigest())
finally:
 if tmp.exists():tmp.unlink()
