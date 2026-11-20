from pathlib import Path,PurePosixPath
import json,hashlib,zipfile,io,sys
folder=Path(sys.argv[1]);dest=Path(sys.argv[2]);assert not dest.exists()or not any(dest.iterdir()),'Use a new empty destination';idx=json.loads((folder/'Checkpoint-Index.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();chunks=[]
for row in idx['parts']:
 b=(folder/row['file']).read_bytes();assert len(b)==row['bytes']and sha(b)==row['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==idx['archiveBytes']and sha(b)==idx['archiveSHA256']
with zipfile.ZipFile(io.BytesIO(b))as z:
 for name in z.namelist():assert not PurePosixPath(name).is_absolute()and'..'not in PurePosixPath(name).parts
 assert z.testzip()is None
 for row in json.loads(z.read('Archive-File-Manifest.json')):assert sha(z.read(row['file']))==row['sha256']
 z.extractall(dest)
print('RESTORE_PASS',idx['archiveSHA256'])
