import io, json, hashlib, math, html
from pathlib import Path
from collections import OrderedDict
from PIL import Image, ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

O=Path(__file__).resolve().parents[1]
plan=json.loads((O/'evidence/capture-plan.json').read_text())
captures={p['id']:p for p in json.loads((O/'evidence/captures.json').read_text())}
poses=plan['poses']; assert len(captures)==len(poses)==52
for p in poses:
    if p['section'] in ['Architectural details','Roofs and services']:
        p['section']='Architectural details and roofs'
checks=[]
for p in poses:
    file=O/p['file']; r=captures[p['id']]
    assert hashlib.sha256(file.read_bytes()).hexdigest()==r['sha256']
    im=Image.open(file); im.load()
    assert list(im.size)==p['viewport'],(p['id'],im.size,p['viewport'])
    stats=ImageStat.Stat(im.convert('RGB'))
    assert max(stats.stddev)>3,(p['id'],'empty image')
    checks.append({'id':p['id'],'size':list(im.size),'sha256':r['sha256'],'bytes':file.stat().st_size})

for name,filename in [('Open','OpenSans-Regular.ttf'),('Semi','OpenSans-Semibold.ttf'),('Bold','OpenSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/open-sans/'+filename))
W,H=960,640
bg='#10191e'; ink='#f0f0e9'; muted='#a6b5bb'; accent='#c4e288'; panel='#1a272e'
out=O/'review/Gullyverse-Full-3D-Environment-2026-11-11.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
c.setTitle('Gullyverse — Full 3D Environment / 52 views')
c.setAuthor('Breeze 2027 / Environment review')
c.setSubject('Current Rev15J1 Blender environment: shops, shutters, houses, windows, roofs, walls and night scene')
cache={}
def color(v):return HexColor(v)
def text(x,y,s,size=11,font='Open',fill=ink):
    c.setFillColor(color(fill)); c.setFont(font,size);c.drawString(x,y,s)
def para(x,y,s,width,size=11,fill=muted):
    p=Paragraph(s,ParagraphStyle('body',fontName='Open',fontSize=size,leading=size*1.5,textColor=color(fill)))
    _,h=p.wrap(width,H);p.drawOn(c,x,y-h);return h
def page(section):
    c.setFillColor(color(bg));c.rect(0,0,W,H,fill=1,stroke=0)
    text(38,H-30,'GULLYVERSE',10,'Bold',accent)
    text(170,H-30,section.upper(),9,'Semi',muted)
    text(W-176,H-30,'11 NOVEMBER 2026',9,'Open',muted)
    c.setStrokeColor(color('#34434b'));c.line(38,32,W-38,32)
    text(38,17,'BREEZE 2027  /  REV15J1  /  FULL ENVIRONMENT REVIEW',8,'Open',muted)
    c.setFont('Open',8);c.drawRightString(W-38,17,str(c.getPageNumber()))
def image_fit(p,x,y,w,h):
    key=p['id']
    if key not in cache:
        im=Image.open(O/p['file']).convert('RGB');b=io.BytesIO()
        # PDF encoding only; original full-resolution PNG captures are retained.
        im.save(b,'JPEG',quality=94,subsampling=0,optimize=True)
        cache[key]=(ImageReader(io.BytesIO(b.getvalue())),im.size)
    reader,(iw,ih)=cache[key];scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
    c.drawImage(reader,x+(w-dw)/2,y+(h-dh)/2,dw,dh)
def badge(p,x,y):
    label='ORIGINAL NIGHT' if p['lighting']=='original' else 'INSPECTION / ARCHITECTURE' if p['scene']=='architecture' else 'INSPECTION / FULL SCENE'
    text(x,y,label,8,'Bold',accent)

groups=OrderedDict()
for p in poses:groups.setdefault(p['section'],[]).append(p)
contact_pages=math.ceil(len(poses)/12)
first_detail=3+contact_pages
detail_pages={p['id']:first_detail+i for i,p in enumerate(poses)}

page('Complete scene capture')
text(38,565,'Full 3D environment',34,'Bold')
text(40,533,'52 views  /  shops, shutters, houses, walls, windows and roofs',14,'Open',muted)
image_fit(poses[0],38,144,884,365)
para(40,127,'Five existing open shops. Three existing closed artist shutters. Eleven surrounding houses. Original night views plus clearly labelled inspection views.',870,12,ink)
text(40,58,'Source: current Organising Committee full-heading master. Captured from Blender.',10,'Open',muted)
c.showPage()

page('Contents and viewing guide')
text(38,565,'Explore the environment',28,'Bold')
y=519
for title,items in groups.items():
    start=detail_pages[items[0]['id']];end=detail_pages[items[-1]['id']]
    text(42,y,title,13,'Semi');text(450,y,f'{len(items)} views',11,'Open',muted)
    text(568,y,f'Pages {start}–{end}',11,'Semi',accent)
    c.linkRect('',items[0]['id'],(38,y-5,720,y+17),relative=0,thickness=0);y-=33
para(40,133,'<b>How to read the images</b><br/>Original night = the saved scene lighting. Inspection = temporary brighter review lighting. Architecture inspection = houses and their construction details, with crowd, screen and free artwork omitted to expose the façades. The original master is preserved.',867,11,muted)
c.showPage()

for group_no in range(contact_pages):
    chunk=poses[group_no*12:(group_no+1)*12]
    page('Visual index')
    text(38,565,f'Visual index / {group_no+1} of {contact_pages}',25,'Bold')
    for j,p in enumerate(chunk):
        col=j%4;row=j//4;x=38+col*225;y=390-row*164
        c.setFillColor(color(panel));c.rect(x,y,209,134,fill=1,stroke=0)
        image_fit(p,x+3,y+3,203,128)
        title=p['id'].split('-')[0]+'  '+p['title']
        if len(title)>34:title=title[:32]+'…'
        text(x,y-15,title,8,'Semi')
        text(x,y-28,f'PAGE {detail_pages[p["id"]]}',7,'Open',accent)
        c.linkRect('',p['id'],(x,y-30,x+209,y+134),relative=0,thickness=0)
    c.showPage()

for i,p in enumerate(poses):
    page(p['section']);c.bookmarkPage(p['id'])
    if i==0 or p['section']!=poses[i-1]['section']:c.addOutlineEntry(p['section'],p['id'],level=0,closed=False)
    c.addOutlineEntry(p['title'],p['id'],level=1,closed=False)
    text(38,563,p['id'][:2]+' / '+p['title'],20 if len(p['title'])<58 else 17,'Bold')
    badge(p,40,538)
    portrait=p['viewport'][1]>p['viewport'][0]
    if portrait:
        image_fit(p,38,49,390,474)
        h=next(h for h in plan['houses'] if h['id']==p['house'])
        text(468,484,'HOUSE '+p['house'],24,'Bold',accent)
        para(468,453,f'{h["edge"].capitalize()} edge of the courtyard<br/>{h["upperLevels"]} upper storeys + lower podium levels',425,13,ink)
        para(468,369,'Wall plaster and repair patches<br/>Window glazing, timber shutters and reveals<br/>Doors, balcony railings and supported galleries<br/>Roof parapet and access structures',425,12,muted)
        para(468,239,'<b>Architecture inspection</b><br/>The crowd, screen and free mural artwork are omitted from this view so the house construction can be seen. The modelled walls, frames and doors are retained.',425,11,muted)
        if p.get('nearClip'):
            para(468,133,'Foreground buildings are clipped at the façade for visibility. Some projecting details are cut at that plane.',425,10,accent)
        text(468,78,'Full-resolution capture: 1000 × 1400 px',10,'Open',muted)
    else:
        image_fit(p,38,89,884,438)
        note=p['notes'] or ('Saved night lighting; current model and materials.' if p['lighting']=='original' else 'Temporary brighter inspection lighting to show the current geometry and materials.')
        para(40,78,note,880,9,muted)
    c.showPage()

page('Capture notes')
text(38,565,'What this review contains',28,'Bold')
notes=[
    ('Current source','Gullyverse-Rev15J1-Full-Heading.blend. The active scene is Rev15J1 / Organising Committee Full Heading. These are actual Blender renders of the existing environment.'),
    ('Shop states','Five shop bays are currently modelled open, with counters and stock. Three other fronts have closed artist shutters: Chaar Diwari, Ritviz and Neha Kakkar. This document shows those existing states; alternate opening or closing states have not been authored.'),
    ('Lighting and isolation','Six views use the source night lighting. Other views use temporary inspection lighting. Architectural views isolate the house geometry. Five end-house views also clip foreground buildings at the facade, as labelled on those pages. Original light energies, source scenes and the master file are preserved.'),
    ('Images and quality','Landscape views are 1280 × 720 px, house views are 1000 × 1400 px. The unchanged Organising Committee mural view is reused from the current 1600 × 900 capture. Original PNG files are included with the review archive. PDF images use JPEG encoding for a smaller combined document.'),
]
y=510
for label,body in notes:
    text(40,y,label,13,'Semi',accent);y-=21
    y-=para(40,y,body,865,11,muted)+29
text(40,70,'MASTER SHA-256',8,'Bold',muted);text(40,53,plan['masterSHA256'],8,'Open',muted)
c.save()

(O/'evidence/image-validation.json').write_text(json.dumps({'status':'PASS','imageCount':len(checks),'images':checks,'pdfPagesExpected':first_detail+len(poses),'masterSHA256':plan['masterSHA256']},indent=2))
cards=[]
for p in poses:
    label='Original night' if p['lighting']=='original' else 'Inspection / architecture isolated' if p['scene']=='architecture' else 'Inspection / full scene'
    cards.append(f'<figure><a href="../{p["file"]}"><img loading="lazy" src="../{p["file"]}" alt="{html.escape(p["title"])}"></a><figcaption><b>{p["id"][:2]} / {html.escape(p["title"])}</b><br>{label}</figcaption></figure>')
(O/'review/gallery.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse / Full environment review</title><style>body{background:#10191e;color:#f0f0e9;font:16px system-ui;max-width:1600px;margin:40px auto;padding:0 24px}a{color:#c4e288}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}figure{margin:0;background:#1a272e}img{width:100%;height:250px;object-fit:contain}figcaption{padding:16px;line-height:1.6}</style><h1>Gullyverse / Full 3D environment</h1><p>52 views · 11 November 2026 · Rev15J1</p><p>Original night views and temporary brighter inspection views. Architecture inspection isolates house geometry. The source master is unchanged.</p><p><a href="'+out.name+'">Combined PDF</a></p><div class="grid">'+''.join(cards)+'</div>')
print('PDF',out,'bytes',out.stat().st_size,'pages',first_detail+len(poses))
