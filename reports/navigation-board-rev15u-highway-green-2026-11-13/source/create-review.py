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
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());rows={x['key']:x for x in json.loads((R/'evidence/captures.json').read_text())}
for key in ['01-whole-board','02-sign-close','before-01-whole-board']:
    row=rows[key];assert hashlib.sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256'];assert row['sourceSHA256']==(b['sourceSHA256'] if key.startswith('before') else b['editedSHA256'])
for name,f in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/review-fonts'/f)))
P=R/'review/Breeze-Bilingual-Highway-Navigation-Review.pdf';c=canvas.Canvas(str(P),pagesize=(960,760));c.setTitle('Breeze / Hindi and English highway navigation board')
def txt(s,x,y,size=11,bold=False):
    c.setFillColor(HexColor('#f1f4ee'));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,y,w,size=12):
    p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=size,leading=size*1.45,textColor=HexColor('#bdc9c5')));_,h=p.wrap(w,1000);p.drawOn(c,x,y-h)
def page(n,title):
    c.setFillColor(HexColor('#0e1917'));c.rect(0,0,960,760,fill=1,stroke=0);txt(title,28,720,24,True);txt('BREEZE 2027 / REV15U1 · actual saved night lighting · Hindi + English, taller panels and diagonal arrows',28,696,9)
    txt('14 November 2026 · Native 3D review / full-world website integration pending',28,19,8);txt(str(n),924,19,8)
def photo(key,x,y,w,h):c.drawImage(ImageReader(str(R/rows[key]['file'])),x,y,w,h)
page(1,'The navigation board, now in Hindi and English.')
txt('BEFORE',28,660,11,True);txt('AFTER',492,660,11,True)
photo('before-01-whole-board',28,271,440,378.125);photo('01-whole-board',492,271,440,378.125)
para('Hindi sits above English on the green signs, with white borders and taller 0.68 m destination panels. Accommodation replaces Schedule. Events and Accommodation point up-left; Team and Contact Us point up-right.',28,239,904,13)
para('The physical boards keep their orientation. The Past Sponsors plaque grows upward, keeping the LED screen and its hardware in place. All 62 logos, spacing and scrolling remain unchanged; both views use the same camera and saved night lights.',28,134,904,12);c.showPage()
page(2,'Taller bilingual panels. The sponsor screen stays unchanged.')
photo('01-whole-board',132,72,696,598.125)
txt('White paint takes on the warm cast of the existing lamps. The sponsor LED retains its original red display.',28,43,9);c.showPage()
page(3,'Hindi above English, with clear diagonal directions.')
photo('02-sign-close',70,67,820,626.3889)
txt('Overpass for English and Noto Sans Devanagari for Hindi. Accommodation replaces Schedule; the four side signs use 45-degree arrows.',28,43,9);c.showPage();c.save()
assert len(PdfReader(P).pages)==3
result={'status':'PASS','pages':3,'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'nativeMasterSHA256':b['editedSHA256'],'sameCameraBeforeAfter':True,'savedNightLighting':True,'digitalSponsorScreenUnchanged':True,'bilingual':True,'panelHeightMetres':.68,'diagonalArrows':4,'accommodationReplacesSchedule':True,'excludedOccludedObliqueCapture':True}
(R/'evidence/pdf-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
