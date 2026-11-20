from pathlib import Path
import json,shutil
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
R=Path('/dev/shm/texture-alpha-fix-2026-11-15');O=Path('/dev/shm/Breeze-2027-runtime/public/models/gullyverse/locked-rev15z-clean-v2');proof=json.loads((R/'evidence/visual-regression.json').read_text());assert proof['status']=='PASS'
for name,label in [('DejaVuSans.ttf','D'),('DejaVuSans-Bold.ttf','DB')]:pdfmetrics.registerFont(TTFont(label,'/usr/share/fonts/truetype/dejavu/'+name))
P=R/'review/Breeze-2027-Clean-Textures-and-Transparent-Graffiti.pdf';c=canvas.Canvas(str(P),pagesize=(900,650));c.setTitle('Breeze 2027 — Clean Textures and Transparent Graffiti');c.setAuthor('Breeze 2027');page=0
style=ParagraphStyle('p',fontName='D',fontSize=11,leading=16,textColor=HexColor('#233b30'))
def text(value,x,y,w=816,size=11):
 p=Paragraph(value,ParagraphStyle('a',parent=style,fontSize=size,leading=size*1.4));_,h=p.wrap(w,600);p.drawOn(c,x,y-h);return y-h
def start(title):
 global page
 page+=1;c.setFillColor(HexColor('#f7f3e9'));c.rect(0,0,900,650,fill=1,stroke=0);c.setFillColor(HexColor('#245a44'));c.rect(42,609,43,5,fill=1,stroke=0);c.setFont('D',10);c.drawString(99,605,'BREEZE 2027 · TEXTURE AND TRANSPARENCY CORRECTION');c.setFillColor(HexColor('#123427'));c.setFont('DB',23);c.drawString(42,566,title);c.setFillColor(HexColor('#647769'));c.setFont('D',9);c.drawString(42,22,'15 November 2026 (IST) · Actual private browser captures · Original artwork preserved');c.drawRightString(858,22,str(page))
def shot(path,x,y,w,h,alpha=False):
 im=ImageReader(str(path));iw,ih=im.getSize();s=min(w/iw,h/ih);c.drawImage(im,x+(w-iw*s)/2,y+(h-ih*s)/2,width=iw*s,height=ih*s,mask='auto'if alpha else None)
def crop(path,roi,box):
 im=ImageReader(str(path));iw,ih=im.getSize();a,b,d,e=roi;x,y,w,h=box;s=min(w/(d-a),h/(e-b));c.saveState();p=c.beginPath();p.rect(x,y,w,h);c.clipPath(p,stroke=0,fill=0);c.drawImage(im,x-a*s,y-(ih-e)*s,width=iw*s,height=ih*s);c.restoreState()
def checker(x,y,w,h):
 size=14
 for yy in range(int(h/size)+1):
  for xx in range(int(w/size)+1):
   c.setFillColor(HexColor('#e4e7df'if(xx+yy)%2 else'#cbd3c5'));c.rect(x+xx*size,y+yy*size,min(size,w-xx*size),min(size,h-yy*size),fill=1,stroke=0)
start('Clean surfaces. No black graffiti rectangle.')
text('The grain came from noisy, sparsely allocated lighting maps. The export now uses a denoised, shared lighting atlas and proper texture filtering. Transparent graffiti no longer bakes a solid shadow onto the wall.',42,539,size=11)
shot(R/'renders/before-laptop.png',42,250,400,250);shot(R/'renders/clean-baseline-laptop.png',458,250,400,250)
text('<b>Before</b> · mottled lighting and a dark rectangular patch',42,239,400,size=10);text('<b>After</b> · clean lighting with the wall visible around the paint',458,239,400,size=10)
text('Closer view of the lettering and wall',42,220,size=10)
crop(R/'renders/before-laptop.png',(470,220,980,370),(42,83,400,118));crop(R/'renders/clean-baseline-laptop.png',(470,220,980,370),(458,83,400,118))
text('Lettering, colours, outlines, placement and original image files are unchanged.',42,63,size=10);c.showPage()
start('Updated laptop browser view')
shot(R/'renders/clean-compressed-laptop.png',42,65,816,485)
text('Actual KTX2/Meshopt browser render at 1440 × 900. Surface texture detail remains; the noisy lighting and rectangular decal shadow are corrected.',42,57,size=9);c.showPage()
start('Phone view and transparent graffiti assets')
shot(R/'renders/clean-compressed-phone.png',42,53,222,480)
text('CONTACT US · original transparent image',295,535,550,size=11);checker(295,367,550,144);shot(O/'graffiti/contact-us.png',307,379,526,120,True)
text('COMING / SOON · original transparent image',295,351,550,size=11);checker(295,140,550,190);shot(O/'graffiti/coming-soon.png',307,150,526,170,True)
text(f"Both headings export with alpha blending and no rectangular shadow. {proof['actualMeshTransparentTexelProbes']} clear points inside the actual CONTACT US mesh matched the wall exactly when the lettering was hidden. Desktop and phone imports, one-canvas cleanup and error checks passed.",295,121,550,size=10)
text('Checkerboard shows transparency. These are the original PNGs, with no redraw or blur.',295,60,550,size=9);c.save()
doc=fitz.open(P);assert len(doc)==3
for i,p in enumerate(doc):assert len(p.get_text())>100;p.get_pixmap(matrix=fitz.Matrix(.9,.9)).save(R/'review'/f'page-{i+1:02d}.png')
(R/'evidence/pdf-check.json').write_text(json.dumps({'status':'PASS','pages':3,'allPagesRendered':True,'pdfBytes':P.stat().st_size},indent=2)+'\n');print(P)
