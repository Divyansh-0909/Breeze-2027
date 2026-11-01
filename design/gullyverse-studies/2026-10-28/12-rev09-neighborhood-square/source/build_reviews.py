"""Actual offline Blender images only; small PDF embeddings, original PNG gallery."""
from pathlib import Path
import json,html,textwrap,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet
O=Path(__file__).resolve().parents[1];R=O/'review';R.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
def frame(ed,pose):return O/'renders'/ed/(pose+'.png')
cache={}
def fitted(c,p,x,y,w,h):
 key=str(p)
 if key not in cache:
  im=Image.open(p).convert('RGB');buf=io.BytesIO();im.save(buf,format='JPEG',quality=87,subsampling=0);buf.seek(0);cache[key]=ImageReader(buf)
 im=cache[key];iw,ih=im.getSize();k=min(w/iw,h/ih);ww,hh=iw*k,ih*k;c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def txt(c,text,x,y,w,font=11,leading=15):
 c.setFont('DV',font);line=''
 for word in text.split():
  t=(line+' '+word).strip()
  if pdfmetrics.stringWidth(t,'DV',font)>w:c.drawString(x,y,line);y-=leading;line=word
  else:line=t
 if line:c.drawString(x,y,line);y-=leading
 return y
def page(c,title,n,W=420,H=746):
 c.setFillColor(HexColor('#f4f2eb'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#212b2a'));c.setFont('DVB',15);y=H-32
 for line in textwrap.wrap(title,44 if W==420 else 90):c.drawString(18,y,line);y-=20
 c.setFont('DV',8);c.drawString(18,14,'REV09 / OFFLINE BLENDER / SUPPORT OFF / NOT WEBSITE');c.drawRightString(W-18,14,str(n))
def pair(c,n,title,a,b,la='BEFORE / Rev08 architecture + old crowd',lb='NEW / Rev09 square + same old crowd',notes='Matched camera, world, exposure and 16 samples. All five optional support lights remain 0 W. Original floor, crowd, screen, board and destinations unchanged.'):
 page(c,title,n);c.setFont('DVB',9);c.drawString(18,650,la);fitted(c,a,18,421,384,216);c.drawString(18,403,lb);fitted(c,b,18,174,384,216);txt(c,notes,18,151,384,10,14);c.showPage()
titles={'01-plan':'Square plan / open center and entry','02-entry-square':'Lane arrival into the neighborhood','03-aerial':'Aerial / residential perimeter','04-front':'Front / same screen and C180','05-back':'Reverse / open lane entrance','06-left-diagonal':'Left diagonal / square enclosure','07-right-diagonal':'Right diagonal / roofline layering','08-left-house':'House detail / left frontage','09-right-house':'House detail / right frontage','10-team':'Team remains on the right','11-events':'Events remains on the left','12-elevation':'Exterior elevation / supported floor','13-return-left':'Original left return artwork','14-return-right':'Original right return artwork','15-mobile':'Mobile / square arrival','16-mobile-lateral':'Mobile / lateral enclosure','17-chaar':'Chaar Diwari / original shutter','18-ritviz':'Ritviz / original shutter','19-neha':'Neha Kakkar / original shutter'}
phone=R/'Rev09-Neighborhood-Square-Phone-Review.pdf';c=canvas.Canvas(str(phone),pagesize=(420,746));c.setTitle('Rev09 neighborhood square and previous C180 crowd — private review');n=1
page(c,'Neighborhood square + preferred C180 crowd',n);fitted(c,frame('after','03-aerial'),18,330,384,330);txt(c,'Fifteen multi-storey houses now define the open courtyard. The exact earlier 180-person Blender crowd is restored. Website crowd remains archived, not selected.',18,294,384,12,18);txt(c,'Private source/render study only. No website changes or lighting changes. Visual approval is pending; steel rack/table identity remains unresolved.',18,172,384,11,16);c.showPage();n+=1
for pose in list(titles)[:14]:
 pair(c,n,titles[pose],frame('before',pose),frame('after',pose));n+=1
for pose in ['15-mobile','16-mobile-lateral']:
 page(c,titles[pose],n);fitted(c,frame('before',pose),18,172,185,460);fitted(c,frame('after',pose),217,172,185,460);txt(c,'Before',18,650,180,10);txt(c,'Rev09',217,650,180,10);txt(c,'Same portrait pose, lens and 576 × 1024 output. This is an actual offline render, not mobile-device performance evidence.',18,136,384,11,16);c.showPage();n+=1
for pose in ['17-chaar','18-ritviz','19-neha']:
 pair(c,n,titles[pose],frame('before',pose),frame('after',pose),notes='Exact original painting, physical slats, host and mapping. New houses do not move, retarget or repaint the art. The other four original wall motifs also remain exact.');n+=1
for pose in ['04-front','03-aerial']:
 pair(c,n,'Crowd control / '+titles[pose],frame('before',pose),frame('web-history',pose),'SELECTED STYLE / previous Blender C180','HISTORICAL ONLY / website Man-Woman crowd','Same Rev08 terrace, camera and lighting. Original crowd: 54,000 triangles; website import: 639,792. User aesthetic preference is authoritative. Rev09 uses the ORIGINAL crowd.');n+=1
page(c,'Steel rack/table source remains pending',n)
inv=sorted((O/'evidence/furniture-inventory').glob('*.png'))
for j,p in enumerate(inv[:3]):fitted(c,p,18,470-j*160,384,150)
txt(c,'Source inventory only: historical actual-browser context and offline source diagnostics. Active truss/barrier/road cases and an archived timber/cloth table are distinct. None is declared the intended steel table.',18,120,384,10,14);txt(c,'Please identify the page, section or object. Existing five shop counters remain unchanged.',18,47,384,10,14);c.showPage();n+=1
page(c,'Decision, costs and remaining limits',n);y=txt(c,'READY FOR USER VISUAL REVIEW. Fifteen 2–5-storey houses enclose 96.14% of eligible projected frontage, excluding the protected 16.6 m entrance. The original 1,088 m² floor and 40-second route remain fixed.',18,650,384,12,18)
y=txt(c,'Rev09: 147,784 triangles, versus 127,008 for Rev08 architecture with the same original crowd. Net architecture +20,776. Same 33 image owners; conservative RGBA8+mips estimate 138.53 MiB. No new lights or emission.',18,y-18,384,11,17)
y=txt(c,'Strict geometry, original-object preservation, crowd/house, sightline and route checks pass. Two inherited negative-Y scooter approaches remain blocked. One cloud-memory-interrupted check passed unchanged after serial rerun.',18,y-18,384,11,17)
y=txt(c,'Remaining art limits: simplified interiors, subdued windows, repeated construction grammar, broad outer/podium surfaces and low-sample walking-video grain. No photorealism, glTF/runtime or physical-device certification is claimed.',18,y-18,384,11,17)
txt(c,'Open GALLERY.html after extracting all five complementary archives. The 40-second offline walk uses 80 genuine samples of the original route; it is not gameplay FPS. Stop for square/crowd approval. Website unchanged.',18,y-18,384,11,17);c.showPage();c.save();assert 15<=n<=25,n
f=canvas.Canvas(str(R/'Rev09-Full-Matched-Comparisons.pdf'),pagesize=(960,780));pg=0
for pose,title in titles.items():
 pg+=1;page(f,title,pg,960,780);f.setFont('DV',10);f.drawString(20,700,'BEFORE / Rev08 architecture + original C180');fitted(f,frame('before',pose),20,373,920,314);f.drawString(20,352,'NEW / Rev09 housing + same C180');fitted(f,frame('after',pose),20,27,920,312);f.showPage()
f.save()
styles=getSampleStyleSheet()
for name in ['BodyText','Heading1','Heading2']:styles[name].fontName='DVB'if name.startswith('Heading')else'DV'
styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;flow=[]
for block in (O/'REPORT.md').read_text().split('\n\n'):
 if not block.strip():continue
 style=styles['Heading1']if block.startswith('# ')else styles['Heading2']if block.startswith('## ')else styles['BodyText'];flow.extend([Paragraph(html.escape(block.lstrip('# ').replace('`','')).replace('\n','<br/>'),style),Spacer(1,7)])
SimpleDocTemplate(str(R/'Rev09-Technical-Report.pdf'),pagesize=(595,842),leftMargin=34,rightMargin=34,topMargin=34,bottomMargin=34).build(flow)
cards=[]
for pose,title in titles.items():
 cards.append('<article><h2>'+html.escape(title)+'</h2><div class="pair">'+''.join('<figure><a href="'+str(frame(e,pose).relative_to(O))+'"><img loading="lazy" src="'+str(frame(e,pose).relative_to(O))+'"></a><figcaption>'+l+'</figcaption></figure>'for e,l in [('before','BEFORE / Rev08 + original crowd'),('after','NEW / Rev09 + original crowd')])+'</div></article>')
for pose in ['04-front','03-aerial']:
 cards.append('<article><h2>Historical crowd control / '+pose+'</h2><div class="pair">'+''.join('<figure><img loading="lazy" src="'+str(frame(e,pose).relative_to(O))+'"><figcaption>'+e+'</figcaption></figure>'for e in ['before','web-history'])+'</div><p>Website crowd archived only. Same Rev08 architecture, pose and lighting.</p></article>')
for p in inv:cards.append('<article><h2>Furniture source inventory / '+html.escape(p.name)+'</h2><p>Historical source context or offline source diagnostic; no furniture selection.</p><img loading="lazy" src="'+str(p.relative_to(O))+'"></article>')
links=' '.join('<a href="'+str(p.relative_to(O))+'">'+str(i+1)+'</a>'for i,p in enumerate(sorted((O/'renders/walk').glob('*.png'))))
gallery='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev09 private neighborhood square</title><style>body{font:16px/1.5 system-ui;max-width:1500px;margin:24px auto;padding:0 20px;background:#152021;color:#f1eee6}a{color:#a6d7dc}article{border-top:1px solid #546463;padding:24px 0}img{width:100%;max-height:1000px;object-fit:contain}figure{margin:0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>Rev09 / neighborhood square + previous C180 crowd</h1><p>Private actual offline Blender renders. Same cameras, world, exposure, 16 samples and five supports OFF. No website edits. User visual approval pending. Steel rack/table identity pending.</p><p><a href="REPORT.md">Technical report</a> · <a href="FURNITURE-SOURCE-STATUS.md">Furniture source status</a> · <a href="review/Rev09-Neighborhood-Square-Phone-Review.pdf">24-page phone PDF</a> · <a href="review/Rev09-Full-Matched-Comparisons.pdf">19 matched full comparisons</a> · <a href="RESTORE.md">Restoration</a></p>'+''.join(cards)+'<h2>Original 40-second straight route / offline inspection</h2><video controls width="100%" src="review/Rev09-Original-40s-Walk-Offline.mp4"></video><p>80 genuine source-frame samples, 2fps, 480×270, 2 EEVEE samples. This is not gameplay FPS.</p><p>'+links+'</p></html>'
(O/'GALLERY.html').write_text(gallery);(O/'evidence/review-build.json').write_text(json.dumps({'status':'PASS','phonePages':n,'fullComparisonPages':pg,'allNewImagesActualOfflineBlender':True,'historicalSourceInventoryLabelled':True,'phonePDF':str(phone.relative_to(O))},indent=2));print('REVIEWS_BUILT',n,pg)
