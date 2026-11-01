from pathlib import Path
import json,hashlib,html,io,ast
from PIL import Image,ImageChops,ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
O=Path(__file__).resolve().parents[1]
# Reuse only presentation helper functions, not the old phase's build/execution code.
tree=ast.parse((O/'source/prior-pilot/build_review.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['para','pic']]
style=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,textColor=HexColor('#dce0e4'))
exec(compile(ast.Module(body=defs,type_ignores=[]),'review_helpers','exec'))
before=json.loads((O/'evidence/render-before.json').read_text());after=json.loads((O/'evidence/render-after.json').read_text());assert len(before)==len(after)==22
master=json.loads((O/'evidence/authoring.json').read_text())['masterSHA256'];keys=['pose','position','rotationEuler','lens','sensorWidth','clipStart','clipEnd','resolution','engine','samples','look','viewTransform','exposure','world','supportW'];pairs=[]
for a in sorted(before,key=lambda r:r['pose']):
 b=next(x for x in after if x['pose']==a['pose']);assert b['masterSHA256']==master
 assert all(a[k]==b[k]for k in keys),(a['pose'],[k for k in keys if a[k]!=b[k]])
 for r in[a,b]:assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
 im1=Image.open(O/a['file']).convert('RGB');im2=Image.open(O/b['file']).convert('RGB');diff=ImageChops.difference(im1,im2);px=list(diff.getdata())
 pairs.append({'pose':a['pose'],'before':a['file'],'after':b['file'],'matchedMetadata':{k:a[k]for k in keys},'fractionPixelsChangedOver12of255':sum(max(p)>12 for p in px)/len(px),'meanAbsoluteRGBDifference':ImageStat.Stat(diff).mean})
(O/'evidence/matched-render-validation.json').write_text(json.dumps({'status':'PASS','pairs':pairs,'matchedFields':keys,'matchedPairs':22,'scenePNGs':44,'masterSHA256':master,'DPR':'not applicable to offline Blender','imageDifferenceIsNotArtScore':True},indent=2)+'\n')
titles=['Lane entry / wide visitor composition','Whole street / multiple bays','Right-hand shop group','Left-hand shop group','Open shop / eye-level','Doorway interior / inspection','Chaar Diwari / locked shutter','Ritviz / locked shutter','Neha Kakkar / locked shutter','Straight lane-to-roof connection','Rooftop wide / screen and crowd','Screen and unchanged audience','Team RIGHT','Events LEFT','Left approved return graphic','Right approved return graphic','Rooftop reverse / street continuity','Mobile portrait / street','Mobile portrait / rooftop','Counter and stock / inspection','Upper facades / elevated inspection','Roof edge and background / inspection']
labels={p['pose']:t for p,t in zip(pairs,titles)};opts=json.loads((O/'evidence/options.json').read_text());assert len(opts['renders'])==11
for r in opts['renders']:assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256']
def page(c,title,sub,W,H):
 c.setFillColor(HexColor('#101318'));c.rect(0,0,W,H,fill=1,stroke=0);y=para(c,title,18,H-18,W-36,14 if W<400 else 18);para(c,sub,18,y-10,W-36,8 if W<400 else 10);c.setFont('Helvetica',6 if W<400 else 7);c.setFillColor(HexColor('#aeb4bc'));c.drawString(18,15,'28 Oct 2026 | Actual offline Blender | SUPPORT OFF | Website unchanged')
def pairpage(c,p,W,H):
 page(c,labels[p['pose']],'APPROVED C+A PILOT BEFORE / WIDER C+A WORLD AFTER',W,H)
 if'mobile'in p['pose']:
  w=(W-50)/2;h=min(H-205,w*1024/576);y=H-125-h
  for i,key in enumerate(['before','after']):x=18+i*(w+14);para(c,key.upper(),x,y+h+18,w,8);pic(c,O/p[key],x,y,w,h)
 else:
  w=W-36;h=w*9/16
  for key,y in[('before',H-110-h),('after',H-151-2*h)]:para(c,key.upper(),18,y+h+18,w,8);pic(c,O/p[key],18,y,w,h)
 para(c,'Identical pose, lens, colour management, atmosphere, world and 16 samples. Five optional supports remain 0 W. Inspection views are labelled; original route/cameras are unchanged.',18,78,W-36,8 if W<400 else 10);c.showPage()
def cover(c,W,H):
 page(c,'Selected C+A / wider neighborhood realism','PRIVATE BLENDER CANDIDATE — NEW VISUAL APPROVAL PENDING',W,H);w=W-36;h=w*9/16;pic(c,O/'renders/after/01-lane-entry.png',18,H-108-h,w,h);y=H-130-h
 for t in['Six remaining shopfronts, upper street window hierarchy, lane finishes and wider rooftop/background construction now use the selected C+A approach.',
 'Exact approved artist shutters and four wall motifs stay locked. Support lighting stays OFF. Original stock, counters, crowd and route retain their positions.',
 'Crowd and counter alternatives are separate PROPOSALS ONLY. They are not replacements in the environment.',
 'The 40-second walk samples the original route at 3 fps: actual offline renders, not browser gameplay or hardware FPS.']:
  y=para(c,t,18,y,W-36,9 if W<400 else 11)-14
 c.showPage()
def contact(c,W,H):
 page(c,'Whole-environment comparison gate',"Is the whole environment more like a believable Indian neighborhood while retaining C's night-time cypher energy?",W,H);w=(W-48)/2;h=w*9/16
 for i,name in enumerate(['01-lane-entry','02-whole-street','11-rooftop-wide','17-rooftop-reverse']):
  p=next(p for p in pairs if p['pose']==name);y=H-116-i*(h+30)-h
  for j,key in enumerate(['before','after']):pic(c,O/p[key],18+j*(w+12),y,w,h)
  para(c,labels[name]+' / BEFORE left, AFTER right',18,y-5,W-36,7)
 c.showPage()
def proposal(c,W,H,kind,front=False):
 page(c,kind.upper()+' OPTIONS / PROPOSALS ONLY','Protected crowd and counter bases are not replaced in the world.',W,H);w=(W-48)/2;h=w*.75
 for i,n in enumerate(range(4)if kind=='crowd'else range(3)):
  name=(('crowd-face-'if front else'crowd-')+str(n))if kind=='crowd'else'counter-'+str(n);x=18+i%2*(w+12);y=H-116-i//2*(h+45)-h;pic(c,O/f'renders/options/{name}.png',x,y,w,h);r=next(r for r in opts['measurements']if r['kind']==kind and r['option']==n);para(c,str(n)+': '+r['description'],x,y-6,w,7 if W<400 else 9)
 y=H-150-2*(h+45)
 if kind=='crowd':
  ts=['0 = current control. 1 = same topology with shading. 2/3 = tapered shoulder/limb/footwear tests at the same source identity, position, yaw and height. All remain stylized, faceless mid-distance studies.',
  'Measured triangles per actor: '+', '.join(str(r['option'])+'='+str(r['trianglesPerActor'])for r in opts['measurements']if r['kind']=='crowd')+'. No full-crowd rollout or new animation.']
 else:ts=['0 = protected cuboid. 1 = open steel service counter. 2 = repairable plywood case. Proposed envelope stays 1 x 3.3 x 1.28 m.',
 'Main world only adds reversible finish/edge strips around exact original counter cores. Structural replacement requires separate approval.']
 for t in ts:y=para(c,t,18,y,W-36,9 if W<400 else 11)-14
 c.showPage()
def qa(c,W,H):
 page(c,'Validation, costs and remaining limits','Review the wide pairs and walking clip before approving adoption.',W,H);y=H-105
 b=json.loads((O/'evidence/scene-budget.json').read_text());rows={r['variant']:r for r in b['sceneBudgets']};p=rows['C+A PILOT'];a=rows['C+A WORLD']
 ts=[f"Triangles {p['triangles']:,} -> {a['triangles']:,}. Mesh/curve owners {p['meshAndConvertedCurveObjects']:,} -> {a['meshAndConvertedCurveObjects']:,}. New static construction is grouped by spatial sector and material.",
 f"Existing {a['uniqueReferencedImages']} image owners reused: {a['estimatedReferencedRGBA8MipMiB']:.2f} MiB estimated RGBA8+mips. No additional texture download or dynamic light; GPU VRAM is not measured.",
 'All original A/B/C and approved pilot data remain exact. A fifth world scene is added. Strict mesh, UV/tangent, shutter depth, art visibility, crowd and route tests pass without tolerance changes.',
 '960 original walk frames checked per scene. Two inherited negative-Y scooter-side shop approaches remain blocked; positive-Y alternatives pass.',
 'Crowd remains low-poly, cartons and counter cores remain simple, shop interiors remain dark with support OFF. Window reveals are built on existing facades rather than new room cavities.',
 'This is more developed private environment art, not final photorealism. Near/mid/far batching and image reductions are proposals, not validated runtime assets.',
 'Website hashes and exact dirty Git states are unchanged. No web build, glTF integration, browser FPS, GPU certification, commit, push, merge or deployment is claimed.']
 for t in ts:y=para(c,t,18,y,W-36,9 if W<400 else 11)-14
 c.showPage()
phone=['01-lane-entry','02-whole-street','03-shop-group-right','04-shop-group-left','05-open-shop-eye','07-chaar-context','08-ritviz-context','09-neha-context','10-lane-roof-transition','11-rooftop-wide','15-return-left','16-return-right','18-mobile-lane','19-mobile-rooftop'];pdfs=[]
for name,W,H,names in[('Selected-C-Wider-Realism-Phone-Review.pdf',360,760,phone),('Selected-C-Wider-Realism-Full-Comparisons.pdf',612,940,[p['pose']for p in pairs])]:
 c=canvas.Canvas(str(O/'review'/name),pagesize=(W,H),pageCompression=1);cover(c,W,H)
 if W>400:contact(c,W,H)
 for n in names:pairpage(c,next(p for p in pairs if p['pose']==n),W,H)
 proposal(c,W,H,'crowd');proposal(c,W,H,'crowd',True);proposal(c,W,H,'counter');qa(c,W,H);c.save();pdfs.append({'file':'review/'+name,'pages':len(names)+(6 if W>400 else 5)})
cards=[]
for p in pairs:
 cards.append('<section><h2>'+html.escape(labels[p['pose']])+'</h2><div class="pair">'+''.join('<figure><figcaption>'+k.upper()+'</figcaption><a href="'+p[k]+'"><img loading="lazy" src="'+p[k]+'"></a></figure>'for k in['before','after'])+'</div><details><summary>Matched camera/render metadata</summary><pre>'+html.escape(json.dumps(p['matchedMetadata'],indent=2))+'</pre></details></section>')
proposals=''.join('<figure><figcaption>'+r['name']+' - PROPOSAL ONLY</figcaption><a href="'+r['file']+'"><img loading="lazy" src="'+r['file']+'"></a></figure>'for r in opts['renders'])
(O/'GALLERY.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse wider C+A realism</title><style>body{max-width:1600px;margin:auto;padding:24px;background:#101318;color:#ddd;font:16px system-ui}a{color:#edb652}.pair,.options{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;max-height:85vh;object-fit:contain}section{margin:36px 0}pre{white-space:pre-wrap}video{max-width:100%}@media(max-width:700px){.pair,.options{grid-template-columns:1fr}}</style></head><body><h1>Selected C+A / wider neighborhood realism</h1><p>Private Blender. Art locked, support OFF, website unchanged. User review pending.</p><p><a href="REPORT.md">Technical report</a> | <a href="RESTORE.md">Restore</a> | <a href="review/Selected-C-Wider-Realism-Phone-Review.pdf">Phone review</a> | <a href="review/Selected-C-Wider-Realism-Full-Comparisons.pdf">Full comparison</a></p><h2>Original 40-second route</h2><p>120 actual Blender frames at 3fps, 480x270, 8 samples; offline inspection, not interactive FPS.</p><video controls src="review/Selected-C-Wider-Realism-Walk-40s.mp4"></video>'+''.join(cards)+'<h2>Proposals only</h2><div class="options">'+proposals+'</div></body></html>')
(O/'evidence/review-build.json').write_text(json.dumps({'status':'PASS','PDFs':pdfs,'scenePNGs':44,'proposalPNGs':11,'walkFrames':120},indent=2)+'\n');print('REVIEW_COMPLETE',pdfs,flush=True)
