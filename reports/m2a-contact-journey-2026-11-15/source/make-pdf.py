from pathlib import Path
import json,fitz
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
R=Path('/dev/shm/m2a-contact-journey-2026-11-15');out=R/'review/Breeze-2027-Native-Contact-Journey.pdf';W,H=842,595
c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Breeze 2027 - Native Contact Journey');c.setAuthor('Breeze 2027 private implementation review')
def page(title,num):
 c.setFillColorRGB(.965,.953,.918);c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColorRGB(.08,.23,.16);c.rect(40,552,40,4,fill=1,stroke=0);c.setFont('Helvetica',9);c.drawString(94,550,'BREEZE 2027 / NATIVE CONTACT JOURNEY');c.setFont('Helvetica-Bold',23);c.drawString(40,513,title);c.setFont('Helvetica',8);c.setFillColorRGB(.32,.43,.37);c.drawString(40,22,'15 November 2026 IST / Actual private browser captures / Original artwork preserved');c.drawRightString(802,22,str(num))
def pic(name,x,y,w,h):
 im=Image.open(R/'renders'/name);iw,ih=im.size;s=min(w/iw,h/ih);c.drawImage(ImageReader(im),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
def text(s,x,y,size=11):c.setFillColorRGB(.12,.25,.18);c.setFont('Helvetica',size);c.drawString(x,y,s)
page('Walk up. Leave a message. Return to your walk.',1)
text('The approved Contact frontage now uses the original walking controller and the adjoining native road.',40,480)
pic('01-contact-approach-laptop.png',40,225,375,235);pic('02-contact-at-window-laptop.png',427,225,375,235)
text('Approach the enquiry window',40,211,10);text('The message action becomes available within reach',427,211,10)
text('Closing the form restores the previous walking position, heading and pitch.',40,171,12)
text('The original quarry / Aftermovie controller matches its previous behavior across 16,800 compared frames.',40,145,10)
text('This subphase covers Contact. Other destinations and the complete world connection remain in progress.',40,111,10)
c.showPage()
page('The working form stays inside the wide window.',2)
pic('03-contact-form-laptop.png',40,63,762,430)
text('Actual desktop view. Test submissions use the existing Contact handler and an isolated local database.',40,44,9)
c.showPage()
page('Touch controls and a readable phone form.',3)
pic('05-contact-form-phone.png',40,54,222,440)
text('Checked in the browser',305,467,16)
lines=['Keyboard and real emulated touch-pad input','One Canvas across walking and form visits','Exact walking pose restored after closing','Back / Forward, deep links and refresh','Draft retained when submission fails','Messages persisted through the existing API','Compatible-texture retry after an asset failure','Readable form when WebGL is unavailable','Reduced motion and keyboard focus handling']
for i,line in enumerate(lines):text('  - '+line,305,432-i*26,11)
text('Phone emulation and software WebGL verify behavior.',305,143,10)
text('Physical-device performance remains a later milestone.',305,125,10)
text('No production route replacement or deployment.',305,91,10)
c.save()
d=fitz.open(out)
assert len(d)==3
for i,p in enumerate(d):
 assert p.get_text().strip();p.get_pixmap(matrix=fitz.Matrix(1,1)).save(R/'review'/f'page-{i+1:02d}.png')
(R/'evidence/pdf-check.json').write_text(json.dumps({'status':'PASS','pages':3,'allPagesRendered':True,'pdfBytes':out.stat().st_size,'visualInspection':'Pending'},indent=2)+'\n');print(out,out.stat().st_size)
