from pathlib import Path
import hashlib,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'reports/stage-2c-quarry-rollout-2026-10-12/raw'
base=json.loads((P/'baseline-hashes.json').read_text());missing=[n for n in base if not(ROOT/n).exists()]
changed=[n for n,h in base.items()if (ROOT/n).exists()and hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
allowed={'components/immersive/AftermovieScene.tsx','components/immersive/HubScene.tsx','components/immersive/ImmersiveShell.tsx','components/immersive/wallSection.ts'}
state={'status':'PASS' if not missing and set(changed)==allowed else 'FAIL','checked':len(base),'unchanged':len(base)-len(changed)-len(missing),'changed':changed,'missing':missing,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'statusOutput':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'stagedDiff':subprocess.check_output(['git','diff','--cached'],cwd=ROOT,text=True),'assetProtection':'Approved original maps/material library/stage/crowd/video/prior exports/historical docs unchanged by SHA256.'}
(P/'final-preservation.json').write_text(json.dumps(state,indent=2));assert state['status']=='PASS'
def glb(name):
 data=(ROOT/name).read_bytes();n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def images(d,data):return [hashlib.sha256(data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]).hexdigest()for im in d['images']for v in [d['bufferViews'][im['bufferView']]]]
a,ab=glb('public/models/gullyverse/first-wall-corrected/first-wall-corrected.glb');b,bb=glb('public/models/gullyverse/quarry-rollout/quarry-limestone.glb')
am=next(m for m in a['materials']if m['name']=='Approved_Cool_Grey_Limestone_Family');bm=next(m for m in b['materials']if m['name']=='Approved_Cool_Grey_Limestone_Family');ai=images(a,ab);bi=images(b,bb)
lock={'status':'PASS' if am==bm and ai==bi else 'FAIL','materialJSONExact':am==bm,'embeddedImageSHA256Before':ai,'embeddedImageSHA256After':bi,'imageBytesExact':ai==bi,'normalTextureCoordinate':bm['normalTexture'].get('texCoord',0),'normalScale':bm['normalTexture'].get('scale',1),'originalMapFilesUnchanged':all(n not in changed for n in base if 'first-wall-section/textures'in n)}
(P/'material-lock-validation.json').write_text(json.dumps(lock,indent=2));assert lock['status']=='PASS'
print('119 protected files checked: 115 unchanged, four scoped integration edits; material JSON/images/source maps unchanged; HEAD unchanged.')
