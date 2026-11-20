import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

def sha256(file):
    result = hashlib.sha256()
    with Path(file).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def restore(index_path, downloads, destination):
    index = json.loads(Path(index_path).read_text())
    downloads, destination = Path(downloads), Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Restore destination must be empty')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='team-mural-restore-') as temporary:
        archive = Path(temporary) / 'payload.zip'
        with archive.open('wb') as output:
            for part in index['parts']:
                file = downloads / part['name']
                if file.stat().st_size != part['bytes'] or sha256(file) != part['sha256']:
                    raise ValueError('Part checksum mismatch: ' + part['name'])
                with file.open('rb') as stream:
                    shutil.copyfileobj(stream, output)
        if sha256(archive) != index['archiveSHA256']:
            raise ValueError('Combined archive checksum mismatch')
        expected = {item['path']: item for item in index['payloads']}
        with zipfile.ZipFile(archive) as source:
            if set(source.namelist()) != set(expected):
                raise ValueError('Archive payload list mismatch')
            for member in source.infolist():
                name = PurePosixPath(member.filename)
                if name.is_absolute() or '..' in name.parts or member.file_size != expected[member.filename]['bytes']:
                    raise ValueError('Invalid archive entry: ' + member.filename)
            source.extractall(destination)
        for relative, item in expected.items():
            file = destination / relative
            if file.stat().st_size != item['bytes'] or sha256(file) != item['sha256']:
                raise ValueError('Payload checksum mismatch: ' + relative)
    print(json.dumps({'status':'PASS','payloads':len(expected),'destination':str(destination)}))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Usage: python restore.py INDEX.json /downloads /empty/restore')
    restore(*sys.argv[1:])
