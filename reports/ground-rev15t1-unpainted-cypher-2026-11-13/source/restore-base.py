from pathlib import Path
import argparse,json,hashlib,tempfile,os
p=argparse.ArgumentParser(description='Restore the complete packed Rev15T native master from verified Drive parts.');p.add_argument('downloads',type=Path);p.add_argument('output',type=Path);p.add_argument('--index',type=Path,default=Path(__file__).resolve().parents[1]/'delivery/Base-Rev15T-Native-Parts.json');a=p.parse_args();d=json.loads(a.index.read_text());assert not a.output.exists(),'Existing output preserved; choose a new filename.';a.output.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='rev15t-',suffix='.partial',dir=a.output.parent);os.close(fd);tmp=Path(tmp);h=hashlib.sha256();total=0
try:
 with tmp.open('wb') as out:
  for row in sorted(d['parts'],key=lambda x:x['index']):
   matches=list(a.downloads.rglob(row.get('name',row.get('file'))));assert len(matches)==1,row.get('name',row.get('file'));part=hashlib.sha256();n=0
   with matches[0].open('rb') as f:
    while b:=f.read(1048576):out.write(b);part.update(b);h.update(b);n+=len(b);total+=len(b)
   assert n==row['bytes'] and part.hexdigest()==row['sha256'],row.get('name',row.get('file'))
 assert total==d['bytes'] and h.hexdigest()==d['sha256'],'Complete master checksum mismatch';os.replace(tmp,a.output);print('PASS',a.output,total,h.hexdigest())
finally:
 if tmp.exists():tmp.unlink()
