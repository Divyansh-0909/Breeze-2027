from pathlib import Path
import json,hashlib,io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];proof=json.loads((R/'evidence/build-verification.json').read_text());refs=json.loads((R/'references/sources.json').read_text());folders=json.loads((R/'evidence/drive-folders.json').read_text())
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=595.28,841.89;M=34;CW=W-2*M;INK=HexColor('#202d2b');GRAY=HexColor('#64716b');GREEN=HexColor('#386052');out=R/'review/Breeze-Open-Shops-Indian-Market-Review.pdf';c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Breeze — Indian market shop revision, Rev15R');c.setAuthor('Breeze project review')
def paragraph(t,x,y,w=CW,size=9,color=INK):
 p=Paragraph(t,ParagraphStyle('p',fontName='Body',fontSize=size,leading=size*1.45,textColor=color));_,hh=p.wrap(w,1000);p.drawOn(c,x,y-hh);return y-hh
def heading(t,n,sub='BREEZE 2027 / GULLYVERSE · REV15R · 13 NOV 2026'):
 c.setFont('Bold',18);c.setFillColor(INK);c.drawString(M,H-46,t);c.setFont('Body',8);c.setFillColor(GRAY);c.drawString(M,H-65,sub);c.setFont('Body',7);c.drawString(M,22,'Private native scene review · website integration pending');c.drawRightString(W-M,22,str(n))
def img(path,x,y,w,h=None):
 im=Image.open(path).convert('RGB');h=h or w*im.height/im.width;scale=min(w/im.width,h/im.height);ww=im.width*scale;hh=im.height*scale;buf=io.BytesIO();im.save(buf,'JPEG',quality=88);buf.seek(0);c.drawImage(ImageReader(buf),x+(w-ww)/2,y-hh,ww,hh);return y-hh
def frame(name,y):return img(R/'renders'/f'{name}.png',M,y,CW)
heading('Open shops, with a market identity',1);y=frame('night-chai',H-89)-20
y=paragraph('Five open shops now draw on photographs of Dharavi kirana stores, an Indian roadside tea stall and a Dharavi mobile repair shop. Hanging stock, working counters, fuller racks and local practical lights replace the repeated empty-shop treatment.',M,y,size=11)-18
for s in proof['shops']:y=paragraph('<b>'+s['id']+'</b> · '+s['title'],M,y)-8
paragraph('The original open/closed layout, artist shutters, central lane and native night atmosphere remain. The earlier Team top-light and original detailed crowd meshes are carried forward in this review.',M,183,size=9)
paragraph(f'<a href="{folders["phase"]["url"]}" color="#386052">Open this revision’s sources and backup on Drive</a>',M,108)
c.showPage()
heading('Photo references / kirana provisions',2)
for i in range(3):
 xx=M+i*(CW/3+4);ww=CW/3-8;img(R/refs[i]['localFile'],xx,H-95,ww,300);paragraph(['Dharavi Kirana Store','Anita Kirana Store, Dharavi','Mohammad Kirana General Store'][i],xx,H-415,ww,size=9);paragraph(f'<a href="{refs[i]["url"]}" color="#386052">Source photograph / Justdial</a>',xx,H-464,ww,size=8)
paragraph('<b>Applied to the scene:</b> colourful sachet strips across the opening, stacked reserve stock, narrow racks, loose-grain sacks, jar lids and a compact weighing scale. The original beige carton rows are hidden only in the new scene.',M,264,size=11)
paragraph('Photographs are research references, credited to their linked sources. They are not used as surface textures or copied branding in the 3D shop assets.',M,130,size=9);c.showPage()
heading('Photo references / tea and repair shops',3)
for j,i in enumerate([3,4,5]):
 yy=H-92-j*218;img(R/refs[i]['localFile'],M,yy,238,184);paragraph(['Varanasi tea stall: kettle, jars, hanging packets. Source: Alamy 3E3GX90.','Tea stall near Sassoon Docks, Colaba, Mumbai. Source: Alamy 2ANFJTP.','The Mobile Doctor, Dharavi: layered service signage. The repair bench and tools are modeled interpretations. Source: Justdial.'][j],290,yy,268,size=10);paragraph(f'<a href="{refs[i]["url"]}" color="#386052">Open source photograph</a>',290,yy-105,268,size=9)
c.showPage()
details={'L25':'Full back-wall rack, hanging stock, rice sacks, jars, scales and reserve cartons.','L07':'Petrol-blue counter, steel worktop, tea kettle and urn, chai glasses, biscuit jars and a small menu.','L02':'Mixed daily essentials, layered packet stock, grain sacks and a compact balance.','R16':'Phones on a repair mat, soldering station, parts trays, a bench lamp and hanging cable loops.','R07':'Bottles, biscuit jars, returnable drink crates, stocked racks and a compact cooler.'}
for page,s in enumerate(proof['shops'],4):
 heading(s['id']+' / '+s['title'],page);y=paragraph('<b>BEFORE</b> · Temporary inspection lighting',M,H-89)-8;y=frame(s['id']+'-before',y)-17;y=paragraph('<b>AFTER</b> · Same camera and inspection lights',M,y)-8;y=frame(s['id']+'-after',y)-14;paragraph(details[s['id']],M,y,size=9);c.showPage()
heading('In the approved night atmosphere',9);y=paragraph('<b>Chai and biscuits</b> · Native night lighting',M,H-87)-7;y=frame('night-chai',y)-17;y=paragraph('<b>Kirana provisions</b> · Native night lighting',M,y)-7;y=frame('night-kirana',y)-15;paragraph('Each shop has one new 55 W shelf practical behind a visible diffuser. Existing optional Rev05B support lights remain off. Exposure, world fill and haze are retained.',M,y,size=9);c.showPage()
heading('The lane stays open',10);y=frame('night-lane',H-91)-22
y=paragraph('<b>Scope:</b> all five existing open bays received detail. The 13 closed fronts retain their state and artist artwork. New assets stay beyond |X| = '+f"{proof['minimumAssetAbsX']:.2f}"+' m, leaving the central movement corridor clear.',M,y)-15
y=paragraph('<b>Preserved:</b> 189 crowd members and eight mural slides; matched Team top-light; original masters and historical scenes. This is an authored native scene revision. The production website and quarry controller have not been changed, and browser performance has not been measured for this new asset set.',M,y)-15
paragraph('<b>Backup:</b> the complete packed native master is stored in verified numbered parts, with a restore script and checksum manifest. The local additions library and build source also preserve the new shop work. The older Drive-folder migration remains a separate pending task.',M,y)
c.save();pdf=PdfReader(out);assert len(pdf.pages)==10
links=sum(1 for p in pdf.pages for a in p.get('/Annots',[]) if a.get_object().get('/A',{}).get('/URI'));assert links>=7
(R/'evidence/pdf-verification.json').write_text(json.dumps({'status':'PASS','pages':len(pdf.pages),'links':links,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2));print(out,len(pdf.pages),out.stat().st_size)
