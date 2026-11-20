import json,hashlib,io,html
from pathlib import Path
from PIL import Image,ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import fitz
O=Path(__file__).resolve().parents[1];rows=json.loads((O/'evidence/captures.json').read_text());assert len(rows)==5
for r in rows:
 p=O/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];im=Image.open(p).convert('RGB');assert sum(ImageStat.Stat(im).mean)/3>25,r['file']
out=O/'review/Crowd-Rev15M-Review.pdf';c=canvas.Canvas(str(out),pagesize=(960,720));c.setTitle('Breeze 2027 / Consistent Aftermovie crowd / Rev15M')
def page(title,note):
 c.setFillColor(HexColor('#101922'));c.rect(0,0,960,720,fill=1,stroke=0);c.setFillColor(HexColor('#f5ba67'));c.setFont('Helvetica-Bold',12);c.drawString(36,684,'BREEZE 2027 / GULLYVERSE / REV15M');c.setFillColor(HexColor('#eee8dd'));c.setFont('Helvetica-Bold',23);c.drawString(36,644,title);c.setFont('Helvetica',11);c.drawString(36,616,note)
def picture(file,x,y,w,h):
 im=Image.open(O/file).convert('RGB');scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale;b=io.BytesIO();im.save(b,'JPEG',quality=95,subsampling=0);c.drawImage(ImageReader(io.BytesIO(b.getvalue())),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
page('The same crowd style across the environment','Nine placeholders replaced with actual Aftermovie character meshes and materials.')
c.setFont('Helvetica-Bold',12);c.drawString(36,578,'BEFORE');picture(rows[0]['file'],36,302,432,265);c.drawString(492,578,'AFTER');picture(rows[1]['file'],492,302,432,265)
c.setFont('Helvetica',13)
for i,line in enumerate(['Three approach-lane characters and six cypher characters now use the existing detailed models.','Nine wardrobe archetypes and varied relaxed/social poses. Original horizontal positions retained.','Existing Aftermovie audience, architecture, murals, navigation board and LED spacing preserved.','43 packed scenes. The previous 42 scenes and original Rev15L1 master remain intact.','This is the editable Blender environment; the separate website renderer has not been changed.']):c.drawString(36,258-i*33,line)
c.showPage()
for row in rows[1:]:
 page(row['title'],'Existing Aftermovie meshes and materials; original audience retained.');picture(row['file'],36,45,888,550);c.showPage()
c.save();d=fitz.open(out);assert len(d)==5 and all(p.get_images() for p in d)
(O/'evidence/review-validation.json').write_text(json.dumps({'status':'PASS','pages':5,'screenshots':5,'allCapturesNonblank':True,'pdfSHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'pdfBytes':out.stat().st_size},indent=2))
cards=''.join('<figure><a href="'+r['file']+'"><img src="'+r['file']+'" alt="'+html.escape(r['title'])+'"></a><figcaption>'+html.escape(r['title'])+'</figcaption></figure>' for r in rows)
(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev15M / Consistent crowd</title><style>body{background:#101922;color:#eee8dd;font:16px system-ui;margin:32px}a{color:#f5ba67}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{padding:12px}</style><h1>Aftermovie crowd models around the environment</h1><p>Nine placeholder people replaced. The original audience and wider sponsor-logo gaps are retained.</p><p><a href="review/Crowd-Rev15M-Review.pdf">Screenshot PDF</a></p><div class="grid">'+cards+'</div>');print('REVIEW PDF COMPLETE',flush=True)
