from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures['captures'])==3 and all(x['masterSHA256']==b['editedSHA256']for x in captures['captures'])
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/review-fonts'/file)))
pdf=R/'review/Breeze-Clean-Accommodation-and-Gully-Contact-Rev15X1.pdf';c=canvas.Canvas(str(pdf),pagesize=(1000,760));c.setTitle('Breeze / Clean Accommodation and gully Contact Us direction');page=0
def text(x,y,t,size=13,bold=False,color='#e7ecee'):
 c.setFillColor(HexColor(color));c.setFont('Bold'if bold else'Body',size);c.drawString(x,y,t)
def para(x,y,t,w=932,size=13,color='#e7ecee'):
 p=Paragraph(t,ParagraphStyle('p',fontName='Body',fontSize=size,leading=size*1.5,textColor=HexColor(color)));_,h=p.wrap(w,700);p.drawOn(c,x,y-h);return y-h
def box(x,y,w,h,color):c.setFillColor(HexColor(color));c.rect(x,y,w,h,fill=1,stroke=0)
def start(title,sub):
 global page
 page+=1;box(0,0,1000,760,'#10191e');text(34,720,title,25,True);para(34,694,sub,size=12,color='#b3c3cb');text(34,22,'BREEZE 2027 / Rev15X1 / 14 November 2026',10,color='#b3c3cb');text(940,22,str(page),10)
def image(file,x,y,w,h):
 im=ImageReader(str(R/file));iw,ih=im.getSize();a=min(w/iw,h/ih);c.drawImage(im,x+(w-iw*a)/2,y+(h-ih*a)/2,width=iw*a,height=ih*a,mask='auto')
start('Accommodation: cleaned wall','The blue-purple graphic on the low wall and the ACCOMMODATION label have been removed.')
image('renders/02-accommodation-inspection.jpg',34,101,932,558);para(34,83,'COMING / SOON and its existing wall-mounted light remain. The original low-wall surface is restored; the wall, windows, doors and surrounding architecture are preserved. Temporary neutral inspection lighting is shown here.',size=12);c.showPage()
start('The cleaned wall at night','Actual saved night lighting, with the same Accommodation lamp settings as Rev15X.')
image('renders/01-accommodation-night.jpg',34,101,932,558);para(34,83,'Only the two requested elements changed. All other graffiti, the Team murals, Events posters, wet road, crowd, gully-only streetlights and overhead cables remain as before.',size=12);c.showPage()
def title_paint(x,y,word,size):
 c.saveState();c.setStrokeColor(HexColor('#442c26'));c.setLineWidth(3);c.setFillColor(HexColor('#f1a339'));t=c.beginText(x,y);t.setFont('Bold',size);t.setTextRenderMode(2);t.textOut(word);c.drawText(t);c.restoreState();reset=c.beginText();reset.setTextRenderMode(0);c.drawText(reset)
def house(x,y,w,h,window=True):
 box(x,y,w,h,'#afa48c');box(x,y,w,24,'#5c5b52');box(x,y+h-8,w,8,'#6c6d60');c.setStrokeColor(HexColor('#817c69'));c.setLineWidth(1)
 for dx in [22,w-26]:c.line(x+dx,y+24,x+dx,y+h-12)
 c.bezier(x+8,y+h-18,x+w*.24,y+h-45,x+w*.61,y+h-25,x+w-9,y+h-6)
 title_paint(x+23,y+h-65,'CONTACT',33);title_paint(x+25,y+h-101,'US',30)
 if window:
  box(x+99,y+62,w-130,108,'#283c34');box(x+105,y+67,w-142,96,'#172a26');box(x+47,y+63,46,111,'#466352');box(x+w-31,y+63,20,111,'#466352')
  for z in range(6):c.line(x+50,y+72+z*15,x+87,y+72+z*15)
  box(x+87,y+58,w-104,12,'#64543c');box(x+87,y+50,w-104,8,'#3e382b');box(x+116,y+104,w-165,39,'#d7ccb2');text(x+125,y+119,'LEAVE A MESSAGE',11,True,color='#2a3e34')
  c.setFillColor(HexColor('#74776c'));p=c.beginPath();p.moveTo(x+79,y+180);p.lineTo(x+w-7,y+180);p.lineTo(x+w-22,y+195);p.lineTo(x+89,y+195);p.close();c.drawPath(p,fill=1,stroke=0)
  for i in range(12):c.line(x+91+i*19,y+180,x+98+i*19,y+194)
  box(x+15,y+75,29,47,'#71594a');box(x+19,y+79,21,39,'#dbd0b9')
 else:
  box(x+36,y+58,w-72,113,'#67563e');box(x+43,y+65,w-86,99,'#d8ceb4');text(x+58,y+140,'TALK TO THE CREW',15,True,color='#31463b');text(x+58,y+111,'Official contacts',12,color='#31463b');text(x+58,y+85,'Leave a message',12,True,color='#31463b')
 box(x+w-84,y+h-33,58,6,'#272d29');box(x+w-80,y+h-36,50,3,'#e6d5ab');box(x,y-18,w,18,'#4c4c44');c.setFillColor(HexColor('#363b37'));c.ellipse(x+34,y-15,x+139,y-4,fill=1,stroke=0)
start('Contact Us: make it part of a house','Design suggestions only. These diagrams are not new native geometry or a website implementation.')
house(34,341,448,300,True);house(518,341,448,300,False);text(34,313,'A / Enquiry window — recommended',16,True);text(518,313,'B / Painted help wall — simpler',16,True)
para(34,287,'Use an existing house opening near the right-hand Contact arrow. Faded green shutters, a worn wooden sill/counter and a small corrugated shade make it feel like a lane-side help point.',w=448,size=12);para(518,287,'Use a normal plaster bay with CONTACT / US graffiti and a pasted-paper contact board. This keeps the frontage flatter if you prefer no added counter or awning.',w=448,size=12)
para(34,193,'Shared style: weathered plaster, orange/gold/magenta paint like the Team titles, cream handwritten-style notices, aged timber/metal and one warm house-mounted practical. Keep the existing wet-road edge and walking space.',size=13)
para(34,119,'Interaction: approach -> tap/click Leave a message -> a readable form opens over the same world -> close to resume walking. Reuse the existing contact submission flow and admin inbox. Display only confirmed current email/phone details.',size=12)
para(34,55,'Choose the frontage direction before Contact construction. No new streetlight poles or separate standalone booth are proposed.',size=11,color='#b3c3cb');c.showPage();c.save();doc=fitz.open(pdf);assert len(doc)==3
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(.9,.9)).save(R/'review'/('page-%02d.png'%(i+1)))
proof={'status':'PASS','pages':len(doc),'output':str(pdf),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'ContactSchematicsLabelled':True};(R/'evidence/pdf.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
