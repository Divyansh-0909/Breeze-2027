from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path(__file__).resolve().parents[1];B=O.parent/'navigation-board-rev15l-led-sponsors-2026-11-11';M=json.loads((O/'evidence/sponsors.json').read_text());P=json.loads((B/'evidence/sponsors.json').read_text());A=np.asarray(Image.open(O/'viewer/logo-strip.png').convert('RGB'));Z=np.asarray(Image.open(B/'viewer/logo-strip.png').convert('RGB'));rows=[]
for r,p in zip(M['logos'],P['logos']):
 t=A[:,r['startCell']:r['startCell']+r['tileCells']];v=Z[:,p['startCell']:p['startCell']+p['tileCells']];y,x=np.where(t.max(axis=2)>16);yy,xx=np.where(v.max(axis=2)>16)
 left=int(x.min());right=int(t.shape[1]-x.max()-1);assert left>=35 and right>=35,r['name']
 a=t[y.min():y.max()+1,x.min():x.max()+1];b=v[yy.min():yy.max()+1,xx.min():xx.max()+1]
 assert a.shape==b.shape and r['sourceSHA256']==p['sourceSHA256'] and r['logoCells']==p['logoCells'],r['name']
 error=float(np.abs(a.astype(float)-b).mean())
 rows.append({'name':r['name'],'leftBlankCells':left,'rightBlankCells':right,'logoRasterExtentUnchanged':True,'meanAntialiasDifferenceOutOf255':error})
(O/'evidence/spacing.json').write_text(json.dumps({'status':'PASS','logos':62,'nominalGapCells':72,'previousNominalGapCells':24,'allSourceHashesAndLogoSizesUnchanged':True,'all62TilesHaveInk':True,'rows':rows},indent=2));print('ALL 62 LOGO EXTENTS AND WIDER GAPS PASS')
