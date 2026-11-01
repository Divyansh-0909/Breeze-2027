from pathlib import Path
import json,html,textwrap,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
O=Path(__file__).resolve().parents[1];R=O/'review';R.mkdir(exist_ok=True);pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
def frame(edition,pose):return O/'renders'/edition/(pose+'.png')
image_cache={}
def fitted(c,p,x,y,w,h):
 # PDFs use efficient JPEG embeddings; the gallery keeps every full-resolution PNG.
 key=str(p)
 if key not in image_cache:
  pic=Image.open(p).convert('RGB');buf=io.BytesIO();pic.save(buf,format='JPEG',quality=87,subsampling=0);buf.seek(0);image_cache[key]=ImageReader(buf)
 im=image_cache[key];iw,ih=im.getSize();k=min(w/iw,h/ih);ww,hh=iw*k,ih*k;c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh,mask='auto')
def txt(c,text,x,y,w,font=11,leading=15):
 c.setFont('DejaVu',font);words=text.split();line=''
 for word in words:
  candidate=(line+' '+word).strip()
  if pdfmetrics.stringWidth(candidate,'DejaVu',font)>w:
   c.drawString(x,y,line);y-=leading;line=word
  else:line=candidate
 if line:c.drawString(x,y,line);y-=leading
 return y
def page(c,title,number,subtitle='',W=420,H=746):
 c.setFillColor(HexColor('#f4f2eb'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#212b2a'));c.setFont('DejaVuBold',15)
 yy=H-32
 for line in textwrap.wrap(title,42):c.drawString(18,yy,line);yy-=20
 if subtitle:txt(c,subtitle,18,yy-5,W-36,9,12)
 c.setFont('DejaVu',8);c.drawString(18,14,'REV08 • PRIVATE BLENDER • SUPPORT OFF • NOT WEBSITE');c.drawRightString(W-18,14,str(number))
def phone_pair(c,n,title,p1,p2,label1,label2,notes):
 page(c,title,n);c.setFont('DejaVuBold',10);c.drawString(18,650,label1);fitted(c,p1,18,421,384,216);c.drawString(18,403,label2);fitted(c,p2,18,174,384,216);txt(c,notes,18,151,384,10,14);c.showPage()
phone=R/'Rev08-Rooftop-Website-Crowd-Phone-Review.pdf';c=canvas.Canvas(str(phone),pagesize=(420,746));c.setTitle('Rev08 rooftop terrace and actual website crowd — private review');n=1
page(c,'Rooftop terrace + actual website crowd',n,'Implemented privately. Furniture identity remains PARTIAL.');fitted(c,frame('crowd','10-roof-elevated'),18,298,384,390);txt(c,'The venue now has supporting storeys, connected service roofs, headhouses and a perimeter around the destinations. Crowd geometry comes from the actual website. No website files or lighting were changed.',18,262,384,12,17);txt(c,'Compare architecture first, then crowd. The archived table proposals are not the confirmed steel-rack asset.',18,143,384,11,16);c.showPage();n+=1
I=[('01-approach','I · Arrival into the terrace'),('02-screen-wide','I · Forward screen / old crowd control'),('04-left-diagonal','I · Left diagonal / Team context'),('05-right-diagonal','I · Right diagonal / Events context'),('06-reverse','I · Terrace surrounds the reverse view'),('10-roof-elevated','I · A roof supported by a building'),('11-top-plan','I · Whole-venue roof plan'),('12-cross-section','I · Side elevation / floor height fixed'),('07-team','I · Team remains on the right'),('08-events','I · Events remains on the left')]
for pose,title in I:
 phone_pair(c,n,title,frame('before',pose),frame('architecture',pose),'BEFORE · wider world','AFTER · architecture only; SAME old crowd','Matched camera, 16 samples, same world/exposure/fog and all five support lights at 0 W. Main floor and destinations stay fixed.');n+=1
phone_pair(c,n,'I · Return graffiti remains intact',frame('before','14-return-art'),frame('architecture','14-return-art'),'BEFORE · original return art','AFTER · same art and host','All three 18-slat name shutters and four supporting motifs pass exact preservation and ray checks. No art was relocated to make room for the terrace.');n+=1
page(c,'I · Mobile approach comparison',n);fitted(c,frame('before','15-mobile-approach'),18,170,185,460);fitted(c,frame('architecture','15-mobile-approach'),217,170,185,460);txt(c,'Before',18,650,180,10);txt(c,'Architecture only',217,650,180,10);txt(c,'Identical portrait camera and 576×1024 output. The straight open arrival route and board are unchanged.',18,132,384,11,16);c.showPage();n+=1
phone_pair(c,n,'II · Authentic website source',O/'evidence/historical-actual-browser-aftermovie-arrival.png',O/'renders/source-diagnostics/01-web-output-vs-blender-clay.png','ACTUAL WEBSITE · historical browser capture','NEUTRAL DIAGNOSTIC · source output vs Blender','Top is an existing actual-browser screenshot. Bottom: direct Node/Three bake output on the left; identical imported Blender poses on the right. Not a fresh web parity capture.');n+=1
phone_pair(c,n,'II · Old crowd versus website models',frame('architecture','02-screen-wide'),frame('crowd','02-screen-wide'),'CONTROL · same terrace; old placeholders','CANDIDATE · source Man/Woman crowd','Same 180 footprints, height/facing and lighting. Source website #05060a diffuse silhouettes are retained; no colored crowd redesign.');n+=1
phone_pair(c,n,'II · Crowd from the side',frame('architecture','04-left-diagonal'),frame('crowd','04-left-diagonal'),'CONTROL · old crowd','CANDIDATE · exact source geometry','16,110 actor pairs checked: no overlaps, route intrusion or new poster/screen occlusion. Existing bystanders outside the C180 audience stay unchanged.');n+=1
phone_pair(c,n,'II · Source style and cost',O/'renders/source-diagnostics/02-four-web-silhouettes.png',frame('crowd','16-mobile-crowd'),'FOUR SOURCE IDLE POSES · neutral diagnostic','MOBILE · selected crowd / approved mood','180 source actors = 639,792 triangles, versus 54,000 placeholders. Four shared pose buffers estimate 971,664 bytes. No new texture images. Hardware/browser performance remains untested.');n+=1
phone_pair(c,n,'III · Source furniture, no invented match',O/'evidence/historical-not-selected-counter-mockup.png',O/'renders/source-diagnostics/03-active-website-roadcase-parity.png','OLD INVENTED COUNTER · NOT SELECTED','ACTIVE WEBSITE ROADCASE · source mesh parity','The actual Aftermovie has steel-trimmed road cases and truss frames. A dedicated active steel rack/table has not been identified. These are not silently renamed service tables.');n+=1
phone_pair(c,n,'III · Two reversible placement proposals',frame('props-a','17-furniture-A'),frame('props-b','18-furniture-B'),'A · rear-right service proposal','B · rear-left service proposal','The table is an ARCHIVED, currently unmounted project GLB: timber top and cloth. Exact roadcase geometry accompanies it. Neither proposal replaces shop counters or enters the default candidate.');n+=1
phone_pair(c,n,'The full terrace candidate',frame('crowd','06-reverse'),frame('crowd','13-rear-terrace'),'REVERSE · perimeter and original arrival','NEAR SCREEN · rear service roof context','No audience ceiling, banner, reveal column or new main screen truss. Nearby roofs are backdrop/service context; they do not create a newly approved walking route.');n+=1
page(c,'Decision and remaining limits',n);txt(c,'READY FOR VISUAL REVIEW: continuous terrace setting and exact website crowd reuse. PARTIAL: exact steel-rack/table identity pending clarification. No final world-art approval is claimed.',18,655,384,13,19);txt(c,'Geometry and preservation checks pass at the existing tolerances. Original five archival scenes, seven art placements, stage/destinations, route and five OFF support lights remain exact. Two old negative-Y scooter approaches remain blocked.',18,500,384,11,17);txt(c,'Main candidate: 712,800 triangles, 33 images / 138.53 MiB conservative RGBA8+mips estimate. Architecture adds 5,676 triangles; the source crowd dominates the increase. Runtime instancing/LOD and physical-device testing require a separately authorized pass.',18,349,384,11,17);txt(c,'Remaining art limits: dark source silhouettes, broad background facade planes, simplified service doors, repeated windows and low-sample walk grain. The movie is 40 seconds of actual offline route renders, not interactive FPS.',18,183,384,11,17);c.showPage();n+=1
page(c,'Review files and safe rollback',n);txt(c,'Open the accompanying GALLERY.html for full-resolution matched PNGs, separate source diagnostics, proposal labels and frame-linked walking inspection. Read REPORT.md and SOURCE-AUDIT.md before choosing furniture.',18,654,384,12,18);fitted(c,frame('crowd','02-screen-wide'),18,243,384,300);txt(c,'The new .blend retains all prior scenes. Select REV08 II / Terrace + Actual Website Crowd for this candidate, REV08 I for architecture only, and REV08 III-A/B for proposals. Final verified Drive index and restoration instructions accompany the checkpoint. Website unchanged; stop for visual review.',18,202,384,11,17);c.showPage();c.save();assert 15<=n<=25,n
# Full-resolution comparison PDF, one pair per landscape page.
full=R/'Rev08-Full-Matched-Comparisons.pdf';W,H=960,780;f=canvas.Canvas(str(full),pagesize=(W,H));pg=0
for section,ed1,ed2 in [('I / architecture only','before','architecture'),('II / source crowd only','architecture','crowd')]:
 for pose in [x[0]for x in I]+['09-perimeter','14-return-art','15-mobile-approach','16-mobile-crowd']:
  pg+=1;page(f,section+' / '+pose,pg,W=W,H=H);f.setFont('DejaVu',10);f.drawString(20,700,ed1);fitted(f,frame(ed1,pose),20,373,920,314);f.drawString(20,352,ed2);fitted(f,frame(ed2,pose),20,27,920,312);f.showPage()
f.save()
# Compact source audit PDF.
ac=canvas.Canvas(str(R/'Rev08-Website-Source-Audit.pdf'),pagesize=(420,746));phone_pair(ac,1,'Actual source: historical website',O/'evidence/historical-actual-browser-aftermovie-arrival.png',O/'evidence/historical-actual-browser-stage-playback.png','HISTORICAL ACTUAL BROWSER · arrival','HISTORICAL ACTUAL BROWSER · playback','The checked code still mounts these source families. These captures are historical; this phase starts no server, changes no website, and claims no fresh deployed parity.');phone_pair(ac,2,'Exact crowd geometry import',O/'renders/source-diagnostics/01-web-output-vs-blender-clay.png',O/'renders/source-diagnostics/02-four-web-silhouettes.png','NODE SOURCE OUTPUT vs BLENDER · neutral','FOUR EXACT POSES · source dark material','Man_Idle / Idle_Neutral at .35 / 1.35 seconds; 1,852 / 6,108 triangles. Same indices and positions after rigid axis conversion, zero maximum position error. 180 uniformly scaled copies; no width fitting.');phone_pair(ac,3,'Furniture source distinction',O/'renders/source-diagnostics/03-active-website-roadcase-parity.png',O/'renders/source-diagnostics/04-archived-table-not-active-steel-table.png','ACTIVE SOURCE · steel-trimmed roadcase','ARCHIVED TABLE · not active / not bare steel','No active standalone steel-table source was identified. Trusses.tsx supplies the active steel frames. Both proposal placements remain unselected. Read SOURCE-AUDIT.md for exact paths, hashes, dimensions, licence gaps and source chain.');ac.save()
# Complete technical text as readable PDF, separate from the visual phone review.
styles=getSampleStyleSheet();styles['BodyText'].fontName='DejaVu';styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;styles['Heading1'].fontName='DejaVuBold';styles['Heading2'].fontName='DejaVuBold';flow=[]
for block in (O/'REPORT.md').read_text().split('\n\n'):
 if not block.strip():continue
 style=styles['Heading1']if block.startswith('# ')else styles['Heading2']if block.startswith('## ')else styles['BodyText'];clean=block.lstrip('# ').replace('`','');flow.append(Paragraph(html.escape(clean).replace('\n','<br/>'),style));flow.append(Spacer(1,7))
SimpleDocTemplate(str(R/'Rev08-Technical-Report.pdf'),pagesize=(595,842),leftMargin=34,rightMargin=34,topMargin=34,bottomMargin=34).build(flow)
# Self-contained gallery root: relative links preserved by checkpoint extraction.
cards=[]
for section,ed1,ed2 in [('I · Architecture; original crowd unchanged','before','architecture'),('II · Exact crowd; same terrace','architecture','crowd')]:
 for p in sorted((O/'renders'/ed1).glob('*.png')):
  q=O/'renders'/ed2/p.name
  if not q.exists():continue
  cards.append(f'<article><h2>{html.escape(section)} — {html.escape(p.stem)}</h2><div class="pair"><figure><img src="{p.relative_to(O)}"><figcaption>{ed1}</figcaption></figure><figure><img src="{q.relative_to(O)}"><figcaption>{ed2}</figcaption></figure></div></article>')
for edition,title in [('source-diagnostics','NEUTRAL OFFLINE SOURCE DIAGNOSTICS'),('props-a','III-A · ARCHIVED TABLE / ACTIVE ROADCASE — PROPOSAL ONLY'),('props-b','III-B · ARCHIVED TABLE / ACTIVE ROADCASE — PROPOSAL ONLY')]:
 for p in sorted((O/'renders'/edition).glob('*.png')):cards.append(f'<article><h2>{title} / {html.escape(p.stem)}</h2><img src="{p.relative_to(O)}"></article>')
for p in sorted((O/'evidence').glob('historical-*.png')):cards.append(f'<article><h2>{html.escape(p.stem)}</h2><p>HISTORICAL evidence — not a new capture or selected asset claim.</p><img src="{p.relative_to(O)}"></article>')
walklinks=' '.join(f'<a href="{p.relative_to(O)}">{i+1}</a>'for i,p in enumerate(sorted((O/'renders/walk-final').glob('*.png'))))
gallery='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev08 private rooftop and website assets</title><style>body{font:16px/1.5 system-ui;max-width:1500px;margin:24px auto;padding:0 20px;background:#152021;color:#f1eee6}a{color:#a6d7dc}article{border-top:1px solid #546463;padding:24px 0}img{width:100%;max-height:900px;object-fit:contain}figure{margin:0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>Rev08 · Private rooftop terrace + actual website crowd</h1><p>Architecture / crowd ready for visual review. Furniture identity PARTIAL. All new images are actual offline Blender renders; historical browser evidence is labelled separately. Five optional supports OFF. No website changes.</p><p><a href="REPORT.md">Technical report</a> · <a href="SOURCE-AUDIT.md">Read-only source audit</a> · <a href="review/Rev08-Rooftop-Website-Crowd-Phone-Review.pdf">Phone PDF</a> · <a href="review/Rev08-Full-Matched-Comparisons.pdf">Full comparison PDF</a> · <a href="RESTORE.md">Restore instructions</a></p>'+''.join(cards)+'<h2>Original straight 40 s walk · offline inspection</h2><video controls width="100%" src="review/Rev08-Original-40s-Walk-Offline.mp4"></video><p>80 sampled source frames; 2 fps, 480×270, two samples. Not gameplay FPS.</p><p>'+walklinks+'</p></html>'
(O/'GALLERY.html').write_text(gallery);(O/'evidence/review-build.json').write_text(json.dumps({'status':'PASS','phonePages':n,'fullComparisonPages':pg,'sourceAuditPages':3,'phonePDF':str(phone.relative_to(O)),'allImagesActualBlenderOrLabelledHistoricalBrowser':True},indent=2));print('REVIEWS_BUILT',n,pg)
