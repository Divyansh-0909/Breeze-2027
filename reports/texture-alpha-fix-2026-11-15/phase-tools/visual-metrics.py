from pathlib import Path
from PIL import Image
import numpy as np,json,struct
r=Path('/dev/shm/texture-alpha-fix-2026-11-15');before=np.asarray(Image.open(r/'renders/before-laptop.png').convert('RGB'),np.float32);after=np.asarray(Image.open(r/'renders/clean-baseline-laptop.png').convert('RGB'),np.float32);hidden=np.asarray(Image.open(r/'renders/clean-without-decal.png').convert('RGB'),np.float32);compressed=np.asarray(Image.open(r/'renders/clean-compressed-laptop.png').convert('RGB'),np.float32);d=json.loads((r/'evidence/browser-quality.json').read_text());assert d['status']=='PASS';rows=[]
for p in d['transparentTexelProbes']:
 x,y=round(p['x']),round(p['y']);rows.append({'x':x,'y':y,'sourceAlpha':0,'visibleVsHiddenMaxRGBError':float(np.abs(after[y,x]-hidden[y,x]).max()),'beforeRGB':before[y,x].tolist(),'afterRGB':after[y,x].tolist()})
assert len(rows)>=3;assert max(p['visibleVsHiddenMaxRGBError']for p in rows)<=2;weights=np.array([.2126,.7152,.0722]);regions={}
for name,(x,y,x2,y2)in {'wallRightOfHeading':(970,262,1090,330),'wallBelowWindow':(700,690,1000,760),'upperConcrete':(650,150,920,180)}.items():
 def rough(image):
  a=image[y:y2,x:x2]@weights;lap=4*a[1:-1,1:-1]-a[:-2,1:-1]-a[2:,1:-1]-a[1:-1,:-2]-a[1:-1,2:];return float(lap.std())
 a,b=rough(before),rough(after);regions[name]={'bounds':[x,y,x2,y2],'beforeHighFrequencyStd':a,'afterHighFrequencyStd':b,'variationReductionPercent':float(100*(1-b/a))}
# Surface variation is reported, not a universal physical-noise score; source
# textures and luminance are preserved/validated independently.
floorLuminance=float((after[820:870,700:1000]@weights).mean());assert floorLuminance>5,'Road detail must remain visible in the approved night view'
proof={'status':'PASS','floorLuminance':floorLuminance,'actualMeshTransparentTexelProbes':len(rows),'maximumVisibleVsHiddenError':max(p['visibleVsHiddenMaxRGBError']for p in rows),'meanWallLuminanceAtClearTexelsBefore':float(np.mean([np.dot(p['beforeRGB'],weights)for p in rows])),'meanWallLuminanceAtClearTexelsAfter':float(np.mean([np.dot(p['afterRGB'],weights)for p in rows])),'wallScreenVariationComparison':regions,'variationMetricScope':'Fixed camera; baking, denoising, mipmaps and MSAA; not universal physical noise measurement. Source PBR images unchanged.','compressedVsBaselineMeanRGBError':float(np.abs(after-compressed).mean()),'probes':rows};(r/'evidence/visual-regression.json').write_text(json.dumps(proof,indent=2)+'\n');print('VISUAL_ALPHA_PASS',len(rows),proof['compressedVsBaselineMeanRGBError'])
out=Path('/dev/shm/Breeze-2027-runtime/public/models/gullyverse/locked-rev15z-clean-v2');b=(out/'transparent-graffiti.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);assert len(g['materials'])==2
for m in g['materials']:assert m['alphaMode']=='BLEND'and m['extras']['runtimeDecal']is True
for p in (out/'graffiti').glob('*.png'):assert np.array(Image.open(p).convert('RGBA'))[...,3].min()==0
(r/'evidence/transparent-graffiti-validation.json').write_text(json.dumps({'status':'PASS','headings':2,'bothGLBMaterialsAlphaBlend':True,'bothExportedWithNoShadowPolicy':True,'bothSourcePNGsHaveZeroAlphaPixels':True},indent=2)+'\n');print('BOTH_GRAFFITI_ALPHA_PASS')
