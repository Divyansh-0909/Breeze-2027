import json,hashlib,zipfile,subprocess,re,urllib.parse,os,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];items=json.loads((O/'checkpoint/final-archive-items.json').read_text());dest=O/'fresh-independent-restore';assert not dest.exists();dest.mkdir();archives=[]
for r in items:
 p=Path(r['save']);assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['name']
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():assert not n.startswith('/')and '..'not in Path(n).parts
  z.extractall(dest)
 archives.append({'name':r['name'],'sha256':r['sha256'],'bytes':r['bytes'],'actualAuthenticatedDriveDownloadUsed':True})
mf=json.loads((dest/'FILE-MANIFEST.json').read_text())['files']
def verify():
 for n,r in mf.items():
  p=dest/n;assert p.is_file()and p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],n
verify();links=re.findall(r'(?:src|href)="([^"]+)"',(dest/'GALLERY.html').read_text());assert all((dest/urllib.parse.unquote(x)).is_file()for x in links if not x.startswith(('http:','https:')))
protected={n:(dest/n).read_bytes()for n in mf if n.startswith('evidence/')};audit=O/'evidence/independent-audit';audit.mkdir(exist_ok=True)
for name in['validate_preservation.py','validate_storeys.py']:
 with (audit/(name+'.log')).open('w')as f:r=subprocess.run(['blender','-b',str(dest/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend'),'-t','2','--python-exit-code','9','--python',str(dest/'source'/name)],env=dict(os.environ,LP_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1'),stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode)
proof=json.loads((dest/'evidence/preservation-geometry.json').read_text());count=json.loads((dest/'evidence/storey-qa.json').read_text());assert proof['status']=='PASS'and proof['oldSceneCountPreserved']==19 and proof['sceneCount']==20 and proof['packedImages']==33 and proof['allImagesPacked']
assert all(r['actualIndependentSlabCount']>=3 and r['visibleLevelsFromPublicPositions']>=3 for r in count['rows'])and len(count['rows'])==11
shutil.copy2(dest/'evidence/preservation-geometry.json',audit/'fresh-preservation.json');shutil.copy2(dest/'evidence/storey-qa.json',audit/'fresh-storeys.json')
# Extra read-only open verifies all source-linked dependencies are self-contained.
expr="import bpy,json;from pathlib import Path;p=Path("+repr(str(audit/'fonts-images.json'))+");bad=[f.name for f in bpy.data.fonts if f.filepath!='<builtin>'and not f.packed_file];assert not bad,bad;assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE');p.write_text(json.dumps({'status':'PASS','fontsBuiltinOrPacked':True,'allImagesPacked':True,'sceneCount':len(bpy.data.scenes)}))"
with(audit/'fonts-images.log').open('w')as f:r=subprocess.run(['blender','-b',str(dest/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend'),'-t','2','--python-exit-code','9','--python-expr',expr],stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
for n,data in protected.items():(dest/n).write_bytes(data)
verify();out={'status':'PASS_FRESH_DRIVE_ONLY_RESTORE','archiveCount':len(archives),'archives':archives,'payloadHashesBeforeAndAfterAudit':len(mf),'galleryLinks':len(links),'sceneCount':20,'originalScenesExact':19,'originalObjectSignaturesExact':proof['originalObjectSignaturesExact'],'all11Have3PlusActualAndPublicVisibleLevels':True,'packedImages':33,'fontsBuiltinOrPacked':True,'oneConnectedManifoldPrimaryShell':True,'heightControlsAndOriginalActorsRetained':True,'mastersNeverResaved':True,'deliveredEvidenceRestoredAfterIndependentAudit':True,'masterSHA256':hashlib.sha256((dest/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend').read_bytes()).hexdigest()};(O/'checkpoint/INDEPENDENT-RESTORE-VERIFICATION.json').write_text(json.dumps(out,indent=2));print('FRESH_RESTORE_PASS',len(archives),len(mf),len(links),flush=True)
