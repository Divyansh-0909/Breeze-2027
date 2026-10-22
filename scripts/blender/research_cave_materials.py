"""Official-provider research and reproducible CC0 cave material preparation.

Downloads real 4K maps, never provider thumbnails. No geometry or accepted
quarry material is modified. Source downloads are authoring-only.
"""
from pathlib import Path
import concurrent.futures, hashlib, json, urllib.request, shutil, time, zipfile
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'assets-source/gullyverse/cave-material-study'
O = ROOT / 'public/models/gullyverse/cave-material-study'
R = ROOT / 'reports/cave-material-study-2026-10-22'
SEEDS = ['rock_01','rock_2','rock_3','worn_rock_natural_01','rock_face_03','rock_face','dark_rock_02','quarry_wall']
EXTRA = ['rock_05']
HEADERS = {'User-Agent':'Breeze-Gullyverse-Cave-Study/1 (licensed asset evaluation)'}

def fetch(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=55) as r, path.with_suffix(path.suffix+'.partial').open('wb') as out:
                    shutil.copyfileobj(r,out)
                path.with_suffix(path.suffix+'.partial').replace(path)
                break
            except Exception:
                if attempt == 2: raise
                time.sleep(1)
    return path

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def metadata(asset):
    p=S/'licensed-source'/asset
    info=json.loads(fetch('https://api.polyhaven.com/info/'+asset+'?caveStudy=20261022',p/'provider-info.json').read_text())
    files=json.loads(fetch('https://api.polyhaven.com/files/'+asset+'?caveStudy=20261022',p/'provider-files.json').read_text())
    return asset, info, files

def variant(files,names,formats):
    for name in names:
        if name not in files:continue
        for fmt in formats:
            item=files[name].get('4k',{}).get(fmt)
            if item:return name,item
    raise KeyError((names,list(files)))

def prepare(row):
    asset,info,files=row;p=S/'licensed-source'/asset;out=O/asset;out.mkdir(parents=True,exist_ok=True)
    selected={
        'basecolor':variant(files,['diff','Diffuse'],['jpg','png']),
        'normal':variant(files,['nor_gl','Normal'],['png','jpg']),
        'roughness':variant(files,['rough','Rough'],['png','jpg']),
        'height':variant(files,['disp','Displacement'],['png','tif']),
    }
    source={}; records=[]
    for slot,(provider_slot,item) in selected.items():
        name=item['url'].split('/')[-1];path=fetch(item['url'],p/name)
        assert path.stat().st_size==item['size'],(asset,slot,'size')
        with path.open('rb')as f:assert hashlib.file_digest(f,'md5').hexdigest()==item['md5'],(asset,slot,'provider checksum')
        image=Image.open(path);assert image.size==(4096,4096),(asset,slot,image.size)
        source[slot]=path
        records.append({'slot':slot,'providerSlot':provider_slot,'file':str(path.relative_to(ROOT)),'url':item['url'],'bytes':path.stat().st_size,'providerMD5':item['md5'],'sha256':digest(path),'pixels':list(image.size)})
    # Keep provider albedo without grade or AO multiplication. Three loads
    # OpenGL normals as non-colour data. ORM R=1, G=roughness, B=0.
    Image.open(source['basecolor']).convert('RGB').save(out/'basecolor.jpg',quality=92,subsampling=0)
    Image.open(source['normal']).convert('RGB').save(out/'normal.png',optimize=True)
    rough=np.asarray(Image.open(source['roughness']).convert('L'))
    orm=np.stack([np.full_like(rough,255),rough,np.zeros_like(rough)],axis=2)
    Image.fromarray(orm).save(out/'orm.png',optimize=True)
    runtime=[]
    for file in out.iterdir():
        runtime.append({'file':str(file.relative_to(ROOT/'public')),'bytes':file.stat().st_size,'sha256':digest(file),'pixels':[4096,4096]})
    result={'id':asset,'provider':'Poly Haven','name':info['name'],'page':'https://polyhaven.com/a/'+asset,'authors':info.get('authors',{}),'license':'CC0 1.0','licenseURL':'https://polyhaven.com/license','nativeDimensionsM':[v/1000 for v in info.get('dimensions',[])],'sourceDimensionsUnit':'Provider metadata millimetres, divided by 1000','availableMaps':list(files),'sourceMaps':records,'runtimeMaps':runtime,'runtimeBytes':sum(x['bytes']for x in runtime),'decodedRGBA8MipBytes':3*4096*4096*4*4/3,'sourceHeightRuntime':False,'displacementRuntime':False,'AOApplied':False,'roughnessRange':[int(rough.min())/255,int(rough.max())/255],'status':'SHORTLISTED_FOR_BROWSER_COMPARISON','independentDiscovery':asset in EXTRA}
    (p/'download-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PREPARED',asset,result['runtimeBytes'],flush=True)
    return result

def main():
    for p in [S,O,R/'raw',R/'scripts',R/'screenshots']:p.mkdir(parents=True,exist_ok=True)
    fetch('https://polyhaven.com/license',S/'polyhaven-license.html')
    fetch('https://ambientcg.com/license',S/'ambientcg-license.html')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:
        rows=list(ex.map(metadata,SEEDS+EXTRA))
    (S/'material-research.json').write_text(json.dumps([{'id':a,'info':i,'mapKeys':list(f)}for a,i,f in rows],indent=2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as ex:prepared=list(ex.map(prepare,rows))
    result={'version':'private-cave-material-shootout-20261022','privateOnly':True,'productionApproved':False,'geometryHost':'UNCHANGED c9-cave-recovery/cave-entrance.glb','quarrySamplerChanged':False,'uniformComparisonTilePeriodM':5.395311,'featureScales':[1,2],'runtimeResolution':4096,'loadPolicy':'One selected material only, sequential retirement after covered preparation; never preload all candidates','materials':prepared}
    (O/'materials.json').write_text(json.dumps(result,indent=2)+'\n');(S/'provenance-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    (S/'PROVENANCE-SHA256.txt').write_text(digest(S/'provenance-manifest.json')+'  provenance-manifest.json\n')

if __name__=='__main__':main()
