from pathlib import Path
import json,hashlib,math,random,io
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from PIL import Image
R=Path(__file__).resolve().parents[1];W,H=842,595
for n,f in [('DV','DejaVuSans.ttf'),('DV-Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/fonts'/f)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
sources=json.loads((R/'references/sources.json').read_text());refs={x['key']:x for x in sources}
P=R/'review/Breeze-Gully-Road-and-Cypher-Ground-Options.pdf';P.parent.mkdir(exist_ok=True)
c=canvas.Canvas(str(P),pagesize=(W,H));c.setTitle('Breeze 2027 / Gully road and cypher ground options');c.setAuthor('Breeze 2027 design study')
ink='#17323b';muted='#53636a';cream='#f5f1e9';accent='#cc6d36';checks=[]
def rect(x,y,w,h,col,stroke=None):
 c.setFillColor(HexColor(col));c.setStrokeColor(HexColor(stroke or col));c.rect(x,y,w,h,stroke=bool(stroke),fill=1)
def text(s,x,y,size=11,col=ink,bold=False):
 c.setFillColor(HexColor(col));c.setFont('DV-Bold' if bold else 'DV',size);c.drawString(x,y,s)
def para(s,x,top,w,size=10,col=ink,leading=None):
 style=ParagraphStyle('p',fontName='DV',fontSize=size,leading=leading or size*1.4,textColor=HexColor(col))
 p=Paragraph(s,style);_,h=p.wrap(w,1000);p.drawOn(c,x,top-h);checks.append({'page':c.getPageNumber(),'top':top,'bottom':top-h,'width':w,'text':s[:70]});assert top-h>=29,(s,top-h);return h
def base(number,title,sub):
 rect(0,0,W,H,cream);text('BREEZE 2027 / GULLYVERSE',34,566,9,muted,True);text('GROUND DIRECTION STUDY',592,566,9,muted,True)
 text(title,34,521,min(27,27*774/max(774,pdfmetrics.stringWidth(title,'DV-Bold',27))),ink,True);para(sub,34,501,774,10,muted)
 c.setStrokeColor(HexColor('#d9d5cb'));c.line(34,32,808,32);text('13 November 2026 · Reference study / scene unchanged',34,17,8,muted);text(str(number),793,17,8,muted)
def photo(key,x,y,w,h):
 s=refs[key];p=R/s['local']
 with Image.open(p) as im:
  iw,ih=im.size;im=im.convert('RGB');im.thumbnail((1500,1100));encoded=io.BytesIO();im.save(encoded,format='JPEG',quality=87);encoded.seek(0)
 scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
 rect(x,y,w,h,'#e4dfd6');c.drawImage(ImageReader(encoded),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
 checks.append({'page':c.getPageNumber(),'photo':key,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
def heading(k,label,x,y,w):
 text(k,x,y,10,accent,True);para('<b>'+label+'</b>',x,y-11,w,12)
base(1,'Let the road open into the cypher.','Recommendation: continue the gully’s worn asphalt into a wider neighbourhood chowk.')
photo('market',34,178,438,289)
para('Dharavi street corner · Baron Reznik / Aisle Seat Please<br/><link href="'+refs['market']['url']+'" color="#16677b">Open photo source</link>',34,165,438,8,muted)
text('ONE CONNECTED STREET',498,451,11,accent,True)
para('<b>The cypher should feel like a place people claimed within the same neighbourhood.</b>',498,429,310,17,ink,23)
y=337
for label,body in [('Gully','Dusty charcoal asphalt, irregular potholes, old repair patches and concrete shop edges.'),('Arrival','Carry the surface through the existing ramp and flare it gradually into the open area.'),('Cypher','Keep the asphalt palette. Use a flatter repaired centre, a faded cream circle, and more wear at the perimeter.')]:
 text(label.upper(),498,y,9,accent,True);h=para(body,498,y-12,310,10);y-=h+36
rect(34,53,774,57,'#17323b')
for x,head,sub in [(49,'MARKET LANE','Patched asphalt'),(312,'EXISTING APPROACH','Same surface family'),(574,'CYPHER CHOWK','Flat centre / worn edges')]:
 text(head,x,90,9,'#f6efdf',True);text(sub,x,70,9,'#f6efdf')
text('→',275,77,19,'#dba67b',True);text('→',538,77,19,'#dba67b',True)
c.showPage()
base(2,'Build the road from layers of use.','These Mumbai photos guide the asphalt damage. Market-lane references guide the edges and shop connections.')
photo('potholes',34,276,376,190);photo('internal',432,276,376,190)
para('Mumbai asphalt · India Today<br/>Uneven rims, mixed sizes and shallow standing water.<br/><link href="'+refs['potholes']['url']+'" color="#16677b">Photo source</link>',34,264,376,8.5,muted)
para('Everard Nagar, Sion East · Kirti Surve Parade / mid-day<br/>Broken edges, exposed aggregate and localized ponding.<br/><link href="'+refs['internal']['url']+'" color="#16677b">Open source and caption</link>',432,264,376,8.5,muted)
tiles=[
('01','Worn asphalt','Muted charcoal with dust and fine aggregate. Keep a visible difference between old surface and repairs.'),
('02','Repair history','Mix rectangular service-cut patches with a few irregular repairs. Vary their age and darkness.'),
('03','Pothole shape','Use broken, asymmetric rims with loose aggregate. Put the larger defects toward the edges.'),
('04','Shop connection','Concrete thresholds, small drain covers and worn aprons should join each shop to the road.'),
('05','Night response','Keep most of the surface matte. A few shallow damp pockets can pick up the existing warm shop lights.'),
('06','Where people move','Keep a clear walkable strip, the existing ramp, and the cypher centre. Let wear accumulate beside them.')]
for i,(k,h,b) in enumerate(tiles):
 x=34+(i%3)*265;y=138-(i//3)*93
 rect(x,y,244,83,'#fffdf8');text(k+' / '+h,x+10,y+64,10,ink,True);para(b,x+10,y+52,224,9,muted,12)
c.showPage()
base(3,'Three ways to finish the cypher.','Concept sketches only. The existing movement route, ramp and courtyard footprint are retained in every option.')
def plan(x,y,w,h,kind):
 rect(x,y,w,h,'#e5ddd0')
 road='#434342';surface={'A':'#494846','B':'#9b9890','C':'#9a9488'}[kind]
 # Continuous neck and flared open area, not a new navigation route.
 p=c.beginPath();p.moveTo(x+w*.37,y);p.lineTo(x+w*.63,y);p.lineTo(x+w*.63,y+h*.19);p.lineTo(x+w*.88,y+h*.34);p.lineTo(x+w*.88,y+h*.94);p.lineTo(x+w*.12,y+h*.94);p.lineTo(x+w*.12,y+h*.34);p.lineTo(x+w*.37,y+h*.19);p.close()
 c.setFillColor(HexColor(road));c.drawPath(p,stroke=0,fill=1)
 if kind!='A':
  rect(x+w*.13,y+h*.35,w*.74,h*.58,surface)
  # Show a broad repaired material seam at arrival.
  c.setStrokeColor(HexColor('#6f6b64'));c.setLineWidth(2);c.line(x+w*.13,y+h*.35,x+w*.87,y+h*.35)
 if kind=='C':
  c.setStrokeColor(HexColor('#77776f'));c.setLineWidth(.4)
  for row in range(10):
   yy=y+h*.35+row*h*.058;c.line(x+w*.13,yy,x+w*.87,yy)
   for col in range(9):
    xx=x+w*.13+(col+(row%2)*.5)*w*.082
    if xx<x+w*.87:c.line(xx,yy,xx,yy+h*.058)
 elif kind=='B':
  c.setStrokeColor(HexColor('#77766e'));c.setLineWidth(.7)
  c.line(x+w*.13,y+h*.61,x+w*.87,y+h*.61);c.line(x+w*.51,y+h*.35,x+w*.51,y+h*.93)
 else:
  # Smaller central resurfacing area blends into the asphalt.
  p=c.beginPath();p.moveTo(x+w*.3,y+h*.44);p.lineTo(x+w*.68,y+h*.42);p.lineTo(x+w*.76,y+h*.73);p.lineTo(x+w*.58,y+h*.84);p.lineTo(x+w*.28,y+h*.76);p.close();c.setFillColor(HexColor('#514f4a'));c.drawPath(p,stroke=0,fill=1)
 for xx,yy,ww,hh in [(.2,.42,.09,.055),(.77,.78,.075,.04),(.18,.79,.08,.04),(.45,.1,.06,.035)]:
  c.setFillColor(HexColor('#302f2c'));c.ellipse(x+w*xx,y+h*yy,x+w*(xx+ww),y+h*(yy+hh),stroke=0,fill=1)
 c.setStrokeColor(HexColor('#e9dfbd' if kind=='A' else '#ded4af'));c.setDash(6,3);c.setLineWidth(1.4);c.circle(x+w*.5,y+h*.64,w*.22,stroke=1,fill=0);c.setDash()
 c.setFillColor(HexColor('#a65f36'))
 for a in [15,55,105,150,200,245,290,330]:
  aa=math.radians(a);c.circle(x+w*.5+math.cos(aa)*w*.295,y+h*.64+math.sin(aa)*w*.295,2.7,fill=1,stroke=0)
 for side in [.02,.91]:
  rect(x+w*side,y+h*.37,w*.07,h*.52,'#b2a995')
 c.setStrokeColor(HexColor('#d1ad68'));c.setLineWidth(2);c.line(x+w*.5,y+5,x+w*.5,y+h*.26);c.line(x+w*.5,y+h*.26,x+w*.48,y+h*.23);c.line(x+w*.5,y+h*.26,x+w*.52,y+h*.23)
cards=[
('A','Continuous asphalt','RECOMMENDED','The lane widens into a road-surfaced chowk. A subtly repaired centre holds the existing cypher circle.','Best for the underground street feel and the strongest visual continuity.'),
('B','Concrete courtyard','ALTERNATIVE','The road arrives at a worn, grey concrete court. Use joints, scuffs and a rough repair seam at the entrance.','Best if you want the cypher to feel like a distinct community gathering space.'),
('C','Worn paving blocks','ALTERNATIVE','Asphalt meets aged interlocking blocks, with dirt in the joints and a few patched sections at the edges.','Fits the market references; the repeated pattern can look more orderly.')]
for i,(k,title,tag,body,verdict) in enumerate(cards):
 x=34+i*265;rect(x,116,244,351,'#fffdf8');text(tag,x+12,448,8,accent,True);text(k+' / '+title,x+12,429,12,ink,True);plan(x+12,239,220,174,k);para(body,x+12,225,220,9.4,ink,13);para(verdict,x+12,159,220,8.5,muted,11.5)
para('<b>My choice: A.</b> Let openness and the painted circle announce the cypher. Keep the material continuous, the centre flat, and the strongest road damage outside the performance area.',34,91,774,12,ink,17)
c.showPage()
base(4,'What the other surfaces would feel like.','The real references include pavers and smooth grey lane floors. Asphalt is our design choice for this gully.')
photo('pavers',34,273,376,193);photo('concrete',432,273,376,193)
para('<b>Paving-block alternative.</b> Dharavi market lane. Worn interlocking blocks, a utility cover and individually raised shop thresholds.<br/>Photo: az3 via Flickr / IIED · <link href="https://creativecommons.org/licenses/by-nc-sa/2.0/" color="#16677b">CC BY-NC-SA 2.0</link>',34,260,376,8.8,muted)
para('<b>Grey courtyard alternative.</b> Dharavi Koliwada alley. The continuous grey floor and small joints are a material reference for option B; this is not a photo of a cypher.<br/>Liron Shalit / urbz · 13 April 2026',432,260,376,8.8,muted)
text('PHOTO SOURCES',34,181,10,ink,True)
entries=[
('Aisle Seat Please / Baron Reznik','market'),
('India Today / Mumbai asphalt','potholes'),
('mid-day / Kirti Surve Parade','internal'),
('IIED / az3 via Flickr','pavers'),
('urbz / Liron Shalit','concrete')]
for i,(label,key) in enumerate(entries):
 x=34 if i<3 else 432;y=159-(i if i<3 else i-3)*23
 para('<link href="'+refs[key]['url']+'" color="#16677b">'+escape(label)+' → open source</link>',x,y,376,9)
rect(34,48,774,32,'#e9e3d6');para('Reference photographs inform new scene artwork. This PDF records a recommendation; no ground, movement or lighting changes have been implemented.',45,71,750,9,muted,12)
c.showPage();c.save()
out={'status':'CREATED','PDF':str(P),'bytes':P.stat().st_size,'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'pages':4,'recommendation':'A / Continuous worn asphalt road widening into the cypher chowk, flat repaired centre and worn perimeter','implementation':'Not started; design decision only','research':'Standard web source pages verified and direct image downloads inspected. No Firecrawl calls after the user asked to stop.','sources':sources,'layout':checks}
(R/'evidence/pdf-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['status','PDF','bytes','sha256','pages','implementation']}))
