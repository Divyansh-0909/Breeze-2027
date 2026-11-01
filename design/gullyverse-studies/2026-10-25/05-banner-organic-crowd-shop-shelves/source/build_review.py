"""Assemble review of implemented banner/crowd changes; shop exception remains pending."""
from pathlib import Path
import json, hashlib, html, csv, shutil, statistics, io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1]; R=O/'review'
rows=json.loads((O/'evidence/render-manifest.json').read_text())
pairs=[];keys=['position','rotationEuler','lens','sensorWidthMM','cameraType','width','height','samples','engine','exposure']
for row in rows:
    assert hashlib.sha256((O/row['file']).read_bytes()).hexdigest()==row['sha256']
    if row['edition']!='after': continue
    before=next(r for r in rows if r['edition']=='before' and r['variant']==row['variant'] and r['camera']==row['camera'])
    assert all(before[k]==row[k] for k in keys),(row['variant'],row['camera'])
    pairs.append((before,row))
assert len(pairs)==21
matched={'status':'PASS','pairs':21,'verifiedIdenticalFields':keys,'beforeCaptures':36,'afterCaptures':21,'supplementaryPreviewCaptures':1,'shopAfterCaptures':0,'shelfStatus':'PENDING_USER_ARCHITECTURE_EXCEPTION','renderSource':'Actual Blender 4.3.2 EEVEE software-rendered concept, not browser images','pairs':[{'variant':a['variant'],'camera':a['camera'],'before':a['file'],'after':b['file']}for a,b in pairs]}
(O/'evidence/matched-render-validation.json').write_text(json.dumps(matched,indent=2)+'\n')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(size):return ImageFont.truetype(font,size)
def comparison(name,variant,camera):
    out=Image.new('RGB',(1200,1580),'#eee9de');d=ImageDraw.Draw(out)
    for y,edition in [(70,'before'),(850,'after')]:
        image=Image.open(O/'renders'/edition/variant/(camera+'.png')).convert('RGB');image.thumbnail((1200,710));out.paste(image,((1200-image.width)//2,y))
        d.text((24,y-48),f'{variant} / {edition.upper()} / {camera}',font=f(28),fill='#20252a')
    d.text((24,1540),'Actual Blender concept. Shelves unchanged; exception pending.',font=f(21),fill='#57251e')
    out.save(R/name,quality=91)
comparison('B-Banner-Removed.jpg','B','17-banner-frontal')
comparison('C-Organic-Audience.jpg','C','08-crowd-middle')
comparison('C-Audience-Plan.jpg','C','16-rooftop-plan')

dens=json.loads((O/'evidence/audience-density-table.json').read_text())
budget=json.loads((O/'evidence/scene-budget-final.json').read_text())
base_tri={'A':44824,'B':47960,'C':46028}
with (O/'evidence/audience-cost-and-density.csv').open('w',newline='')as h:
    w=csv.writer(h);w.writerow(['variant','audience_before','audience_after','triangles_before','triangles_after','triangle_delta','occupied_2m_cells_before','occupied_2m_cells_after','max_people_per_4m2_after','central_body_clear_width_m'])
    for d,s in zip(dens['variants'],budget['scenes']):
        v=d['variant'];w.writerow([v,d['before']['actors'],d['after']['actors'],base_tri[v],s['evaluatedMeshAndCurveTriangles'],s['evaluatedMeshAndCurveTriangles']-base_tri[v],d['before']['occupied2mCells'],d['after']['occupied2mCells'],d['after']['maxActorsIn2mCell'],3.3])

titles={'17-banner-frontal':'Banner: frontal inspection','18-banner-oblique':'Banner: oblique inspection','08-crowd-middle':'Audience: human-eye view','16-rooftop-plan':'Audience: overhead plan','19-hub-wide':'Hub / rooftop wide context','01-landing':'Lane landing / straight route','12-mobile-landing':'Mobile-aspect lane','21-shop-left-25':'Open shop left / Y -25','22-shop-left-7':'Open shop left / Y -7','23-shop-left2':'Open shop left / Y +2','24-shop-right-16':'Open shop right / Y -16','25-shop-right-7':'Open shop right / Y -7'}
order=['17-banner-frontal','18-banner-oblique','08-crowd-middle','16-rooftop-plan','19-hub-wide','01-landing','12-mobile-landing']
shoporder=[k for k in titles if k.startswith(('21','22','23','24','25'))]
W,H=600,960
c=canvas.Canvas(str(R/'Gullyverse-Rev05A-Banner-Crowd-Pending-Shops.pdf'),pagesize=(W,H));page=0
def text(s,x,y,size=11,color='#20252a'):
    c.setFillColor(color);c.setFont('Helvetica',size);c.drawString(x,y,s)
def paragraph(s,y,width=89,size=11):
    import textwrap
    for line in textwrap.wrap(s,width):text(line,24,y,size);y-=size*1.45
    return y
def image(path,x,y,w,h):
    # PDF uses high-quality JPEG embedding; untouched full-resolution PNGs remain in the gallery.
    buf=io.BytesIO();Image.open(path).convert('RGB').save(buf,format='JPEG',quality=91,subsampling=0);buf.seek(0)
    c.drawImage(ImageReader(buf),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c')
def start(title,subtitle=''):
    global page
    page+=1;c.setFillColor('#f2eee5');c.rect(0,0,W,H,fill=1,stroke=0)
    text('BREEZE 2027 / GULLYVERSE',24,930,11)
    text(title,24,902,18)
    if subtitle:paragraph(subtitle,878,size=10)
    text(f'25 Oct 2026 | Rev05A | {page}',24,16,9)
def end():c.showPage()
start('Banner + organic audience','PARTIAL: shelf relocation blocked by locked solid shop architecture.')
image(O/'renders/after/C/16-rooftop-plan.png',24,455,552,345)
y=paragraph('Implemented: only the large red rooftop banner is removed; a fuller, seeded, casually clustered semicircular audience replaces the exact arcs. A/B/C remain separate and unselected.',422)
y=paragraph('Counts: A 48 -> 144, B 56 -> 152, C 52 -> 148. The 3.3m clear central aisle and original 40-second straight camera action are preserved.',y-14)
y=paragraph('Shops: the five open fronts are solid cuboids without interiors. Moving stock inside would hide it in masonry. No shelf or building change has been applied while approval for narrow interior recesses is pending. All five counters and the DJ table remain exact.',y-14)
paragraph('These are actual Blender EEVEE concept renders. The live website and WIP source are unchanged. This is not production art acceptance or hardware performance certification.',y-14)
end()
for variant in ['A','B','C']:
    for camera in order:
        before,after=next((a,b)for a,b in pairs if a['variant']==variant and a['camera']==camera)
        start(f'{variant} | {titles[camera]}','Identical pose, lens, dimensions, samples, exposure, world and lights. Shelves unchanged.')
        if 'mobile'in camera:
            text('REV04 BEFORE',28,819,11);text('REV05A AFTER',310,819,11)
            image(O/before['file'],24,300,268,478);image(O/after['file'],308,300,268,478)
        else:
            text('REV04 BEFORE',24,820,11);image(O/before['file'],24,464,552,345)
            text('REV05A AFTER - banner/crowd only',24,439,11);image(O/after['file'],24,82,552,345)
        paragraph('Full-resolution PNGs and exact camera metadata are in GALLERY.html and evidence/render-manifest.json.',52,size=9)
        end()
start('Density and occupancy','2m cells (4m2) are foot-center occupancy only; actual bodies are checked independently.')
image(R/'density-occupancy.png',24,155,552,706)
paragraph('After counts A144/B152/C148. Occupied cells A63/B64/C63; maximum 6 people per 4m2 cell. This is a spatial measure, not a visual realism score.',107,size=10);end()
start('Shop exception: concrete proposal','NOT IMPLEMENTED. Sections 4-5 lock storefront architecture and all other geometry.')
image(R/'shop-interior-exception-proposal.png',24,350,552,460)
y=paragraph('Each of five solid blocks needs a local cavity: depth 3.8m, opening width 6.2m, height 2.85m. Proposed shelves and their merchandise rotate together to both interior side walls. Exterior building dimensions, signs, shutters and counters stay fixed.',315)
y=paragraph('Only unlinked diagnostic copies have been topology-tested. The delivered Rev05A master retains the original solid blocks and all original stock placement. The guarded prepare_shop_interior.py must not be executed without approval.',y-14)
paragraph('Requested exception: allow these five small interior recesses behind the existing open-shop fronts. If architecture must stay unchanged, the side-wall-stock requirement cannot be met visibly.',y-14);end()
for variant in ['A','B','C']:
    start(f'{variant} | all five open shops','Current / unchanged shop frontage. No after-relocation claim; exception pending.')
    for n,camera in enumerate(shoporder):
        y=674-n*151;text(titles[camera],24,y+143,10)
        image(O/'renders/before'/variant/(camera+'.png'),24,y,552,132)
    end()
start('Checks, costs and remaining work','Banner and crowd correction validated. Overall prompt remains incomplete.')
y=paragraph('PASS: all 960 walk frames in each variant; X=0, monotonic Y, eye-height tolerance 0.002m, original 0.35m camera checks; straight entry/screen, Team-right and Events-left routes.',836)
y=paragraph('PASS: 156 actor instances / 1,248 body parts across all variants combined; 12,090 actor pairs, zero triangle overlaps; zero crowd/prop triangle overlaps. Conservative projected-body footprints keep the central aisle clear.',y-16)
y=paragraph('PASS: only the targeted banner is removed. All original non-target geometry, UVs, materials, lights, world, cameras, counters/tables and 40-second action are preserved. 768 linked new body-part instances, 480 old body-part transforms changed.',y-16)
for d,s in zip(dens['variants'],budget['scenes']):
    v=d['variant'];y=paragraph(f"{v}: audience {d['before']['actors']} -> {d['after']['actors']}; evaluated triangles {base_tri[v]:,} -> {s['evaluatedMeshAndCurveTriangles']:,}; 12 authoring lights unchanged.",y-12)
y=paragraph('24 unique packed images, 95.86MiB estimated RGBA8+mips authoring payload, unchanged. People remain simple static proxy meshes with only three inherited gesture templates. No runtime GLB, website performance, animated crowd, hardware FPS or new video-playback verification is claimed.',y-16)
y=paragraph('All 1,213 protected WIP files and Git status remain unchanged at e638140b37045a805b23b4d406d387a8870f8486. No commit, push, merge or deployment. Prior checkpoints retained.',y-16)
paragraph('Next action requires only the narrow shop-interior geometry exception. A/B/C aesthetic selection and any high-fidelity look-dev remain separate user decisions.',y-16);end()
c.save()
(O/'evidence/review-build.json').write_text(json.dumps({'pages':page,'renderedPNGCount':58,'matchedPairs':21,'shopViewsBeforeOnly':15,'status':'PARTIAL_SHOP_EXCEPTION_PENDING'},indent=2)+'\n')

parts=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Gullyverse Rev05A</title><style>body{font:17px system-ui;max-width:1400px;margin:auto;padding:22px;background:#f2eee5;color:#20252a} .pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{max-width:100%;height:auto}article{margin:35px 0}figure{margin:0}small{color:#555}.pending{padding:20px;background:#ffe6bf}a{color:#204d79}@media(max-width:700px){.pair{grid-template-columns:1fr}}</style></head><body><h1>Gullyverse Rev05A: banner + organic audience</h1><p class="pending">PARTIAL — shop-interior exception pending. Stock and building meshes are unchanged. This is actual Blender concept evidence; the website is untouched.</p><p><a href="review/Gullyverse-Rev05A-Banner-Crowd-Pending-Shops.pdf">Phone-friendly comparison PDF</a> · <a href="REPORT.md">Technical report</a> · <a href="RESTORE.md">Restoration instructions</a> · <a href="evidence/render-manifest.json">Camera/render metadata</a></p>']
for variant in ['A','B','C']:
    parts.append(f'<h2>{variant} — matched comparisons</h2>')
    for camera in order:
        a,b=next((a,b)for a,b in pairs if a['variant']==variant and a['camera']==camera)
        parts.append(f'<article><h3>{html.escape(titles[camera])}</h3><div class="pair">')
        for r,label in [(a,'Rev04 before'),(b,'Rev05A banner/crowd after')]:
            parts.append(f'<figure><figcaption>{label}</figcaption><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{variant} {label} {camera}"></a></figure>')
        parts.append('</div></article>')
    parts.append('<h3>Five open shops: unchanged / pending relocation</h3><div class="pair">')
    for camera in shoporder:
        path=f'renders/before/{variant}/{camera}.png';parts.append(f'<figure><figcaption>{titles[camera]} — before / unchanged</figcaption><a href="{path}"><img loading="lazy" src="{path}"></a></figure>')
    parts.append('</div>')
parts+=['<h2>Measurements and conditional shop proposal</h2><p>Measured diagrams, not rendered implementations.</p><img loading="lazy" src="review/density-occupancy.png"><img loading="lazy" src="review/shop-interior-exception-proposal.png">','<h2>Supplementary high-angle audience inspection</h2><p>Not a matched pair.</p><img loading="lazy" src="renders/preview/C/15-semicircle-high.png">','<footer>Full resolution: desktop 1200×750, mobile 540×960. Blender 4.3.2 / EEVEE / 16 samples / original exposure. No A/B/C selection or final visual acceptance is assumed.</footer></body></html>']
(O/'GALLERY.html').write_text('\n'.join(parts))
print('REVIEW_BUILT',page,'pages',len(rows),'raw renders; 21 matched pairs')
