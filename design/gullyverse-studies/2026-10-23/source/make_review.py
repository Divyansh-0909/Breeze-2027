from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json,hashlib,html,math,io
O=Path(__file__).resolve().parents[1];V=O/'review';V.mkdir(exist_ok=True);rows=json.loads((O/'evidence/render-manifest.json').read_text());shots=[r for r in rows if r['mode']=='final'];assert len(shots)==36
names={'A':'Grounded Indian Neighborhood','B':'Festival Heavy Block','C':'Balanced Neighborhood Cypher'};poses=[f'{i:02}-'+s for i,s in enumerate(['landing','lane-walk','opening','hub','team','events','cutscene-begin','cutscene-mid','screen-reveal','screen-watch','overhead','mobile-landing'],1)];lookup={(r['variant'],r['camera']):r for r in shots};font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';captions={'01-landing':'Proposed landing hero / shops on both sides / screen hidden','02-lane-walk':'Forward lane walk / continuous gentle ramp','03-opening':'Service-room corner / progressive rooftop reveal','04-hub':'First hub / original sign artwork / central route stays open','05-team':'RIGHT / authorized project portraits / wanted-style paste-ups','06-events':'LEFT / clearly labelled event-art placeholders','07-cutscene-begin':'Crowd move begins / same open center aisle','08-cutscene-mid':'Through the watching crowd / no stage structure','09-screen-reveal':'Digital screen reveal / existing footage as a still','10-screen-watch':'Aftermovie watch-party composition','11-overhead':'Actual Blender orthographic site view','12-mobile-landing':'Narrow mobile hero / same camera pose and lens across A/B/C'}
def fit(im,w,h):return ImageOps.contain(im.convert('RGB'),(int(w),int(h)))
for v in names:
 sheet=Image.new('RGB',(1920,1840),'#f1ede1');d=ImageDraw.Draw(sheet);d.text((30,20),v+' / '+names[v],font=ImageFont.truetype(bold,32),fill='#213c35')
 for i,n in enumerate(poses):
  x=30+(i%3)*630;y=80+(i//3)*435;im=fit(Image.open(O/lookup[v,n]['file']),600,375);sheet.paste(im,(x+(600-im.width)//2,y));d.text((x,y+383),n,font=ImageFont.truetype(font,20),fill='#213c35')
 sheet.save(V/('Contact-Sheet-'+v+'.jpg'),quality=92,subsampling=0)
for n in poses:
 strip=Image.new('RGB',(2400,600),'#f1ede1');d=ImageDraw.Draw(strip)
 for i,v in enumerate(names):
  x=i*800;d.text((x+16,14),v+' / '+names[v],font=ImageFont.truetype(bold,22),fill='#213c35');im=fit(Image.open(O/lookup[v,n]['file']),770,500);strip.paste(im,(x+(800-im.width)//2,52))
 strip.save(V/('Matched-'+n+'.jpg'),quality=92,subsampling=0)
# Phone-oriented long portrait pages: A/B/C use identical image boxes and camera settings.
pdf=V/'Gullyverse-Lane-Rooftop-ABC-Review.pdf';c=canvas.Canvas(str(pdf),pagesize=(612,1224));page=0

def header(title,sub='Blender concept study / same site and camera rig / no website change'):
 global page;page+=1;c.setFillColorRGB(.95,.94,.9);c.rect(0,0,612,1224,fill=1,stroke=0);c.setFillColorRGB(.12,.23,.2);c.setFont('Helvetica-Bold',11);c.drawString(28,1190,'BREEZE 2027 / GULLYVERSE');c.setFont('Helvetica-Bold',17);c.drawString(28,1157,title);c.setFont('Helvetica',9);c.drawString(28,1137,sub);c.setFont('Helvetica',8);c.drawString(28,18,f'PRIVATE CONCEPT / USER REVIEW REQUIRED / {page}')
def paragraph(s,y,size=12):
 c.setFont('Helvetica',size);c.setFillColorRGB(.12,.23,.2);line=''
 for word in s.split():
  if c.stringWidth(line+word,'Helvetica',size)>552:c.drawString(28,y,line);y-=size*1.5;line=''
  line+=word+' '
 if line:c.drawString(28,y,line);y-=size*1.5
 return y

def figure(file,x,y,w,h):
 im=Image.open(file).convert('RGB');factor=min(w/im.width,h/im.height);buffer=io.BytesIO();im.save(buffer,format='JPEG',quality=92,subsampling=0);buffer.seek(0);c.drawImage(ImageReader(buffer),x+(w-im.width*factor)/2,y+(h-im.height*factor)/2,width=im.width*factor,height=im.height*factor,mask='auto')
header('One journey. Three art directions.');y=1087
for s in ['A night-time Indian shop lane becomes an elevated rooftop cypher and Aftermovie watch party. Team is to the right, Events to the left, screen straight ahead.','A / Grounded: ordinary neighborhood intimacy with restrained festival takeover. B / Festival Heavy: more temporary graphics, warm practicals and crowd energy. C / Balanced: a quieter lane opening into an identifiable watch-party hub.','These are editable Blender blockouts, not production art, browser screenshots or a claim of finished realism. All A/B/C views share site dimensions, camera poses, lenses, floor route and screen position. Lights, temporary graphics and secondary crowd density vary.','The shop signs are fictional generic businesses. Team portraits come from the authorized existing project. Event posters and human bodies are labelled concept proxies. No missing artist graffiti is invented.','Recommendation: review C as the strongest balance, with A retained as a quieter alternative. No version has been selected or implemented on the website.']:
 y=paragraph(s,y)-20
figure(O/lookup['C','01-landing']['file'],28,155,556,348);c.showPage()
header('Scaled master layout');figure(V/'master-layout.png',28,65,556,1030);c.showPage();header('Accessible level transition');figure(V/'access-section.png',28,590,556,470);y=540
for s in ['The fictional lane already occupies a supported market podium at +6.0m. A 24m run rises 1.2m at 1:20 into the +7.2m roof. There is no required stair/elevator or loading cut.','A service-room corner hides the screen from the landing view; the route passes its left shoulder and opens at the hub. The geometric tests exclude participating haze so visibility is not faked by fog.','The 32m x 34m roof has parapets, a clear central audience aisle and side routes to poster walls. This is a virtual concept feasibility study, not structural, regulatory or accessibility certification.']:
 y=paragraph(s,y)-18
c.showPage()
for v in names:
 header(v+' / '+names[v],'Equal-sized contact sheet / all 12 required viewpoints');figure(V/('Contact-Sheet-'+v+'.jpg'),28,95,556,1015);c.showPage()
for n in poses:
 header(n+' / matched A-B-C',captions[n])
 for i,v in enumerate(names):
  yy=760-i*354;c.setFont('Helvetica-Bold',11);c.drawString(28,yy+337,v+' / '+names[v]);figure(O/lookup[v,n]['file'],28,yy,556,325)
 c.showPage()
header('Review gate and known limitations');y=1085
for s in ['Choose an environment direction before runtime work. C is recommended for discussion, not automatically adopted. The current WIP quarry/cave/canal-material code and all prior checkpoints remain unchanged.','The new crowd bodies, scooters, stocked shops and skyline are intentionally simplified. They need production asset detail, animation and surface refinement if this direction is approved. The distant crowd is a small visible group, not a simulated moving crowd.','The concept uses the existing GULLYVERSE hero-board artwork with a resized support frame and the existing screen proportions at uniform 0.65 scale. This is conceptual reuse, not byte-identical scaffold/screen component integration.','The digital screen displays a still extracted at 12 seconds from the existing Aftermovie. Visible concert structures inside the footage belong to the video; no old stage/truss/platform is modelled in the new scene.','The proposed 20-second camera move is editable in Blender. Its separate movie is a keyframe animatic, not a real-time walkthrough or browser benchmark. Sound is described in the storyboard; no unlicensed music was added.','Source, camera guide, ray/route checks, image hashes, budgets, provenance and complete restoration instructions accompany this pack. Physical-device/runtime/collision integration has not been performed for this new concept.']:
 y=paragraph(s,y)-22
c.showPage();c.save()
# Offline full-resolution gallery. Source PNGs are the actual Blender outputs, not generated stills.
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse lane / rooftop ABC</title><style>body{margin:0;background:#f1ede1;color:#213c35;font:16px system-ui}header,main{max-width:1500px;margin:auto;padding:20px}section{margin:38px 0}article{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0;background:#fff;padding:10px}img{width:100%;height:auto}a{color:#24685a}small{line-height:1.5}@media(max-width:750px){article{grid-template-columns:1fr}}</style><header><h1>Gullyverse / Lane to Rooftop</h1><p>Private Blender concept. Shared architecture, route and cameras. No live website changes.</p><p><a href="Gullyverse-Lane-Rooftop-ABC-Review.pdf">Phone-friendly review PDF</a> / <a href="master-layout.png">Master layout</a> / <a href="access-section.png">Access section</a> / <a href="Crowd-Reveal-20s-Animatic.mp4">20s keyframe animatic</a></p></header><main>']
for n in poses:
 parts.append('<section><h2>'+html.escape(captions[n])+'</h2><p><a href="Matched-'+n+'.jpg">A/B/C side by side</a></p><article>')
 for v in names:
  r=lookup[v,n];parts.append('<figure><h3>'+v+' / '+names[v]+'</h3><a href="../'+r['file']+'"><img loading="lazy" src="../'+r['file']+'"></a><small>'+html.escape(str(r['position']))+' / lens '+str(r['lens'])+'mm<br>'+str(r['width'])+' x '+str(r['height'])+' / '+r['engine']+' / '+str(r['samples'])+' samples</small></figure>')
 parts.append('</article></section>')
parts.append('</main>');(V/'index.html').write_text(''.join(parts));print('REVIEW_PACK',page,'pages / 36 final renders / 12 matched strips / 3 contact sheets')
# Equality assertion uses actual final renderer records, not just labels.
for n in poses:
 r=[lookup[v,n]for v in names]
 for key in ['position','rotationEuler','lens','sensor','cameraType','width','height','samples','engine','exposure']:assert r[0][key]==r[1][key]==r[2][key],(n,key)
(O/'evidence/matched-render-settings.json').write_text(json.dumps({'status':'PASS','finalRenders':36,'matchedCameraViews':12,'variants':['A','B','C'],'fieldsCompared':['position','rotationEuler','lens','sensor','cameraType','width','height','samples','engine','exposure'],'note':'Lighting/graphics/secondary crowd intentionally vary; no live website modifications.'},indent=2))
