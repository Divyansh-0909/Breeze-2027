import json,zipfile,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];p=Path('/dev/shm/rev07-delivery/Rev07-Validated-Source-v2.zip')
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,6)as z:
 for f in (O/'source').glob('*'):
  if f.is_file()and f.name!='APPROVED-PILOT.blend':z.write(f,'source/'+f.name)
 for f in(O/'evidence').glob('*'):
  if f.is_file():z.write(f,'evidence/'+f.name)
 z.write(O/'PROGRESS.md','PROGRESS.md')
r={'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'folder':'checkpoint'}
(O/'checkpoint/validated-source-v2.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
