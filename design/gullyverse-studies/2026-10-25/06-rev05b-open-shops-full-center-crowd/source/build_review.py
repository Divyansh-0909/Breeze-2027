"""Build full and concise review only after all matched captures exist and validate."""
from pathlib import Path
import json,hashlib,sys,io,textwrap,csv,html
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1];R=O/'review';sys.path.insert(0,str(O/'source'))
from diagnostic_cameras import POSES,SHOP_NAMES,SHOP_POSES,CROWD_POSES
rows={}
for f in sorted((O/'evidence').glob('render-manifest*.json')):
    for r in json.loads(f.read_text()):
        p=O/r['file']
        if r['edition']in ['before','after']and p.exists()and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']:rows[r['file']]=r
keys=['position','rotationEuler','lens','sensorWidthMM','cameraType','orthoScale','clipStart','clipEnd','width','height','samples','engine','viewTransform','look','exposure'];pairs=[]
for v in ['A','B','C']:
    for name in POSES:
        a=rows[f'renders/before/{v}/{name}.png'];b=rows[f'renders/after/{v}/{name}.png'];assert all(a[k]==b[k]for k in keys),(v,name)
        assert b['masterSHA256']==hashlib.sha256((O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend').read_bytes()).hexdigest()
        pairs.append((a,b))
assert len(pairs)==75
(O/'evidence/final-render-manifest.json').write_text(json.dumps(list(rows.values()),indent=2)+'\n')
(O/'evidence/matched-render-validation.json').write_text(json.dumps({'status':'PASS','matchedPairs':75,'finalPNGs':150,'identicalFields':keys,'streetAndGlobalLightingIdentical':True,'authorizedException':'Five shadowed 45W interior-only shop area sources in AFTER. They are intentional local additions, not a global lighting/exposure change.','sectionViews':'Camera near-plane cut at local +2.7m, identical before/after; no mesh hidden.','insideViews':'Diagnostic viewpoint; before camera is inside solid host, not a valid historical walking interior.'},indent=2)+'\n')
light=json.loads((O/'evidence/lighting-isolation.json').read_text())
for r in light['captures']:assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
titles={'08-crowd-middle':'Audience at eye height','16-rooftop-plan':'Audience overhead: filled center','19-hub-wide':'Full hub and signboard context','46-left-spillover':'Loose left wing','47-right-spillover':'Loose right wing','48-board-foreground':'Sparse spectators beyond the board','49-center-filled':'Walking approach to dense center','50-mobile-crowd':'Portrait crowd context','01-landing':'Unchanged lane landing','12-mobile-landing':'Portrait lane landing'}
for i,n in enumerate(SHOP_NAMES):
    suffix=['left / Y-25','left / Y-7','left / Y+2','right / Y-16','right / Y-7'][i]
    titles[n]='Shop '+suffix+' / lane view';titles[f'{31+i}-shop-inside-{i+1}']='Shop '+suffix+' / inside diagnostic';titles[f'{41+i}-shop-section-{i+1}']='Shop '+suffix+' / cutaway plan'
W,H=600,960
class PDF:
    def __init__(self,name):self.c=canvas.Canvas(str(R/name),pagesize=(W,H));self.n=0
    def txt(self,s,x,y,size=10,color='#26303a'):
        self.c.setFillColor(color);self.c.setFont('Helvetica',size);self.c.drawString(x,y,s)
    def para(self,s,y,size=11,width=88):
        for line in textwrap.wrap(s,width):self.txt(line,24,y,size);y-=size*1.4
        return y
    def start(self,title,sub=''):
        self.n+=1;self.c.setFillColor('#f3eee3');self.c.rect(0,0,W,H,fill=1,stroke=0);self.txt('BREEZE 2027 / GULLYVERSE / REV05B',24,933,10);self.txt(title,24,907,17)
        if sub:self.para(sub,883,size=9,width=104)
        self.txt(f'25 Oct 2026 | Blender concept | {self.n}',24,16,9)
    def image(self,path,x,y,w,h):
        buf=io.BytesIO();Image.open(path).convert('RGB').save(buf,'JPEG',quality=85,subsampling=1);buf.seek(0);self.c.drawImage(ImageReader(buf),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c')
    def end(self):self.c.showPage()
    def save(self):self.c.save()
def pair(v,n):return next((a,b)for a,b in pairs if a['variant']==v and a['camera']==n)
def caption(n):
    return 'Diagnostic section: camera near clipping cuts above local Z+2.7m; no mesh hidden.'if'section'in n else'Inside inspection: BEFORE is inside the original solid host, not a usable old interior.'if'inside'in n else'Matched pose/lens/exposure/render quality; street/world fixed; local shop light exception documented.'
full=PDF('Gullyverse-Rev05B-Full-Comparisons.pdf')
full.start('Open shops + full-center audience','Implemented private Blender correction. A/B/C remain alternatives; no website changes.')
full.image(O/'renders/after/C/16-rooftop-plan.png',24,450,552,345)
y=full.para('Real cavities in all five open shops. All 45 shelf boards and 180 cartons move together onto interior side walls. Existing counters remain exact. Audience A176 / B184 / C180, with a filled center and a narrow static walking passage.',420)
y=full.para('This full review contains all 75 same-camera pairs (150 final PNGs) across A/B/C. PDF images use compact JPEG embedding; the gallery retains every original full-resolution PNG. Diagrams and light-only diagnostics are labelled separately.',y-18)
full.para('All 960 walk frames per variant retain the existing 0.35m camera and 0.002m floor checks. Two optional shop-side approaches remain blocked by unchanged scooters; each affected shop has a clear other approach. Full failures are retained.',y-18);full.end()
for a,b in pairs:
    v=a['variant'];n=a['camera'];full.start(v+' | '+titles[n],caption(n))
    if'mobile'in n:
        full.txt('REV05A BEFORE',24,822,10);full.txt('REV05B AFTER',310,822,10);full.image(O/a['file'],24,295,268,478);full.image(O/b['file'],308,295,268,478)
    else:
        full.txt('REV05A BEFORE',24,823,10);full.image(O/a['file'],24,465,552,345);full.txt('REV05B AFTER',24,439,10);full.image(O/b['file'],24,82,552,345)
    full.para('Camera poses, source hashes, clipping, samples and PNG hashes: evidence/final-render-manifest.json',51,size=8,width=116);full.end()
full.start('Measured density and footprint checks','Foot centers / 2m cells. Actual body collision checks are independent.');full.image(R/'density-occupancy.png',24,110,552,730);full.end()
for name in ['21-shop-left-25','31-shop-inside-1']:
    full.start('Same geometry | interior lighting only','Only five interior light energies change: 0W versus 45W each. Master not saved in diagnostic state.')
    for y,state in [(466,'off'),(82,'on')]:full.txt('LOCAL INTERIOR LIGHTS '+state.upper(),24,y+350,10);full.image(O/f'renders/lighting-inspection/C/{name}-{state}.png',24,y,552,345)
    full.end()
full.start('Checks and remaining limitations','READY FOR USER VISUAL REVIEW; not final art or browser acceptance.')
y=full.para('PASS: closed manifold cavity/trim topology, positive volumes, nonzero faces, finite UV/tangent data, front/side/floor/ceiling ray normals, stock in bounds, rigid shelf/carton placement and shelf support.',835)
y=full.para('PASS: actual body overlaps, prop overlaps, 960 frames per A/B/C and the protected entry/screen/Team/Events routes. Narrow static path retained; 16/18/16 spectators now occupy the former center gap ahead of the camera endpoint.',y-18)
y=full.para('Counters/DJ furniture, their contents, closed stores, all original cameras/actions/materials/images, world and original street lighting are unchanged. Only authorized local shop geometry, stock, crowd placement, five interior lights and new diagnostics change.',y-18)
y=full.para('Inherited limitation: negative-Y shop approaches at left Y+2 and right Y-7 encounter fixed scooters. Positive-Y approaches pass. The blocked tests remain in the report with object IDs. No scooter or counter has moved.',y-18)
y=full.para('Offline evaluated triangles A83,564 / B86,698 / C84,768; 17 authoring lights versus 12. No new images: 24 packed, 95.86MiB estimated RGBA8+mips. People remain static low-detail proxies. Future web conversion needs instancing/batching and baked interior lighting; no hardware FPS is claimed.',y-18)
full.para('All 1,213 protected WIP files and Git status stay unchanged at e638140b. No commit, push, merge, deployment, next look-dev pilot or A/B/C promotion.',y-18);full.end();full.save()

brief=PDF('Gullyverse-Rev05B-Review.pdf')
brief.start('Five usable open shops + fuller crowd','Rev05B / private Blender layout correction / all A/B/C preserved')
brief.image(O/'renders/after/C/16-rooftop-plan.png',24,470,552,345)
y=brief.para('Crowd center filled beyond the walk endpoint. Sparse people just beyond the board build toward a denser main audience. Outer wings use loose cartesian groups instead of arc tails.',432)
y=brief.para('Five stores now have real 6.2m-wide x 4.4m-deep x 2.85m-high cavities, stock on side walls and exact unchanged counters. The original 3.8m draft failed doorway clearance; the depth was repaired inside existing exterior bounds.',y-17)
brief.para('Actual Blender EEVEE renders. No website changes or final A/B/C choice. The complete 80-page companion and full-resolution gallery show every matched viewpoint.',y-17);brief.end()
for v in ['A','B','C']:
    brief.start(v+' | audience before / after','Same cameras and approved global lighting; all counters and navigation remain fixed.')
    for i,n in enumerate(['16-rooftop-plan','08-crowd-middle','48-board-foreground']):
        y=638-i*244;brief.txt(titles[n],24,y+199,11)
        for x,(r,label)in zip([24,310],[(pair(v,n)[0],'REV05A'),(pair(v,n)[1],'REV05B')]):brief.txt(label,x,y+181,9);brief.image(O/r['file'],x,y,266,167)
    brief.end()
for i,n in enumerate(SHOP_NAMES):
    brief.start('Open shop '+['left Y-25','left Y-7','left Y+2','right Y-16','right Y-7'][i],'C representative; all corresponding A/B/C pairs are in the full companion and PNG gallery.')
    for j,camera in enumerate([n,f'{31+i}-shop-inside-{i+1}',f'{41+i}-shop-section-{i+1}']):
        y=640-j*242;brief.txt(['From lane / counter fixed','Inside diagnostic / side-wall stock','Camera-clipped section / no hidden meshes'][j],24,y+198,10)
        for x,(r,label)in zip([24,310],[(pair('C',camera)[0],'REV05A'),(pair('C',camera)[1],'REV05B')]):brief.txt(label,x,y+179,9);brief.image(O/r['file'],x,y,266,167)
    brief.end()
brief.start('Density and straight route','2m cells; narrow physical clearance ends before the dense center.');brief.image(R/'density-occupancy.png',24,110,552,730);brief.end()
brief.start('Low -> medium -> dense','A176 / B184 / C180. No mirrored permanent crowd halves or animated collision bypass.')
brief.image(R/'density-gradient.png',24,480,552,330)
y=brief.para('Six sparse board-zone people, fourteen transition people, thirty-six mid-zone people, ninety-two dense shared viewers and fourteen people in each irregular wing. B has eight extra dense viewers; C has four.',435)
brief.para('The static camera passage has body bounds at least 0.45m from X=0 until Y36.95. The exact straight action stops at Y36.5; people can occupy the full center beyond that point. Existing 0.35m camera tolerance is unchanged.',y-17);brief.end()
brief.start('Local shop light exception','Same final geometry, exposure, camera and samples. Original street/global lights untouched.')
for y,state in [(466,'off'),(82,'on')]:brief.txt('INTERIOR SUPPORT '+state.upper(),24,y+350,10);brief.image(O/f'renders/lighting-inspection/C/21-shop-left-25-{state}.png',24,y,552,345)
brief.end()
brief.start('Checks, costs and inherited limits','Every open shop has at least one tested clear approach; all failures are disclosed.')
y=brief.para('All 225 stock objects remain complete and are visible from the union of tested lane angles. Real closed cavity/trim surfaces pass manifold, UV, tangent and facing-normal checks. All counters, DJ furniture and closed shops have exact preservation proofs.',835)
y=brief.para('All 960 walk frames in A/B/C pass the original camera/floor checks. Actual full-body and person/prop overlaps are zero. Main nav raster rays from landing/arrival cameras are not newly occluded by crowd.',y-18)
y=brief.para('Negative-Y approaches at left Y+2 and right Y-7 are blocked by inherited scooters. Positive-Y approaches pass. Scooter/counter positions remain locked. Shop thresholds follow existing differing lane elevations; these are concept clearances, not accessibility certification.',y-18)
y=brief.para('Evaluated triangles: A73,624 -> 83,564; B76,758 -> 86,698; C74,828 -> 84,768. Add 32 linked proxy actors / 256 parts and five interior lights. No new textures; authoring image estimate remains 95.86MiB. Software-render times are not web FPS or physical-GPU acceptance.',y-18)
brief.para('Static proxy silhouettes, matte blockout surfaces and inherited signage limits remain. No photoreal/final-production claim or A/B/C selection. Further look-dev requires separate visual approval.',y-18);brief.end()
brief.start('Review, restore and next decision','No automatic next phase or website promotion.')
y=brief.para('The complete matched comparison PDF and GALLERY.html contain all 150 final PNGs, including all three angles for all five shops in every A/B/C scene. Diagnostic images and density plots are labelled separately.',835)
y=brief.para('The new checkpoint includes the packed editable Rev05B master, exact Rev05A input, deterministic authoring scripts, provenance/license references, technical tests, per-member hashes and restore instructions. Source opens independently from earlier website backups.',y-18)
y=brief.para('Archive sizes/SHA-256, authenticated download-back checks and independent restored-master open proof are recorded in the external verification receipt alongside the archives. Previous Rev05A and Rev04 backups remain untouched.',y-18)
brief.para('Stop for user review of crowd fullness, shop organization and overall A/B/C direction. Do not infer approval for full look-dev, website changes, commits or deployment.',y-18);brief.end();brief.save()

font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
for name,cam in [('Crowd-Center-Comparison.jpg','16-rooftop-plan'),('Crowd-Eye-Comparison.jpg','08-crowd-middle'),('Open-Shop-Comparison.jpg','21-shop-left-25')]:
    im=Image.new('RGB',(1200,1600),'#eee8dd');draw=ImageDraw.Draw(im)
    for yy,(r,label)in zip([65,860],[(pair('C',cam)[0],'REV05A BEFORE'),(pair('C',cam)[1],'REV05B AFTER')]):
        s=Image.open(O/r['file']).convert('RGB');s.thumbnail((1200,720));im.paste(s,((1200-s.width)//2,yy));draw.text((20,yy-43),label,font=font,fill='#20252a')
    draw.text((20,1555),'Actual Blender concept; counter and straight action preserved.',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20),fill='#20252a');im.save(R/name,quality=91)
parts=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse Rev05B</title><style>body{font:17px system-ui;max-width:1400px;margin:auto;padding:22px;background:#f3eee3;color:#26303a}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{max-width:100%;height:auto}article{margin:34px 0}figure{margin:0}.note{padding:18px;background:#dedfc8}@media(max-width:700px){.pair{grid-template-columns:1fr}}</style></head><body><h1>Rev05B: real open shops + filled crowd center</h1><p class="note">Actual Blender EEVEE concept evidence. A/B/C remain unselected. The website is unchanged. Two inherited scooter-side approaches remain blocked; each shop has another tested clear entry.</p><p><a href="review/Gullyverse-Rev05B-Review.pdf">Concise phone review</a> · <a href="review/Gullyverse-Rev05B-Full-Comparisons.pdf">Every matched screenshot</a> · <a href="REPORT.md">Technical report</a> · <a href="RESTORE.md">Restore</a></p>']
for v in ['A','B','C']:
    parts.append(f'<h2>{v} / matched Rev05A versus Rev05B</h2>')
    for n in CROWD_POSES+SHOP_POSES:
        a,b=pair(v,n);parts.append(f'<article><h3>{html.escape(titles[n])}</h3><p>{caption(n)}</p><div class="pair">')
        for r,label in [(a,'Rev05A before'),(b,'Rev05B after')]:parts.append(f'<figure><figcaption>{label}</figcaption><a href="{r["file"]}"><img loading="lazy" src="{r["file"]}" alt="{v} {label} {n}"></a></figure>')
        parts.append('</div></article>')
parts.append('<h2>Measured diagrams</h2><img loading="lazy" src="review/density-occupancy.png"><img loading="lazy" src="review/density-gradient.png"><h2>Light-only inspection, final geometry</h2>')
for n in ['21-shop-left-25','31-shop-inside-1']:
    parts.append('<div class="pair">')
    for state in ['off','on']:parts.append(f'<figure><figcaption>Interior light {state}; geometry unchanged</figcaption><img loading="lazy" src="renders/lighting-inspection/C/{n}-{state}.png"></figure>')
    parts.append('</div>')
parts.append('<p>Rejected draft captures and tightly cropped earlier section diagnostics are retained in the technical evidence, excluded from the final comparisons. Pixel/source hashes and camera settings are in evidence/final-render-manifest.json.</p></body></html>');(O/'GALLERY.html').write_text('\n'.join(parts))
(O/'evidence/review-build.json').write_text(json.dumps({'status':'PASS','fullPDFPages':full.n,'concisePDFPages':brief.n,'matchedPairs':75,'fullResolutionFinalPNGs':150,'lightingOnlyDiagnostics':4},indent=2)+'\n')
print('REVIEW_BUILT',full.n,'full pages,',brief.n,'concise pages, 75 pairs',flush=True)
