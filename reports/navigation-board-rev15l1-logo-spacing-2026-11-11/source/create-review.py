from pathlib import Path
import json,hashlib,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import fitz
O=Path(__file__).resolve().parents[1];B=O.parent/'navigation-board-rev15l-led-sponsors-2026-11-11';out=O/'review/Navigation-Board-Rev15L1-Review.pdf';c=canvas.Canvas(str(out),pagesize=(960,720));c.setTitle('Rev15L1 / Wider sponsor-logo gaps')
def page(title,sub):
 c.setFillColor(HexColor('#101922'));c.rect(0,0,960,720,fill=1,stroke=0);c.setFillColor(HexColor('#f5ba67'));c.setFont('Helvetica-Bold',12);c.drawString(36,684,'BREEZE 2027 / GULLYVERSE / REV15L1');c.setFillColor(HexColor('#eee8dd'));c.setFont('Helvetica-Bold',25);c.drawString(36,642,title);c.setFont('Helvetica',12);c.drawString(36,614,sub)
def image(p,x,y,w,h):
 im=Image.open(p).convert('RGB');scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale;buf=io.BytesIO();im.save(buf,'JPEG',quality=95,subsampling=0);c.drawImage(ImageReader(io.BytesIO(buf.getvalue())),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
page('More space between sponsor logos','Three times the nominal gap; same 62 logos, fitted sizes and scrolling speed.')
c.setFont('Helvetica-Bold',12);c.drawString(36,584,'BEFORE / 24 cells');image(B/'renders/02-led-close.png',36,322,888,250);c.drawString(36,302,'AFTER / 72 cells');image(O/'renders/02-led-close.png',36,40,888,250);c.showPage()
for title,file in [('LED close-up','02-led-close.png'),('Whole navigation board','01-navigation-board.png')]:
 page(title,'Aftermovie points up. Past Sponsors stays below, with its closely hung scrolling LED.');image(O/'renders'/file,36,50,888,540);c.showPage()
c.save();d=fitz.open(out);assert len(d)==3 and all(p.get_images() for p in d)
(O/'evidence/review-validation.json').write_text(json.dumps({'status':'PASS','pages':3,'pdfBytes':out.stat().st_size,'pdfSHA256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
print('REVIEW PDF COMPLETE',flush=True)
