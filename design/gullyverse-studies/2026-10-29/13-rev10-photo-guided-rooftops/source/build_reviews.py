"""Labelled actual-photo / actual-Blender review; no generated concept imagery."""
from pathlib import Path
import json,html,textwrap,io,csv
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet
O=Path(__file__).resolve().parents[1];R=O/'review';R.mkdir(exist_ok=True);refs=json.loads((O/'source/REFERENCE-PROVENANCE.json').read_text());pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'));cache={}
def frame(ed,p):return O/'renders'/ed/(p+'.png')
def fitted(c,p,x,y,w,h):
 key=str(p)
 if key not in cache:
  im=Image.open(p).convert('RGB');im.thumbnail((1800,1400));buf=io.BytesIO();im.save(buf,'JPEG',quality=88,subsampling=0);buf.seek(0);cache[key]=ImageReader(buf)
 im=cache[key];iw,ih=im.getSize();k=min(w/iw,h/ih);ww,hh=iw*k,ih*k;c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def txt(c,s,x,y,w,font=10,leading=14):
 c.setFont('DV',font);line=''
 for word in str(s).split():
  t=(line+' '+word).strip()
  if pdfmetrics.stringWidth(t,'DV',font)>w and line:c.drawString(x,y,line);y-=leading;line=word
  else:line=t
 if line:c.drawString(x,y,line);y-=leading
 return y
def page(c,title,n,W=420,H=840):
 c.setFillColor(HexColor('#f4f2eb'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#212b2a'));c.setFont('DVB',14);y=H-30
 for line in textwrap.wrap(title,45 if W==420 else 90):c.drawString(18,y,line);y-=20
 c.setFont('DV',7);c.drawString(18,13,'REV10 / PRIVATE REVIEW / ORIGINAL LIGHTING + SUPPORT OFF');c.drawRightString(W-18,13,str(n))
titles={'01-plan':'Plan / open floor and roof edges','02-entry-square':'Arrival / lane to roof gathering','03-aerial':'Aerial / compare roofscape hierarchy','04-front':'Same screen and exact C180 crowd','05-back':'Reverse / open lane connection','06-left-diagonal':'Left diagonal / inhabited edge','07-right-diagonal':'Right diagonal / roof setbacks','08-left-house':'Left detail / deep openings and galleries','09-right-house':'Right detail / roof-room scale','10-team':'Team stays on the right','11-events':'Events stays on the left','12-elevation':'Elevation / roof and supporting storeys','13-return-left':'Original left return artwork','14-return-right':'Original right return artwork','15-mobile':'Mobile / same arrival pose','16-mobile-lateral':'Mobile / residential edge','20-roof-utility':'R1 / tank and domestic roof detail','21-roof-gallery':'R3-R5 / usable gallery depth','22-street-entry':'Original street-entry choreography','23-screen-side':'R4 / crowd-equipment-roof composition'}
def triple(c,n,pose):
 page(c,titles[pose],n)
 for j,(ed,label)in enumerate([('before','REV09 / rejected visual baseline'),('A','PROPOSAL A / connected working roofs'),('B','PROPOSAL B / layered residential galleries')]):
  top=763-j*220;c.setFont('DVB',9);c.drawString(18,top,label);fitted(c,frame(ed,pose),18,top-203,384,198)
 txt(c,'Identical pose/lens, EEVEE 16 samples, world/exposure/fog. Same floor, crowd and destinations. No new light, emission or image owners. Both proposals await your choice.',18,83,384,9,12);c.showPage()
# Explicit two-page real-photo/current/proposed board; photographs never called scene evidence.
bc=canvas.Canvas(str(R/'Rev10-Real-Photo-to-Blender-Board.pdf'),pagesize=(1190,842));bc.setTitle('Six real-photo references vs actual Rev09 and proposed Rev10 — private reference only')
for num,group in enumerate([refs[:3],refs[3:]],1):
 page(bc,'REAL PHOTOS / CURRENT REV09 / PROPOSED REV10 — PRIVATE REFERENCE BOARD',num,1190,842)
 for j,r in enumerate(group):
  top=770-j*242
  for col,label in enumerate(['REAL PHOTO / '+r['id'],'ACTUAL BLENDER / Rev09','ACTUAL BLENDER / proposal '+r['proposal']]):bc.setFont('DVB',10);bc.drawString(18+col*390,top,label)
  fitted(bc,O/r['file'],18,top-166,370,157);bc.linkURL(r['sourcePage'],(18,top-166,388,top-9),relative=0);fitted(bc,frame('before',r['pose']),408,top-166,370,157);fitted(bc,frame(r['proposal'],r['pose']),798,top-166,370,157)
  y=txt(bc,r['credit']+' | '+r['license'],18,top-179,1150,8,10);y=txt(bc,'SOURCE: '+r['sourcePage'],18,y,1150,7.3,9.5);txt(bc,'TRANSLATION / LIMIT: '+r['translationAndLimit'],18,y,1150,8,10)
 bc.showPage()
bc.save()
# Phone review: core triptychs + portraits + plain-language decision.
c=canvas.Canvas(str(R/'Rev10-Two-Rooftop-Alternatives-Phone-Review.pdf'),pagesize=(420,840));c.setTitle('Rev10 real-photo-guided rooftop alternatives — choose A or B');n=1
page(c,'Two real-photo-guided rooftop directions',n);fitted(c,frame('A','03-aerial'),18,461,384,220);fitted(c,frame('B','03-aerial'),18,216,384,220);txt(c,'A / connected working roofs — lower edge, more sky. B / layered galleries — deeper residential enclosure. Both retain the exact original 180-person crowd, floor, screen, route, artwork and SUPPORT OFF. Neither is approved.',18,180,384,11,16);txt(c,'All scene images are genuine offline Blender. Six real photographs are separately credited in the two-page reference board. No website change.',18,65,384,9,13);c.showPage();n+=1
for group in [refs[:3],refs[3:]]:
 page(c,'Actual photographs / distinct reference roles',n)
 for j,r in enumerate(group):
  yy=575-j*230;fitted(c,O/r['file'],18,yy,170,180);txt(c,r['id']+' / '+r['role'],200,yy+164,202,11,15);txt(c,r['credit']+' / '+r['license'],200,yy+112,202,8,11);txt(c,r['translationAndLimit'],200,yy+58,202,8,11)
 c.showPage();n+=1
page(c,'Why Rev09 was rejected visually',n);fitted(c,frame('before','03-aerial'),18,470,384,240);txt(c,'Targeted hypotheses from the original reviewed images: too much repeated facade grammar, a clean near-continuous apartment edge, sparse domestic roof use and a large exposed floor. These are design hypotheses, not a list the user separately dictated.',18,434,384,12,18);txt(c,'The photographs show much smaller informal gatherings. The approved 1,088 m² floor, large screen and 180 exact people stay locked. Architecture alone cannot make their scale identical; the comparison must expose that difference.',18,270,384,12,18);txt(c,'No photo pixels enter scene materials, no new graffiti is invented, no crowd is moved and no light is added. R6 is not a rooftop. R3 is not permission to build palace ornament.',18,108,384,10,15);c.showPage();n+=1
core=['01-plan','03-aerial','02-entry-square','05-back','04-front','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','20-roof-utility','21-roof-gallery','10-team','11-events','12-elevation','22-street-entry','23-screen-side']
for pose in core:triple(c,n,pose);n+=1
for pose in ['15-mobile','16-mobile-lateral']:
 page(c,titles[pose]+' / A versus B',n);fitted(c,frame('A',pose),18,254,185,500);fitted(c,frame('B',pose),217,254,185,500);txt(c,'PROPOSAL A',18,238,180,10);txt(c,'PROPOSAL B',217,238,180,10);txt(c,'Same portrait camera,576×1024 output and dark lighting. These are aspect-ratio inspections, not physical-phone performance tests. The full comparison PDF also includes the unchanged Rev09 control.',18,185,384,11,16);c.showPage();n+=1
page(c,'Both protected entry-art returns remain',n);fitted(c,frame('A','13-return-left'),18,462,384,220);fitted(c,frame('B','14-return-right'),18,210,384,220);txt(c,'Exact original artworks/hosts; houses and terraces are modeled around them. Three original named shutters retain all 54 slats and their paint mapping. No art was moved or recolored. Both before/A/B return pairs are in the full gallery.',18,170,384,11,16);c.showPage();n+=1
page(c,'Technical preservation / honest limits',n);budget=json.loads((O/'evidence/budget.json').read_text());y=730
for r in budget['rows']:y=txt(c,r['variant']+': '+format(r['triangles'],',')+' triangles / '+str(r['meshCurveOwners'])+' mesh-curve owners / '+str(r['imageOwners'])+' image owners.',18,y,384,11,16)-12
y=txt(c,'Strict geometry,960-frame route/.35m capsule, crowd/architecture, sign/art rays and exact original assets pass. All 13 historical scenes remain. Two inherited negative-Y scooter approaches remain blocked. Five optional supports 0 W; twelve original active lights unchanged.',18,y-12,384,11,16)
y=txt(c,'Remaining limits: simplified interiors, repeated construction vocabulary, broad outer podiums, low-poly locked crowd, large protected floor and subdued roof details. Night lighting differs from daylight photos. No photorealism, glTF readiness, browser FPS or hardware acceptance is claimed.',18,y-16,384,11,16)
txt(c,'Full 40-second offline walks for BOTH proposals use80 real source-frame samples each at 2 fps. They are deliberately coarse inspections, not gameplay FPS.',18,y-20,384,11,16);c.showPage();n+=1
page(c,'Your choice / safe source recovery',n);txt(c,'Choose A for a lower working-roof edge and open skyline, or B for closer layered residential galleries. Neither is automatically selected as final art or website geometry. Use the real-photo board to identify a specific further correction if neither works.',18,735,384,13,19);txt(c,'All original 180 actors, screen, signs, floor,40-second route and seven approved paintings stay locked. Steel rack/table identity is still unresolved; no guessed furniture is adopted.',18,535,384,11,17);txt(c,'The packed editable master contains 15 scenes:13 untouched archives plus A and B. New numbered Drive archives contain actual masters, photos with provenance, complete source, all original PNGs, PDF/HTML gallery, walks and hash manifests. Follow the final recovery index; interim safety files are not final restore inputs.',18,365,384,11,17);txt(c,'Backup is declared verified only after full authenticated download-back and fresh extraction/reopen. See the final receipt. STOP for user visual choice. No website edits, builds, Git changes or deployment.',18,133,384,11,17);c.showPage();c.save()
# Full matched original PNG comparisons, one camera per page.
f=canvas.Canvas(str(R/'Rev10-Full-Matched-Rev09-A-B.pdf'),pagesize=(960,1100));pg=0
for pose,title in titles.items():
 pg+=1;page(f,title,pg,960,1100)
 for j,(ed,label)in enumerate([('before','REV09 / control'),('A','REV10 A / connected roofs'),('B','REV10 B / galleries')]):
  yy=1020-j*331;f.setFont('DVB',10);f.drawString(20,yy,label);fitted(f,frame(ed,pose),20,yy-314,920,305)
 f.showPage()
f.save()
styles=getSampleStyleSheet()
for key in ['BodyText','Heading1','Heading2']:styles[key].fontName='DVB'if key.startswith('Heading')else'DV'
styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;flow=[]
for block in (O/'REPORT.md').read_text().split('\n\n'):
 if not block.strip():continue
 style=styles['Heading1']if block.startswith('# ')else styles['Heading2']if block.startswith('## ')else styles['BodyText'];flow.extend([Paragraph(html.escape(block.lstrip('# ').replace('`','')).replace('\n','<br/>'),style),Spacer(1,7)])
SimpleDocTemplate(str(R/'Rev10-Technical-Report.pdf'),pagesize=(595,842),leftMargin=34,rightMargin=34,topMargin=34,bottomMargin=34).build(flow)
cards=[]
for pose,title in titles.items():cards.append('<article><h2>'+html.escape(title)+'</h2><div class="three">'+''.join('<figure><a href="renders/'+e+'/'+pose+'.png"><img loading="lazy" src="renders/'+e+'/'+pose+'.png"></a><figcaption>'+label+'</figcaption></figure>'for e,label in [('before','Rev09 control'),('A','Proposal A'),('B','Proposal B')])+'</div></article>')
photos=''.join('<article><h2>REAL PHOTO '+r['id']+' / '+html.escape(r['role'])+'</h2><img loading="lazy" src="'+r['file']+'"><p>'+html.escape(r['credit']+' / '+r['license'])+'</p><p><a href="'+r['sourcePage']+'">Original source / credit</a></p><p>'+html.escape(r['translationAndLimit'])+'</p></article>'for r in refs)
walks=''.join('<h2>Proposal '+ed+' / genuine40-second offline route</h2><video controls width="100%" src="review/Rev10-'+ed+'-40s-Offline-Walk.mp4"></video><p>80 actual samples /2fps; NOT gameplay FPS.</p><p>'+' '.join('<a href="renders/walk-'+ed+'/'+p.name+'">'+str(i+1)+'</a>'for i,p in enumerate(sorted((O/('renders/walk-'+ed)).glob('*.png'))))+'</p>'for ed in ['A','B'])
(O/'GALLERY.html').write_text('<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev10 two photo-guided rooftop proposals</title><style>body{font:16px/1.5 system-ui;max-width:1700px;margin:24px auto;padding:0 20px;background:#152021;color:#f1eee6}a{color:#a6d7dc}article{border-top:1px solid #546463;padding:24px 0}img{width:100%;max-height:1000px;object-fit:contain}figure{margin:0}.three{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}@media(max-width:800px){.three{grid-template-columns:1fr}}</style><h1>Rev10 / two private rooftop proposals</h1><p>USER CHOICE PENDING. All scene images actual offline Blender; real photos separately labelled. Exact original crowd, floor, screen, route/art/light preserved; supportsOFF. No website changes.</p><p><a href="REPORT.md">Technical report</a> · <a href="review/Rev10-Two-Rooftop-Alternatives-Phone-Review.pdf">Phone review</a> · <a href="review/Rev10-Real-Photo-to-Blender-Board.pdf">2-page real-photo board</a> · <a href="review/Rev10-Full-Matched-Rev09-A-B.pdf">All 20 matched cameras</a> · <a href="RESTORE.md">Restore</a></p>'+''.join(cards)+walks+'<h1>Separately labelled real-photo references / PRIVATE</h1><p>No photo is a scene texture. Rights restrictions retained. Reference Google Doc unchanged.</p>'+photos+'</html>')
(O/'evidence/review-build.json').write_text(json.dumps({'status':'PASS','phonePages':n,'photoBoardPages':2,'fullComparisonPages':pg,'allSixRealPhotosCredited':True,'allNewSceneImagesActualOfflineBlender':True,'userChoicePending':True},indent=2));print('REVIEWS_BUILT',n,pg,flush=True)
