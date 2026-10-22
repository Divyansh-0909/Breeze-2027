"""Self-contained gallery and reading PDFs from ungraded renderer PNGs."""
from pathlib import Path
import json,html,re,shutil,hashlib
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,LongTable,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab import rl_config
rl_config.useA85=False  # Binary Flate streams; lossless, less transfer than ASCII85.

ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20'
review=json.loads((R/'raw/review-captures.json').read_text());diag=json.loads((R/'raw/cave-diagnostic-captures.json').read_text());package=json.loads((R/'review-package.json').read_text())
assert review['status']=='PASS'and diag['status']=='PASS'
shots=review['shots'];pairs=[]
position_rows=json.loads((R/'review-position-classification.json').read_text())['rows']
def classification(s):
 return next((r['classification']for r in position_rows if r['id']==s.get('id')and r['mobile']==s.get('mobile')),'DIAGNOSTIC / NON-PUBLIC INSPECTION')
for after in (s for s in shots if s['candidate']):
 before=next(s for s in shots if not s['candidate']and s['mobile']==after['mobile']and s['id']==after['id'])
 pairs.append({'before':before,'after':after})
references=[];(R/'references').mkdir(exist_ok=True)
for p in sorted((ROOT/'assets-source/gullyverse/c9-cave-recovery/references').iterdir()):
 if not p.is_file()or p.suffix.lower()not in ['.png','.jpg','.jpeg']:continue
 dst=R/'references'/p.name;shutil.copy2(p,dst);references.append({'file':'references/'+p.name,'label':'REFERENCE ONLY / '+p.stem,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
def text(c,s,x,y,size=10,width=550,bold=False):
 font='Bold'if bold else'Body';c.setFont(font,size);line=''
 for word in str(s).split():
  proposed=(line+' '+word).strip()
  if line and pdfmetrics.stringWidth(proposed,font,size)>width:c.drawString(x,y,line);y-=size*1.4;line=word
  else:line=proposed
 if line:c.drawString(x,y,line);y-=size*1.4
 return y
def img(c,file,x,y,w,h):
 p=R/file
 if 'Phone-Review' in str(c._filename):
  cache=R/'.pdf-cache';cache.mkdir(exist_ok=True)
  q=cache/(hashlib.sha256(p.read_bytes()).hexdigest()+'.jpg')
  if not q.exists():
   with Image.open(p)as original:
    im=original.convert('RGB');im.thumbnail((1200,1600));im.save(q,quality=88,optimize=True)
  p=q
 with Image.open(p)as im:iw,ih=im.size
 scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
 c.drawImage(ImageReader(str(p)),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
def header(c,title,n,w,h):
 c.setFillColorRGB(.06,.12,.10);c.rect(0,h-64,w,64,fill=1,stroke=0);c.setFillColorRGB(1,1,1);text(c,title,18,h-27,13,w-36,True);c.setFont('Body',8);c.drawString(18,h-51,'BREEZE 2027 / PRIVATE CAVE CANDIDATE');c.setFillColorRGB(.10,.15,.12);text(c,f'{n} / Stage3A visual approval pending / C9 + 3× preserved',18,14,7,w-36)
def describe(s):
 d=s.get('data',s);cam=d.get('camera',s.get('pose',{}));vp=d.get('viewport',{})
 brief={k:round(cam[k],6)for k in ['x','y','z','yaw','pitch','fov']if k in cam}
 return f"{classification(s)}; pose {json.dumps(brief,separators=(',',':'))}; tier {d.get('snapshot',{}).get('quality')}; actual DPR {d.get('stats',{}).get('dpr')}. Full precision, viewport and quaternion are in the gallery JSON."

# Every screenshot keeps all native pixels; no JPEG conversion or crop.
all_pages=[]
for p in pairs:
 all_pages.extend([(p['before'],'BEFORE / selected C9 + surviving legacy entrance'),(p['after'],'AFTER / new private natural-cave candidate')])
all_pages.extend((s,'DIAGNOSTIC / '+s.get('note',''))for s in diag['shots'])
all_pages.extend((s,s['label'])for s in references)
full=canvas.Canvas(str(R/package['fullScreenshotPDF']));full.setTitle('Gullyverse Stage3A full-resolution browser screenshots')
for n,(s,label)in enumerate(all_pages,1):
 with Image.open(R/s['file'])as im:iw,ih=im.size
 w=max(iw+40,600);h=ih+205;full.setPageSize((w,h));header(full,s.get('title',s.get('id','Cave reference')),n,w,h);text(full,label,20,h-91,13,w-40,True);img(full,s['file'],20,85,w-40,ih);text(full,describe(s)if 'data'in s or'pose'in s else'Reference image, not an implementation screenshot.',20,67,9,w-40);full.showPage()
full.save()

# Short portrait review with matched comparisons, not a replacement for PNGs.
pw,ph=612,990;short=canvas.Canvas(str(R/package['phonePDF']),pagesize=(pw,ph));short.setTitle('Gullyverse Stage3A phone review');n=1
header(short,'Natural cave and tunnel / review',n,pw,ph);img(short,'screenshots/review-after-desktop/landing-ui.png',22,415,568,480);y=385
for s in ['Private candidate only. C9 + approved 3× rock material are preserved. No public promotion, commit or deploy.',
          'The 42 m rocky passage and local mouth-clearance repair are implemented. No large physical entrance lettering and no visible ceiling/hanging lights.',
          'Art is not production-ready: the mouth return still looks engineered, some captured edges read thin, and floor contacts remain too clean. Exact artwork for all seven artists is pending.',
          'Build/type/lint and97 units pass. New cave geometry/LOD gates pass; seven inherited quarry visibility defects and physical-device performance remain outstanding. Read the technical report for all browser/deadline results.']:
 y=text(short,s,22,y,12,568)-12
short.showPage();n+=1
ids=['landing-ui','entrance-diagonal','mouth-left','mouth-right','ground-contact','raised-rock','tunnel-first','tunnel-mid','rock-vault','tunnel-bend','final-enclosed','look-back','hub','aerial-map','stage']
for p in pairs:
 a,b=p['before'],p['after']
 if b['mobile']or b['id']not in ids:continue
 header(short,b['title'],n,pw,ph);text(short,'BEFORE / selected C9 with legacy entrance',22,906,10,568,True);img(short,a['file'],22,510,568,380);text(short,'AFTER / private natural cave',22,479,10,568,True);img(short,b['file'],22,83,568,380);text(short,'Identical camera/FOV/tier/DPR/global dusk. '+classification(b).replace('_',' '),22,64,8,568);short.showPage();n+=1
for s in diag['shots']:
 if s['id']not in ['entrance-neutral-geometry','tunnel-neutral-geometry','tunnel-unfiltered-ambient']:continue
 header(short,s['id'].replace('-',' '),n,pw,ph);img(short,s['file'],22,365,568,520);text(short,s['note'],22,324,12,568);text(short,'Temporary diagnostic only. The neutral entrance exposes a smoother joining collar and thin scan edges; successful geometry checks do not establish art acceptance.',22,238,12,568);short.showPage();n+=1
for b in (s for s in shots if s['candidate']and s['mobile']and s['id']in ['landing-ui','tunnel-first','tunnel-mid']):
 header(short,'Mobile aspect / '+b['title'],n,pw,ph);img(short,b['file'],22,69,568,825);text(short,'390×844 / DPR1 / Q0 / browser aspect, not physical phone verification.',22,48,9,568);short.showPage();n+=1
header(short,'Stop for visual review',n,pw,ph);y=885
for s in ['Do not promote this candidate to public-default rendering. C9 remains the selected quarry and all earlier comparisons remain intact.',
          'The entrance is not yet as thick, eroded or naturally integrated as the supplied concept/photos. Some tunnel surfaces still follow a regular cross-section; the floor is too clean and its contact too crisp.',
          'Final exact artist PNGs are missing for Neha Kakkar, Khullar G, Nikhitha Gandhi, Ritviz, Twin Strings, Chaar diwari and Yellow diaries. No generic artwork was invented. Artwork close-up/readability approval cannot be claimed.',
          'Seven inherited C9/terrain defects remain. SwiftShader diagnostic frame rates are not real laptop or phone FPS. The full report preserves failed attempts and the cold-stage preparation limitations.',
          'The Drive checkpoint includes editable Blender source, runtime GLBs, source/tests, evidence and exact prior dependencies. Use the separate final verification receipt and independent restore result.',
          'Next action: user visual review, followed by a separately authorized bounded correction or artwork integration. No Stage3B has started.']:
 y=text(short,s,22,y,13,568)-27
short.showPage();short.save()

# Portable technical reading copy. Markdown remains the editable report.
normal=ParagraphStyle('Body',fontName='Body',fontSize=9,leading=13,spaceAfter=8);heading=ParagraphStyle('Heading',fontName='Bold',fontSize=14,leading=19,spaceBefore=14,spaceAfter=8,keepWithNext=True);cell=ParagraphStyle('Cell',fontName='Body',fontSize=6.8,leading=9)
story=[];table=[]
def clean(s):return re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',s).replace('**','').replace('`','')
def flush():
 if not table:return
 widths=[552/len(table[0])]*len(table[0]);t=LongTable([[Paragraph(html.escape(clean(x)),cell)for x in row]for row in table],colWidths=widths,repeatRows=1,spaceAfter=10);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#cad8cc')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f1f4f1'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(t);table.clear()
for line in (R/'technical-report.md').read_text().splitlines()+['']:
 if line.startswith('|'):
  if set(line)-set('| :-'):table.append([x.strip()for x in line.strip('|').split('|')])
  continue
 flush()
 if line.strip():story.append(Paragraph(html.escape(clean(line.lstrip('# '))),heading if line.startswith('#')else normal))
def footer(c,d):c.setFont('Body',7);c.drawString(30,17,'Private Stage3A candidate / visual approval pending');c.drawRightString(582,17,str(d.page))
SimpleDocTemplate(str(R/package['technicalPDF']),pagesize=(612,810),leftMargin=30,rightMargin=30,topMargin=30,bottomMargin=30).build(story,onFirstPage=footer,onLaterPages=footer)

def figure(s,label):return '<figure><figcaption>'+html.escape(label)+'</figcaption><a href="'+s['file']+'"><img loading="lazy" src="'+s['file']+'" alt="'+html.escape(label)+'"></a></figure>'
cards=[]
for p in pairs:
 a,b=p['before'],p['after'];cards.append('<section><h2>'+html.escape(b['title']+(' / mobile'if b['mobile']else''))+'</h2><p>'+classification(b).replace('_',' ')+'</p><div class="pair">'+figure(a,'BEFORE / C9 with surviving legacy entrance')+figure(b,'AFTER / private cave candidate')+'</div><details><summary>Exact renderer and camera metadata</summary><pre>'+html.escape(json.dumps({'before':a,'after':b},indent=2))+'</pre></details></section>')
cards.append('<section><h2>Separate browser diagnostics</h2><div class="pair">'+''.join(figure(s,s['note'])for s in diag['shots'])+'</div></section>')
cards.append('<section><h2>Supplied cave references</h2><p>Reference images only; no concept or offline render substitutes for browser evidence.</p><div class="pair">'+''.join(figure(s,s['label'])for s in references)+'</div></section>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse Stage3A private cave review</title><style>body{background:#111a15;color:#edf1e9;font:16px/1.5 system-ui;margin:0}main{max-width:1600px;margin:auto;padding:24px}a{color:#cfdfbe}section{border-top:1px solid #57654e;margin-top:30px;padding-top:15px}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{background:#202c24;margin:0 0 16px;padding:12px}img{width:100%;max-height:900px;object-fit:contain}figcaption{font-size:13px;margin-bottom:8px}pre{white-space:pre-wrap;font-size:12px}.notice{padding:15px;background:#393121;border-left:4px solid #ceb176}nav{display:flex;gap:20px;flex-wrap:wrap}@media(max-width:800px){.pair{grid-template-columns:1fr}main{padding:14px}}</style><main><p>BREEZE 2027 / PRIVATE REVIEW</p><h1>Natural cave entrance and rocky tunnel</h1><p class="notice">C9 and approved3× sampling preserved. Private candidate only; NOT production-ready. Engineered entrance collar and thin scan edges remain visible; seven exact artist images are pending. No visible fixtures or giant entrance lettering. Inherited C9 visibility defects and physical-device acceptance remain outstanding. No public promotion or deployment.</p><nav><a href="Gullyverse-Stage3A-Phone-Review.pdf">Phone review PDF</a><a href="Gullyverse-Stage3A-Full-Screenshots.pdf">All full-resolution screenshots PDF</a><a href="Gullyverse-Stage3A-Technical-Report.pdf">Technical report PDF</a><a href="technical-report.md">Editable report</a><a href="videos/visitor-journey.mp4">Full browser journey</a><a href="videos/automatic-lod-inspection.mp4">Automatic LOD inspection</a><a href="matched-pose-verification.json">Matched pose verification</a></nav><p>Tap images for untouched full-resolution PNGs. Same camera/FOV/DPR/tier/global lighting. Diagnostic and non-public views are labelled separately. Before images are the surviving C9/legacy entrance, not the lost rejected Stage3A assets.</p>'''+''.join(cards)+'</main></html>'
(R/'gallery.html').write_text(page);(R/'comparison-index.json').write_text(json.dumps(pairs,indent=2)+'\n')
package.update(fullScreenshotPages=len(all_pages),phonePages=n,referenceCount=len(references),diagnosticImages=len(diag['shots']),PDFImageHandling='Full screenshot PDF embeds native PNGs losslessly. Phone review uses JPEG88 reading derivatives up to1200x1600. All original full-resolution PNG files are untouched; no cropping or colour grading.')
(R/'review-package.json').write_text(json.dumps(package,indent=2)+'\n');print(json.dumps({k:package[k]for k in ['fullScreenshotPages','phonePages','referenceCount','diagnosticImages']}))
