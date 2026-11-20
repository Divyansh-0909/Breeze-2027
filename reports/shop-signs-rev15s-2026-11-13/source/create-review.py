from pathlib import Path
import json,hashlib,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];refs=json.loads((R/'references/sources.json').read_text());proof=json.loads((R/'evidence/build-verification.json').read_text());shots=json.loads((R/'evidence/captures.json').read_text());assert len(shots)==12
for s in shots:assert s['masterSHA256']==proof['editedSHA256'] and hashlib.sha256((R/'renders'/f"{s['key']}.png").read_bytes()).hexdigest()==s['sha256']
folders=json.loads((R/'evidence/drive-folders.json').read_text());specs=json.loads((R/'evidence/sign-art-specs.json').read_text())
for name,f in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/fonts'/f)))
W,H=595.28,841.89;M=30;CW=W-2*M;INK=HexColor('#273732');GRAY=HexColor('#64736a');GREEN=HexColor('#3b6352');out=R/'review/Breeze-Realistic-Shop-Boards-Review.pdf';c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Breeze — Realistic Indian shop name boards / Rev15S');c.setAuthor('Breeze project review')
def text(t,x,y,w=CW,size=9,color=INK):
 p=Paragraph(t,ParagraphStyle('p',fontName='Body',fontSize=size,leading=size*1.4,textColor=color));_,hh=p.wrap(w,1000);p.drawOn(c,x,y-hh);return y-hh
def head(t,n):
 c.setFillColor(INK);c.setFont('Bold',18);c.drawString(M,H-42,t);c.setFillColor(GRAY);c.setFont('Body',8);c.drawString(M,H-59,'BREEZE 2027 / GULLYVERSE · REV15S · 13 NOV 2026');c.setFont('Body',7);c.drawString(M,18,'Private native scene review · website integration pending');c.drawRightString(W-M,18,str(n))
def img(path,x,y,w,h):
 im=Image.open(path).convert('RGB');scale=min(w/im.width,h/im.height);ww,hh=im.width*scale,im.height*scale;buf=io.BytesIO();im.save(buf,'JPEG',quality=89);buf.seek(0);c.drawImage(ImageReader(buf),x+(w-ww)/2,y-hh,ww,hh);return y-hh
def render(key,y,h=305):return img(R/'renders'/f'{key}.png',M,y,CW,h)
head('Shop boards with a street identity',1);y=render('L07-after',H-82,330)-22
y=text('Five shop name boards now use bilingual lettering, painted colour fields, folded metal frames, visible screws and short bracket lamps. The designs draw from real Indian sign painting and shopfront photographs.',M,y,size=11)-18
y=text('The accepted shop interiors remain in place. Their small rear labels use matching artwork. The boards sit ahead of the lintel so it no longer hides the lower lettering.',M,y,size=10)-20
y=text('<b>What changed:</b> stronger Hindi/English name hierarchy; restrained fading and edge wear; physical frames and fixings; two warm 10 W sign lights per shop; correctly oriented paint on both sides of the lane.',M,y,size=10)-20
text(f'<a href="{folders["phase"]["url"]}" color="#3b6352">Sources and native checkpoint on the new Breeze Drive</a>',M,y)
c.showPage();head('New photographic references',2)
captions=['Painted red letters, borders and illustrated stock. Mohanlal Sihani / Shiv Arts, New Delhi.','Letter shadows and a fabricated frame. Mohanlal Sihani / Shiv Arts, New Delhi.','Bilingual lettering and restrained rust on sheet metal. India Street Lettering / BLAG.','Tapri Chai, Panvel: clear name hierarchy and a tea illustration. Justdial.','Mobile repair signage, Laxmi Nagar, Delhi: service-led lettering. Justdial.','General store, Bundi: bilingual fascia and its mounting context. Alamy T0E4JJ.']
for i,r in enumerate(refs):
 col,row=i%2,i//2;xx=M+col*(CW/2+7);yy=H-83-row*235;ww=CW/2-7;img(R/r['localFile'],xx,yy,ww,151);text(captions[i],xx,yy-159,ww,size=8);text(f'<a href="{r["url"]}" color="#3b6352">Source photograph</a>',xx,yy-207,ww,size=7.5)
c.showPage()
for page,s in enumerate(specs,3):
 head(s['id']+' / '+s['english'],page);y=text('<b>BEFORE</b> · Previous accepted shop scene',M,H-78,size=9)-5;y=render(s['id']+'-before',y)-13;y=text('<b>AFTER</b> · Same camera and inspection lights',M,y,size=9)-5;y=render(s['id']+'-after',y)-12;text('Bilingual paint, folded frame, screws and local sign lamps; the accepted shop goods and counter are retained.',M,y,size=8);c.showPage()
head('Night lighting / physical sign lamps',8);y=text('<b>Chai &amp; biscuits</b> · Actual scene lighting',M,H-78)-5;y=render('L07-night',y)-13;y=text('<b>Mobile repair</b> · Actual scene lighting',M,y)-5;y=render('R16-night',y)-12;text('The sign faces use reflected light, with two 10 W bracket lamps per board. Existing night exposure, haze, shop practicals, crowd and murals remain.',M,y,size=8);c.showPage()
head('The five original sign artworks',9);y=H-83
for s in specs:
 y=text('<b>'+s['id']+'</b> · '+s['english'],M,y,size=8.5)-5;y=img(R/f"delivery/sign-art/{s['id']}-face.png",M,y,CW,81)-19
text('These are original texture artworks, shown flat for lettering review. Reference photographs are credited research and are not used as the sign textures. The native master and a smaller board asset library are preserved with source and restoration instructions.',M,106,size=9);c.save();reader=PdfReader(out);assert len(reader.pages)==9
proof={'status':'PASS','pages':len(reader.pages),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'capturedViews':12,'masterSHA256':proof['editedSHA256'],'sourcePhotoCount':6};(R/'evidence/pdf-verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
