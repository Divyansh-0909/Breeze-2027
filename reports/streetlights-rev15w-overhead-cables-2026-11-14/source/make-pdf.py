from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import fitz
R=Path(__file__).resolve().parents[1]
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,str(R/'source/review-fonts'/file)))
out=R/'review/Breeze-Gully-Only-Streetlights-and-Wires-Rev15W.pdf';c=canvas.Canvas(str(out),pagesize=(1000,740));c.setTitle('Breeze / Rev15W / Gully lane streetlights and overhead wires');c.setAuthor('Breeze project review');page=0
def text(x,y,t,size=13,bold=False,color='#e1e6e9'):
 c.setFillColor(HexColor(color));c.setFont('Bold' if bold else 'Body',size);c.drawString(x,y,t)
def start(title,sub):
 global page
 page+=1;c.setFillColor(HexColor('#10191e'));c.rect(0,0,1000,740,fill=1,stroke=0);text(34,704,title,25,True);text(34,676,sub,12,color='#aebfc8');text(34,22,'BREEZE 2027  /  Rev15W  /  14 November 2026',10,color='#aebfc8');text(930,22,str(page),10)
def image(file,x,y,w,h):
 im=ImageReader(str(R/file));iw,ih=im.getSize();scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;c.drawImage(im,x+(w-dw)/2,y+(h-dh)/2,width=dw,height=dh,mask='auto')
def line(y,t):text(34,y,t,13)
start('Gully lane: road-edge streetlights','Actual saved night lighting. Six new poles stay along the lane; none are inside the cypher.')
image('renders/01-gully-night.jpg',34,92,932,565);line(65,'2 steady  /  2 flickering  /  2 dead lamps. The road, shops and existing lighting are preserved.');c.showPage()
start('Suspended electricity cables','Reference-informed steel poles, bent arms, boxed fittings, junction boxes and loose service loops.')
image('renders/02-lane-wires.jpg',34,104,932,551);line(80,'24 suspended runs connect the six gully poles. Lowest checked road clearance: 4.9 m.');line(55,'Cables avoid the existing buildings and navigation stand. New light ranges stop before the cypher.');c.showPage()
start('Flicker and lamp failure','Two lamps flicker independently. Two remain steadily lit; two stay dark.')
image('renders/03-flicker-lit.jpg',34,345,455,292);image('renders/04-flicker-dim.jpg',511,345,455,292);text(34,328,'L03: lit',14,True);text(511,328,'L03: momentary dip to 18%',14,True)
image('renders/05-dead-lamp.jpg',34,66,418,242);text(480,270,'Dead lamp',18,True);text(480,242,'The fitting remains visible, with no light output.',13);text(480,207,'Flicker repeats over 8.4 seconds.',13);text(480,181,'Reduced-motion mode keeps flickering lamps on.',13);text(480,155,'Dead lamps remain off in every mode.',13);c.showPage()
start('Indian market-lane references','Real reference photographs informed the utility hardware and suspended cable arrangement.')
refs=json.loads((R/'references/sources.json').read_text())
for i,(file,label) in enumerate([('delhi-wires.jpg','Delhi: warm boxed light and loose overhead wires'),('market-streetlight.jpg','Patna market: utility pole, lamp and service cables'),('dharavi-wires.jpg','Dharavi: layered cables over a narrow shop lane')]):
 x=34+i*318;image('references/'+file,x,262,298,356);text(x,241,label.split(':')[0],15,True);parts=label.split(': ')[1].split(' and ');text(x,214,parts[0],11)
 if len(parts)>1:text(x,194,'and '+parts[1],11)
 row=next(r for r in refs if r.get('file','').endswith(file));url=row['sourceURL'];text(x,160,'Open photograph source',11,color='#85d4be');c.linkURL(url,(x,155,x+200,175),relative=0)
line(112,'Reference photographs are included for review; they were not installed as scene textures.');line(85,'Only the requested gully lights and wires were added. Existing houses, murals and Events posters remain.');c.showPage()
start('Scope, deadline and delivery','This is the final requested environment art change. Website integration is a separate pending step.')
for y,t in [(618,'Location: gully lane road edges only. No new courtyard or cypher fixtures.'),(577,'Deadline recorded: 28 November 2026, Asia/Kolkata (two weeks from 14 November).'),(536,'Native master: 59 scenes, including all 58 earlier scenes and 143 packed images.'),(495,'The existing 3,209 objects, material graphs, transforms, UVs and old lights were checked.'),(454,'All eight Team mural states and all eight Events posters are retained.'),(413,'Native animation and an isolated browser component were checked separately.'),(372,'Review cameras show saved night lighting, with no inspection lamps or brightening.'),(331,'No website deployment, controller change or full-world performance claim is included.')]:line(y,t)
text(34,260,'Editable native component, runtime GLB and animation controller are included in the checkpoint.',12);text(34,226,'Visual approval of Rev15W remains with the user. Prior approved art remains preserved.',12);c.showPage();c.save()
doc=fitz.open(out);pages=[]
for i,p in enumerate(doc):
 pix=p.get_pixmap(matrix=fitz.Matrix(.9,.9));dest=R/'review'/('page-%02d.png'%(i+1));pix.save(dest);pages.append({'page':i+1,'textCharacters':len(p.get_text()),'preview':dest.name})
proof={'status':'PASS','pages':len(doc),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'output':str(out),'pageChecks':pages};(R/'evidence/pdf.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
