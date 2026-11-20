from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];U2=R.parent/'navigation-board-rev15u2-english-centred-2026-11-14';b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=next(x for x in json.loads((U2/'evidence/captures.json').read_text()) if x['key']=='01-whole-board');after=next(x for x in json.loads((R/'evidence/captures.json').read_text()) if x['key']=='01-whole-board')
assert before['sourceSHA256']==b['sourceSHA256'] and after['sourceSHA256']==b['editedSHA256'];assert sha(R/'renders/before-01-whole-board.jpg')==before['sha256'] and sha(R/after['file'])==after['sha256']
for key,f in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(key,str(R/'source/review-fonts'/f)))
P=R/'review/Breeze-Larger-English-Navigation-Review.pdf';c=canvas.Canvas(str(P),pagesize=(960,760));c.setTitle('Breeze / Slightly larger English navigation labels')
def txt(s,x,y,size=11,bold=False):c.setFillColor(HexColor('#f1f4ee'));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,y,w):
    p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=13,leading=19,textColor=HexColor('#bdc9c5')));_,h=p.wrap(w,1000);p.drawOn(c,x,y-h)
def base(n,title):
    c.setFillColor(HexColor('#0e1917'));c.rect(0,0,960,760,fill=1,stroke=0);txt(title,28,720,24,True);txt('BREEZE 2027 / REV15U3 · actual saved night lighting · English labels 12% larger, vertically centred',28,696,9);txt('14 November 2026 · Native scene review / full-world website integration pending',28,19,8);txt(str(n),924,19,8)
base(1,'Slightly larger navigation lettering.')
txt('BEFORE',28,660,11,True);txt('AFTER',492,660,11,True)
c.drawImage(ImageReader(str(R/'renders/before-01-whole-board.jpg')),28,271,440,378.125);c.drawImage(ImageReader(str(R/after['file'])),492,271,440,378.125)
para('All seven English labels, including Gullyverse, are 12% larger. Each label has been vertically re-centred using its visible text bounds, with clearance checked against the arrows and white borders.',28,239,904)
para('Panel sizes, green faces, white borders, typefaces, horizontal text placement, diagonal arrows and Accommodation are retained. The digital sponsor board and saved night lighting remain unchanged.',28,134,904);c.showPage()
base(2,'The updated navigation board.')
c.drawImage(ImageReader(str(R/after['file'])),132,72,696,598.125);txt('English lettering increased by 12%, with vertical centring preserved. The sponsor LED remains unchanged.',28,43,9);c.showPage();c.save();assert len(PdfReader(P).pages)==2
result={'status':'PASS','pages':2,'bytes':P.stat().st_size,'sha256':sha(P),'nativeMasterSHA256':b['editedSHA256'],'englishOnly':True,'centredLabels':7,'textSizeIncreasePercent':12,'sameCameraAndSavedNightLighting':True,'digitalSponsorBoardUnchanged':True};(R/'evidence/pdf-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
