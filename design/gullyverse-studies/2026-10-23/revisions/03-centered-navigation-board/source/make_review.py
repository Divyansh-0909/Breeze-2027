from pathlib import Path
import json,hashlib,shutil,io,html
from PIL import Image,ImageOps,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1];OLD=O.parent/'02-no-reveal-column';V=O/'review'
rows=json.loads((O/'evidence/render-manifest.json').read_text());assert len(rows)==19
lookup={(r['variant'],r['camera']):r for r in rows}
poses=['01-landing','02-lane-walk','03-opening','04-hub','11-overhead','12-mobile-landing']
prior={(r['variant'],r['camera']):r for r in json.loads((OLD/'evidence/render-manifest.json').read_text())}
names={'A':'Grounded Indian Neighborhood','B':'Festival Heavy Block','C':'Balanced Neighborhood Cypher'}
for name in poses:
    views=[lookup[v,name]for v in names]
    for field in ['position','rotationEuler','lens','sensor','cameraType','width','height','samples','engine','exposure']:
        assert views[0][field]==views[1][field]==views[2][field]
        for v in names:assert lookup[v,name][field]==prior[v,name][field]
for r in rows:r['sha256']=hashlib.sha256((O/r['file']).read_bytes()).hexdigest()
(O/'evidence/render-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
(O/'evidence/matched-settings.json').write_text(json.dumps({'status':'PASS','matchedABCViews':6,'matchedRenders':18,'newInspectionView':'C/14-board-arrival','originalCamerasUnchanged':True},indent=2)+'\n')
for name in ['01-landing','03-opening']:
    shutil.copy2(OLD/'renders/C'/(name+'.png'),V/('Before-C-'+name+'.png'))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for v in names:
    sheet=Image.new('RGB',(1440,1500),'#f1ede1');d=ImageDraw.Draw(sheet)
    d.text((24,18),v+' / CENTERED NAVIGATION BOARD',font=ImageFont.truetype(bold,27),fill='#213c35')
    for i,n in enumerate(poses):
        x=20+i%2*710;y=74+i//2*470;im=ImageOps.contain(Image.open(O/lookup[v,n]['file']).convert('RGB'),(680,425));sheet.paste(im,(x+(680-im.width)//2,y));d.text((x,y+431),n,font=ImageFont.truetype(font,19),fill='#213c35')
    sheet.save(V/('Contact-'+v+'.jpg'),quality=92)
pdf=V/'Gullyverse-Centered-Navigation-Board-Review.pdf';c=canvas.Canvas(str(pdf),pagesize=(612,1224));page=0
def header(title,sub='Revision 03 / actual Blender concept renders / website unchanged'):
    global page
    page+=1;c.setFillColorRGB(.95,.94,.9);c.rect(0,0,612,1224,fill=1,stroke=0);c.setFillColorRGB(.12,.23,.2)
    c.setFont('Helvetica-Bold',11);c.drawString(28,1190,'BREEZE 2027 / GULLYVERSE');c.setFont('Helvetica-Bold',18);c.drawString(28,1157,title)
    c.setFont('Helvetica',9);c.drawString(28,1136,sub);c.setFont('Helvetica',8);c.drawString(28,18,f'PRIVATE BLENDER CONCEPT / USER REVIEW / {page}')
def paragraph(text,y,size=11):
    c.setFont('Helvetica',size);line=''
    for word in text.split():
        if c.stringWidth(line+word,'Helvetica',size)>552:c.drawString(28,y,line);y-=size*1.5;line=''
        line+=word+' '
    if line:c.drawString(28,y,line);y-=size*1.5
    return y
def fig(path,x,y,w,h):
    im=Image.open(path).convert('RGB');f=min(w/im.width,h/im.height);buf=io.BytesIO();im.save(buf,format='JPEG',quality=92);buf.seek(0);c.drawImage(ImageReader(buf),x+(w-im.width*f)/2,y+(h-im.height*f)/2,width=im.width*f,height=im.height*f)
header('Navigation board in the approach')
paragraph('The existing board now sits on the centerline, before the rooftop cypher. Size, artwork and geometry are unchanged. Its three existing local lights follow the move. No reveal column is restored.',1088)
c.setFont('Helvetica-Bold',12);c.drawString(28,1000,'BEFORE / board off to the right');fig(V/'Before-C-03-opening.png',28,642,556,348)
c.drawString(28,609,'AFTER / centered board / identical camera');fig(O/lookup['C','03-opening']['file'],28,250,556,348)
paragraph('The open connection remains. Team stays right, Events stays left and the screen stays straight ahead. Original routes, camera rig, crowd, shops and global lighting are retained.',190);c.showPage()
header('Board encountered before the cypher','New frontal inspection camera; separate from the six matched poses')
fig(O/lookup['C','14-board-arrival']['file'],28,690,556,348);y=620
for text in ['Board center moves from [5.6, 25, 7.2]m to [0, 21, 7.2]m, across the arrival line before the original hub point [0, 22, 7.2]m. The cypher remains at [-6, 25]m.','Existing artwork, sign hierarchy, frame scale and support geometry remain. No new display, lamp or texture collection is introduced.','The 0.35m visitor-capsule, floor and sampled camera-path tests pass. Minimum sampled one-sided ray clearances are 0.902m entry, 0.981m Team and 0.625m Events; these are not certification of a continuous 3m-wide path.','The former screen-hidden-at-landing condition remains retired after the user requested removal of the reveal block. No numerical geometry tolerances are changed.','Original camera poses are retained, including the close hub camera; its framing can crop the much nearer centered board. This additional arrival camera shows the full board without silently altering matched comparisons.']:
    y=paragraph(text,y)-24
c.showPage();header('Updated layout / same destinations');fig(V/'master-layout.png',28,52,556,1060);c.showPage()
for n in poses:
    header(n+' / matched A-B-C','Identical original pose, lens, quality and exposure for each variant')
    for i,v in enumerate(names):
        yy=760-i*354;c.setFont('Helvetica-Bold',11);c.drawString(28,yy+337,v+' / '+names[v]);fig(O/lookup[v,n]['file'],28,yy,556,325)
    c.showPage()
c.save()
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Centered Gullyverse navigation board</title><style>body{font:16px system-ui;background:#f1ede1;color:#213c35;max-width:1500px;margin:auto;padding:20px}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}img{width:100%}figure{margin:0}section{margin:36px 0}@media(max-width:750px){.row{grid-template-columns:1fr}}</style><h1>Navigation board in rooftop approach</h1><p>19 actual Blender renders; original cameras preserved; website unchanged.</p><a href="Gullyverse-Centered-Navigation-Board-Review.pdf">Review PDF</a><section><h2>New frontal arrival inspection</h2><img src="../renders/C/14-board-arrival.png"></section>']
for n in poses:
    parts.append('<section><h2>'+html.escape(n)+'</h2><div class="row">')
    for v in names:
        r=lookup[v,n];parts.append('<figure><h3>'+v+' / '+names[v]+'</h3><a href="../'+r['file']+'"><img loading="lazy" src="../'+r['file']+'"></a><p>'+str(r['lens'])+'mm / '+str(r['width'])+' x '+str(r['height'])+'</p></figure>')
    parts.append('</div></section>')
(V/'index.html').write_text(''.join(parts));print('REVIEW_COMPLETE',page,'pages',flush=True)
