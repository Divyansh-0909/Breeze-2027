from pathlib import Path
import json,html,re,hashlib,shutil
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
ROOT=Path.cwd();R=ROOT/'reports/recovery-phase3-c9-2026-10-19';CACHE=R/'.pdf-cache';CACHE.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ReviewBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
groups={label:json.loads((R/'raw'/f'{label}-captures.json').read_text())for label in ['c51','c8-3x','c9']}
matched=json.loads((R/'matched-pose-verification.json').read_text());assert matched['status']=='PASS'
names={'c51':'Protected C5.1','c8-3x':'Recovered C8 · approved 3×','c9':'Recovered C9 · native 0.9× / C8 3×'}
by={label:{Path(c['file']).name:c for c in data['captures']}for label,data in groups.items()}
historical=json.loads((R/'references/historical-image-index.json').read_text())
for name in ['quarry-open-sky-geometry.jpeg','quarry-warm-dappled-light.jpeg']:
 shutil.copyfile(ROOT/'design/references/03-open-roof-quarry'/name,R/'references'/name)

def jpg(path):
 path=Path(path);key=hashlib.sha256(path.read_bytes()).hexdigest()[:20];p=CACHE/(key+'.jpg')
 if not p.exists():
  im=Image.open(path).convert('RGB');im.thumbnail((1500,1500));im.save(p,quality=87,optimize=True)
 return ImageReader(str(p))
def text(c,value,x,y,size=10,width=540,leading=None,bold=False):
 c.setFont('ReviewBold'if bold else'Review',size);leading=leading or size*1.5
 words=str(value).split();line=''
 for word in words:
  new=(line+' '+word).strip()
  if pdfmetrics.stringWidth(new,'ReviewBold'if bold else'Review',size)>width and line:
   c.drawString(x,y,line);y-=leading;line=word
  else:line=new
 if line:c.drawString(x,y,line);y-=leading
 return y
def draw(c,path,x,y,w,h):
 im=Image.open(path);scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
 c.drawImage(jpg(path),x+(w-iw)/2,y+(h-ih)/2,width=iw,height=ih)
def head(c,title,subtitle='',height=900):
 c.setFillColorRGB(.12,.17,.15);c.rect(0,height-75,612,75,fill=1,stroke=0);c.setFillColorRGB(1,1,1)
 text(c,title,30,height-30,15,bold=True);text(c,subtitle,30,height-55,8.5,width=552)
 c.setFillColorRGB(.12,.15,.14)
def foot(c,n,height=900):
 c.setFillColorRGB(.36,.4,.38);text(c,f'BREEZE 2027 / GULLYVERSE · private recovery review · {n}',30,22,8)
def single(c,record,label,n,height=810):
 head(c,record['title'],label,height);draw(c,R/record['file'],30,140,552,height-235)
 camera=record['data']['camera'];meta=f"Camera [{camera['x']:.3f}, {camera['y']:.3f}, {camera['z']:.3f}] · yaw {camera['yaw']:.6f} · pitch {camera['pitch']:.6f} · FOV {camera['fov']:.3f} · DPR {record['canvas']['effectiveDpr']} · Q{record['data']['snapshot']['quality']}"
 text(c,meta,30,117,8.5,width=552);text(c,record['note'],30,82,9,width=552);foot(c,n,height);c.showPage()

full=canvas.Canvas(str(R/'Gullyverse-Recovery-Phase3-C9-Full-Screenshots.pdf'),pagesize=(612,810));n=1
head(full,'Recovery Phase 3 · full screenshot evidence',f"{matched['images']} matched runtime PNGs + separately labelled historical/context diagnostics",810)
draw(full,R/by['c9']['desktop-visitor-1.png']['file'],30,290,552,385)
text(full,'C9 is selected by the user. This is a private reconstruction on surviving C5.1, not an identical restoration of the lost C6.2 host.',30,260,11)
text(full,'Current comparisons: identical pose, FOV, lights, viewport, actual DPR1 and Q0. Historical PDF panels are reference-aligned and retain their original compression. Seven inherited visibility hits remain. Real hardware acceptance is pending.',30,190,10)
text(full,'No Stage 3A reconstruction, public promotion, commit, push, merge or deployment.',30,100,10,bold=True);foot(full,n,810);full.showPage();n+=1
for label,data in groups.items():
 for record in data['captures']:single(full,record,names[label],n);n+=1
for item in historical:
 head(full,f"Historical {item['series'].upper()} · PDF page {item['page']}",'Original embedded PDF image, not a new renderer capture',810)
 draw(full,R/item['file'],30,140,552,565);text(full,item['caption'][:420],30,117,9,width=552);foot(full,n,810);full.showPage();n+=1
extra_path=R/'raw/inspection-captures.json';extras=json.loads(extra_path.read_text()).get('captures',[])if extra_path.exists()else[]
for record in extras:
 head(full,record['title'],record['note'],810);draw(full,R/record['file'],30,120,552,580);foot(full,n,810);full.showPage();n+=1
full.save();full_pages=n-1

short=canvas.Canvas(str(R/'Gullyverse-Recovery-Phase3-C9-Review.pdf'),pagesize=(612,936));n=1
head(short,'Selected C9 · recovery review','Native-scale scanned rock 0.9× · approved C8 material 3×',936)
draw(short,R/by['c9']['desktop-visitor-1.png']['file'],30,430,552,400)
y=text(short,'READY FOR VISUAL REVIEW',30,397,16,bold=True)
y=text(short,'One bounded native scan is integrated into the surviving continuous quarry. The public C5.1 baseline, lighting, layout and stage remain unchanged.',30,y-10,11)
y=text(short,'Important differences: the lost C6.2 host is not recreated, the crop/joins are reconstructed, neighbouring walls remain smoother and some joins still look faceted. Seven inherited visibility hits remain unresolved.',30,y-12,11)
text(short,'Read the technical report for measured costs, tests and backup restoration. All source PNGs and exact camera metadata are in the gallery. PDFs compress screenshots for phone viewing; no colour grading is applied.',30,165,10)
foot(short,n,936);short.showPage();n+=1
for page,mode,current in [(6,'c8','c8-3x'),(2,'c9','c9'),(5,'c9','c9')]:
 h=next(x for x in historical if x['series']==mode and x['page']==page)
 name='desktop-visitor-1.png'if page in [6,2]else'desktop-medium-inspection.png';current_record=by[current][name]
 head(short,'Historical evidence / reconstruction',f"Original {mode.upper()} PDF page {page}; historical C9 pose is reference-aligned, not certified identical",936)
 text(short,'Historical reference',30,842,10,bold=True);draw(short,R/h['file'],30,480,552,350)
 text(short,'Current reconstruction under approved dusk',30,458,10,bold=True);draw(short,R/current_record['file'],30,95,552,350)
 text(short,'Original PDF image bytes retained; missing old host/mask/crop data prevent a pixel-identical claim.',30,67,8.5);foot(short,n,936);short.showPage();n+=1
selected=['desktop-visitor-1.png','desktop-medium-inspection.png','desktop-close-rock.png','desktop-along-wall.png','desktop-scan-left-join.png','desktop-scan-right-join.png','desktop-wall-foot.png','desktop-upper-rim.png','desktop-neutral-material.png','desktop-neutral-geometry.png','desktop-hub-scaffold.png','desktop-historical-tunnel.png','desktop-behind-left-stalls.png','desktop-aerial-map.png']
for name in selected:
 a,b=by['c8-3x'][name],by['c9'][name];head(short,b['title'],'Matched current C8 / C9 · approved dusk unless explicitly diagnostic',936)
 text(short,names['c8-3x'],30,842,10,bold=True);draw(short,R/a['file'],30,480,552,350)
 text(short,names['c9'],30,458,10,bold=True);draw(short,R/b['file'],30,95,552,350)
 text(short,b['note'],30,67,8.5);foot(short,n,936);short.showPage();n+=1
for name in ['mobile-visitor-1.png','mobile-aerial-map.png']:
 record=by['c9'][name];single(short,record,names['c9']+' · portrait emulation, not hardware acceptance',n,936);n+=1
head(short,'What remains / review decision','Selected C9 direction preserved; no quarry-wide rollout',936)
y=827
for paragraph in ['The new geometry preserves native geological proportions and physical depth without the C6.2 width stretching. Compare the geometry-only page before judging the fine texture.',
 'C5.1 around the crop is smoother than the historical C6.2 host. Colour and grain change at some joins; coastal scallops differ from the angular quarry photographs. These are visible limitations, not hidden engineering successes.',
 'Two of the three requested public viewpoints are stall-occluded. The first is the useful unoccluded visitor-distance comparison. Close inspection cameras do not establish ordinary visitor quality by themselves.',
 'Candidate geometry/UV/tangent/border checks pass. Full-scene visibility remains FAIL_INHERITED for seven unchanged-surface hits. Actual physical laptop/phone performance is pending.',
 'The technical report and complete gallery contain source provenance, exact dimensions, all comparison metadata, loading/frame-time measurements and lifecycle assertions. The Drive checkpoint includes an independently restorable Phase3 overlay on protected Phase1+2.',
 'Stop for user visual review. Stage3A, further quarry sectors, public-default changes and deployment are outside this recovery phase.']:
 y=text(short,paragraph,30,y,11,width=552)-22
foot(short,n,936);short.showPage();short.save();short_pages=n

# Portable technical-report PDF; source Markdown remains the authoritative text.
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyReview',fontName='Review',fontSize=9,leading=13,spaceAfter=7));styles.add(ParagraphStyle(name='HeadReview',fontName='ReviewBold',fontSize=14,leading=19,spaceBefore=12,spaceAfter=8))
story=[]
for line in (ROOT/'docs/gullyverse-recovery-phase3-c9-composition.md').read_text().splitlines():
 if not line.strip():continue
 if line.startswith('```'):continue
 clean=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',line);clean=clean.replace('**','').replace('`','')
 if line.startswith('#'):story.append(Paragraph(html.escape(clean.lstrip('# ')),styles['HeadReview']))
 elif line.startswith('|'):
  if set(clean)-set('| :-'):
   story.append(Paragraph(html.escape(clean),styles['BodyReview']))
 else:story.append(Paragraph(html.escape(clean),styles['BodyReview']))
SimpleDocTemplate(str(R/'Gullyverse-Recovery-Phase3-C9-Technical-Report.pdf'),pagesize=(612,810),rightMargin=32,leftMargin=32,topMargin=35,bottomMargin=35).build(story)

cards=[]
for name in by['c9']:
 record=by['c9'][name];sections=[]
 for label in groups:
  c=by[label][name];meta={'camera':c['data']['camera'],'actualDPR':c['canvas']['effectiveDpr'],'quality':c['data']['snapshot']['quality'],'lighting':c['lighting'],'build':matched['build']}
  sections.append(f'<figure data-mode="{label}"><figcaption>{html.escape(names[label])}</figcaption><a href="{c["file"]}"><img loading="lazy" src="{c["file"]}" alt="{html.escape(c["title"])}"></a><details><summary>Camera / render metadata</summary><pre>{html.escape(json.dumps(meta,indent=2))}</pre></details></figure>')
 cards.append(f'<section><h2>{html.escape(record["title"])}</h2><p>{html.escape(record["note"])}</p><div class="compare">'+''.join(sections)+'</div></section>')
hist=''.join(f'<figure><figcaption>Historical {h["series"].upper()} · PDF page {h["page"]} · {h["width"]}×{h["height"]}</figcaption><a href="{h["file"]}"><img loading="lazy" src="{h["file"]}" alt="Original historical evidence"></a></figure>'for h in historical)
extra=''.join(f'<figure><figcaption>{html.escape(c["title"])} · {html.escape(c["note"])}</figcaption><a href="{c["file"]}"><img loading="lazy" src="{c["file"]}" alt="Browser diagnostic"></a></figure>'for c in extras)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse / recovered C9 review</title><style>body{margin:0;background:#101613;color:#e4e9e6;font:16px/1.55 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:24px}h1{font-size:clamp(28px,4vw,48px);line-height:1.12}h2{font-size:22px;margin-bottom:6px}a{color:#c5e0d0}section{border-top:1px solid #43564a;margin-top:30px;padding-top:12px}.compare{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}figure{margin:8px 0;background:#1b261f;padding:10px;border-radius:8px}figcaption{font-size:14px;margin-bottom:8px}img{display:block;width:100%;height:auto;max-height:700px;object-fit:contain;background:#080d0a}pre{overflow:auto;max-height:300px;font-size:11px}.notice{padding:16px;border-left:4px solid #c1a76f;background:#25271d}.links{display:flex;gap:16px;flex-wrap:wrap}button{padding:9px;background:#344d3e;color:white;border:1px solid #718677;border-radius:4px;cursor:pointer}@media(max-width:850px){.compare{grid-template-columns:1fr}main{padding:16px}}</style><main><p>BREEZE 2027 / GULLYVERSE · RECOVERY PHASE 3</p><h1>Selected C9<br>native scanned-rock composition</h1><p class="notice">Private reconstruction: native geometry 0.9×, approved C8 material 3×. The lost C6.2 host, exact crop and mask are not claimed identical. Seven inherited visibility hits remain. Physical hardware acceptance is pending. No Stage3A, public promotion or deployment.</p><nav class="links"><a href="Gullyverse-Recovery-Phase3-C9-Review.pdf">Phone review PDF</a><a href="Gullyverse-Recovery-Phase3-C9-Full-Screenshots.pdf">Full screenshot PDF</a><a href="Gullyverse-Recovery-Phase3-C9-Technical-Report.pdf">Technical report</a><a href="matched-pose-verification.json">Matched metadata</a><a href="videos/visitor-journey.mp4">Visitor journey</a><a href="videos/automatic-lod-inspection.mp4">Automatic LOD inspection</a></nav><p>Tap an image for its original full-resolution PNG. Current mode comparisons have identical actual pose, FOV, lighting, viewport, quality and DPR. Historical images are original embedded PDF bytes with their source page identified.</p>'''+''.join(cards)+'<section><h2>Historical references</h2><p>Reference-aligned comparisons, not a pixel-identical restoration claim. Earlier C8 verdicts are superseded by the user’s later 3× and C9 choices.</p><div class="compare">'+hist+'</div></section><section><h2>Separate runtime diagnostics / context</h2><div class="compare">'+extra+'</div></section></main></html>'
(R/'gallery.html').write_text(page)
(R/'review-package.json').write_text(json.dumps({'status':'PASS','build':matched['build'],'finalMatchedImages':matched['images'],'historicalEmbeddedImages':len(historical),'additionalDiagnostics':len(extras),'phoneReviewPages':short_pages,'fullScreenshotPages':full_pages,'PDFCompression':'JPEG quality87 derivatives, no colour grading; original PNGs retained unchanged','selfContainedReview':'Extract all C-review parts together; gallery and report PDF use relative links. Technical/source restoration additionally needs A/B and protected Phase1+2.'},indent=2)+'\n')
print('ASSEMBLED',short_pages,'phone pages;',full_pages,'full screenshot pages')
