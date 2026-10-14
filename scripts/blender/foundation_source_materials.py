"""Download licensed editable source maps; retain provider hashes/provenance.
No project reference-image pixels or original rock-pilot files are modified.
"""
from pathlib import Path
import json, hashlib, subprocess, concurrent.futures, shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets-source/gullyverse/quarry-foundation'
RAW=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13/raw'
OUT.mkdir(parents=True,exist_ok=True)
jobs=[]
for family,asset in [('rock-face','rock_face_04'),('terrain','rocky_terrain')]:
    info=json.loads((RAW/(family+'-info.json')).read_text())
    data=json.loads((RAW/(family+'-files.json')).read_text())
    directory=OUT/'licensed-source'/asset;directory.mkdir(parents=True,exist_ok=True)
    for slot in ['Diffuse','nor_gl','Rough','AO','Displacement']:
        resolution='2k' if family=='rock-face' else '1k'
        fmt='jpg'if slot=='Diffuse'else'png'
        item=data[slot][resolution][fmt]
        path=directory/item['url'].split('/')[-1]
        jobs.append((path,item,{'asset':asset,'slot':slot,'resolution':resolution,'author':info['authors']}))
    shutil.copyfile(RAW/(family+'-info.json'),directory/'provider-info.json')
    shutil.copyfile(RAW/(family+'-files.json'),directory/'provider-files.json')

def download(job):
    path,item,meta=job
    if not path.exists():
        subprocess.run(['curl','-fsSL','--retry','2','--max-time','55',item['url'],'-o',str(path)],check=True)
    blob=path.read_bytes()
    assert hashlib.md5(blob).hexdigest()==item['md5'],path
    return {**meta,'file':str(path.relative_to(ROOT)),'url':item['url'],
            'providerMD5':item['md5'],'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)}

with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
    rows=list(pool.map(download,jobs))
shutil.copyfile(RAW/'polyhaven-license.html',OUT/'licensed-source/polyhaven-license.html')
manifest={'provider':'Poly Haven','license':'CC0 1.0 Universal','licenseURL':'https://polyhaven.com/license',
          'legalCodeURL':'https://creativecommons.org/publicdomain/zero/1.0/legalcode',
          'sourceKind':'Provider photographic PBR surface assets; the provider API does not certify capture technique or displacement metre amplitude. No claim that the authored quarry itself is a physical scan.',
          'referencesUsedAsTextures':False,'files':rows}
(OUT/'source-provenance.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'downloaded':len(rows),'bytes':sum(r['bytes']for r in rows),'license':manifest['license']},indent=2))
