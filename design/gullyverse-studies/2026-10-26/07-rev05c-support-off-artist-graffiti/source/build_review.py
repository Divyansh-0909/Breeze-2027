from pathlib import Path
import json,hashlib,statistics,html,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
O=Path(__file__).resolve().parents[1]
rows=json.loads((O/'evidence/render-manifest.json').read_text())
assert len(rows)==60
keys=['position','rotationEuler','lens','sensorWidthMM','cameraType','orthoScale','clipStart','clipEnd','width','height','samples','engine','viewTransform','look','exposure']
for v in ['A','B','C']:
 for n in sorted({r['camera']for r in rows}):
  a=next(r for r in rows if r['variant']==v and r['camera']==n and r['edition']=='on');b=next(r for r in rows if r['variant']==v and r['camera']==n and r['edition']=='off')
  assert all(a[k]==b[k]for k in keys)
  for r in [a,b]:
   p=O/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert Image.open(p).size==(r['width'],r['height'])
(O/'evidence/matched-render-validation.json').write_text(json.dumps({'status':'PASS','pairs':30,'originalPNGs':60,'matchedFields':keys,'baselineON':'Verified prior Rev05B actual render, not rerendered/replaced','afterOFF':'Fresh real Blender EEVEE16sample renders','DPR':'Not applicable to offline Blender','lightingDifference':'Only five optional45W support lights changed to0W','artworkStatus':'No graffiti is present or claimed'},indent=2)+'\n')
poses=['01-landing','21-shop-left-25','22-shop-left-7','23-shop-left2','24-shop-right-16','25-shop-right-7','31-shop-inside-1','12-mobile-landing','19-hub-wide','08-crowd-middle']
labels={'01-landing':'Lane-wide landing at night','21-shop-left-25':'Open shop: left Y-25','22-shop-left-7':'Open shop: left Y-7','23-shop-left2':'Open shop: left Y+2','24-shop-right-16':'Open shop: right Y-16','25-shop-right-7':'Open shop: right Y-7','31-shop-inside-1':'Inside-shop diagnostic: left Y-25','12-mobile-landing':'Portrait landing','19-hub-wide':'Hub / navigation / screen context','08-crowd-middle':'Audience at eye height'}
def wrap(c,text,x,y,width,size=10,leading=14,color=(.87,.89,.91)):
 c.setFont('Helvetica',size);c.setFillColorRGB(*color)
 for p in text.split('\n'):
  line=''
  for w in p.split():
   s=(line+' '+w).strip()
   if c.stringWidth(s,'Helvetica',size)>width and line:c.drawString(x,y,line);y-=leading;line=w
   else:line=s
  c.drawString(x,y,line);y-=leading
 return y
def image(c,p,x,y,w,h):
 im=Image.open(p).convert('RGB');iw,ih=im.size;scale=min(w/iw,h/ih);nw,nh=iw*scale,ih*scale
 b=io.BytesIO();im.save(b,'JPEG',quality=88,subsampling=1);b.seek(0);c.drawImage(ImageReader(b),x+(w-nw)/2,y+(h-nh)/2,nw,nh)
def base(c,title,sub='Rev05C / LIGHTING COMPLETE — GRAFFITI BLOCKED'):
 c.setFillColorRGB(.055,.065,.08);c.rect(0,0,360,640,fill=1,stroke=0);c.setFillColorRGB(.92,.72,.38);c.setFont('Helvetica-Bold',13);c.drawString(18,610,title[:50]);wrap(c,sub,18,588,324,9,12)
 c.setFillColorRGB(.58,.63,.69);c.setFont('Helvetica',8);c.drawString(18,17,'Private Blender only • website untouched • 26 October 2026')
def pair(c,v,n):
 base(c,labels[n],f'Variant {v} • identical geometry, pose, exposure and EEVEE quality')
 a=next(r for r in rows if r['variant']==v and r['camera']==n and r['edition']=='on');b=next(r for r in rows if r['variant']==v and r['camera']==n and r['edition']=='off')
 if 'mobile'in n:
  image(c,O/a['file'],18,192,158,350);image(c,O/b['file'],184,192,158,350)
  wrap(c,'BEFORE /45W each',20,176,156,9);wrap(c,'AFTER /0W each',186,176,156,9)
 else:
  image(c,O/a['file'],18,334,324,203);image(c,O/b['file'],18,95,324,203)
  wrap(c,'BEFORE — Rev05B / support45W each',18,548,324,9);wrap(c,'AFTER — Rev05C / support OFF',18,310,324,9)
 wrap(c,'Original twelve street/shop/board lights remain unchanged. No compensating exposure or helper light.',18,69,324,9,12)
 c.showPage()
def textpage(c,title,text):base(c,title);wrap(c,text,18,548,324,11,16);c.showPage()
phone=O/'review/Gullyverse-Rev05C-Lighting-PARTIAL-Review.pdf';full=O/'review/Gullyverse-Rev05C-Lighting-All-ABC.pdf'
c=canvas.Canvas(str(phone),pagesize=(360,640))
textpage(c,'Rev05C — status and scope','Implemented: five optional interior supports now0W in every A/B/C scene.\n\nAll geometry, shelves, counters, crowd, camera route, materials, original lighting and website files preserved.\n\nNOT COMPLETE: the combined artist-shutter and supporting-wall graffiti pass. Original Chaar Diwari, Ritviz and Neha Kakkar artwork was not found in accessible Drive or local sources. No substitute name art was fabricated.\n\nImage generation is available; style-matched supporting pieces are deferred until the originals can actually be inspected.\n\nA/B/C aesthetic selection remains yours.')
for v in ['A','B','C']:pair(c,v,'01-landing')
for n in poses[1:6]:pair(c,'C',n)
pair(c,'C','31-shop-inside-1');pair(c,'C','12-mobile-landing');pair(c,'C','19-hub-wide');pair(c,'C','08-crowd-middle')
textpage(c,'Graffiti asset gate / next action','Three separate closed shutters are available:\n\nCHAAR DIWARI → right Y-25\nRITVIZ → left Y-16\nNEHA KAKKAR → right Y+2\n\nThese are measured PLANNED placements, not rendered artwork. Source Drive IDs/hashes are unresolved.\n\nPlease provide the folder or three original-file links. No more geometry or lighting work is required before that asset step.\n\nLighting, shop and route validations pass. Two inherited negative-Y scooter approaches remain blocked; positive-Y approaches pass.\n\nAll60 full-resolution PNGs and exact camera metadata are in the complementary review package.')
c.save()
c=canvas.Canvas(str(full),pagesize=(360,640))
textpage(c,'Complete lighting comparison','30 matched pairs /60 original PNGs.\n\nAll five shops, inside diagnostic, landing, mobile and hub/audience context in each A/B/C variant.\n\nBEFORE images are the exact hash-verified final Rev05B renders on the same master geometry. AFTER images are freshly rendered from the0W derivative.\n\nNo graffiti result is claimed. Full combined Rev05C remains blocked on original artist files.\n\nNo physical-device FPS, runtime deployment or final-art approval is implied.')
for v in ['A','B','C']:
 for n in poses:pair(c,v,n)
c.save()
parts=['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev05C lighting / graffiti blocked</title><style>body{background:#10151d;color:#eee;font:16px system-ui;max-width:1200px;margin:auto;padding:20px}section{padding:14px 0;border-bottom:1px solid #555}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}img{width:100%}small{color:#bbc}@media(max-width:650px){.pair{grid-template-columns:1fr}}</style><h1>Rev05C — lighting correction complete; graffiti blocked</h1><p>Private real Blender renders. No invented artist artwork or generated-motif result. Original12 lights and all geometry preserved; five optional45W supports are OFF.</p>']
for v in ['A','B','C']:
 for n in poses:
  parts.append(f'<section><h2>{v} / {html.escape(labels[n])}</h2><div class="pair">')
  for e in ['on','off']:
   r=next(r for r in rows if r['variant']==v and r['camera']==n and r['edition']==e);p=html.escape(r['file']);parts.append(f'<div><h3>{"BEFORE45W"if e=="on"else"AFTER0W"}</h3><a href="{p}"><img loading="lazy" src="{p}"></a><small>{r["width"]}×{r["height"]};{r["lens"]}mm;16samples;exposure{r["exposure"]}</small></div>')
  parts.append('</div></section>')
(O/'GALLERY.html').write_text('\n'.join(parts))
import fitz
result={'status':'PASS','phonePages':len(fitz.open(phone)),'fullPages':len(fitz.open(full)),'fullResolutionPNGs':60,'matchedPairs':30,'artworkComparisonsAvailable':False}
(O/'evidence/review-build.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
