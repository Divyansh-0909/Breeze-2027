"""Install official pinned CLI dependencies into a dedicated tools directory."""
from pathlib import Path
import urllib.request,hashlib,tarfile,json,sys,platform
assert platform.machine().lower()in['x86_64','amd64'];root=Path(sys.argv[1]if len(sys.argv)>1 else'/dev/shm/gullyverse-runtime-tools');root.mkdir(parents=True,exist_ok=True);rows=[]
packages=[('ktx','https://github.com/KhronosGroup/KTX-Software/releases/download/v4.4.2/KTX-Software-4.4.2-Linux-x86_64.tar.bz2','a8781bad05f9624edbf910b7f258cd0a4ba7d3e63b49ecc0a0ab440bf6a0a245'),('oidn','https://github.com/RenderKit/oidn/releases/download/v2.5.1/oidn-2.5.1.x86_64.linux.tar.gz','743c3e2aff8c220d5d70fe6cb970fb3d36f2702d2693c61d1d148e404cf37cd6')]
for name,url,expected in packages:
 file=root/url.rsplit('/',1)[1]
 if not file.exists():urllib.request.urlretrieve(url,file)
 actual=hashlib.sha256(file.read_bytes()).hexdigest();assert actual==expected,(name,actual);dest=root/name;dest.mkdir(exist_ok=True)
 with tarfile.open(file)as t:t.extractall(dest,filter='data')
 rows.append({'name':name,'url':url,'sha256':actual,'bytes':file.stat().st_size,'status':'PASS'});print('PINNED_TOOL_PASS',name,flush=True)
(root/'tool-verification.json').write_text(json.dumps(rows,indent=2)+'\n')
