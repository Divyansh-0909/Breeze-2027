from pathlib import Path
import json,hashlib,html,io,statistics
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import fitz
O=Path(__file__).resolve().parents[1]
rows=[]
for ed in ['before','after']:
 for v in ['A','B','C']:
  r=json.loads((O/f'evidence/render-{ed}-{v}.json').read_text());assert len(r)==(27 if v=='C' else 13);rows.extend(r)
profiles=[]
for ed in ['profile-before','profile-after']:
 r=json.loads((O/f'evidence/render-{ed}-C.json').read_text());assert len(r)==3;profiles.extend(r)
keys=['position','rotationEuler','lens','sensorWidthMM','cameraType','orthoScale','clipStart','clipEnd','width','height','engine','samples','exposure','viewTransform','look','optionalSupportW']
for collection,eds in [(rows,['before','after']),(profiles,['profile-before','profile-after'])]:
 for a in [r for r in collection if r['edition']==eds[0]]:
  b=next(r for r in collection if r['edition']==eds[1]and r['variant']==a['variant']and r['camera']==a['camera'])
  assert all(a[k]==b[k]for k in keys),(a['camera'],[(k,a[k],b[k])for k in keys if a[k]!=b[k]])
  for r in [a,b]:
   p=O/r['file'];assert p.is_file()and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert Image.open(p).size==(r['width'],r['height'])
(O/'evidence/final-render-manifest.json').write_text(json.dumps(rows+profiles,indent=2)+'\n')
(O/'evidence/matched-render-validation.json').write_text(json.dumps({'status':'PASS','mainMatchedPairs':53,'profileDiagnosticMatchedPairs':3,'finalPNGCount':112,'matchingFields':keys,'quality':'EEVEE16samples;desktop1200x750,portrait540x960;offline Blender DPR not applicable','supportLighting':'0W optional supports in ALL before/after/diagnostic frames','profileIsolation':'Only shutter materials replaced with same neutral metal for both profile diagnostics. No world/light/exposure edits.','sourceImagesAreNotSceneEvidence':True},indent=2)+'\n')
artists=[('chaar-diwari','CHAAR DIWARI'),('ritviz','RITVIZ'),('neha-kakkar','NEHA KAKKAR')]
def label(n):
 for k,a in artists:
  if k in n:return a+' / '+n.split(k+'-')[-1].replace('-',' ')
 return {'01-landing':'Lane-wide landing','12-mobile-landing':'Portrait landing','04-hub':'Hub / board / audience','05-team':'Team RIGHT preserved','06-events':'Events LEFT preserved','ART-rooftop-back-context':'Entry-parapet context','ART-wall-pier-left':'Left lane-pier proposal','ART-wall-pier-right':'Right lane-pier proposal','ART-wall-return-left':'Left parapet proposal','ART-wall-return-right':'Right parapet proposal','ART-lane-left-context':'Left lane context','ART-lane-right-context':'Right lane context'}.get(n,n)
def wrap(c,text,x,y,width,size=10,leading=14):
 c.setFont('Helvetica',size);c.setFillColorRGB(.87,.90,.92)
 for para in text.split('\n'):
  line=''
  for word in para.split():
   candidate=(line+' '+word).strip()
   if c.stringWidth(candidate,'Helvetica',size)>width and line:c.drawString(x,y,line);y-=leading;line=word
   else:line=candidate
  c.drawString(x,y,line);y-=leading
 return y
def base(c,title,subtitle='Private Blender / SUPPORT OFF LOCKED / art approval pending'):
 c.setFillColorRGB(.055,.065,.08);c.rect(0,0,360,640,fill=1,stroke=0);c.setFillColorRGB(.96,.74,.35);c.setFont('Helvetica-Bold',13);c.drawString(18,611,title[:50]);wrap(c,subtitle,18,588,324,9,12);c.setFillColorRGB(.58,.63,.69);c.setFont('Helvetica',8);c.drawString(18,17,'27 October 2026 • actual Blender renders • website unchanged')
def picture(c,p,x,y,w,h,alpha=False):
 im=Image.open(p);iw,ih=im.size;s=min(w/iw,h/ih);nw,nh=iw*s,ih*s
 if alpha:
  c.drawImage(str(p),x+(w-nw)/2,y+(h-nh)/2,nw,nh,mask='auto')
 else:
  b=io.BytesIO();im.convert('RGB').save(b,'JPEG',quality=87,subsampling=1);b.seek(0);c.drawImage(ImageReader(b),x+(w-nw)/2,y+(h-nh)/2,nw,nh)
def pair(c,v,n,diagnostic=False):
 collection=profiles if diagnostic else rows;eds=['profile-before','profile-after']if diagnostic else['before','after'];a=next(r for r in collection if r['variant']==v and r['camera']==n and r['edition']==eds[0]);b=next(r for r in collection if r['variant']==v and r['camera']==n and r['edition']==eds[1])
 base(c,label(n),f'Variant {v} • same pose, exposure, lighting and quality'+(' • neutral-metal diagnostic'if diagnostic else''))
 if 'mobile'in n:
  picture(c,O/a['file'],18,190,158,350);picture(c,O/b['file'],184,190,158,350);wrap(c,'BEFORE',20,174,154,9);wrap(c,'AFTER',186,174,154,9)
 else:
  picture(c,O/a['file'],18,334,324,203);picture(c,O/b['file'],18,95,324,203);wrap(c,'BEFORE / existing flat-strip shutter'if diagnostic else'BEFORE / verified0W baseline',18,549,324,9);wrap(c,'AFTER / real rolled-profile metal'if diagnostic else'AFTER / original artwork on physical surfaces',18,310,324,9)
 wrap(c,'Five optional supports remain0W. No global light, world, fog or exposure change. Full PNGs in gallery.',18,69,324,9,12);c.showPage()
def source_contact(c,k,a):
 base(c,a+' — source / matte / real shutter')
 wrap(c,'SOURCE JPEG / user-supplied original, unchanged',18,551,324,9);picture(c,O/f'source/originals/{k}.jpeg',18,432,324,108)
 wrap(c,'DERIVED RGBA / original colour + clean paint matte',18,417,324,9);picture(c,O/f'source/derived/{k}-paint-rgba.png',18,298,324,108,True)
 wrap(c,'ACTUAL BLENDER / painted physical shutter',18,283,324,9);r=next(r for r in rows if r['edition']=='after'and r['variant']=='C'and r['camera']==f'ART-{k}-front');picture(c,O/r['file'],18,61,324,203)
 wrap(c,'Matte',18,47,52,8);picture(c,O/f'source/derived/{k}-paint-mask.png',69,30,95,31,True)
 wrap(c,'Opaque core RGB matches source exactly; only white-matted edge pixels corrected.',171,51,171,8,10);c.showPage()
def text_page(c,title,text):base(c,title);wrap(c,text,18,548,324,10.5,15);c.showPage()
def generated_page(c):
 base(c,'Generated supporting art / four proposals')
 wrap(c,'RAW IMAGE-GENERATED ATLAS / asset, not a scene render',18,549,324,9);picture(c,O/'source/generated/supporting-wall-atlas.png',18,430,324,108,True)
 names=['ART-wall-pier-left','ART-wall-pier-right','ART-wall-return-left','ART-wall-return-right']
 for i,n in enumerate(names):
  x=18+(i%2)*166;y=242-(i//2)*142;r=next(r for r in rows if r['edition']=='after'and r['variant']=='C'and r['camera']==n);picture(c,O/r['file'],x,y,158,99);wrap(c,label(n),x,y-13,158,8,10)
 wrap(c,'Actual tool:image_gen.imagegen. Three original images were style inputs. Original name designs retained; supporting motifs are non-name. Placements proposed.',18,69,324,9,12);c.showPage()
phone=O/'review/Gullyverse-Rev05C-Shutter-Graffiti-Review.pdf';full=O/'review/Gullyverse-Rev05C-Full-Art-Comparisons.pdf'
c=canvas.Canvas(str(phone),pagesize=(360,640))
text_page(c,'Rev05C — shutter paintings for review','Three exact user designs are now painted onto true shallow rolled-steel slats. Four supporting abstract pieces are proposed on existing surfaces.\n\nSupport OFF remains locked in A/B/C. The original twelve lights, shops, counters, shelves, crowd, board, screen and40second straight walk remain preserved.\n\nThis is private Blender art. No website implementation or A/B/C style selection.\n\nThe source JPEGs are preserved byte-for-byte. The final opaque paint colours match them exactly; enclosed silver/white highlights are retained. Generated extraction trials were not substituted as replacement name designs.\n\nAll scene images are actual Blender renders. Raw generated art and source images are labelled separately.')
for k,a in artists:source_contact(c,k,a)
for k,a in artists:
 pair(c,'C',f'ART-{k}-front');pair(c,'C',f'ART-{k}-grazing')
pair(c,'C','ART-ritviz-grazing',True)
for v in ['A','B','C']:pair(c,v,'01-landing')
generated_page(c)
for n in ['ART-wall-pier-left','ART-wall-pier-right','ART-wall-return-left','ART-wall-return-right','ART-rooftop-back-context']:pair(c,'C',n)
pair(c,'C','12-mobile-landing');pair(c,'C','ART-ritviz-mobile')
budget=json.loads((O/'evidence/scene-budget-final.json').read_text())
text_page(c,'Verification / honest limits',f"Three closed shutters,18slats each. True3cm groove depth /3mm metal thickness. Outer assembly bounds unchanged within the original strict tolerance. No floating artwork planes.\n\nAll original17lights and39cameras retained;22review cameras added. Five optional supports stay0W.\n\nGeometry:+5,184triangles per variant. Four shared added images; estimated unique RGBA8+mips95.86→{budget['estimatedUniqueImageRGBA8MipMiB']:.2f}MiB. No new runtime export or hardware FPS claim.\n\n960frames per A/B/C and original route/stock/crowd checks pass. Two inherited scooter-side negative-Y approaches remain blocked; positive-Y alternatives pass.\n\nFacades, crowds and stock remain concept-quality. Final shutter appearance, four wall placements and A/B/C art selection remain for user review.")
c.save()
c=canvas.Canvas(str(full),pagesize=(360,640))
text_page(c,'Full actual-render comparison','53main matched pairs +3profile-only diagnostic pairs =112final scene PNGs.\n\nEvery artist has front,grazing and lane-context views in each A/B/C. C adds close detail,mobile readability, supporting wall views and Team/Events preservation.\n\nAll use0W support, identical matched camera/FOV/quality and unchanged global environment. Neutral-profile comparisons replace only shutter materials identically before/after; this diagnostic is not saved as the normal candidate.\n\nSource/alpha/surface contacts and generated-asset/application page follow. Full PNGs remain separate and unchanged.')
for k,a in artists:source_contact(c,k,a)
generated_page(c)
for v in ['A','B','C']:
 for r in [r for r in rows if r['variant']==v and r['edition']=='after']:pair(c,v,r['camera'])
for k,a in artists:pair(c,'C',f'ART-{k}-grazing',True)
c.save()
parts=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Rev05C corrugated shutters</title><style>body{background:#10151c;color:#eee;font:16px system-ui;max-width:1400px;margin:auto;padding:20px}section{padding:18px 0;border-bottom:1px solid #444}.pair,.assets{display:grid;grid-template-columns:1fr 1fr;gap:14px}img{width:100%}.assets{grid-template-columns:repeat(3,1fr)}small{color:#abb}@media(max-width:700px){.pair,.assets{grid-template-columns:1fr}}</style></head><body><h1>Rev05C: exact artist art on physical corrugated shutters</h1><p>Private actual Blender comparison; support OFF locked. All four supporting wall placements remain proposals. No website changes or A/B/C selection.</p><p><a href="REPORT.md">Technical report</a> · <a href="RESTORE.md">Restoration instructions</a></p>']
parts.append('<h2>Source assets — these are not scene renders</h2>')
for k,a in artists:
 parts.append(f'<section><h3>{a}</h3><div class="assets">')
 for title,p in [('Original user JPEG',f'source/originals/{k}.jpeg'),('Derived RGBA paint',f'source/derived/{k}-paint-rgba.png'),('Paper exclusion matte',f'source/derived/{k}-paint-mask.png')]:parts.append(f'<div>{title}<a href="{p}"><img loading="lazy" src="{p}"></a></div>')
 parts.append('</div></section>')
parts.append('<h2>Actual image-generated supporting atlas — raw asset</h2><a href="source/generated/supporting-wall-atlas.png"><img style="max-width:900px" src="source/generated/supporting-wall-atlas.png"></a><h2>Actual Blender scene renders</h2>')
for v in ['A','B','C']:
 for r in [r for r in rows if r['variant']==v and r['edition']=='after']:
  n=r['camera'];a=next(a for a in rows if a['variant']==v and a['camera']==n and a['edition']=='before');parts.append(f'<section><h3>{v} / {html.escape(label(n))}</h3><div class="pair">')
  for title,x in [('BEFORE',a),('AFTER',r)]:parts.append(f'<div><h4>{title}</h4><a href="{x["file"]}"><img loading="lazy" src="{x["file"]}"></a><small>{x["width"]}×{x["height"]};{x["lens"]}mm;EEVEE16samples;support0W</small></div>')
  parts.append('</div></section>')
parts.append('<h2>Neutral-metal geometry diagnostics — same real scene lighting</h2>')
for k,a in artists:
 parts.append(f'<section><h3>{a}</h3><div class="pair">')
 for ed in ['profile-before','profile-after']:
  r=next(r for r in profiles if r['camera']==f'ART-{k}-grazing'and r['edition']==ed);parts.append(f'<div>{ed}<a href="{r["file"]}"><img loading="lazy" src="{r["file"]}"></a></div>')
 parts.append('</div></section>')
parts.append('</body></html>');(O/'GALLERY.html').write_text('\n'.join(parts))
proof={'status':'PASS','phonePDFPages':len(fitz.open(phone)),'fullPDFPages':len(fitz.open(full)),'mainMatchedPairs':53,'profileMatchedPairs':3,'finalScenePNGs':112,'artists':3,'generatedSupportingPlacements':4,'allSceneImagesActualBlender':True,'noArtDirectionSelected':True}
(O/'evidence/review-build.json').write_text(json.dumps(proof,indent=2)+'\n');print('ART_REVIEW_BUILT',proof)
