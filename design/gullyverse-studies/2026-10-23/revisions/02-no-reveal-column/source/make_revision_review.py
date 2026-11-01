from pathlib import Path
import hashlib, html, io, json, shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

O=Path(__file__).resolve().parents[1];BASE=O.parents[1];V=O/'review'
rows=json.loads((O/'evidence/render-manifest.json').read_text())
assert len(rows)==18
names={'A':'Grounded Indian Neighborhood','B':'Festival Heavy Block','C':'Balanced Neighborhood Cypher'}
poses=['01-landing','02-lane-walk','03-opening','04-hub','11-overhead','12-mobile-landing']
lookup={(r['variant'],r['camera']):r for r in rows}
comparison=json.loads((O/'evidence/master-comparison.json').read_text());assert comparison['status']=='PASS'
for n in poses:
    r=[lookup[v,n]for v in names]
    for k in ['position','rotationEuler','lens','sensor','cameraType','width','height','samples','engine','exposure']:
        assert r[0][k]==r[1][k]==r[2][k],(n,k)
for r in rows:
    r['masterSHA256']=comparison['revisionSHA256']
    r['sha256']=hashlib.sha256((O/r['file']).read_bytes()).hexdigest()
(O/'evidence/render-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
(O/'evidence/matched-settings.json').write_text(json.dumps({'status':'PASS','views':6,'renders':18,'sameOriginalCameraRig':True,'lightingUnchangedFromOriginalVariant':True,'originalRenderSettingsMatched':True},indent=2)+'\n')
V.mkdir(exist_ok=True)
for n in ['01-landing','03-opening']:
    shutil.copy2(BASE/'renders/C'/(n+'.png'),V/('Before-C-'+n+'.png'))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for v in names:
    sheet=Image.new('RGB',(1440,1500),'#f1ede1');d=ImageDraw.Draw(sheet)
    d.text((24,18),v+' / '+names[v]+' / NO REVEAL COLUMN',font=ImageFont.truetype(bold,25),fill='#213c35')
    for i,n in enumerate(poses):
        x=20+(i%2)*710;y=74+(i//2)*470;im=ImageOps.contain(Image.open(O/lookup[v,n]['file']).convert('RGB'),(680,425))
        sheet.paste(im,(x+(680-im.width)//2,y));d.text((x,y+431),n,font=ImageFont.truetype(font,19),fill='#213c35')
    sheet.save(V/('Contact-'+v+'.jpg'),quality=92)
for n in poses:
    strip=Image.new('RGB',(2400,600),'#f1ede1');d=ImageDraw.Draw(strip)
    for i,v in enumerate(names):
        x=i*800;d.text((x+16,14),v+' / '+names[v],font=ImageFont.truetype(bold,22),fill='#213c35')
        im=ImageOps.contain(Image.open(O/lookup[v,n]['file']).convert('RGB'),(770,500));strip.paste(im,(x+(800-im.width)//2,52))
    strip.save(V/('Matched-'+n+'.jpg'),quality=92)

pdf=V/'Gullyverse-No-Reveal-Column-Review.pdf';c=canvas.Canvas(str(pdf),pagesize=(612,1224));page=0
def header(title,sub='Revision 02 / actual Blender renders / original camera rig'):
    global page
    page+=1;c.setFillColorRGB(.95,.94,.9);c.rect(0,0,612,1224,fill=1,stroke=0)
    c.setFillColorRGB(.12,.23,.2);c.setFont('Helvetica-Bold',11);c.drawString(28,1190,'BREEZE 2027 / GULLYVERSE')
    c.setFont('Helvetica-Bold',18);c.drawString(28,1157,title);c.setFont('Helvetica',10);c.drawString(28,1136,sub)
    c.setFont('Helvetica',8);c.drawString(28,18,f'PRIVATE BLENDER CONCEPT / NO WEBSITE CHANGE / {page}')
def paragraph(s,y,size=11):
    c.setFont('Helvetica',size);line=''
    for word in s.split():
        if c.stringWidth(line+word,'Helvetica',size)>552:c.drawString(28,y,line);y-=size*1.5;line=''
        line+=word+' '
    if line:c.drawString(28,y,line);y-=size*1.5
    return y
def fig(path,x,y,w,h):
    im=Image.open(path).convert('RGB');f=min(w/im.width,h/im.height);buf=io.BytesIO();im.save(buf,format='JPEG',quality=92);buf.seek(0)
    c.drawImage(ImageReader(buf),x+(w-im.width*f)/2,y+(h-im.height*f)/2,width=im.width*f,height=im.height*f)
header('Reveal column removed')
y=paragraph('User correction applied to all A/B/C variants. The large reveal block, its roof, tank and wall-mounted paste-ups are removed. No replacement occluder is added. All other objects, cameras, destination positions and lighting remain unchanged.',1090)
c.setFont('Helvetica-Bold',12);c.drawString(28,1000,'BEFORE / C opening');fig(V/'Before-C-03-opening.png',28,642,556,348)
c.drawString(28,609,'AFTER / C opening / identical pose');fig(O/lookup['C','03-opening']['file'],28,250,556,348)
paragraph('The view toward the rooftop is intentionally more open. The previous screen-hidden-from-landing requirement is superseded by this removal; it is not claimed to still pass.',190)
c.showPage()
header('Open connection / updated plan and section')
fig(V/'master-layout.png',28,443,556,655);fig(V/'access-section.png',28,72,556,334);c.showPage()
for n in poses:
    header(n+' / A-B-C','Same camera and render settings as the previous concept')
    for i,v in enumerate(names):
        yy=760-i*354;c.setFont('Helvetica-Bold',11);c.drawString(28,yy+337,v+' / '+names[v]);fig(O/lookup[v,n]['file'],28,yy,556,325)
    c.showPage()
header('Verification / review boundary');y=1086
survey=json.loads((O/'evidence/concept-feasibility-with-original-reveal-rule.json').read_text())
for s in [
    'Nine objects were removed. All 1,617 remaining objects match the original master snapshots, including surviving mesh coordinates, topology and UVs, camera parameters, light parameters and scene exposure. Three scenes and all 25 packed images remain.',
    'The original reveal-rule survey reports REVIEW_FAILURES because the screen is now visible from the landing: 11/15 rays, compared with the old 0/15. Opening visibility is 14/15 and final screen visibility remains 15/15. This is the direct requested visual change, not a hidden regression or a loosened geometry tolerance.',
    'All original walking-route floor and 0.35m capsule checks still pass. Sampled camera motion remains clear. This is concept validation only; the earlier route-width pinch-point caveats and lack of runtime/device certification still apply.',
    'Shops, signboard, Team/right, Events/left, screen, crowd and routes remain in the same positions. The earlier side route is retained; no broader layout redesign is implied by removing the block.',
    'Eighteen new renders cover six affected views in all three variants. The original master, PDF, renders, animatic and verified checkpoint remain historical evidence. This revision is saved separately and does not overwrite that backup.',
    'This is not selection of A, B or C. Crowd/vehicles/stock remain concept proxies and event posters remain labelled placeholders. No website files, defaults, Git history or deployments changed.'
]:
    y=paragraph(s,y)-28
c.showPage();c.save()
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse / No reveal column</title><style>body{font:16px system-ui;background:#f1ede1;color:#213c35;max-width:1500px;margin:auto;padding:20px}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}img{width:100%}figure{margin:0}section{margin:36px 0}@media(max-width:750px){.row{grid-template-columns:1fr}}</style><h1>No reveal column / revision 02</h1><p>Actual Blender renders. Same original cameras, materials and lighting. Website unchanged.</p><a href="Gullyverse-No-Reveal-Column-Review.pdf">Review PDF</a>']
for n in poses:
    parts.append('<section><h2>'+html.escape(n)+'</h2><div class="row">')
    for v in names:
        r=lookup[v,n];parts.append('<figure><h3>'+v+' / '+names[v]+'</h3><a href="../'+r['file']+'"><img src="../'+r['file']+'" loading="lazy"></a><p>'+str(r['width'])+' x '+str(r['height'])+' / '+str(r['lens'])+'mm</p></figure>')
    parts.append('</div></section>')
(V/'index.html').write_text(''.join(parts))
print('REVISION_REVIEW_COMPLETE',page,'pages',flush=True)
