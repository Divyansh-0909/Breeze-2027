import io,json,hashlib,html
from pathlib import Path
from PIL import Image,ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz

O=Path(__file__).resolve().parents[1]
manifest=json.loads((O/'evidence/carousel-manifest.json').read_text())
captures=json.loads((O/'evidence/captures.json').read_text())
details=json.loads((O/'evidence/detail-captures.json').read_text())
assert len(captures)==8 and len(details)==2
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for r in captures+details:
 assert sha(O/r['file'])==r['sha256']
 im=Image.open(O/r['file']);im.load();assert im.size==(1600,900) and max(ImageStat.Stat(im.convert('RGB')).stddev)>5
for name,font in [('Open','OpenSans-Regular.ttf'),('Bold','OpenSans-Bold.ttf'),('Semi','OpenSans-Semibold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/open-sans/'+font))
W,H=960,640;bg='#101317';fg='#f6eddc';muted='#b7b8b7';pink='#ff589e';gold='#f4c66d'
out=O/'review/Team-Murals-Black-Brick-Rev15K.pdf';c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1);c.setTitle('Gullyverse / Black Brick Team Murals / Rev15K');c.setAuthor('Breeze 2027')
def text(x,y,s,size=11,font='Open',col=fg):c.setFillColor(HexColor(col));c.setFont(font,size);c.drawString(x,y,s)
def para(x,y,s,w=880,size=11):
 p=Paragraph(s,ParagraphStyle('body',fontName='Open',fontSize=size,leading=size*1.5,textColor=HexColor(muted)));_,h=p.wrap(w,H);p.drawOn(c,x,y-h);return h
def page(label):
 c.setFillColor(HexColor(bg));c.rect(0,0,W,H,stroke=0,fill=1);text(38,610,'GULLYVERSE / BREEZE 2027',9,'Bold',gold);text(390,610,label.upper(),9,'Semi',muted);text(787,610,'11 NOVEMBER 2026',8,'Open',muted)
 c.setStrokeColor(HexColor('#3b3639'));c.line(38,32,922,32);text(38,17,'REV15K / BLACK BRICK TEAM MURALS / BLENDER SCENE REVIEW',8,'Open',muted);c.setFont('Open',8);c.drawRightString(922,17,str(c.getPageNumber()))
cache={}
def picture(r,x,y,w,h):
 k=r['file']
 if k not in cache:
  im=Image.open(O/k).convert('RGB');b=io.BytesIO();im.save(b,'JPEG',quality=95,subsampling=0,optimize=True);cache[k]=ImageReader(io.BytesIO(b.getvalue()))
 scale=min(w/1600,h/900);dw,dh=1600*scale,900*scale;c.drawImage(cache[k],x+(w-dw)/2,y+(h-dh)/2,dw,dh)

page('The new mural direction');text(38,562,'Black brick. Bold lettering.',32,'Bold');text(40,532,'Eight teams / overlapping portraits / handwritten names and roles',13,'Open',muted);picture(captures[0],38,115,884,400)
para(40,100,'Black-painted masonry with worn brick texture. Large titles overlap the lower portraits. Single-word titles stay on one line; two-word titles are stacked. Every non-OC role reads LEAD.',880,11);c.showPage()

page('Visual index');text(38,562,'All eight team murals',28,'Bold')
for i,r in enumerate(captures):
 x=38+(i%4)*225;y=355-(i//4)*195;picture(r,x,y,209,130);text(x,y-19,r['team'],10,'Semi');text(x,y-36,'PAGE '+str(i+3),8,'Open',gold);c.linkRect('','team-'+str(i),(x,y-40,x+209,y+130),relative=0,thickness=0)
para(40,107,'Two portraits: left and right, like Content. Four portraits: low outer pair with a higher centre pair, like Organising Committee. Three portraits: left, right and top centre. Names and role labels stay beside the faces.',880,11);c.showPage()

for i,r in enumerate(captures):
 slide=manifest['slides'][i];page('Team mural '+str(i+1)+' / 8');c.bookmarkPage('team-'+str(i));c.addOutlineEntry(r['team'],'team-'+str(i),0)
 text(38,563,r['team'],28,'Bold');text(40,535,'STACKED TWO-LINE TITLE' if len(slide['titleLines'])==2 else 'SINGLE-LINE TITLE',9,'Bold',pink)
 picture(r,38,91,884,434)
 para(40,79,' · '.join(p['name']+' — '+p['role'] for p in slide['people']),880,10);c.showPage()
for i,r in enumerate(details):
 page('Paint and wall detail');text(38,563,r['title'],24,'Bold');picture(r,38,95,884,440);para(40,80,'The black wall and the mural paint share the same masonry relief. Original scene lighting; no new review lights.',880,10);c.showPage()
c.save()
d=fitz.open(out);assert len(d)==12 and len(d.get_toc())==8
for p in d:
 assert len(p.get_images())>=1
(O/'evidence/review-validation.json').write_text(json.dumps({'status':'PASS','pages':len(d),'teams':8,'detailViews':2,'pdfBytes':out.stat().st_size,'pdfSHA256':sha(out),'allCaptureChecksumsMatch':True},indent=2))
cards=[]
for r in captures+details:
 title=r.get('team') or r['title'];cards.append(f'<figure><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{html.escape(title)}"></a><figcaption>{html.escape(title)}</figcaption></figure>')
(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse / Black brick murals</title><style>body{background:#101317;color:#f6eddc;font:16px system-ui;margin:40px}a{color:#f4c66d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{padding:10px}</style><h1>Black brick team murals / Rev15K</h1><p><a href="review/'+out.name+'">Combined laptop PDF</a> · <a href="viewer/">Interactive preview (serve this folder over HTTP)</a></p><div class="grid">'+''.join(cards)+'</div>')
print('PDF COMPLETE',len(d),'pages',out.stat().st_size,'bytes')
