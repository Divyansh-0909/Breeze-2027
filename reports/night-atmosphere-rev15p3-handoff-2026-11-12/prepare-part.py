import sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
src=Path(sys.argv[1]); index=int(sys.argv[2]); size=24*1024*1024
out=root/(src.name+f'.part{index+1:03d}')
with src.open('rb') as f:
 f.seek(index*size);b=f.read(size)
assert b
out.write_bytes(b)
print(json.dumps({'path':str(out),'archive':str(src),'index':index,'offset':index*size,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'totalParts':(src.stat().st_size+size-1)//size}))
