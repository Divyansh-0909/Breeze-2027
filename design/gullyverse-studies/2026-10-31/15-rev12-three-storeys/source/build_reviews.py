import json,io,html,hashlib,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet
O=Path(__file__).resolve().parents[1];R=O/'review';F=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);cache={}
def picture(c,p,x,y,w,h):
 p=Path(p)
 if str(p)not in cache:
  im=Image.open(p).convert('RGB');buf=io.BytesIO();im.save(buf,'JPEG',quality=90);buf.seek(0);cache[str(p)]=(ImageReader(buf),im.size)
 reader,(iw,ih)=cache[str(p)];sc=min(w/iw,h/ih);ww,hh=iw*sc,ih*sc;c.drawImage(reader,x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def page(c,title,n,W,H,note='Actual offline Blender; original cameras/night, 12 lights + 5 supports OFF'):
 c.setFillColor(HexColor('#faf9f6'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#172b36'));c.setFont('Helvetica-Bold',14)
 for i,line in enumerate(textwrap.wrap(title,70 if W<600 else 140)):c.drawString(18,H-26-17*i,line)
 c.setFont('Helvetica',7);c.drawString(18,13,note);c.drawRightString(W-15,13,str(n))
poses=['03-aerial','02-entry-square','04-front','05-back','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','10-team','11-events','13-return-left','14-return-right','15-mobile','16-mobile-lateral','12-elevation','24-right-elevation','01-plan','20-roof-utility','21-roof-gallery','22-street-entry','23-screen-side','25-back-junction','26-left-junction','27-right-junction','28-roof-joins']
# Photo-to-model board, no source image pixels are used in scene textures.
im=Image.new('RGB',(1800,1700),'#faf9f6');dr=ImageDraw.Draw(im);dr.text((30,20),'REAL PHOTO REFERENCES / private study only',font=F(32),fill='#172b36')
roles=['R1: tanks / plumbing / roof thickness','R2: informal inhabited roof context','R3: supported galleries / real openings','R4: open-sky performance composition','R5: inhabited bays / service details','R6: ground-level cypher spacing only']
for i,key in enumerate(['R1','R2','R3','R4','R5','R6']):
 pp=O/'references'/(key+'.jpg')
 if not pp.exists():pp=next((O/'references').glob(key+'*'))
 src=Image.open(pp).convert('RGB');src.thumbnail((550,370));x=30+(i%3)*590;y=100+(i//3)*450;im.paste(src,(x+(550-src.width)//2,y));dr.text((x,y+382),roles[i],font=F(18),fill='#172b36')
src=Image.open(O/'renders/new/03-aerial.png').convert('RGB');src.thumbnail((1000,570));im.paste(src,(40,1030));dr.multiline_text((1080,1070),'Rev12 translation:\n3/4/5-storey main houses\nJoined bearing walls\nSupported galleries\nSetbacks and roof services\nSame C180 / night lights\n\nNot a literal photograph copy.\nNo new photo textures.\nR2/R4 rights unverified:\nprivate reference only.',font=F(23),fill='#172b36',spacing=13);im.save(R/'photo-to-model-board.png')
pairs=[('Neutral actual slab annotations / '+p,R/('DIAGNOSTIC-count-before-'+p+'.png'),R/('DIAGNOSTIC-count-new-'+p+'.png'))for p in['03-aerial','12-elevation','04-front','01-plan']]
pairs+=[('True roofline silhouettes / '+p,R/('DIAGNOSTIC-silhouette-before-'+p+'.png'),R/('DIAGNOSTIC-silhouette-new-'+p+'.png'))for p in['04-front','03-aerial']]
pairs += [('Unchanged screen masking / diagnostic only',O/'renders/new/04-front.png',R/'DIAGNOSTIC-screen-media-hidden.png'),('Measured 11-parcel plan',R/'storey-plan-before.png',R/'storey-plan-after.png')]
singles=[('All eleven / independent physical count',R/'all-eleven-count-schedule.png'),('Every parcel / unrolled elevation',R/'all-eleven-storey-elevation.png'),('Reference photos / model continuity',R/'photo-to-model-board.png'),('Original stature / proposal / scale ruler',R/'actual-blender-scale-rulers.png')]
for mode,(W,H)in [('Phone',(460,980)),('Full',(1400,950))]:
 c=canvas.Canvas(str(R/('Rev12-'+mode+'-Review.pdf')),pagesize=(W,H));n=0
 for pose in poses:
  n+=1;page(c,'Rev11 BEFORE / Rev12 AFTER — '+pose,n,W,H)
  for k,ed in enumerate(['before','new']):
   x=18 if mode=='Phone'else 18+k*690;y=H-72-k*435 if mode=='Phone'else H-75;c.setFont('Helvetica-Bold',10);c.drawString(x,y,'Rev11 / original +7% crowd'if ed=='before'else'Rev12 / 3–5 real upper floors / same crowd');picture(c,O/'renders'/ed/(pose+'.png'),x,y-(405 if mode=='Phone'else 825),W-36 if mode=='Phone'else 670,395 if mode=='Phone'else 810)
  c.showPage()
 for title,pa,pb in pairs:
  n+=1;page(c,title,n,W,H,'DIAGNOSTIC ONLY / annotations or neutral lighting; master never saved')
  for k,pp in enumerate([pa,pb]):
   x=18 if mode=='Phone'else 18+k*690;y=H-75-k*435 if mode=='Phone'else H-75;picture(c,pp,x,y-(405 if mode=='Phone'else 825),W-36 if mode=='Phone'else 670,395 if mode=='Phone'else 810)
  c.showPage()
 for title,pp in singles:
  n+=1;page(c,title,n,W,H,'Measured/reference diagnostic, not selected scene lighting or user art approval');picture(c,pp,18,35,W-36,H-105);c.showPage()
 # Source height controls remain Rev11, correctly labelled, not different Rev12 crowd transforms.
 n+=1;page(c,'Preserved Rev11 stature controls / original, +6%, +7%, +9%',n,W,H,'Historical source geometry / same pose; Rev12 shares exact +7% objects')
 for k,ed in enumerate(['H00','H06','before','H09']):
  x=18+(k%2)*(W/2);y=30+(1-k//2)*(H-100)/2;picture(c,O/'renders'/ed/'04-front.png',x,y,W/2-30,(H-120)/2)
 c.showPage()
 if mode=='Phone':
  for pose in['15-mobile','16-mobile-lateral']:
   n+=1;page(c,'Full portrait / Rev12 — '+pose,n,W,H);picture(c,O/'renders/new'/(pose+'.png'),18,35,W-36,H-105);c.showPage()
 c.save();globals()[mode.lower()+'Pages']=n
# Technical PDF retains complete prose; pipe tables become native PDF tables.
styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;story=[];lines=(O/'REPORT.md').read_text().splitlines();i=0
while i<len(lines):
 line=lines[i]
 if line.startswith('|'):
  table=[]
  while i<len(lines)and lines[i].startswith('|'):
   rr=[x.strip()for x in lines[i].strip('|').split('|')]
   if not all(set(x)<=set('-: ')for x in rr):table.append([Paragraph(html.escape(x),styles['BodyText'])for x in rr])
   i+=1
  t=Table(table,repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#dde5e1')),('GRID',(0,0),(-1,-1),.3,HexColor('#9caeaa')),('VALIGN',(0,0),(-1,-1),'TOP')]));story.extend([t,Spacer(1,12)]);continue
 if line:story.append(Paragraph(html.escape(line.lstrip('# ')),styles['Title']if line.startswith('# ')else styles['Heading2']if line.startswith('## ')else styles['BodyText']));story.append(Spacer(1,7))
 i+=1
SimpleDocTemplate(str(R/'Rev12-Technical-Report.pdf'),pagesize=(680,960),leftMargin=34,rightMargin=34,topMargin=34,bottomMargin=34).build(story)
groups=[('Rev12 candidate',sorted((O/'renders/new').glob('*.png'))),('Exact Rev11 controls',sorted((O/'renders/before').glob('*.png'))),('Separate diagnostics and measured diagrams',sorted(R.glob('*.png'))),('Preserved Rev11 stature controls',[p for e in['H00','H06','H09']for p in sorted((O/'renders'/e).glob('*.png'))])]
body=['<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rev12 private review</title><style>body{font:17px system-ui;max-width:1400px;margin:24px auto;padding:0 16px;background:#faf9f6;color:#172b36}img,video{max-width:100%;height:auto}figure{margin:30px 0}a{color:#286e5a}nav{line-height:2}</style><h1>Rev12 / 3–5 real upper storeys on all eleven houses</h1><p>PRIVATE PROPOSAL awaiting user visual review. No final A/B/hybrid or +7% stature approval inferred. Same cameras, crowd, floor, screen and night lighting. Two inherited scooter approaches and six rear lightwell floor openings remain unresolved. All images are actual offline Blender or clearly labelled measured diagrams; no website/runtime FPS claim.</p><nav><a href="REPORT.md">Technical report</a> · <a href="review/Rev12-Phone-Review.pdf">Phone PDF</a> · <a href="review/Rev12-Full-Review.pdf">Full screenshot PDF</a> · <a href="review/Rev12-Technical-Report.pdf">Technical PDF</a> · <a href="evidence/11-parcel-storey-schedule.csv">11-parcel CSV</a> · <a href="RESTORE.md">Restore instructions</a></nav><video controls preload="metadata" src="review/Rev12-40s-Actual-Blender-Walk.mp4"></video><p>40s offline inspection:80 real frames at2fps; not live/gameplay performance.</p>']
for title,files in groups:
 body.append('<h2>'+title+'</h2>')
 for pp in files:
  rel=str(pp.relative_to(O));body.append(f'<figure><a href="{html.escape(rel)}"><img loading="lazy" src="{html.escape(rel)}"></a><figcaption>{html.escape(rel)}</figcaption></figure>')
body.append('</html>');(O/'GALLERY.html').write_text('\n'.join(body));(O/'evidence/review-build.json').write_text(json.dumps({'phonePages':phonePages,'fullPages':fullPages,'galleryPNGs':sum(len(x[1])for x in groups),'allActualBlenderOrLabelledDiagrams':True},indent=2));print('REVIEW_COMPLETE',phonePages,fullPages)
