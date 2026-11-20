from pathlib import Path
import json,hashlib
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
from PIL import Image
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'evidence/build-verification.json').read_text());fresh=json.loads((R/'evidence/fresh-open.json').read_text());browser=json.loads((R/'evidence/browser-check.json').read_text());captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures)==10
for x in captures:assert x['masterSHA256']==proof['editedSHA256'] and hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256']
assert fresh['status']=='PASS' and browser['status']=='PASS'
for name,file in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/fonts'/file)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
W,H=842,595;ink='#18343d';muted='#53646b';cream='#f5f1e9';accent='#b66434'
P=R/'review/Breeze-Continuous-Asphalt-Implementation-Review.pdf';c=canvas.Canvas(str(P),pagesize=(W,H));c.setTitle('Breeze 2027 / Continuous asphalt implementation');layout=[]
def rect(x,y,w,h,col):
 c.setFillColor(HexColor(col));c.rect(x,y,w,h,fill=1,stroke=0)
def text(s,x,y,size=11,col=ink,bold=False):
 c.setFillColor(HexColor(col));c.setFont('DV-Bold' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,top,w,size=10,col=ink,leading=None):
 p=Paragraph(s,ParagraphStyle('body',fontName='DV',fontSize=size,leading=leading or size*1.4,textColor=HexColor(col)));_,h=p.wrap(w,800);assert top-h>34,(s,top-h);p.drawOn(c,x,top-h);layout.append({'page':c.getPageNumber(),'bottom':top-h,'text':s[:70]});return h
def base(n,title,sub):
 rect(0,0,W,H,cream);text('BREEZE 2027 / GULLYVERSE',34,567,9,muted,True);text('REV15T / OPTION A IMPLEMENTED',576,567,9,muted,True)
 size=min(27,27*774/max(774,pdfmetrics.stringWidth(title,'DV-Bold',27)));text(title,34,521,size,ink,True);para(sub,34,500,774,10,muted)
 c.setStrokeColor(HexColor('#d8d2c7'));c.line(34,31,808,31);text('13 November 2026 · Native scene review / private runtime ground asset',34,16,8,muted);text(str(n),794,16,8,muted)
def photo(key,x,y,w,h):
 p=R/'renders'/(key+'.jpg')
 with Image.open(p) as im:iw,ih=im.size
 scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;rect(x,y,w,h,'#ddd8ce');c.drawImage(ImageReader(str(p)),x+(w-dw)/2,y+(h-dh)/2,dw,dh);layout.append({'page':c.getPageNumber(),'capture':key})
def comparison(n,title,sub,key,left,right,notes):
 base(n,title,sub);text('BEFORE / REV15S',34,456,9,muted,True);text('AFTER / REV15T',432,456,9,accent,True);photo(key+'-before',34,210,376,235);photo(key+'-after',432,210,376,235);para(left,34,197,376,9.5,muted);para(right,432,197,376,9.5,ink)
 rect(34,55,774,76,'#e9e2d5');para(notes,47,117,748,11,ink,15.5);c.showPage()
comparison(1,'One asphalt road through the gully.','Matched native captures under the same temporary inspection lighting. The saved night lighting is preserved.','01-lane','The earlier flat lane surface beside the existing market shops.','Dusty charcoal asphalt, repairs of different ages, shallow edge defects and concrete apron patches at the open shops.','<b>Implemented:</b> the same asphalt treatment now runs over all four connected floor sections. The clear centre strip stays on its original grade; larger defects sit toward the edges.')
comparison(2,'The road carries through the approach.','The existing lane, 1:20 ramp and flared apron retain their footprint, height and slope.','02-approach','The previous approach into the courtyard, below the navigation board.','The asphalt continues up the original approach with consistent world-scale texture and wear.','<b>Flow preserved:</b> 471 sampled points along the walking strip match the original grade. Nine checks across the three floor joins show no new step. The original website movement, input and navigation source files are unchanged.')
comparison(3,'A flatter centre for the cypher.','The performance circle keeps its existing centre and 4.3 m radius. All 189 crowd models remain.','03-cypher','The previous courtyard surface with separate raised chalk-arc pieces.','A subtly resurfaced asphalt centre with a worn cream ring painted flush into the ground.','<b>Performance area:</b> 320 checks across the cypher centre remain flat. Most larger road damage is outside this area. Two planned defects were omitted to protect existing crowd positions.')
base(4,'Shallow broken asphalt at the edges.','Sixteen irregular depressions, with small rim chips and localized cracks. Five retain a shallow damp pocket.');photo('04-pothole-after',34,106,774,363)
para('<b>Surface detail:</b> the depressions measure about 3.4–6.5 cm at their sampled centres. Twelve repair patches, five shop-mouth apron repairs, three nearly flush drain covers and sparse loose aggregate complete the road treatment.',34,91,774,10,ink,14);c.showPage()
base(5,'The existing night atmosphere stays.','These two views use the saved native night lights. No temporary inspection lights are present.');photo('01-lane-night',34,210,376,235);photo('03-cypher-night',432,210,376,235)
para('<b>Gully:</b> the road picks up the existing warm shop and sign lighting. Most asphalt remains matte, with a few restrained damp details.',34,197,376,10,muted)
para('<b>Cypher:</b> the darker asphalt keeps the surrounding lamps and aftermovie screen prominent. The worn circle remains part of the road.',432,197,376,10,muted)
rect(34,55,774,76,'#e9e2d5');para('The comparison pages use the same temporary inspection setup to make the ground changes readable. This page records the unchanged night lighting without brightening the exported images.',47,117,748,11,ink,15.5);c.showPage()
base(6,'Scene preserved. Ground asset checked.','The complete editable master, runtime ground asset, source textures and restoration files are backed up separately.');photo('05-overview-after',34,126,520,325)
text('VERIFICATION',579,448,10,accent,True)
y=427
for line in ['49 native scenes / 48 historical','95 packed source images','189 original LOD0 crowd models','8 retained mural states','16 shallow road defects','12 varied asphalt repairs','5 damp pockets / 3 drain covers','3 browser views passed','71,068 ground-asset triangles']:
 y-=para(line,579,y,225,10,ink,14)+9
para('<b>Scope:</b> the editable 3D scene and a separate browser-ready ground asset are updated. Full-world production website integration remains pending. The existing production movement code was preserved, not replaced.',34,103,774,10,ink,14)
para('<link href="https://drive.google.com/drive/folders/1irpOPfPbjGSp4qry_JOhfhBn1p2PSFuZ" color="#16677b">Open the verified Rev15T source and native backup phase →</link>',34,60,774,9);c.showPage();c.save()
reader=PdfReader(P);assert len(reader.pages)==6
t=' '.join(' '.join(p.extract_text().split()) for p in reader.pages);assert all(x in t for x in ['OPTION A IMPLEMENTED','471','320','production website integration remains pending'])
out={'status':'PASS','file':str(P),'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'pages':6,'captures':10,'nativeMasterSHA256':proof['editedSHA256'],'sourceCaptureHashesVerified':True,'layout':layout,'imageKind':'Actual native 3D captures; inspection and native night lighting explicitly labelled','websiteIntegration':'Pending; separate runtime ground asset checked'}
(R/'evidence/pdf-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','file','bytes','sha256','pages','captures']}))
