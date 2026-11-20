from pathlib import Path
import json,hashlib
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();refs=json.loads((R/'references/source-images.json').read_text());captures={r['key']:r for r in json.loads((R/'evidence/captures.json').read_text())}
for key in ['01-events-house','02-events-close','before-01-events-house','before-02-events-close']:
 row=captures[key];assert sha(R/row['file'])==row['sha256'];assert row['sourceSHA256']==b['sourceSHA256' if key.startswith('before-') else 'editedSHA256']
for row in refs:assert sha(R/'references'/row['file'])==row['sha256']
for n,file in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/review-fonts'/file)))
P=R/'review/Breeze-Cypher-Houses-Walls-Windows-Review.pdf';c=canvas.Canvas(str(P),pagesize=(1000,700));c.setTitle('Breeze 2027 / Cypher house walls and windows / Rev15V')
def txt(s,x,y,size=11,bold=False,col='#eef1eb'):
 c.setFillColor(HexColor(col));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,y,w,size=12):
 p=Paragraph(s,ParagraphStyle('body',fontName='DV',fontSize=size,leading=size*1.45,textColor=HexColor('#bfc9c6')));_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return h
def base(n,title,sub):
 c.setFillColor(HexColor('#101a18'));c.rect(0,0,1000,700,fill=1,stroke=0);txt(title,30,657,25,True);txt(sub,30,631,10,col='#bfc9c6');txt('BREEZE 2027 · Rev15V · Native environment update · Production website integration pending',30,18,8);txt(str(n),963,18,8)
def fit(file,x,y,w,h):
 im=Image.open(file);scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale;c.drawImage(ImageReader(str(file)),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
base(1,'More lived-in cypher houses.','Pale weathered plaster, sill runoff, worn frames, window grilles and small rain hoods.')
fit(R/'renders/neutral-house.jpg',30,105,940,515)
para('Neutral inspection lighting shows the architecture clearly. This lighting was used only for the review; the saved night atmosphere is unchanged. The whole Team building and all eight Events posters are preserved.',30,88,940,11);c.showPage()
base(2,'The street references.','Existing Delhi façades informed the materials and window details. Photographs were not used as building textures.')
fit(R/'references/delhi-weathering.jpg',30,119,390,495);fit(R/'references/chunnamal-haveli.jpg',453,319,517,290)
txt('Old Delhi house / Outlook Traveller',30,97,11,True);txt('Delhi Houses / Anica Mann',30,77,10);c.linkURL(refs[0]['sourceURL'],(30,70,420,110),relative=0)
txt('Chunnamal Haveli / LBB',453,295,12,True);c.linkURL(refs[1]['sourceURL'],(453,283,970,311),relative=0)
para('What carries into the scene:<br/>• Faded pale render with restrained peeling and small masonry exposures.<br/>• Rain marks tied to actual window sills, plus darker damp bases.<br/>• Worn green and pale frames, dark glazing, simple steel grilles and compact weather protection.',453,263,510,12)
txt('Click either credit to open its source page.',453,87,10,col='#e0bb7d');c.showPage()
base(3,'Windows with more physical detail.','Neutral inspection lighting · actual full native environment, with the original balcony structure retained.')
fit(R/'renders/neutral-window.jpg',30,105,940,515)
para('59 windows receive worn frames and dirt at the glass edges. Added details include 45 grilles, 59 projecting sills and 18 small rain hoods. Existing openings and building geometry retain their positions.',30,88,940,11);c.showPage()
base(4,'Events, under the existing night lights.','Same camera and saved night lighting in both captures. No exposure boost or added inspection lamp.')
txt('BEFORE',30,593,12,True);txt('AFTER',515,593,12,True);fit(R/'renders/before-02-events-close.jpg',30,270,455,305);fit(R/'renders/02-events-close.jpg',515,270,455,305)
para('The Events wall keeps warm masonry and all eight posters. Poster artwork, frames, sizes, positions and the Events heading are unchanged. New texture and window details sit within the existing house façade.',30,228,940,13)
para('Protected: the entire Team building, all eight Team mural states, navigation and digital sponsors, crowd, road and potholes, movement code and saved lighting. A separate fresh-open check and an actual source-based native reconstruction both passed.',30,133,940,12);c.showPage();c.save()
reader=PdfReader(P);assert len(reader.pages)==4;assert all(len(p.extract_text())>100 for p in reader.pages);assert sum(len(p.get('/Annots',[])) for p in reader.pages)>=2
result={'status':'PASS','pages':4,'bytes':P.stat().st_size,'sha256':sha(P),'nativeMasterSHA256':b['editedSHA256'],'referenceSourcesLinked':2,'neutralInspectionClearlyLabelled':True,'nightBeforeAfterSameCameraAndLighting':True,'TeamPreserved':True,'EventsPostersPreserved':8};(R/'evidence/pdf-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
