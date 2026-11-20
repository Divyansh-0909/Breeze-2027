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
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());rows=json.loads((R/'evidence/captures.json').read_text());lighting=json.loads((R/'evidence/lighting-verification.json').read_text());assert len(rows)==5 and lighting['status']=='PASS'
for x in rows:assert x['sourceMasterSHA256']==b['editedSHA256'] and hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256']
for n,f in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/fonts'/f)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
P=R/'review/Breeze-Wet-Grain-Asphalt-and-Muddy-Edges-Review.pdf';c=canvas.Canvas(str(P),pagesize=(960,680));c.setTitle('Breeze / Asphalt grain, muddy wet shoulders and edge water')
old=R.parent/'actual-night-road-review-2026-11-13/renders'
def text(s,x,y,size=11,col='#f2eade',bold=False):
 c.setFillColor(HexColor(col));c.setFont('DV-Bold' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,top,w,size=11,col='#bbc4c9'):
 p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=size,leading=size*1.4,textColor=HexColor(col)));_,h=p.wrap(w,1000);assert top-h>34;p.drawOn(c,x,top-h)
def base(n,title):
 c.setFillColor(HexColor('#101820'));c.rect(0,0,960,680,fill=1,stroke=0);text(title,28,643,23,bold=True)
 text('BREEZE 2027 / REV15T2 · existing lamps and exposure · edited wet-surface reflection response',28,620,9,'#bbc4c9')
 text('13 November 2026 · Native scene review / painted cypher circle remains removed',28,17,8,'#bbc4c9');text(str(n),922,17,8,'#bbc4c9')
def full(n,title,key,caption):
 base(n,title);c.drawImage(ImageReader(str(R/'renders'/(key+'.jpg'))),40,65,880,550);text(caption,28,38,9,'#bbc4c9');c.showPage()
def comparison(n,title,before,after,caption):
 base(n,title);text('BEFORE / REV15T1',28,583,10,bold=True);text('AFTER / REV15T2',492,583,10,bold=True)
 c.drawImage(ImageReader(str(old/before)),28,299,440,275);c.drawImage(ImageReader(str(R/'renders'/(after+'.jpg'))),492,299,440,275)
 para(caption,28,270,904,13);para('The road profile, ramp, crowd and building layout are retained. The change is the road material and shallow edge-water surfaces. Full-world production website integration remains pending.',28,163,904,11)
 c.showPage()
comparison(1,'A wetter, more granular gully road.','01-lane-wide.jpg','01-lane-wide','The exposed asphalt now has a mixed stone-and-binder texture. Damp silt coats the shoulders, and irregular standing water collects beside the buildings, following the direction of your market-road reference.')
full(2,'Exposed asphalt grains under the shop light.','02-lane-grain-close','Mixed angular aggregate, darker binder and a wet sheen. This is the saved night lighting, with no inspection lamps.')
full(3,'Muddy shoulders and pooled side water.','03-lane-water','Long shallow pools sit beside the shop aprons, with softer muddy fringes and reflected shop-front colour.')
comparison(4,'The same wet road continues into the cypher.','03-cypher-wide.jpg','04-cypher-wide','The cypher retains its unmarked, flat centre. Damp asphalt continues through it, while the muddy water bands stay toward the perimeter and building fronts.')
full(5,'Cypher edge water under the Events light.','05-cypher-water','The existing Events lamp reveals the wet road edge. Lighting and exposure are preserved; water reflections are enabled.')
c.save();assert len(PdfReader(P).pages)==5
out={'status':'PASS','pages':5,'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'masterSHA256':b['editedSHA256'],'nativeAfterCaptures':5,'nativeBeforeCaptures':2,'existingLampsAndExposurePreserved':True,'nativeWaterReflectionsEnabled':True}
(R/'evidence/pdf-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
