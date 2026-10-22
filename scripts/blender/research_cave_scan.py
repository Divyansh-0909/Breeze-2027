"""Independent second-library texture and native-scale 3D source research."""
from pathlib import Path
import sys,json,hashlib,zipfile
from PIL import Image
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_cave_materials import ROOT,S,O,fetch,digest

catalog=json.loads((S/'ambientcg-rock-research.json').read_text())
asset=next(a for a in catalog['foundAssets']if a['assetId']=='Rock041')
p=S/'licensed-source/ambientcg_Rock041';p.mkdir(parents=True,exist_ok=True)
(p/'provider-info.json').write_text(json.dumps(asset,indent=2))
item=next(x for x in asset['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads']if x['attribute']=='4K-JPG')
archive=fetch(item['downloadLink'],p/item['fileName']);assert archive.stat().st_size==item['size']
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    for n in z.namelist():
        assert Path(n).name==n
        z.extract(n,p)
out=O/'ambientcg_Rock041';out.mkdir(parents=True,exist_ok=True)
slots={'basecolor':'Color.jpg','normal':'NormalGL.jpg','roughness':'Roughness.jpg'};source=[]
for key,suffix in slots.items():
    f=next(p.glob('*_'+suffix));im=Image.open(f);assert im.size==(4096,2048)
    if key=='basecolor':im.convert('RGB').save(out/'basecolor.jpg',quality=92,subsampling=0)
    if key=='normal':im.convert('RGB').save(out/'normal.png',optimize=True)
    if key=='roughness':
        a=np.asarray(im.convert('L'));Image.fromarray(np.stack([np.full_like(a,255),a,np.zeros_like(a)],axis=2)).save(out/'orm.png',optimize=True)
    source.append({'slot':key,'file':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':digest(f),'pixels':[4096,2048]})
runtime=[{'file':str(f.relative_to(ROOT/'public')),'bytes':f.stat().st_size,'sha256':digest(f),'pixels':[4096,2048]}for f in out.iterdir()]
result={'id':'ambientcg_Rock041','provider':'ambientCG','name':'Rock 041','page':asset['shortLink'],'authors':{'ambientCG / Lennart Demes':'Asset library publisher; individual photographer not identified by API'},'license':'CC0 1.0','licenseURL':'https://ambientcg.com/license','creationMethod':asset['creationMethod'],'nativeDimensionsM':None,'sourceDimensionsUnit':'Provider supplies zero dimensions; native metre scale UNKNOWN, not inferred','availableMaps':[f.name for f in p.glob('*.jpg')],'sourceArchive':{'url':item['downloadLink'],'file':str(archive.relative_to(ROOT)),'bytes':archive.stat().st_size,'sha256':digest(archive)},'sourceMaps':source,'runtimeMaps':runtime,'runtimeBytes':sum(x['bytes']for x in runtime),'decodedRGBA8MipBytes':3*4096*2048*4*4/3,'aspect':2,'AOApplied':False,'displacementRuntime':False,'status':'SHORTLISTED_FOR_BROWSER_COMPARISON','independentDiscovery':True}
(S/'ambientcg-material.json').write_text(json.dumps(result,indent=2)+'\n')
print('AMBIENT_PREPARED',result['runtimeBytes'],flush=True)

files=json.loads((S/'namaqualand-cliff-files.json').read_text());item=files['blend']['1k']['blend'];p=S/'licensed-source/namaqualand_cliff_01';p.mkdir(parents=True,exist_ok=True)
rows=[]
for rel,entry in [(item['url'].split('/')[-1],item)]+list(item.get('include',{}).items()):
    f=fetch(entry['url'],p/rel)
    with f.open('rb')as h:assert hashlib.file_digest(h,'md5').hexdigest()==entry['md5']
    assert f.stat().st_size==entry['size']
    rows.append({'file':str(f.relative_to(ROOT)),'url':entry['url'],'bytes':f.stat().st_size,'sha256':digest(f),'providerMD5':entry['md5']})
(p/'source-downloads.json').write_text(json.dumps(rows,indent=2)+'\n')
print('NATIVE_SCAN_DOWNLOADED',rows[0]['bytes'],flush=True)
