from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
for n,f in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/fonts'/f)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
proof=json.loads((R/'evidence/build-verification.json').read_text());assert json.loads((R/'evidence/paint-only-check.json').read_text())['status']=='PASS';assert json.loads((R/'evidence/runtime-verification.json').read_text())['status']=='PASS'
P=R/'review/Breeze-Cypher-Circle-Removed-Review.pdf';c=canvas.Canvas(str(P),pagesize=(842,595));c.setTitle('Breeze 2027 / Painted cypher circle removed')
def text(s,x,y,size=11,col='#19343c',bold=False):
 c.setFillColor(HexColor(col));c.setFont('DV-Bold' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,top,w,size=10):
 p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=size,leading=size*1.4,textColor=HexColor('#53646b')));_,h=p.wrap(w,1000);p.drawOn(c,x,top-h)
c.setFillColor(HexColor('#f5f1e9'));c.rect(0,0,842,595,fill=1,stroke=0)
text('BREEZE 2027 / GULLYVERSE',34,567,9,bold=True);text('REV15T1',752,567,9,bold=True)
text('Painted cypher circle removed.',34,520,27,bold=True)
para('The road now continues through an unmarked cypher area. Matched native inspection views.',34,498,774)
for label,key,x in [('BEFORE / REV15T','cypher-before',34),('AFTER / REV15T1','cypher-no-circle',432)]:
 text(label,x,456,9,bold=True);c.drawImage(ImageReader(str(R/'renders'/(key+'.jpg'))),x,210,376,235)
para('The previous cream circle, painted into the asphalt.',34,195,376,9.5);para('The paint is removed, exposing the existing repaired asphalt beneath.',432,195,376,9.5)
c.setFillColor(HexColor('#e9e2d5'));c.rect(34,63,774,84,fill=1,stroke=0)
para('<b>Only the painted marking changed.</b> The underlying road surface, repair patches, potholes, crowd, lighting, ramp and movement route are preserved. The native material and runtime ground asset are updated.',47,132,748,11)
para('13 November 2026 · Native scene review / public website integration remains pending.',34,30,774,8)
c.showPage();c.save();assert len(PdfReader(P).pages)==1
rows=[{'file':x.name,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in sorted((R/'renders').glob('*.jpg'))]
(R/'evidence/pdf-verification.json').write_text(json.dumps({'status':'PASS','file':str(P),'pages':1,'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'captures':rows,'nativeMasterSHA256':proof['editedSHA256']},indent=2)+'\n');print('PDF_READY',P.stat().st_size,hashlib.sha256(P.read_bytes()).hexdigest())
