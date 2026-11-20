import io,json,hashlib,html
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
O=Path(__file__).resolve().parents[1];rows=json.loads((O/'evidence/captures.json').read_text());assert len(rows)==4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for r in rows:assert sha(O/r['file'])==r['sha256']
for key,f in [('Open','OpenSans-Regular.ttf'),('Bold','OpenSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(key,'/usr/share/fonts/truetype/open-sans/'+f))
W,H=960,720;out=O/'review/Navigation-Board-Rev15L-Review.pdf';c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1);c.setTitle('Gullyverse / Aftermovie and Past Sponsors LED / Rev15L');c.setAuthor('Breeze 2027')
def text(x,y,s,size=11,font='Open',color='#eee8db'):c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)
def para(x,y,s,w=884,size=11):
 p=Paragraph(s,ParagraphStyle('body',fontName='Open',fontSize=size,leading=size*1.45,textColor=HexColor('#b8bfc5')));_,h=p.wrap(w,H);p.drawOn(c,x,y-h)
def page(title):
 c.setFillColor(HexColor('#101922'));c.rect(0,0,W,H,stroke=0,fill=1);text(38,690,'GULLYVERSE / BREEZE 2027',9,'Bold','#f4bb6b');text(760,690,'11 NOVEMBER 2026',9,color='#b8bfc5');text(38,650,title,25,'Bold');c.setStrokeColor(HexColor('#3c4852'));c.line(38,31,922,31);text(38,16,'REV15L / NAVIGATION BOARD / SCENE REVIEW',8,color='#a3aeb6');c.setFont('Open',8);c.drawRightString(922,16,str(c.getPageNumber()))
cache={}
def pic(file,x,y,w,h):
 if file not in cache:
  im=Image.open(O/file).convert('RGB');b=io.BytesIO();im.save(b,'JPEG',quality=95,subsampling=0,optimize=True);cache[file]=(ImageReader(io.BytesIO(b.getvalue())),im.size)
 reader,(iw,ih)=cache[file];scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;c.drawImage(reader,x+(w-dw)/2,y+(h-dh)/2,dw,dh)
page('The updated navigation board')
text(38,614,'BEFORE',10,'Bold','#f4bb6b');text(499,614,'REV15L',10,'Bold','#f4bb6b');pic('inputs/navigation-before.png',38,205,422,395);pic(rows[0]['file'],499,205,422,395)
para(40,177,'<b>Aftermovie points up</b> as the first direction sign below Gullyverse. The bottom plaque reads <b>Past Sponsors</b> without an arrow. A closely hung red/amber dot-matrix screen scrolls the branch’s existing sponsor logos.',880,12)
para(40,102,'<b>Proposed replacement: Schedule.</b> It gives visitors a quick route to event timings. The preview shows that label in the freed-up slot; no new website route is claimed.',880,11);c.showPage()
for i,r in enumerate(rows):
 page(r['title']);c.bookmarkPage('view-'+str(i));c.addOutlineEntry(r['title'],'view-'+str(i),0);pic(r['file'],38,80,884,548)
 note='62 existing branch logo marks · continuous repeating scroll · closely hung below the non-directional Past Sponsors plaque.'
 if i==0:note='Aftermovie points up at the top; Schedule is proposed for the old Past Sponsors slot. The LED case leaves 2.15 m of walkway clearance.'
 if i==2:note='Short mounting brackets keep the screen 6 cm below the plaque. The frame is extended upward to fit the added top sign and screen.'
 para(40,69,note,880,10);c.showPage()
c.save();d=fitz.open(out);assert len(d)==5 and len(d.get_toc())==4
assert all(len(p.get_images()) for p in d)
(O/'evidence/review-validation.json').write_text(json.dumps({'status':'PASS','pages':len(d),'captures':4,'pdfSHA256':sha(out),'pdfBytes':out.stat().st_size},indent=2))
cards=''.join('<figure><a href="'+r['file']+'"><img loading="lazy" src="'+r['file']+'" alt="'+html.escape(r['title'])+'"></a><figcaption>'+html.escape(r['title'])+'</figcaption></figure>' for r in rows)
(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse / Navigation board</title><style>body{background:#101922;color:#eee8db;font:16px system-ui;margin:36px}a{color:#f4bb6b}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{padding:12px}video{width:min(100%,1000px)}</style><h1>Aftermovie and Past Sponsors LED / Rev15L</h1><p>62 existing sponsor marks · Schedule is proposed for the freed-up slot.</p><p><a href="review/'+out.name+'">Review PDF</a> · <a href="viewer/">Live 3D preview (serve over HTTP)</a></p><video controls preload="metadata" src="review/Navigation-Board-LED-Preview.mp4"></video><div class="grid">'+cards+'</div>')
print('PDF COMPLETE',len(d),'pages',out.stat().st_size)
