from pathlib import Path
import argparse,json,hashlib,zipfile,tempfile,os
ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);ap.add_argument('output',type=Path);ap.add_argument('--index',type=Path,required=True);a=ap.parse_args();d=json.loads(a.index.read_text())
assert not a.output.exists(),'Existing output preserved; choose a new filename.'
a.output.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=a.output.parent,prefix='checkpoint-',suffix='.partial');os.close(fd);tmp=Path(tmp);whole=hashlib.sha256();total=0
try:
    with tmp.open('wb') as out:
        for row in sorted(d['parts'],key=lambda x:x['index']):
            matches=list(a.downloads.rglob(row['file']));assert len(matches)==1,row['file'];part=hashlib.sha256();n=0
            with matches[0].open('rb') as f:
                while data:=f.read(1048576):out.write(data);part.update(data);whole.update(data);n+=len(data);total+=len(data)
            assert n==row['bytes'] and part.hexdigest()==row['sha256'],row['file']
    assert total==d['bytes'] and whole.hexdigest()==d['sha256']
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for row in json.loads(z.read('PAYLOAD-SHA256.json')):
            data=z.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    os.replace(tmp,a.output);print('PASS',a.output,total,whole.hexdigest())
finally:
    if tmp.exists():tmp.unlink()
