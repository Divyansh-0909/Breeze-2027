from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures,shutil,time
from PIL import Image,ImageOps,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'assets-source/gullyverse/canal-material-study'; O=ROOT/'public/models/gullyverse/canal-material-study'
HEADERS={'User-Agent':'Breeze-Gullyverse-Cave-Study/1 (licensed asset evaluation)'}
def get(url,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():return path
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=45)as r,path.with_suffix(path.suffix+'.partial').open('wb')as f:shutil.copyfileobj(r,f)
   path.with_suffix(path.suffix+'.partial').replace(path);return path
  except Exception:
   if attempt==2:raise
   time.sleep(1)
def sha(path,alg='sha256'):
 with path.open('rb')as f:return hashlib.file_digest(f,alg).hexdigest()
def prepare(row):
 a=row['id']; info=row['info']; files=row['files']; p=S/'licensed-source'/a;out=O/a;p.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 (p/'provider-info.json').write_text(json.dumps(info,indent=2));(p/'provider-files.json').write_text(json.dumps(files,indent=2));records=[];source={}
 for slot,names,formats in [('basecolor',['diff','Diffuse'],['jpg','png']),('normal',['nor_gl'],['png','jpg']),('roughness',['rough','Rough'],['png','jpg'])]:
  key=next(k for k in names if k in files);items=files[key]['2k'];fmt=next(f for f in formats if f in items);item=items[fmt];name=item['url'].split('/')[-1];path=get(item['url'],p/name)
  assert path.stat().st_size==item['size'];assert sha(path,'md5')==item['md5'];img=Image.open(path);assert img.size==(2048,2048);source[slot]=path;records.append({'slot':slot,'providerSlot':key,'file':str(path.relative_to(ROOT)),'url':item['url'],'bytes':path.stat().st_size,'providerMD5':item['md5'],'sha256':sha(path),'pixels':list(img.size),'mode':img.mode})
 Image.open(source['basecolor']).convert('RGB').save(out/'basecolor.jpg',quality=93,subsampling=0)
 # Source RGB normal maps may be 16bit; PIL explicitly converts RGB, preserves GL axis.
 Image.open(source['normal']).convert('RGB').save(out/'normal.png',optimize=True)
 raw=np.asarray(Image.open(source['roughness']));
 if raw.ndim==3:
  assert np.array_equal(raw[:,:,0],raw[:,:,1]) and np.array_equal(raw[:,:,0],raw[:,:,2]), 'Unexpected non-grey roughness'
  raw=raw[:,:,0]
 assert raw.ndim==2
 norm=raw.astype(np.float64)/(65535 if raw.max()>255 else 255)
 rough=np.round(norm*255).clip(0,255).astype('uint8');orm=np.stack([np.full_like(rough,255),rough,np.zeros_like(rough)],axis=2);Image.fromarray(orm).save(out/'orm.png',optimize=True)
 runtime=[{'file':str(f.relative_to(ROOT/'public')),'bytes':f.stat().st_size,'sha256':sha(f),'pixels':list(Image.open(f).size)}for f in sorted(out.iterdir())]
 r={'id':a,'provider':'Poly Haven','name':info['name'],'page':'https://polyhaven.com/a/'+a,'authors':info.get('authors',{}),'license':'CC0 1.0','licenseURL':'https://polyhaven.com/license','nativeDimensionsM':[v/1000 for v in info['dimensions']],'sourceMaps':records,'availableMaps':list(files),'runtimeMaps':runtime,'runtimeBytes':sum(x['bytes']for x in runtime),'decodedRGBA8MipBytes':3*2048*2048*4*4/3,'roughnessRange':[float(norm.min()),float(norm.max())],'AOApplied':False,'displacementRuntime':False,'sourceHeightDownloaded':False}
 (p/'download-manifest.json').write_text(json.dumps(r,indent=2));print(a,r['runtimeBytes'],flush=True);return r
IDS=['cracked_concrete_wall','concrete_wall_006','worn_plaster_wall','plastered_stone_wall','plaster_stone_wall_02','rock_embedded_concrete_wall','concrete_wall_008','scuffed_cement','chipped_concrete']
rows=[]
for a in IDS:
 row={'id':a}
 for kind in ['info','files']:
  row[kind]=json.loads(get('https://api.polyhaven.com/'+kind+'/'+a+'?canalStudy=20261023',S/'licensed-source'/a/('provider-'+kind+'.json')).read_text())
 rows.append(row)
# Additional discovery, official provider catalog; small metadata only.
try:get('https://api.polyhaven.com/assets?t=textures&canalStudy=20261023',S/'provider-texture-catalog.json')
except Exception as e:(S/'catalog-attempt.txt').write_text(str(e))
get('https://polyhaven.com/license',S/'polyhaven-license.html')
with concurrent.futures.ThreadPoolExecutor(2)as ex:result=list(ex.map(prepare,rows))
# Reuse one credible coarse mineral control from the earlier study, verify the actual source images first.
a='quarry_wall';old=ROOT/'assets-source/gullyverse/cave-material-study/licensed-source'/a
prior=json.load(open(old/'download-manifest.json'))
for rec in prior['sourceMaps']:assert sha(ROOT/rec['file'])==rec['sha256']
# Prior maps are licensed and immutable, make only 2K runtime derivatives. No new 4K downloads.
p=O/a;p.mkdir(exist_ok=True)
for n in ['basecolor.jpg','normal.png','orm.png']:
 img=Image.open(ROOT/'public/models/gullyverse/cave-material-study'/a/n).resize((2048,2048),Image.Resampling.LANCZOS)
 if n=='normal.png':
  v=np.asarray(img).astype(np.float32)/255*2-1;v/=np.maximum(np.linalg.norm(v,axis=2,keepdims=True),1e-6);img=Image.fromarray(np.rint((v+1)*127.5).clip(0,255).astype('uint8'))
 if n.endswith('jpg'):img.save(p/n,quality=93,subsampling=0)
 else:img.save(p/n,optimize=True)
rec={**prior,'runtimeMaps':[{'file':str(f.relative_to(ROOT/'public')),'bytes':f.stat().st_size,'sha256':sha(f),'pixels':[2048,2048]}for f in sorted(p.iterdir())],'decodedRGBA8MipBytes':3*2048*2048*4*4/3,'reusedEarlierStudy':True,'runtimeResolution':2048};rec['runtimeBytes']=sum(x['bytes']for x in rec['runtimeMaps']);result.append(rec)
manifest={'version':'private-canal-material-study-20261023','privateOnly':True,'finalMaterialSelected':False,'geometryHost':'UNCHANGED c9-cave-recovery/cave-entrance.glb','comparisonTilePeriodM':2*129.487464/128,'nominalComparisonPeriodM':2,'projectionChartPeriodUV':129.487464,'tilesPerChartPeriodAt1x':128,'tilesPerChartPeriodAt2x':64,'hostUVMetresPerUnit':2,'featureScales':[1,2],'runtimeResolution':2048,'loadPolicy':'Only one selected family; retire after covered preparation. No material preload catalog.','materials':result}
(S/'provenance-manifest.json').write_text(json.dumps(manifest,indent=2));(O/'materials.json').write_text(json.dumps(manifest,indent=2));(S/'CC0.txt').write_text('Poly Haven assets: CC0 1.0 https://polyhaven.com/license\nOfficial source metadata, authors, provider hashes and URLs in provenance-manifest.json. Prior quarry_wall source dependency remains unchanged and hash-verified.\n')
# Authoring-only source contact, not browser acceptance evidence.
canvas=Image.new('RGB',(900,((len(result)+2)//3)*330),(35,35,35));d=ImageDraw.Draw(canvas)
for i,r in enumerate(result):
 im=Image.open(ROOT/'public'/r['runtimeMaps'][0]['file']).convert('RGB').resize((280,280));x=i%3*300;y=i//3*330;canvas.paste(im,(x,y));d.text((x,y+285),r['id'],fill='white')
canvas.save(S/'source-map-contact.jpg')
print('DONE',sum(r['runtimeBytes']for r in result))
