"""Stream independently restorable ZIPs into bounded binary parts.

No duplicate giant archive is stored locally. The supplied restore program reads
the part sequence as one seekable ZIP without requiring a second concatenation.
"""
from pathlib import Path
import json,hashlib,zipfile,io,os
ROOT=Path.cwd();W=Path('/workspace/cave-shootout/2026-10-22/checkpoint');W.mkdir(parents=True,exist_ok=True)
LIMIT=50*1024*1024
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
class SplitWriter(io.RawIOBase):
    def __init__(self,name):self.name=name;self.total=0;self.partBytes=0;self.stream=None;self.parts=[];self.whole=hashlib.sha256()
    def writable(self):return True
    def seekable(self):return False
    def tell(self):return self.total
    def write(self,data):
        original=len(data);self.whole.update(data)
        while data:
            if self.stream is None:
                p=W/(self.name+'.part'+str(len(self.parts)+1).zfill(3));self.stream=p.open('wb');self.parts.append({'name':p.name});self.partBytes=0
            n=min(len(data),LIMIT-self.partBytes);self.stream.write(data[:n]);self.total+=n;self.partBytes+=n;data=data[n:]
            if self.partBytes==LIMIT:self.stream.close();self.stream=None
        return original
    def finish(self):
        if self.stream:self.stream.close();self.stream=None
        for r in self.parts:r.update(bytes=(W/r['name']).stat().st_size,sha256=sha(W/r['name']))
        return {'archive':self.name,'bytes':self.total,'sha256':self.whole.hexdigest(),'parts':self.parts}
def archive(name,files):
    writer=SplitWriter(name)
    with zipfile.ZipFile(writer,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True)as z:
        for p in files:z.write(p,'project/'+str(p.relative_to(ROOT)))
    result=writer.finish();result['files']=len(files);return result
if __name__=='__main__':
    inventories=[];archives=[];excluded=[]
    for category,rel in [('Source-Art','assets-source/gullyverse/cave-material-study'),('Runtime','public/models/gullyverse/cave-material-study')]:
        files=[]
        for p in sorted((ROOT/rel).rglob('*')):
            if not p.is_file():continue
            if p.suffix in ['.blend1','.blend2','.zip','.pyc']or'__pycache__'in p.parts or p.name.endswith('.partial'):
                excluded.append({'path':str(p.relative_to(ROOT)),'reason':'Redundant autosave/provider ZIP or temporary cache; current master and extracted source maps are included'});continue
            files.append(p);inventories.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p),'category':category})
        result=archive('Cave-Study-'+category+'.zip',files);archives.append(result);print(category,result['bytes'],len(result['parts']),'parts',flush=True)
    (W/'asset-file-manifest.json').write_text(json.dumps(inventories,indent=2)+'\n')
    (W/'asset-archives.json').write_text(json.dumps({'archives':archives,'excluded':excluded},indent=2)+'\n')
    (W/'upload-manifest.json').write_text(json.dumps({'phase':'CAVE-STUDY-20261022','sealed':False,'files':[]},indent=2)+'\n')
