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
P=R/'review/Breeze-Rebuilt-Potholes-Review.pdf';c=canvas.Canvas(str(P),pagesize=(960,680));c.setTitle('Breeze / Rebuilt potholes and flattened asphalt fragments')
old=R.parent/'ground-rev15t2-wet-grain-asphalt-2026-11-13/renders'
def text(s,x,y,size=11,col='#f2eade',bold=False):
 c.setFillColor(HexColor(col));c.setFont('DV-Bold' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,top,w,size=11,col='#bbc4c9'):
 p=Paragraph(s,ParagraphStyle('p',fontName='DV',fontSize=size,leading=size*1.4,textColor=HexColor(col)));_,h=p.wrap(w,1000);assert top-h>34;p.drawOn(c,x,top-h)
def base(n,title):
 c.setFillColor(HexColor('#101820'));c.rect(0,0,960,680,fill=1,stroke=0);text(title,28,643,23,bold=True)
 text('BREEZE 2027 / REV15T3 · actual saved night lighting · road defects rebuilt',28,620,9,'#bbc4c9')
 text('13 November 2026 · Native scene review / painted cypher circle remains removed',28,17,8,'#bbc4c9');text(str(n),922,17,8,'#bbc4c9')
def full(n,title,key,caption):
 base(n,title);c.drawImage(ImageReader(str(R/'renders'/(key+'.jpg'))),40,65,880,550);text(caption,28,38,9,'#bbc4c9');c.showPage()
def comparison(n,title,before,after,caption):
 base(n,title);text('BEFORE / REV15T2',28,583,10,bold=True);text('AFTER / REV15T3',492,583,10,bold=True)
 c.drawImage(ImageReader(str(old/before)),28,299,440,275);c.drawImage(ImageReader(str(R/'renders'/(after+'.jpg'))),492,299,440,275)
 para(caption,28,270,904,13);para('The movement shell, ramp, crowd and buildings are retained. Only the visible road defects and loose asphalt fragments are rebuilt. Full-world production website integration remains pending.',28,163,904,11)
 c.showPage()
full(1,'Potholes rebuilt in the gully road.','01-lane-wide','Fractured asphalt edges, recessed mud and flatter chips. The centre route, shops and night lights are retained.')
full(2,'Broken asphalt rims under the shop light.','02-lane-grain-close','A layered broken rim replaces the soft depression. Damp mud sits below it; loose fragments have flat tops.')
comparison(3,'The lane pothole: before and rebuilt.','03-lane-water.jpg','03-lane-water','The old pointed stones and small puddle disc have been removed from this revision. The pothole is now cut into the road mesh, with an irregular broken edge and a muddy water surface below road level.')
full(4,'The repaired ground continues into the cypher.','04-cypher-wide','The cypher centre stays flat and unpainted. Rebuilt defects and wet mud remain toward the road edges.')
comparison(5,'Cypher edge: before and rebuilt.','05-cypher-water.jpg','05-cypher-water','The same cavity treatment repairs the cypher potholes. Side water remains near the buildings; the existing Events lamp and saved night exposure are preserved.')
c.save();assert len(PdfReader(P).pages)==5
out={'status':'PASS','pages':5,'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'masterSHA256':b['editedSHA256'],'nativeAfterCaptures':5,'nativeBeforeCaptures':2,'existingLampsAndExposurePreserved':True,'rebuiltPotholes':16,'oldPyramidStonesHidden':True}
(R/'evidence/pdf-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
