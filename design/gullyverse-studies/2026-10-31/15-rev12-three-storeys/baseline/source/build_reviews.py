import json,math,io,html,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
O=Path(__file__).resolve().parents[1];R=O/'review';font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';F=lambda n:ImageFont.truetype(font,n)
b=json.loads((O/'evidence/before-survey.json').read_text());a=json.loads((O/'evidence/authoring.json').read_text());j=json.loads((O/'evidence/adjacency-after.json').read_text())
def fp(h):
 if 'footprint'in h:return h['footprint']
 c,w,f,d,e=h['center'],h['widthM'],h['frontM'],h['depthM'],h['edge'];return [[-f-d,-f],[c-w/2,c+w/2]]if e=='left'else[[f,f+d],[c-w/2,c+w/2]]if e=='right'else[[c-w/2,c+w/2],[f,f+d]]if e=='back'else[[c-w/2,c+w/2],[f-d,f]]
colors=['#b3c4bd','#c8b8a4','#a9b8c3','#c0b7a5','#bdbda8']
for edition,houses in [('before',b['houses']),('after',a['houses'])]:
 im=Image.new('RGB',(1500,1120),'#faf9f6');d=ImageDraw.Draw(im);d.text((30,20),'MEASURED PLAN / '+('Rev10 A detached house bodies'if edition=='before'else'Rev11 connected structural block'),font=F(30),fill='#172b36');P=lambda x,y:(750+16*x,1050-16*y);d.rectangle((*P(-16,48),*P(16,14)),outline='#75489b',width=4);d.text(P(-14,34),'PROTECTED 32 × 34m\n1,088m² / Z7.2m',font=F(24),fill='#75489b')
 for k,h in enumerate(houses):
  (x0,x1),(y0,y1)=fp(h);d.rectangle((*P(x0,y1),*P(x1,y0)),fill=colors[k%5],outline='#172b36',width=2);p=P((x0+x1)/2,(y0+y1)/2);d.text((p[0]-18,p[1]-12),h['id'],font=F(22),fill='#172b36')
 for k,r in enumerate(j['joins'],1):
  if edition=='after':
   z=r['joinPlaneCoordinateM'];lo,hi=r['sharedContactIntervalM'];p0=P(z,lo)if r['joinPlaneAxis']=='X'else P(lo,z);p1=P(z,hi)if r['joinPlaneAxis']=='X'else P(hi,z)
  else:
   f0=fp(next(h for h in houses if h['id']==r['from']));f1=fp(next(h for h in houses if h['id']==r['to']));p0=P(sum(f0[0])/2,sum(f0[1])/2);p1=P(sum(f1[0])/2,sum(f1[1])/2)
  d.line((p0,p1),fill='#178355'if edition=='after'else'#bf4a42',width=5);p=((p0[0]+p1[0])/2,(p0[1]+p1[1])/2);d.ellipse((p[0]-13,p[1]-13,p[0]+13,p[1]+13),fill='white',outline='#172b36');d.text((p[0]-8,p[1]-12),str(k),font=F(17),fill='#172b36')
 d.text((30,1000),'All ten shared interfaces closed; 16.6m lane opening stays clear.'if edition=='after'else'Body gaps: 0.55–5.764m; the original floor/service terraces were already connected.',font=F(23),fill='#172b36');d.text((30,1050),'Measured coordinate diagram; not a beauty render. Roof-height steps retain intentional open sky.',font=F(20),fill='#425963');im.save(R/('measured-plan-'+edition+'.png'))
im=Image.new('RGB',(1650,900),'#faf9f6');d=ImageDraw.Draw(im);d.text((30,20),'MEASURED LEFT ELEVATION / before above, connected proposal below',font=F(28),fill='#172b36')
for k,(name,houses)in enumerate([('Rev10 A',b['houses']),('Rev11',a['houses'])]):
 z0=390+410*k
 for n,h in enumerate([h for h in houses if h['edge']=='left']):
  lo,hi=h.get('alongM',[h.get('center',0)-h['widthM']/2,h.get('center',0)+h['widthM']/2]);x0=150+(lo-8)*20;x1=150+(hi-8)*20;top=h['mainRoofZ'];d.rectangle((x0,z0-top*20,x1,z0),fill=colors[n],outline='#172b36',width=2);d.text((x0+4,z0-top*20-22),h['id']+f' {top:.2f}m',font=F(18),fill='#172b36')
  for z in[.6,3.9,7.2,10.2,13.2,16.2]:
   if z<top:d.line((x0,z0-z*20,x1,z0-z*20),fill='#5e727e',width=2)
 d.text((25,z0-65),name,font=F(23),fill='#172b36');d.line((130,z0-144,1100,z0-144),fill='#75489b',width=3)
d.text((1120,250),'Protected roof Z7.2m\nUpper storeys 3.0m\nLower storeys 3.3m\nMain aperture 2.10m\nBelow lintel ~2.06m\nGallery depth 1.50m\nParapet 1.05m\nParty leaves total 0.60m',font=F(22),fill='#172b36');d.text((1120,650),'Guide, not code certification.\nRoof service hatch ~1.92m;\noutside visitor route.',font=F(19),fill='#425963');im.save(R/'measured-elevation.png')
im=Image.new('RGB',(1500,900),'#faf9f6');d=ImageDraw.Draw(im);d.text((40,25),'PROTECTED SCREEN / SIZE AND OCCLUSION LIMIT',font=F(30),fill='#172b36');d.rectangle((100,180,984,778),outline='#172b36',width=5);d.rectangle((188,240,896,718),outline='#b14e40',width=4);d.text((120,200),'80% outline = 7.07 × 4.78m\nDIAGRAM ONLY — NOT APPLIED',font=F(24),fill='#b14e40');d.text((1040,200),'UNCHANGED\n8.84 × 5.98m\nmain media screen\n\nHead-top median\n1.696 → 1.815m\n\nScreen / head-top\nheight ratio\n3.53 → 3.29',font=F(25),fill='#172b36');d.text((40,840),'The fixed screen masks rear housing; this remains a scale constraint. No screen/route changes.',font=F(24),fill='#425963');im.save(R/'screen-scale-diagram.png')
cache={}
def img(path):
 path=Path(path)
 if str(path)not in cache:
  im=Image.open(path).convert('RGB');buf=io.BytesIO();im.save(buf,'JPEG',quality=88);buf.seek(0);cache[str(path)]=ImageReader(buf)
 return cache[str(path)]
def picture(c,p,x,y,w,h):
 im=Image.open(p);sc=min(w/im.width,h/im.height);ww,hh=im.width*sc,im.height*sc;c.drawImage(img(p),x+(w-ww)/2,y+(h-hh)/2,ww,hh)
def page(c,title,number,W,H,note='Actual offline Blender; support OFF / original night lighting'):
 c.setFillColor(HexColor('#faf9f6'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#172b36'));c.setFont('Helvetica-Bold',15);c.drawString(18,H-27,title);c.setFont('Helvetica',8);c.drawString(18,13,note);c.drawRightString(W-16,13,str(number))
poses=['03-aerial','04-front','05-back','08-left-house','09-right-house','02-entry-square','22-street-entry','01-plan','12-elevation','06-left-diagonal','07-right-diagonal','15-mobile','16-mobile-lateral','21-roof-gallery','23-screen-side']
W,H=460,980;c=canvas.Canvas(str(R/'Rev11-Phone-Review.pdf'),pagesize=(W,H));num=0
def trio(pose):
 global num
 num+=1;page(c,pose.replace('-',' ').title()+' / A / B / Rev11',num,W,H)
 for k,(ed,label)in enumerate([('A','Preserved Rev10 A / original crowd'),('B','Preserved Rev10 B / original crowd'),('new','Proposed connected hybrid / +7%')]):
  yy=H-70-k*292;c.setFont('Helvetica-Bold',10);c.drawString(18,yy,label);picture(c,O/'renders'/ed/(pose+'.png'),15,yy-267,W-30,258)
 c.showPage()
for p in poses:trio(p)
for p in ['25-back-junction','26-left-junction','27-right-junction','28-roof-joins','24-right-elevation']:
 num+=1;page(c,p.replace('-',' ').title()+' / proposal',num,W,H,'Actual Blender inspection view; not a newly approved public route');picture(c,O/'renders/new'/(p+'.png'),15,170,W-30,680);c.showPage()
for name in ['measured-plan-before','measured-plan-after','measured-elevation','screen-scale-diagram','actual-blender-scale-rulers']:
 num+=1;page(c,name.replace('-',' ').title(),num,W,H,'Separately labelled diagnostic / measured guide; not a selected scene change');picture(c,R/(name+'.png'),12,160,W-24,740);c.showPage()
for p in ['04-front','06-left-diagonal','15-mobile','03-aerial']:
 num+=1;page(c,'Same architecture / crowd height / '+p,num,W,H)
 for k,(ed,label)in enumerate([('H00','Original height'),('H06','+6% control'),('new','+7% proposal'),('H09','+9% control')]):
  yy=H-64-k*222;c.setFont('Helvetica-Bold',10);c.drawString(18,yy,label);picture(c,O/'renders'/ed/(p+'.png'),15,yy-200,W-30,190)
 c.showPage()
num+=1;page(c,'Full portrait / proposed connected hybrid',num,W,H);picture(c,O/'renders/new/15-mobile.png',18,35,W-36,H-85);c.showPage()
num+=1;page(c,'Screen obscuration / diagnostic only',num,W,H,'Media hidden only for inspection; selected screen/lighting unchanged')
for k,(path,label)in enumerate([(O/'renders/new/04-front.png','Selected proposal: original screen'),(R/'DIAGNOSTIC-screen-media-hidden.png','Diagnostic: media planes hidden')]):
 yy=H-70-k*430;c.setFont('Helvetica-Bold',10);c.drawString(18,yy,label);picture(c,path,15,yy-390,W-30,380)
c.showPage();num+=1;page(c,'Optional floor patina / NOT selected',num,W,H,'Same floor mesh/UV route; temporary cloned material; no master write')
for k,(path,label)in enumerate([(O/'renders/new/03-aerial.png','Selected floor unchanged'),(R/'OPTIONAL-floor-03-aerial.png','Optional patina, maximum 6.6% darkening')]):
 yy=H-70-k*430;c.setFont('Helvetica-Bold',10);c.drawString(18,yy,label);picture(c,path,15,yy-390,W-30,380)
c.showPage();c.save();phonePages=num
# Larger matched comparison pages keep every original bitmap available in the gallery.
W,H=1400,900;c=canvas.Canvas(str(R/'Rev11-Full-Matched-Comparisons.pdf'),pagesize=(W,H));num=0
for p in poses:
 num+=1;page(c,p+' / preserved A / preserved B / proposed Rev11',num,W,H)
 for k,ed in enumerate(['A','B','new']):
  x=15+k*463;c.setFont('Helvetica-Bold',13);c.drawString(x,830,ed);picture(c,O/'renders'/ed/(p+'.png'),x,75,450,735)
 c.showPage()
for p in ['04-front','06-left-diagonal','15-mobile','03-aerial']:
 num+=1;page(c,'Crowd-height isolation / '+p,num,W,H)
 for k,ed in enumerate(['H00','H06','new','H09']):
  x=18+(k%2)*690;y=55+(1-k//2)*395;c.setFont('Helvetica-Bold',12);c.drawString(x,y+365,ed);picture(c,O/'renders'/ed/(p+'.png'),x,y,670,352)
 c.showPage()
c.save();fullPages=num
groups=[('Proposed Rev11',list((O/'renders/new').glob('*.png'))),('Original A',list((O/'renders/A').glob('*.png'))),('Original B',list((O/'renders/B').glob('*.png'))),('Height controls',[p for ed in['H00','H06','H09']for p in(O/'renders'/ed).glob('*.png')]),('Diagnostics',list(R.glob('*.png')))]
body=['<!doctype html><meta charset="utf-8"><title>Rev11 private review</title><style>body{font:17px system-ui;background:#f6f3ec;color:#172b36;margin:25px}img{max-width:100%;height:auto}figure{max-width:1280px;margin:25px 0}video{max-width:100%}</style><h1>Rev11 — connected roofscape + height study</h1><p>Private proposal awaiting user visual approval. Website unchanged. All images are actual offline Blender or explicitly labelled measured diagrams. Source A/B are byte-exact historical controls. The selected floor, screen and lighting remain unchanged.</p><p><a href="REPORT.md">Technical report</a> · <a href="review/Rev11-Phone-Review.pdf">Phone review</a> · <a href="review/Rev11-Full-Matched-Comparisons.pdf">Full comparisons</a> · <a href="RESTORE.md">Restore instructions</a></p><video controls src="review/Rev11-40s-Actual-Blender-Walk.mp4"></video><p>40 seconds, 80 actual Blender samples played at 2fps; not interactive/device FPS.</p>']
for label,files in groups:
 body.append('<h2>'+label+'</h2>')
 for p in sorted(files):
  rel=str(p.relative_to(O));body.append(f'<figure><a href="{html.escape(rel)}"><img loading="lazy" src="{html.escape(rel)}"></a><figcaption>{html.escape(rel)}</figcaption></figure>')
(O/'GALLERY.html').write_text('\n'.join(body));(O/'evidence/review-build.json').write_text(json.dumps({'phonePages':phonePages,'fullComparisonPages':fullPages,'sourcePNGs':sum(len(g[1])for g in groups),'actualBlenderNotConceptArt':True},indent=2));print('REVIEWS_COMPLETE',phonePages,fullPages)
