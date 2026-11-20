from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import fitz
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
b=read('evidence/build-verification.json');captures=read('evidence/captures.json')['captures']
assert len(captures)==5 and all(x['masterSHA256']==b['editedSHA256'] and sha(R/x['file'])==x['sha256'] for x in captures)
assert read('evidence/browser.json')['status']=='PASS'
for n,f in [('DV','DejaVuSans.ttf'),('DVB','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,str(R/'source/review-fonts'/f)))
out=R/'review/Breeze-Contact-Window-and-Clean-Accommodation-Rev15Y.pdf';c=canvas.Canvas(str(out),pagesize=(842,595),pageCompression=1);c.setTitle('Breeze — Contact enquiry window and clean Accommodation wall — Rev15Y');c.setAuthor('Breeze project review');page=0
def text(s,x,y,size=10,bold=False,color='#c8d1ce'):
 c.setFillColor(HexColor(color));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def start(title,sub):
 global page
 page+=1;c.setFillColor(HexColor('#14221d'));c.rect(0,0,842,595,fill=1,stroke=0);text('BREEZE / GULLYVERSE',28,567,9,True,'#a8c9b7');text(title,28,535,21,True,'#ffffff');text(sub,28,514,9);text('14 November 2026 · Rev15Y · Native art + private component review',28,18,8);text(str(page),805,18,8)
def picture(name,x,y,w,h):
 p=R/'renders'/name;i=Image.open(p);iw,ih=i.size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale;c.drawImage(str(p),x+(w-ww)/2,y+(h-hh)/2,width=ww,height=hh)
def end():c.showPage()
start('Contact Us — enquiry window','Native scene · temporary neutral inspection lighting makes the wall and placement easy to inspect.')
picture('01-contact-inspection.jpg',28,69,786,430)
text('Person inside the left opening · wide message panel on the right · centred white brush heading',28,49,10)
end()
start('Contact Us — lighting and house context','Left: actual saved night lighting. Right: wider native context with temporary neutral inspection lighting.')
picture('02-contact-night.jpg',28,173,387,302);picture('03-contact-context.jpg',427,173,387,302)
text('The existing house bay supplies the opening.',28,134,11,True,'#ffffff');text('Local shaded lamps serve the counter and heading.',28,112,10)
text('The message surface takes about 72% of the usable frontage.',28,89,10);text('Native form labels illustrate the layout; browser fields are shown on the next pages.',28,67,10)
end()
start('Accommodation — house wall only','The complete foreground barrier, coping and trim are removed. COMING / SOON uses the same white brush style.')
picture('04-accommodation-inspection.jpg',28,173,387,302);picture('05-accommodation-night.jpg',427,173,387,302)
text('Neutral inspection',28,156,10,True,'#ffffff');text('Actual saved night lighting',427,156,10,True,'#ffffff')
text('The cypher house wall, door, window and existing wall light remain.',28,110,11)
text('The extra Accommodation label and small supporting graphic remain removed.',28,86,10)
end()
start('Contact form — laptop component review','1440 × 900 browser capture · temporary review context, separate from the full website environment.')
picture('browser-contact-laptop.jpg',28,62,786,432)
text('Accessible HTML fields align with the right panel. Review mode sends no messages.',28,43,10)
end()
start('Contact form — phone layout','390 × 844 browser capture · a readable form sheet follows the scene on a narrow screen.')
picture('browser-contact-phone.jpg',34,43,209,453)
for s,y,size,bold in [('Checked in the private component',458,15,True),('Person remains on the left of the message panel.',423,10,False),('The form fits a narrow screen without horizontal overflow.',398,10,False),('A failed send preserves the message.',373,10,False),('A confirmed test success resets the form.',348,10,False),('No external message was sent during review.',323,10,False),('Next integration step',266,15,True),('Mount the component into the existing world and movement flow.',231,10,False),('Connect the existing contact endpoint and admin inbox.',206,10,False),('Full-world integration and visual approval remain open.',181,10,False)]:text(s,276,y,size,bold,'#ffffff' if bold else '#c8d1ce')
end();c.save()
doc=fitz.open(out);assert len(doc)==5 and all(p.get_text().strip() for p in doc)
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1,1)).save(R/'review'/f'pdf-page-{i+1}.png')
result={'status':'PASS','file':str(out),'pages':len(doc),'bytes':out.stat().st_size,'sha256':sha(out),'allNativeCapturesFromCurrentMaster':True,'browserCaptureScope':'Isolated component; no live messages; not full-world integration'};(R/'evidence/pdf.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
