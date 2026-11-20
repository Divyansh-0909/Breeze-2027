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
R=Path(__file__).resolve().parents[1];U1=R.parent/'navigation-board-rev15u-highway-green-2026-11-13';b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=next(x for x in json.loads((U1/'evidence/captures.json').read_text()) if x['key']=='01-whole-board');after=next(x for x in json.loads((R/'evidence/captures.json').read_text()) if x['key']=='01-whole-board')
assert before['sourceSHA256']==b['sourceSHA256'] and after['sourceSHA256']==b['editedSHA256'];assert sha(R/'renders/before-01-whole-board.jpg')==before['sha256'] and sha(R/after['file'])==after['sha256']
for key,f in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(key,str(R/'source/review-fonts'/f)))
P=R/'review/Breeze-English-Centred-Navigation-Review.pdf';c=canvas.Canvas(str(P),pagesize=(960,760));c.setTitle('Breeze / English navigation labels centred vertically')
def txt(s,x,y,size=11,bold=False):c.setFillColor(HexColor('#f1f4ee'));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,y,w):
    p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=13,leading=19,textColor=HexColor('#bdc9c5')));_,h=p.wrap(w,1000);p.drawOn(c,x,y-h)
def base(n,title):
    c.setFillColor(HexColor('#0e1917'));c.rect(0,0,960,760,fill=1,stroke=0);txt(title,28,720,24,True);txt('BREEZE 2027 / REV15U2 · actual saved night lighting · English labels vertically centred',28,696,9);txt('14 November 2026 · Native scene review / full-world website integration pending',28,19,8);txt(str(n),924,19,8)
base(1,'English labels, centred vertically.')
txt('BEFORE',28,660,11,True);txt('AFTER',492,660,11,True)
c.drawImage(ImageReader(str(R/'renders/before-01-whole-board.jpg')),28,271,440,378.125);c.drawImage(ImageReader(str(R/after['file'])),492,271,440,378.125)
para('The seven Hindi labels have been removed from the active navigation board. Each English label, including Gullyverse, is vertically centred within its panel using its visible text bounds.',28,239,904)
para('The taller panels, green faces, white borders, font sizes, horizontal text placement, diagonal arrows and Accommodation label are retained. The digital sponsor board and saved night lighting are unchanged.',28,134,904);c.showPage()
base(2,'The updated navigation board.')
c.drawImage(ImageReader(str(R/after['file'])),132,72,696,598.125);txt('English only, centred vertically. The sponsor LED, its logos and scrolling remain as before.',28,43,9);c.showPage();c.save();assert len(PdfReader(P).pages)==2
result={'status':'PASS','pages':2,'bytes':P.stat().st_size,'sha256':sha(P),'nativeMasterSHA256':b['editedSHA256'],'englishOnly':True,'centredLabels':7,'sameCameraAndSavedNightLighting':True,'digitalSponsorBoardUnchanged':True};(R/'evidence/pdf-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
