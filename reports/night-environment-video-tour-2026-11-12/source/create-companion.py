from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader

R=Path(__file__).resolve().parents[1];tour=json.loads((R/'tour-path.json').read_text());shots=tour['shots'];folders=json.loads((R/'evidence/drive-folders.json').read_text())
upload=json.loads((R/'evidence/video-upload.json').read_text());video_url=upload['url']
for n,f in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
W,H=A4;M=36;CW=W-2*M;INK=colors.HexColor('#19252e');TEAL=colors.HexColor('#087a80');GRAY=colors.HexColor('#55636c');LINE=colors.HexColor('#d7dfe3')
out=R/'review/Breeze-Night-Environment-Tour-Companion.pdf';c=canvas.Canvas(str(out),pagesize=A4);c.setTitle('Breeze — Full night environment camera tour');c.setAuthor('Breeze project review')
style=ParagraphStyle('body',fontName='Body',fontSize=9.5,leading=14,textColor=INK)
def text(s,x,y,width=CW,font='Body',size=9.5,leading=14,color=INK):
 p=Paragraph(s,ParagraphStyle('p',parent=style,fontName=font,fontSize=size,leading=leading,textColor=color));_,h=p.wrap(width,1000);p.drawOn(c,x,y-h);return y-h
def footer(n):
 c.setStrokeColor(LINE);c.line(M,33,W-M,33);c.setFillColor(GRAY);c.setFont('Body',7.3);c.drawString(M,21,'BREEZE 2027 / GULLYVERSE · PRIVATE NIGHT PREVIEW · 12 NOV 2026');c.drawRightString(W-M,21,str(n))
def head(title,n):
 c.setFont('Bold',17);c.setFillColor(INK);c.drawString(M,H-49,title);c.setFillColor(GRAY);c.setFont('Body',8.5);c.drawString(M,H-67,'Key views from the full rendered camera tour');footer(n)
def stamp(v):return f'{int(v)//60:02d}:{int(v)%60:02d}'
def image(shot,y,width=CW):
 path=R/'renders'/f"{shot['id']}.jpg";height=width*720/1280;c.drawImage(ImageReader(path),M,y-height,width,height,preserveAspectRatio=True,mask='auto');return y-height

c.setFillColor(INK);c.setFont('Bold',25);c.drawString(M,H-62,'Night environment');c.drawString(M,H-94,'Full camera tour');c.setFont('Body',12);c.setFillColor(GRAY);c.drawString(M,H-121,'1 minute 54 seconds · 720p · 13 chapters')
c.setFillColor(TEAL);c.setFont('Bold',11.5);c.drawString(M,H-147,'WATCH THE VIDEO ON BREEZE DRIVE');c.linkURL(video_url,(M,H-151,W-M,H-135),relative=0)
bottom=image(shots[-1],H-164)
y=bottom-14;text('The approved cool night fill, warm shops, damp ground and distance haze.',M,y,size=9,color=GRAY)
y-=40;c.setFillColor(INK);c.setFont('Bold',11);c.drawString(M,y,'CHAPTER GUIDE');y-=17
for col,items in enumerate([shots[:7],shots[7:]]):
 xx=M+col*(CW/2+7);yy=y
 for s in items:
  text(stamp(s['start'])+' · '+s['title'],xx,yy,width=CW/2-13,size=8.2,leading=11);yy-=26
text('This is a camera inspection of the private night scene. Live website integration remains pending; the original quarry controller and native scene files are unchanged.',M,108,size=9,leading=13)
footer(1);c.showPage()

page=2
for start in range(0,12,2):
 head(['Lane and warm shops','Shutters and shop interior','Ramp and navigation','Cypher and surrounding crowd','Events and Team wall','Screens and residential façades'][start//2],page)
 y=H-93
 for s in shots[start:start+2]:
  y=text(f"<b>{stamp(s['start'])}–{stamp(s['end'])}</b> · {s['title']}",M,y,size=10.2,leading=14)-8
  y=image(s,y)-23
 c.showPage();page+=1

head('The complete night scene',page);y=image(shots[-1],H-94)-24
y=text('<b>Coverage.</b> The full visible capture export contains all 189 source crowd meshes and 1,433 evaluated source objects. It includes the lane, open and closed shop fronts, shutters and artist paint, navigation/LED board, courtyard, Events façade, Organising Committee mural, rear screens and surrounding houses.',M,y)-13
y=text('<b>Capture state.</b> The camera follows a scripted inspection path. Crowd poses and screen images are static; the sponsor LED scrolls. The Team wall shows its current Organising Committee state. All eight mural states remain in the packed native master.',M,y)-13
y=text('<b>Playback.</b> The delivery video is 24 FPS, interpolated from deterministic 10 FPS camera renders at 1280×720 with a 0.85 internal render ratio. This is offline video delivery; physical-device website FPS is unmeasured.',M,y)-13
y=text('<b>Preservation.</b> The native master and all eight recorded quarry movement/rendering files retain their checksums. The capture-only mural lighting map was checked against a native night render. Walkable production integration remains pending. The rejected Schedule label is still an unresolved source placeholder.',M,y)-13
y=text(f'<a href="{folders["sources"]["url"]}" color="#087a80"><b>Capture sources and restore instructions on Drive</b></a>',M,y,size=9.5)
footer(page);c.save();reader=PdfReader(out);assert len(reader.pages)==8
proof={'status':'PASS','pages':len(reader.pages),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'videoUrl':video_url,'sourceFrames':'13 chapter midpoint JPEG frames captured from the same source render sequence','pageTextLengths':[len(p.extract_text()) for p in reader.pages]}
(R/'evidence/pdf-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
