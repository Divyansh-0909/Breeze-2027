from pathlib import Path
import json,hashlib,html,io,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1];V=O/'review';OLD=Path('/workspace/gullyverse-world-concept/2026-10-23/revisions/03-centered-navigation-board')
rows=json.loads((O/'evidence/render-manifest.json').read_text());shots=[r for r in rows if r['mode']=='stills'];walk=[r for r in rows if r['mode']=='walk']
assert len(shots)==23 and len(walk)==120
assert json.loads((O/'evidence/layout-validation.json').read_text())['status']=='PASS'
assert json.loads((O/'evidence/master-comparison.json').read_text())['status']=='PASS'
lookup={(r['variant'],r['camera']):r for r in shots}
poses=['01-landing','03-opening','04-hub','08-crowd-middle','09-screen-front','11-overhead']
names={'A':'Grounded Indian Neighborhood','B':'Festival Heavy Block','C':'Balanced Neighborhood Cypher'}
for n in poses:
    views=[lookup[v,n]for v in names]
    for key in ['position','rotationEuler','lens','sensorWidthMM','width','height','samples','engine','exposure']:
        assert views[0][key]==views[1][key]==views[2][key]
for r in rows:assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
(O/'evidence/matched-settings.json').write_text(json.dumps({'status':'PASS','matchedABCViews':6,'matchedStills':18,'additionalCViews':5,'totalStills':23,'actualRenderedWalkFrames':120,'walkFPS':6,'nativeWalkResolution':[384,240],'noInterpolatedOrGeneratedFrames':True},indent=2)+'\n')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for v in names:
    sheet=Image.new('RGB',(1440,1500),'#f1ede1');d=ImageDraw.Draw(sheet);d.text((24,18),v+' / STRAIGHT WALK + SEMICIRCULAR CROWD',font=ImageFont.truetype(bold,24),fill='#213c35')
    for i,n in enumerate(poses):
        x=20+i%2*710;y=74+i//2*470;im=ImageOps.contain(Image.open(O/lookup[v,n]['file']).convert('RGB'),(680,425));sheet.paste(im,(x+(680-im.width)//2,y));d.text((x,y+431),n,font=ImageFont.truetype(font,19),fill='#213c35')
    sheet.save(V/('Contact-'+v+'.jpg'),quality=92)
shutil.copy2(OLD/'renders/C/03-opening.png',V/'Before-Left-Detour.png')
shutil.copy2(OLD/'renders/C/11-overhead.png',V/'Before-Crowd-Grid.png')
pdf=V/'Gullyverse-Straight-Walk-Semicircular-Crowd-Review.pdf';c=canvas.Canvas(str(pdf),pagesize=(612,1224));page=0
def header(title,sub='Revision 04 / actual Blender renders / private concept only'):
    global page
    page+=1;c.setFillColorRGB(.95,.94,.9);c.rect(0,0,612,1224,fill=1,stroke=0);c.setFillColorRGB(.12,.23,.2)
    c.setFont('Helvetica-Bold',11);c.drawString(28,1190,'BREEZE 2027 / GULLYVERSE');c.setFont('Helvetica-Bold',17);c.drawString(28,1157,title);c.setFont('Helvetica',9);c.drawString(28,1136,sub);c.setFont('Helvetica',8);c.drawString(28,18,f'PRIVATE CONCEPT / WEBSITE UNCHANGED / {page}')
def para(text,y,size=11):
    c.setFont('Helvetica',size);line=''
    for word in text.split():
        if c.stringWidth(line+word,'Helvetica',size)>552:c.drawString(28,y,line);y-=size*1.5;line=''
        line+=word+' '
    if line:c.drawString(28,y,line);y-=size*1.5
    return y
def fig(path,x,y,w,h):
    im=Image.open(path).convert('RGB');f=min(w/im.width,h/im.height);buf=io.BytesIO();im.save(buf,format='JPEG',quality=92);buf.seek(0);c.drawImage(ImageReader(buf),x+(w-im.width*f)/2,y+(h-im.height*f)/2,width=im.width*f,height=im.height*f)
header('Straight connection. Curved audience.')
para('The camera now walks directly down the middle of the lane and through the open connection. No side detour, separate reveal stage or cinematic lift remains. Audience rows curve around the Aftermovie screen and face inward, leaving a clear central aisle.',1088)
fig(O/lookup['C','15-semicircle-high']['file'],28,640,556,348);fig(O/lookup['C','03-opening']['file'],28,235,556,348)
para('The centered navigation board stays in place. Shops, cypher circle, screen, poster destinations, architecture, materials and lighting are preserved.',174);c.showPage()
header('Continuous walk / no reveal section')
c.setFont('Helvetica-Bold',11);c.drawString(28,1080,'BEFORE / old left-side inspection / different camera pose');fig(V/'Before-Left-Detour.png',28,716,556,348)
c.drawString(28,678,'AFTER / centerline through open connection');fig(O/lookup['C','03-opening']['file'],28,313,556,348)
y=255
for s in ['One editable 40-second Blender action walks from Y -27m to +36.5m, with X fixed at zero. Eye height remains 1.72m above the existing floor; only Z follows the gentle ramp. Forward heading and lens stay constant.','The separate 20-second MP4 is an actual uncut rendered excerpt of the connection: 120 genuine Blender frames at 6fps, native 384 x 240, two samples. It is a low-resolution motion proof, not hardware FPS or an interpolated video.']:
    y=para(s,y)-18
c.showPage();header('Semicircular audience / screen facing');fig(O/lookup['C','16-rooftop-plan']['file'],28,635,556,348);y=573
for s in ['The existing 48 shared audience figures form three curved tiers at radii 7.8m, 10.2m and 12.6m from the screen center. Ends stop five degrees short of a full front semicircle for grazing-view clearance.','Everyone faces the screen center. Existing festival and balanced extras sit on supplementary arcs. No people are placed behind the screen. The center foot-position gap is 4m; raised arms and bodies are included in clearance checks.','The audience uses existing geometry and clothing; the formation changes, with no new crowd or texture set. Simplified figures remain concept proxies.']:
    y=para(s,y)-22
c.showPage();header('Updated layout / straight centerline');fig(V/'master-layout.png',28,50,556,1060);c.showPage()
for n in poses:
    header(n+' / matched A-B-C','Same current pose, lens, samples and exposure across the three variants')
    for i,v in enumerate(names):
        yy=760-i*354;c.setFont('Helvetica-Bold',11);c.drawString(28,yy+337,v+' / '+names[v]);fig(O/lookup[v,n]['file'],28,yy,556,325)
    c.showPage()
header('Mobile and navigation context');fig(O/lookup['C','12-mobile-landing']['file'],28,555,556,550);fig(O/lookup['C','14-board-arrival']['file'],28,145,556,348);c.showPage()
header('Validation and preserved work');y=1088
validation=json.loads((O/'evidence/layout-validation.json').read_text());budget=json.loads((O/'evidence/scene-budget-final.json').read_text())
for s in ['All 960 frames of the continuous action were checked in every variant. X remains zero, forward motion is monotonic, eye height follows the floor within 0.002m and the camera does not intersect the tested 0.35m clearance envelope.','Straight entry, straight screen aisle, Team and Events routes pass the existing floor and 0.35m capsule tests. Actual crowd object locations and their inward-facing orientation were independently checked. These are Blender concept checks, not certification of the current website registry, accessibility regulations or hardware.','The inactive festival collection initially returned cached world matrices during authoring. Composition now uses unparented local basis transforms and validation uses evaluated geometry. Incorrect draft B captures are excluded; all final variants pass without relaxed tolerances.','Existing mesh data, UVs and materials remain identical. Only audience-object transforms and requested cameras change. The board, screen, shops, light settings and all unrelated geometry are preserved.','The master packs '+str(budget['imageCount'])+' used images. One previously unused wayfinding image retired naturally on resave; it remains recoverable in all preceding masters. No active surface material or texture scale was changed.','No website code, public default, commit, push, merge or deployment. Previous masters and checkpoints remain intact. Source, 23 full-resolution stills, actual walk frames, MP4, gallery, report, hashes and restoration instructions accompany this revision.']:
    y=para(s,y)-26
c.showPage();c.save()
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse straight walk and semicircular audience</title><style>body{font:16px system-ui;background:#f1ede1;color:#213c35;max-width:1500px;margin:auto;padding:20px}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}img,video{width:100%}figure{margin:0}section{margin:36px 0}@media(max-width:750px){.row{grid-template-columns:1fr}}</style><h1>Straight walk + semicircular audience</h1><p>Actual Blender concept evidence. Website unchanged.</p><p><a href="Gullyverse-Straight-Walk-Semicircular-Crowd-Review.pdf">Review PDF</a></p><video controls preload="metadata" src="Straight-Connection-Walk-20s.mp4"></video><p>Actual 20-second Blender excerpt; 6fps / 384 x 240. No interpolated frames.</p>']
for n in poses:
    parts.append('<section><h2>'+html.escape(n)+'</h2><div class="row">')
    for v in names:
        r=lookup[v,n];parts.append('<figure><h3>'+v+' / '+names[v]+'</h3><a href="../'+r['file']+'"><img loading="lazy" src="../'+r['file']+'"></a></figure>')
    parts.append('</div></section>')
for n in ['02-lane-walk','12-mobile-landing','14-board-arrival','15-semicircle-high','16-rooftop-plan']:
    r=lookup['C',n];parts.append('<section><h2>'+n+' / C</h2><a href="../'+r['file']+'"><img loading="lazy" src="../'+r['file']+'"></a></section>')
(V/'index.html').write_text(''.join(parts));print('REVIEW_COMPLETE',page,'pages',flush=True)
