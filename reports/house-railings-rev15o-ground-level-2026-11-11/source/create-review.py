import json,hashlib,io,html
from pathlib import Path
from PIL import Image,ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import fitz
O=Path(__file__).resolve().parents[1];rows=json.loads((O/'evidence/captures.json').read_text());assert len(rows)==5
for r in rows:
 p=O/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert sum(ImageStat.Stat(Image.open(p).convert('RGB')).mean)/3>25,r['file']
out=O/'review/Ground-House-Railings-Rev15O-Review.pdf';c=canvas.Canvas(str(out),pagesize=(960,720));c.setTitle('Clear ground-level house fronts / Rev15O')
def page(title,note):
 c.setFillColor(HexColor('#101922'));c.rect(0,0,960,720,fill=1,stroke=0);c.setFillColor(HexColor('#f5ba67'));c.setFont('Helvetica-Bold',12);c.drawString(36,684,'BREEZE 2027 / GULLYVERSE / REV15O');c.setFillColor(HexColor('#eee8dd'));c.setFont('Helvetica-Bold',23);c.drawString(36,644,title);c.setFont('Helvetica',11);c.drawString(36,616,note)
def picture(file,x,y,w,h):
 im=Image.open(O/file).convert('RGB');scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale;b=io.BytesIO();im.save(b,'JPEG',quality=95,subsampling=0);c.drawImage(ImageReader(io.BytesIO(b.getvalue())),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
page('Clear ground-level house fronts','Low rails and pickets removed from four house fronts; upper balcony railings retained.')
c.setFont('Helvetica-Bold',12);c.drawString(36,578,'BEFORE');picture(rows[0]['file'],36,302,432,265);c.drawString(492,578,'AFTER');picture(rows[1]['file'],492,302,432,265);c.setFont('Helvetica',13)
for i,line in enumerate(['Four remaining ground-level railing sections removed: L2/Events, R1, R3 and B2.','204 connected metal pieces removed, without changing any retained metalwork face.','Upper balconies, structural posts, beams, slabs, doors and windows remain.','The warm brick Events finish, current posters, crowds, murals and sponsor LED are retained.','45 packed scenes. The previous 44 scenes and original Rev15N master remain intact.']):c.drawString(36,260-i*32,line)
c.showPage()
for row in rows[1:]:
 page(row['title'],'Ground-level guardrails removed. Upper balcony railings and architecture retained.');picture(row['file'],36,45,888,550);c.showPage()
c.save();d=fitz.open(out);assert len(d)==5 and all(p.get_images() for p in d);(O/'evidence/review-validation.json').write_text(json.dumps({'status':'PASS','pages':5,'screenshots':5,'allCapturesNonblank':True,'pdfSHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'pdfBytes':out.stat().st_size},indent=2))
cards=''.join('<figure><a href="'+r['file']+'"><img src="'+r['file']+'" alt="'+html.escape(r['title'])+'"></a><figcaption>'+html.escape(r['title'])+'</figcaption></figure>' for r in rows)
(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev15O / Ground-level railings</title><style>body{background:#101922;color:#eee8dd;font:16px system-ui;margin:32px}a{color:#f5ba67}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{padding:12px}</style><h1>Clear ground-level house fronts</h1><p>Low railings removed at four house fronts. Upper balconies and the current Events finish are retained.</p><p><a href="review/Ground-House-Railings-Rev15O-Review.pdf">Before/after screenshot PDF</a></p><div class="grid">'+cards+'</div>');print('REVIEW PDF COMPLETE',flush=True)
