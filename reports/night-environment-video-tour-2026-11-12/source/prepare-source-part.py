from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parents[1];src=R/'video/Night-Environment-Tour-Source10fps.mp4';i=int(sys.argv[1]);size=8*1024*1024;out=R/'checkpoint'/f'Night-Environment-Tour-Source10fps.mp4.part{i+1:03d}'
with src.open('rb') as f:f.seek(i*size);b=f.read(size)
assert b;out.write_bytes(b)
print(json.dumps({'name':out.name,'path':str(out),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'sourceOffset':i*size,'partIndex':i,'sourceVideoBytes':src.stat().st_size,'temporaryPart':True}))
