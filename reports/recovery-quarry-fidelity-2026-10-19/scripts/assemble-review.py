"""Portable gallery and PDFs from untouched browser images, with honest history labels."""
from pathlib import Path
import json,html,hashlib,re,csv
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,LongTable,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19';CACHE=R/'.pdf-cache';CACHE.mkdir(exist_ok=True)
labels=['c51','c8','recovered','material','corrected']
names={'c51':'Protected C5.1 / unchanged public','c8':'Recovered C8 / approved 3x scale','recovered':'Rejected recovered C9','material':'Corrected material coverage / same C5.1 mesh','corrected':'Corrected C9 geological composition'}
groups={k:json.loads((R/'raw'/f'{k}-captures.json').read_text())for k in labels}
assert all(g['status']=='PASS'for g in groups.values())
by={k:{Path(c['file']).name:c for c in g['captures']}for k,g in groups.items()}
checks=[]
for name,c in by['corrected'].items():
 for k in labels:
  a=by[k][name]
  checks.append({'file':name,'mode':k,'matched':a['data']['camera']==c['data']['camera']and a['canvas']==c['canvas']and a['lighting']==c['lighting']and a['data']['snapshot']['quality']==c['data']['snapshot']['quality']})
assert all(c['matched']for c in checks),'Actual camera/DPR/quality mismatch'
matched={'status':'PASS','build':groups['corrected']['build'],'currentImages':sum(len(g['captures'])for g in groups.values()),'posesPerMode':len(by['corrected']),'comparisons':checks,'historicalClaim':'Reference-aligned only; original camera metadata incomplete. Exact matches apply to five freshly captured runtime modes, not historical renders.'}
(R/'matched-pose-verification.json').write_text(json.dumps(matched,indent=2)+'\n')
history=json.loads((R/'references/historical-image-index.json').read_text())
pdfmetrics.registerFont(TTFont('R','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('B','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
def text(c,s,x,y,size=10,w=552,bold=False):
 font='B'if bold else'R';c.setFont(font,size);line=''
 for word in str(s).split():
  trial=(line+' '+word).strip()
  if line and pdfmetrics.stringWidth(trial,font,size)>w:c.drawString(x,y,line);y-=size*1.45;line=word
  else:line=trial
 if line:c.drawString(x,y,line);y-=size*1.45
 return y
def image(c,path,x,y,w,h):
 p=R/path;im=Image.open(p);key=hashlib.sha256(p.read_bytes()).hexdigest()[:20];q=CACHE/(key+'.jpg')
 if not q.exists():
  im=im.convert('RGB');im.thumbnail((1600,1600));im.save(q,quality=88,optimize=True)
 scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
 c.drawImage(ImageReader(str(q)),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
def head(c,title,n,h=810):
 c.setFillColorRGB(.08,.15,.13);c.rect(0,h-75,612,75,fill=1,stroke=0);c.setFillColorRGB(1,1,1);text(c,title,28,h-30,14,bold=True);text(c,'BREEZE 2027 / PRIVATE QUARRY FIDELITY REVIEW',28,h-58,8)
 c.setFillColorRGB(.12,.15,.13);text(c,f'{n} / Visual approval pending; Stage 3A on hold',28,20,8)
def single(c,record,label,n):
 head(c,record['title'],n);text(c,label,28,705,10,bold=True);image(c,record['file'],28,155,556,535)
 camera=record['data']['camera'];text(c,f"Camera position [{camera['x']:.6f}, {camera['y']:.6f}, {camera['z']:.6f}]; yaw {camera['yaw']:.8f}; pitch {camera['pitch']:.8f}; FOV {camera['fov']}; clip {camera['near']}/{camera['far']}. Full pose/quaternion in gallery metadata.",28,130,8)
 text(c,f"{record['lighting']} / DPR{record['canvas']['effectiveDpr']} / Q{record['data']['snapshot']['quality']} / {record['note']}",28,95,9);c.showPage()
extras=json.loads((R/'raw/inspection-captures.json').read_text())
assert extras['status']=='PASS'
full=canvas.Canvas(str(R/'Gullyverse-Quarry-Fidelity-Full-Screenshots.pdf'),pagesize=(612,810));n=1
head(full,'Original / recovered / corrected evidence',n);image(full,by['corrected']['desktop-visitor-1.png']['file'],28,270,556,430)
text(full,'Current captures are matched; historical embedded PDF images are authentic pre-loss references. Neither successful validation nor this review package grants visual acceptance.',28,225,11)
text(full,'Protected public C5.1 and recovered C8/C9 remain available. New material-only and geological previews preserve approved 3x sampling. No Stage 3A or public promotion.',28,140,10);full.showPage();n+=1
for label in labels:
 for record in groups[label]['captures']:single(full,record,names[label],n);n+=1
for h in history:
 head(full,f"Original {h['source']} / p{h['page']}",n);image(full,h['file'],28,145,556,555)
 text(full,f"Panel {h['panel']} / original {h['width']}x{h['height']}. {h['caption']}",28,115,9);full.showPage();n+=1
for rec in extras['captures']:
 head(full,rec['title'],n);image(full,rec['file'],28,140,556,555);text(full,rec['note'],28,110,9);full.showPage();n+=1
full.save();fullpages=n-1
for rec in extras['captures']:assert(R/rec['file']).exists()
triples=[]
for page,stem in [(2,'desktop-visitor-1.png'),(3,'desktop-visitor-2.png'),(4,'desktop-visitor-3.png'),(5,'desktop-medium-inspection.png'),(6,'desktop-close-rock.png'),(8,'desktop-left-join.png'),(9,'desktop-right-join.png'),(10,'desktop-upper-rim.png'),(11,'desktop-wall-foot.png'),(12,'desktop-hub-scaffold.png'),(14,'desktop-historical-tunnel.png'),(15,'desktop-behind-left-stalls.png'),(17,'mobile-visitor-1.png'),(19,'desktop-aerial-map.png'),(20,'mobile-aerial-map.png'),(21,'desktop-along-wall.png')]:
 original=next(h for h in history if h['source']=='C9_54page_browser_comparison.pdf'and h['page']==page and h['panel']=='D')
 triples.append({'title':by['corrected'][stem]['title'],'original':original,'recovered':by['recovered'][stem],'corrected':by['corrected'][stem],'kind':'Reference-aligned original C9 D; current recovered/corrected exactly matched'})
for page,stem in [(6,'desktop-visitor-1.png'),(7,'desktop-historical-close.png'),(8,'desktop-historical-tunnel.png'),(9,'desktop-behind-left-stalls.png'),(11,'mobile-visitor-1.png')]:
 original=next(h for h in history if h['source'].startswith('c8/')and h['page']==page)
 triples.append({'title':'C8 material / '+by['material'][stem]['title'],'original':original,'recovered':by['c8'][stem],'corrected':by['material'][stem],'kind':'Approved original C8 3x; material-only correction on different C5.1 host, not lost C6.2'})
# Full-size, ungraded three-column contact sheets: no screenshot cropping.
(R/'contact-sheets').mkdir(exist_ok=True);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
for i,t in enumerate(triples):
 sheet=Image.new('RGB',(3*1366,1020),'#101b16');draw=ImageDraw.Draw(sheet)
 for col,(record,label)in enumerate([(t['original'],f"ORIGINAL / {t['original']['source']} p{t['original']['page']} {t['original']['panel']}"),(t['recovered'],'RECOVERED / preserved comparison'),(t['corrected'],'CORRECTED / private candidate')]):
  im=Image.open(R/record['file']).convert('RGB');im.thumbnail((1366,900));sheet.paste(im,(col*1366+(1366-im.width)//2,60+(900-im.height)//2));draw.text((col*1366+12,14),label,font=font,fill='white')
 draw.text((12,978),t['kind'],font=font,fill='white');file=f'contact-sheets/{i+1:02}-{Path(t["corrected"]["file"]).stem}.jpg';sheet.save(R/file,quality=90);t['contactSheet']=file
short=canvas.Canvas(str(R/'Gullyverse-Quarry-Fidelity-Phone-Review.pdf'),pagesize=(612,1280));n=1
head(short,'Quarry fidelity correction / review',n,1280);image(short,by['corrected']['desktop-visitor-1.png']['file'],28,660,556,480)
y=610
for s in ['Private candidate ready for comparison, not approved for production. Material scope now matches the documented35.557m study extent. Historical geological fidelity is only partially recovered.',
 'The historic native 0.9 hero is preserved exactly. New relief uses disjoint Coastal Cliff04 crops at uniform 1.03/1.06 scale; only two of four authoring crops contribute measured front-surface detail. The approved 3x material sampling and global lights are unchanged.',
 'Brown-grey coverage is closer to original C9, but smooth boundary strips, triangular/faceted joins and folded coastal forms remain. The neutral view exposes these weaknesses. Historical C6.2 host/mask pixels are lost. This is not a pixel-identical restoration.',
 'Strict new-region geometry gates pass. All seven known legacy component hits remain; the current first-hit survey returns six. Laptop/phone performance is unverified; browser software measurements are diagnostic only.',
 'Stop for user review of BOTH material fidelity and geological fidelity. Stage 3A remains on hold.']:
 y=text(short,s,28,y,12)-20
short.showPage();n+=1
for t in triples:
 head(short,t['title'],n,1280)
 for record,label,y in [(t['original'],f"ORIGINAL / p{t['original']['page']} panel {t['original']['panel']}",825),(t['recovered'],'RECOVERED / preserved rejected recovery',440),(t['corrected'],'CORRECTED / new private candidate',55)]:
  text(short,label,28,y+355,10,bold=True);image(short,record['file'],28,y,556,345)
 text(short,t['kind'],28,37,7);short.showPage();n+=1
for stem in ['desktop-broad-upper.png','desktop-neutral-geometry.png','desktop-neutral-material.png']:
 a,b=by['recovered'][stem],by['corrected'][stem];head(short,b['title'],n,1280);text(short,'RECOVERED',28,1170,11,bold=True);image(short,a['file'],28,665,556,490);text(short,'CORRECTED',28,630,11,bold=True);image(short,b['file'],28,130,556,490);text(short,b['note'],28,92,10);short.showPage();n+=1
head(short,'Limitations and approval gate',n,1280);y=1160
for s in ['The genuine original C5.1 assets survive unchanged. C6/C6.1/C6.2 do not have recovered standalone runtimes; their historical panels are compared to the nearest host and identified as non-equivalent.',
 'C7 remains rejected. C8.1 remains an optional historical study. Neither has been silently adopted.',
 'Three public visitor views are included without removing stalls. Positions2/3 remain substantially occluded. Non-public close/along-wall cameras are labelled and do not establish visitor acceptance on their own.',
 'Some source-derived folds and faceted boundary transitions remain unlike the photographic quarry. Dusk still hides fine relief. No exposure or fill-light change was used to manufacture improvement.',
 'Middle/far LODs remain too expensive for quarry-wide replication (40,940/35,296 triangles). A combined multi-context mobile startup timed out; unchanged isolated assertions passed. The full report preserves that failure and all remaining limits.',
 'Use the new checkpoint folder and restoration index for backup. Prior Phase 1/2/3 checkpoints remain immutable. No commit, push, merge, deployment or public-default change.']:
 y=text(short,s,28,y,12)-26
short.showPage();short.save();shortpages=n
# Technical Markdown remains authoritative; PDF is a portable reading copy.
style=ParagraphStyle('Body',fontName='R',fontSize=9,leading=13,spaceAfter=7);heading=ParagraphStyle('Head',fontName='B',fontSize=14,leading=18,spaceBefore=13,spaceAfter=9,keepWithNext=True);story=[]
cell=ParagraphStyle('Cell',fontName='R',fontSize=7,leading=10,spaceAfter=0)
cellhead=ParagraphStyle('CellHead',parent=cell,fontName='B',textColor=colors.white)
def cleanline(line):return re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',line).replace('**','').replace('`','')
def addtable(rows):
 count=len(rows[0]);widths={2:[145,407],3:[145,135,272],4:[145,155,85,167],5:[130,105,105,105,107],8:[150,38,42,56,56,56,45,109]}.get(count,[552/count]*count)
 widths=[v*552/sum(widths)for v in widths]
 cells=[[Paragraph(html.escape(cleanline(v)),cellhead if i==0 else cell)for v in row]for i,row in enumerate(rows)]
 t=LongTable(cells,colWidths=widths,repeatRows=1,hAlign='LEFT',spaceAfter=12)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173328')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#edf2ef'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#486858'))]));story.append(t)
pending=[]
for line in (ROOT/'docs/gullyverse-recovery-quarry-fidelity-correction.md').read_text().splitlines()+['']:
 if line.startswith('|'):
  if set(line)-set('| :-'):pending.append([v.strip()for v in line.strip('|').split('|')])
  continue
 if pending:addtable(pending);pending=[]
 if not line.strip()or line.startswith('```'):continue
 clean=cleanline(line);story.append(Paragraph(html.escape(clean.lstrip('# ')if line.startswith('#')else clean),heading if line.startswith('#')else style))
def techfooter(c,d):c.setFont('R',7);c.setFillColorRGB(.2,.3,.25);c.drawString(30,18,'Private fidelity correction / visual approval pending / Stage 3A on hold');c.drawRightString(582,18,str(d.page))
SimpleDocTemplate(str(R/'Gullyverse-Quarry-Fidelity-Technical-Report.pdf'),pagesize=(612,810),leftMargin=30,rightMargin=30,topMargin=32,bottomMargin=32).build(story,onFirstPage=techfooter,onLaterPages=techfooter)
def fig(rec,label):return f'<figure><figcaption>{html.escape(label)}</figcaption><a href="{rec["file"]}"><img loading="lazy" src="{rec["file"]}" alt="{html.escape(label)}"></a></figure>'
cards=[]
for t in triples:cards.append('<section><h2>'+html.escape(t['title'])+'</h2><p>'+html.escape(t['kind'])+'</p><a href="'+t['contactSheet']+'">Full-size contact sheet</a><div class="triple">'+fig(t['original'],f"Original {t['original']['source']} p{t['original']['page']} / {t['original']['panel']}")+fig(t['recovered'],'Recovered comparison')+fig(t['corrected'],'Corrected private candidate')+'</div></section>')
for stem,rec in by['corrected'].items():
 cards.append('<section><h2>Five current modes / '+html.escape(rec['title'])+'</h2><p>'+html.escape(rec['note'])+'</p><div class="modes">'+''.join(fig(by[k][stem],names[k])for k in labels)+'</div><details><summary>Exact camera/render metadata</summary><pre>'+html.escape(json.dumps({'camera':rec['data']['camera'],'canvas':rec['canvas'],'quality':rec['data']['snapshot']['quality'],'lighting':rec['lighting'],'build':matched['build']},indent=2))+'</pre></details></section>')
cards.append('<section><h2>Earlier historical stages / not new runtime candidates</h2><p>C6/C6.1/C6.2 are transitional evidence; C7 rejected; C8.1 optional study. See stage-fidelity-matrix.csv for nearest-host non-equivalence.</p><div class="modes">'+''.join(fig(h,f"{h['source']} p{h['page']} / {h['panel']}")for h in history if not h['source'].startswith(('C9_','c8/')))+'</div></section>')
cards.append('<section><h2>Separate runtime diagnostics and original stage</h2><div class="modes">'+''.join(fig(c,c['title']+' / '+c['note'])for c in extras['captures'])+'</div></section>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse / quarry fidelity correction</title><style>body{margin:0;background:#101b16;color:#edf1e9;font:16px/1.5 system-ui}main{max-width:1800px;margin:auto;padding:24px}a{color:#c9e0b7}section{margin-top:30px;padding-top:12px;border-top:1px solid #667863}.triple,.modes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}figure{margin:0 0 16px;padding:10px;background:#1e2b21}figcaption{font-size:13px;margin-bottom:8px}img{width:100%;max-height:800px;object-fit:contain}pre{white-space:pre-wrap;font-size:12px}nav{display:flex;gap:20px;flex-wrap:wrap}.notice{background:#343225;border-left:4px solid #bdad77;padding:15px}@media(max-width:900px){.triple,.modes{grid-template-columns:1fr}main{padding:14px}}</style><main><p>BREEZE 2027 / PRIVATE REVIEW</p><h1>Original → recovered → corrected quarry</h1><p class="notice">Visual approval pending. Authentic original browser images are reference-aligned; five current modes have identical actual poses, FOV, lighting, DPR and quality. Public C5.1 unchanged. C8 3× and native hero 0.9× preserved. Known legacy visibility defects remain, including the coincident seventh component hit. Stage 3A is on hold.</p><nav><a href="Gullyverse-Quarry-Fidelity-Phone-Review.pdf">Phone review</a><a href="Gullyverse-Quarry-Fidelity-Full-Screenshots.pdf">All screenshots PDF</a><a href="Gullyverse-Quarry-Fidelity-Technical-Report.pdf">Technical report</a><a href="videos/visitor-journey.mp4">Visitor journey</a><a href="videos/automatic-lod-inspection.mp4">Automatic LOD</a><a href="matched-pose-verification.json">Matched metadata</a><a href="stage-fidelity-matrix.csv">Stage fidelity matrix</a></nav><p>Tap images for full-resolution source files. Screenshots have no colour grading. PDFs/contact sheets are compressed reading copies; original PNGs are retained.</p>'''+''.join(cards)+'</main></html>'
(R/'gallery.html').write_text(page)
(R/'comparison-index.json').write_text(json.dumps(triples,indent=2)+'\n')
(R/'review-package.json').write_text(json.dumps({'status':'PASS','build':matched['build'],'currentMatchedImages':matched['currentImages'],'historicalImages':len(history),'contactSheets':len(triples),'additionalDiagnostics':len(extras['captures']),'phonePages':shortpages,'fullScreenshotPages':fullpages,'visualApproval':'PENDING','PDFCompression':'JPEG88 derivatives; original full-resolution PNGs untouched'},indent=2)+'\n')
print('REVIEW_ASSEMBLED',json.loads((R/'review-package.json').read_text()))
