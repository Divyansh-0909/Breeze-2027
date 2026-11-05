from pathlib import Path
import json,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1]
def image(c,p,x,y,w,h):
 im=Image.open(p).convert('RGB');iw,ih=im.size;k=min(w/iw,h/ih);im.thumbnail((int(w*2),int(h*2)));b=io.BytesIO();im.save(b,format='JPEG',quality=91);b.seek(0);c.drawImage(ImageReader(b),x+(w-iw*k)/2,y+(h-ih*k)/2,iw*k,ih*k)
def page(c,title,sub):
 c.setFillColorRGB(.06,.08,.10);c.rect(0,0,420,760,fill=1,stroke=0);c.setFillColorRGB(.95,.77,.47);c.setFont('Helvetica',10);c.drawString(18,735,'BREEZE 2027 / GULLYVERSE');c.setFillColorRGB(.98,.96,.91);c.setFont('Helvetica-Bold',20);c.drawString(18,700,title);c.setFont('Helvetica',10);c.drawString(18,678,sub)
c=canvas.Canvas(str(O/'review/Rev15I1-Wider-OC-Names.pdf'),pagesize=(420,760));page(c,'Wider OC names','Each name now spans 90% of its portrait share');image(c,O/'renders/before.png',10,370,400,270);image(c,O/'renders/oc-wall.png',10,65,400,300);c.setFont('Helvetica',10);c.drawString(18,355,'Before above / wider name layout below');c.showPage()
for name,label in [('oc-wall','Updated wall'),('oc-mobile','Portrait composition'),('browser-oc','Interactive browser'),('browser-mobile','Mobile browser')]:
 page(c,label,'Portraits, roles and team heading remain unchanged');image(c,O/'renders'/f'{name}.png',10,90,400,550);c.showPage()
c.save();(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Wider OC names</title><style>body{background:#14191d;color:#f7eedb;max-width:1600px;margin:auto;padding:24px;font:18px system-ui}img{width:100%;display:block;margin:24px 0}</style><h1>Wider OC names</h1><p>All four names span 90% of their allocated portrait width. Portraits, role labels and team heading are preserved.</p>'+''.join('<h2>'+x+'</h2><img src="renders/'+x+'.png">'for x in ['before','oc-wall','oc-mobile','browser-oc','browser-mobile']));print('Review ready')
