from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import fitz
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();b=read('evidence/build-verification.json');captures=read('evidence/captures.json')['captures'];assert len(captures)==5 and all(x['masterSHA256']==b['editedSHA256'] and sha(R/x['file'])==x['sha256']for x in captures);assert read('evidence/browser.json')['status']=='PASS'
for n,f in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/review-fonts'/f)))
out=R/'review/Breeze-Wide-Contact-Window-and-Restored-Graffiti-Rev15Z.pdf';c=canvas.Canvas(str(out),pagesize=(842,595),pageCompression=1);c.setTitle('Breeze — Wide Contact window and restored colour graffiti — Rev15Z');c.setAuthor('Breeze project review');page=0
def text(s,x,y,size=10,bold=False,color='#c8d1ce'):
 c.setFillColor(HexColor(color));c.setFont('DVB'if bold else'DV',size);c.drawString(x,y,s)
def start(title,sub):
 global page
 page+=1;c.setFillColor(HexColor('#14221d'));c.rect(0,0,842,595,fill=1,stroke=0);text('BREEZE / GULLYVERSE',28,567,9,True,'#a8c9b7');text(title,28,535,21,True,'#ffffff');text(sub,28,514,9);text('14 November 2026 · Rev15Z · 3D scene and private component review',28,18,8);text(str(page),805,18,8)
def picture(name,x,y,w,h):
 p=R/'renders'/name;i=Image.open(p);iw,ih=i.size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale;c.drawImage(str(p),x+(w-ww)/2,y+(h-hh)/2,width=ww,height=hh)
def end():c.showPage()
start('Contact Us — one wide window','Matching orange, gold and pink graffiti · person removed · the form fills the window without a centre divider.')
picture('01-contact-inspection.jpg',28,67,786,430);text('Native scene with temporary neutral inspection lighting.',28,46,10);end()
start('Accommodation — original graffiti restored','Exact earlier COMING / SOON artwork, placement and material. The foreground board and trim remain removed.')
picture('04-accommodation-inspection.jpg',28,67,786,430);text('Native scene with temporary neutral inspection lighting.',28,46,10);end()
start('Both places — actual night lighting','These views use the saved night lighting and local house fixtures, with no inspection fill.')
picture('02-contact-night.jpg',28,154,387,321);picture('05-accommodation-night.jpg',427,154,387,321);text('Contact Us',28,140,11,True,'#ffffff');text('Accommodation',427,140,11,True,'#ffffff');text('The Contact window contains only the form. The existing cypher house walls remain.',28,92,10);end()
start('Contact form — laptop and phone','Private browser component with temporary house context and review lighting. No messages are sent here.')
picture('browser-contact-laptop.jpg',28,95,596,396);picture('browser-contact-phone.jpg',647,77,167,414);text('1440 × 900 laptop',28,79,10,True,'#ffffff');text('390 × 844 phone',647,58,9,True,'#ffffff');text('Full-width desktop form and readable phone sheet. Full website integration remains pending.',28,45,9);end();c.save()
doc=fitz.open(out);assert len(doc)==4 and all(p.get_text().strip()for p in doc)
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1,1)).save(R/'review'/f'pdf-page-{i+1}.png')
result={'status':'PASS','file':str(out),'pages':len(doc),'bytes':out.stat().st_size,'sha256':sha(out),'allNativeCapturesFromCurrentMaster':True,'browserCaptureScope':'Isolated component; no live messages; not full-world integration'};(R/'evidence/pdf.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
