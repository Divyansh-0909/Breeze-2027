from pathlib import Path
import json,math,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
R=Path(__file__).resolve().parents[1];build=json.loads((R/'evidence/build-verification.json').read_text());captures=json.loads((R/'evidence/captures.json').read_text());assert len(captures['captures'])==4 and all(x['masterSHA256']==build['editedSHA256']for x in captures['captures']),'Wait for all final captures';design=json.loads((R/'source/destination-design.json').read_text())
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/review-fonts'/file)))
pdf=R/'review/Breeze-Events-Accommodation-and-Contact-Proposal-Rev15X.pdf';c=canvas.Canvas(str(pdf),pagesize=(1000,760));c.setTitle('Breeze / Events poster policy, Accommodation wall and Contact Us proposal');page=0
def text(x,y,t,size=13,bold=False,color='#e4e9eb'):
 c.setFillColor(HexColor(color));c.setFont('Bold'if bold else'Body',size);c.drawString(x,y,t)
def para(x,y,t,w=930,size=13,color='#e4e9eb'):
 p=Paragraph(t,ParagraphStyle('p',fontName='Body',fontSize=size,leading=size*1.5,textColor=HexColor(color)));_,h=p.wrap(w,700);p.drawOn(c,x,y-h);return y-h
def start(title,sub):
 global page
 page+=1;c.setFillColor(HexColor('#10191e'));c.rect(0,0,1000,760,fill=1,stroke=0);text(34,721,title,25,True);para(34,696,sub,size=12,color='#afc0c9');text(34,22,'BREEZE 2027  /  Rev15X  /  14 November 2026',10,color='#afc0c9');text(940,22,str(page),10)
def image(file,x,y,w,h):
 im=ImageReader(str(R/file));iw,ih=im.getSize();a=min(w/iw,h/ih);c.drawImage(im,x+(w-iw*a)/2,y+(h-ih*a)/2,width=iw*a,height=ih*a,mask='auto')
def box(x,y,w,h,color):c.setFillColor(HexColor(color));c.rect(x,y,w,h,fill=1,stroke=0)
start('Accommodation: COMING / SOON','Implemented in the native scene. The two-line graffiti uses the Team title palette on a normal painted house wall.')
image('renders/02-accommodation-inspection.jpg',34,119,932,550);para(34,97,'Temporary neutral inspection lighting makes the lettering and wall finish readable. Both words sit above the existing parapet; windows, doors and the wider environment are preserved.',size=12);c.showPage()
start('Accommodation in its surroundings','Left entrance house-wall bay. Normal plaster, stacked graffiti and one small wall-mounted light for night legibility.')
image('renders/03-accommodation-context.jpg',34,331,562,326);image('renders/01-accommodation-night.jpg',609,331,357,326);text(34,316,'Temporary neutral inspection / location',12,True);text(609,316,'Actual saved night lighting',12,True);para(34,275,'The normal plaster finish and transparent graffiti are new editable additions to the existing F1 house bay. The 60-scene master retains the entire Rev15W environment, including the six gully-only streetlights and overhead cables.',size=14);para(34,181,'Placement uses the left entrance wall, consistent with the Accommodation arrow. The live website destination and final lighting/export match remain part of the later integration stage.',size=14);c.showPage()
def wall_diagram(x,y,n,label):
 w,h=450,180;box(x,y,w,h,'#9b7e67');box(x+202,y+28,46,112,'#3c4c48');box(x,y+155,w,10,'#746f65');text(x+12,y+164,label,12,True);slots={0:(x+42,y+18),1:(x+103,y+18),2:(x+284,y+18),3:(x+345,y+18),4:(x+42,y+88),5:(x+103,y+88),6:(x+284,y+88),7:(x+345,y+88)};shown=min(n,8)
 if not n:text(x+35,y+91,'EVENTS ANNOUNCED SOON',17,True,color='#ede5d4')
 else:
  chosen=design['events']['fillOrderByCount'][str(shown)];assert len(chosen)==shown and len(set(chosen))==shown
  for j,k in enumerate(chosen):
   sx,sy=slots[k];box(sx,sy,49,61,['#d56c42','#dbb957','#5d8986','#b67a99'][j%4]);box(sx+4,sy+6,41,13,'#f2e6cf');text(sx+7,sy+41,'EVENT',8,True,color='#17262b');text(sx+16,sy+25,str(j+1).zfill(2),10,True,color='#17262b')
 text(x+12,y-20,(f'{n} event'if n==1 else f'{n} events')+(f'  /  {math.ceil(n/8)} pages: 8 + 8 + 1'if n==17 else''),12,True)
start('Events: a flexible poster wall','Recommended layout policy, shown schematically. No live feed, admin change or Events art replacement is implemented here.')
for x,y,n,label in [(34,451,1,'ONE EVENT'),(516,451,3,'THREE EVENTS'),(34,197,8,'EIGHT EVENTS'),(516,197,17,'MORE THAN EIGHT')]:wall_diagram(x,y,n,label)
para(34,141,'Use the eight existing safe positions around the house openings. Hide unused posters and frames. Keep every poster readable at a consistent size, preserve its image proportions and use manual page controls for overflow.',size=13);para(34,76,'No automatic rotation, shrinking posters, added wall area or repeated filler images. Category and club filters narrow the same event feed.',size=12);c.showPage()
start('Events: admin data and expiry','The wall should read the existing event catalog and poster URLs, with a few data-model additions for reliable timing.')
y=645
for title,body in [('One catalog','Admin poster upload -> Supabase image_url + EventItem details -> active event feed -> wall slots -> readable event detail and existing registration flow.'),('Upcoming / ongoing','Show ongoing events first, then the nearest upcoming date. A multi-day event stays visible until its final end time.'),('Registration closed','Keep the event visible with a clear closed label while it is still upcoming or ongoing. Registration closing and an event ending are different states.'),('Ended / cancelled','Remove from active wall pages and clamp the current page if needed. Keep historical event and booking records in admin; do not delete them just to hide a poster.'),('Nothing announced / loading failure','With zero events, show normal plaster and an Events announced soon message. A network failure gets a separate retry state; it must not look like an empty catalog.')]:
  text(34,y,title,15,True);y=para(34,y-15,body,w=930,size=12)-23
para(34,166,'Main-branch finding: event_date and event_end_date are display strings. Add typed start/end times with explicit India timezone handling. Single-day legacy entries can expire at the next local midnight after their final date; missing or ambiguous dates need admin review.',size=12);para(34,75,'Main currently lets only Breeze Admin publish/edit events; clubs are read-only. If clubs should submit, agree a draft -> admin approval -> publish flow before changing permissions.',size=12);c.showPage()
start('Contact Us: a neighbourhood help desk','Recommended direction / schematic only. No Contact geometry or live form was changed in this phase.')
box(34,330,560,312,'#aa9e85');box(34,330,560,24,'#6f6a5e');box(51,587,525,32,'#314d45');text(148,594,'CONTACT US',25,True);box(65,400,221,157,'#4f4b3d');box(76,411,199,135,'#dbd0b5');text(93,516,'TALK TO THE CREW',13,True,color='#293b35');text(93,488,'Official email / phone',11,color='#293b35');text(93,464,'Verified current contacts',11,color='#293b35');text(93,438,'Tap to call or email',11,color='#293b35');box(322,420,232,125,'#344941');text(343,509,'LEAVE A MESSAGE',16,True);text(343,477,'Tap / click / keyboard',11);text(343,454,'Opens a readable form',11);box(85,365,106,28,'#426156');text(97,374,'ENQUIRIES',11,True);text(34,311,'Painted heading, worn noticeboard, compact enquiry panel',11)
image('assets/existing-help-desk-reference.png',617,337,349,293);para(617,322,'Existing local website help-desk capture, saved 10 November: a reference for reusing the form treatment, not a new cypher render.',w=349,size=11,color='#afc0c9');para(34,252,'Approach the frontage, then choose Leave a message. The existing world remains behind an HTML panel: a side panel on a laptop and a readable sheet on a phone. Pause walking while typing, then close to resume at the same position.',size=14);para(34,150,'Reuse the current contact fields and backend: name, email, phone and message -> POST /api/contact -> ContactSubmission -> the existing Breeze Admin Contact inbox. Use only confirmed current contact details on the noticeboard.',size=13);para(34,65,'This avoids another 3D canvas and keeps typing, accessibility, mobile keyboards and error messages clear.',size=12);c.showPage()
start('What is ready, and what needs a decision','The user reopened destination work before art freeze. No art freeze or full-world production milestone is claimed.')
y=645
for title,body in [('Accommodation artwork — implemented','COMING above SOON on normal plaster. Source and editable native/runtime components are saved; the existing environment remains preserved.'),('Events layout — recommended','Eight safe positions per wall page, balanced when fewer events exist, manual pages for more, automatic expiry from proper end times and no deleting booking history.'),('Publishing workflow — to agree','Main is admin-only today. Decide whether clubs submit drafts for Breeze Admin approval or continue sending materials to the admin team.'),('Contact frontage — recommended','A compact house-wall help desk with verified quick contacts and the existing enquiry form/inbox. Final frontage styling can be chosen before implementation.')]:
 text(34,y,title,16,True);y=para(34,y-18,body,w=930,size=13)-31
para(34,208,'The checked main branch is a8ebff2 (13 November 2026). Source references are preserved in the checkpoint. Events live-feed/expiry changes, Contact construction, database migrations and permission changes remain proposed; this phase changes Accommodation art only.',size=12)
for y,label,url in [(113,'Event data model and fields','https://github.com/Divyansh-0909/Breeze-2027/blob/a8ebff2d2f2c13ba7c3ee22029e6459199a9ce1a/prisma/schema.prisma'),(84,'Admin event publishing and contact inbox','https://github.com/Divyansh-0909/Breeze-2027/tree/a8ebff2d2f2c13ba7c3ee22029e6459199a9ce1a/app/(admin)/admin/breeze-admin')]:
 text(34,y,label,11,color='#88d6be');c.linkURL(url,(34,y-3,500,y+14),relative=0)
c.showPage();c.save();doc=fitz.open(pdf);assert len(doc)==6
for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(.9,.9)).save(R/'review'/('page-%02d.png'%(i+1)))
proof={'status':'PASS','pages':len(doc),'bytes':pdf.stat().st_size,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'output':str(pdf),'nativeAndSchematicViewsLabelled':True,'mainSourceLinked':True};(R/'evidence/pdf.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
