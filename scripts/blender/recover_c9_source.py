"""Fetch only the authentic CC0 Coastal Cliff 01 source and its 2K dependencies.
Original maps remain authoring-only; C9 runtime borrows the approved C8 family.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets-source/gullyverse/quarry-scanned-composition'
ORIGINALS = OUT / 'licensed-source/coastal_cliff_01'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def metadata(kind):
    path = ORIGINALS / ('provider-' + kind + '.json')
    if not path.exists():
        url = 'https://api.polyhaven.com/' + kind + '/coastal_cliff_01'
        request = urllib.request.Request(url, headers={'User-Agent': 'Breeze-Gullyverse-Recovery/3'})
        with urllib.request.urlopen(request, timeout=55) as response:
            path.write_bytes(response.read())
    return json.loads(path.read_text())


def download(job):
    name, item = job
    path = ORIGINALS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        request = urllib.request.Request(item['url'], headers={'User-Agent': 'Breeze-Gullyverse-Recovery/3'})
        temporary = path.with_suffix(path.suffix + '.download')
        with urllib.request.urlopen(request, timeout=55) as response, temporary.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        temporary.rename(path)
    with path.open('rb') as stream:
        md5 = hashlib.file_digest(stream, 'md5').hexdigest()
    assert path.stat().st_size == item['size'] and md5 == item['md5']
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': sha(path), 'providerMD5': md5, 'url': item['url']}


def main():
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    info, files = metadata('info'), metadata('files')
    source = files['blend']['2k']['blend']
    jobs = [('coastal_cliff_01_2k.blend', source)] + list(source.get('include', {}).items())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        downloaded = list(pool.map(download, jobs))
    license_path = OUT / 'licensed-source/polyhaven-license.html'
    shutil.copyfile(ROOT / 'assets-source/gullyverse/recovered-c8-material/licensed-source/polyhaven-license.html', license_path)
    provenance = {'asset': 'coastal_cliff_01', 'provider': 'Poly Haven',
                  'sourcePage': 'https://polyhaven.com/a/coastal_cliff_01',
                  'license': 'CC0 1.0 Universal', 'licenseURL': 'https://polyhaven.com/license',
                  'providerAuthors': info['authors'], 'providerDimensions': info.get('dimensions'),
                  'geometry': 'Genuine scanned 3D source; actual native bounds inspected separately in Blender',
                  'files': downloaded, 'runtimeSourceMeshesOrTexturesShipped': False,
                  'runtimeMaterialOwner': 'recovered-c8-material; approved 3x sampling unchanged'}
    (OUT / 'source-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(json.dumps({'status': 'VERIFIED', 'files': len(downloaded), 'bytes': sum(x['bytes'] for x in downloaded)}, indent=2))


if __name__ == '__main__':
    main()
