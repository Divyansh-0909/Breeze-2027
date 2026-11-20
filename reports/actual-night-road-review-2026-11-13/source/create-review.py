from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'evidence/lighting-verification.json').read_text());rows=json.loads((R/'evidence/captures.json').read_text())
assert proof['status']=='PASS' and proof['lightingWorldAndExposureUnchanged'] and not proof['inspectionLightsAdded'] and not proof['postCaptureBrightening'] and len(rows)==4
for n,f in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/fonts'/f)))
W,H=960,680;P=R/'review/Breeze-Lane-and-Cypher-Actual-Night-Lighting.pdf';c=canvas.Canvas(str(P),pagesize=(W,H));c.setTitle('Breeze / Lane and cypher roads under actual night lighting')
for i,row in enumerate(rows,1):
 p=R/row['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'] and row['sourceMasterSHA256']==proof['sourceSHA256']
 c.setFillColor(HexColor('#101820'));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor('#f2eade'));c.setFont('DV-Bold',19);c.drawString(28,648,row['title'])
 c.setFont('DV',9);c.setFillColor(HexColor('#b8c0c4'));c.drawString(28,630,'Breeze 2027 / Rev15T1 · saved scene lighting and exposure · 1440 × 900 native capture')
 c.drawImage(ImageReader(str(p)),28,57,904,565)
 c.setFont('DV',9);c.drawString(28,35,'Lighting, world, exposure and scene artwork unchanged. No inspection lamps or image brightening.')
 c.setFont('DV',8);c.drawString(28,17,'13 November 2026 · Native scene review');c.drawRightString(932,17,str(i));c.showPage()
c.save();assert len(PdfReader(P).pages)==4
out={'status':'PASS','pages':4,'file':str(P),'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'sourceMasterSHA256':proof['sourceSHA256'],'sourceImagesUnaltered':True,'lightingVerification':'Lighting, world and colour-management signature identical before and after all four native renders'}
(R/'evidence/pdf-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
