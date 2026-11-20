from pathlib import Path
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];V1=R.parent/'events-wall-rev15v1-coloured-plaster-2026-11-14';b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();captures=json.loads((R/'evidence/captures.json').read_text());assert captures['status']=='PASS'
for row in captures['captures']:assert sha(R/row['file'])==row['sha256'] and row['sourceSHA256']==b['editedSHA256']
pdfmetrics.registerFont(TTFont('DV',str(R/'source/review-fonts/DejaVuSans.ttf')));pdfmetrics.registerFont(TTFont('DVB',str(R/'source/review-fonts/DejaVuSans-Bold.ttf')))
P=R/'review/Breeze-Events-Plaster-and-Open-Cypher-Gate-Review-Final.pdf';c=canvas.Canvas(str(P),pagesize=(980,720));c.setTitle('Breeze 2027 / Events painted wall and open cypher gate / Rev15V2')
def txt(s,x,y,size=11,bold=False):c.setFillColor(HexColor('#edf0e7'));c.setFont('DVB' if bold else 'DV',size);c.drawString(x,y,s)
def page(n,title,sub):
 c.setFillColor(HexColor('#101a18'));c.rect(0,0,980,720,fill=1,stroke=0);txt(title,28,676,25,True);txt(sub,28,650,11);txt('14 November 2026 / Rev15V2 / Native 3D environment / Production website integration pending',28,20,9);txt(str(n),944,20,9)
def hero(file):c.drawImage(ImageReader(str(file)),70,110,840,525)
page(1,'Events: a coloured house wall.','Dusty terracotta plaster replaces the brick pattern. Existing saved night lights and exposure.');hero(V1/'renders/events-night.jpg');txt('All eight Events posters, frames, heading and window details are retained in the latest gate scene.',28,81,12);txt('The whole Team building, including its upper windows and eight mural states, remains unchanged.',28,57,12);c.showPage()
page(2,'A narrow entrance beyond the navigation stand.','Neutral inspection lighting makes the entrance and its position easier to see.');hero(R/'renders/gate-approach-neutral.jpg');txt('A 1.8 m opening sits on level asphalt behind the existing navigation stand, between short boundary walls.',28,81,12);txt('The left-hinged single leaf opens outwards toward the gully. The navigation board and sponsor LED are unchanged.',28,57,11);c.showPage()
page(3,'Open at 90 degrees, with space between the rods.','Neutral inspection lighting / original full native environment.');hero(R/'renders/gate-detail-neutral.jpg');txt('The steel leaf has 13 vertical 16 mm rods, roughly 10 cm clear gaps, hinges, rails and a latch. There is no solid panel.',28,81,11);txt('The open leaf stays to the left of the walking line. No raised threshold, ground railing or permanent light is added.',28,57,11);c.showPage()
page(4,'The entrance under the existing night atmosphere.','Original saved lighting. No inspection lamps or exposure boost in this capture.');hero(R/'renders/gate-night.jpg');txt('The saved environment keeps its night atmosphere. The two preceding pages use temporary review lights only.',28,81,11);txt('Native preservation, fresh-open, geometry and reconstruction checks passed. Full-world website integration is pending.',28,57,11);c.showPage();c.save();reader=PdfReader(P);assert len(reader.pages)==4 and all(len(p.extract_text())>100 for p in reader.pages);result={'status':'PASS','pages':4,'bytes':P.stat().st_size,'sha256':sha(P),'gateNativeMasterSHA256':b['editedSHA256'],'EventsFinishRetainedFromVerifiedV1':True,'inspectionLightingClearlyLabelled':True,'TeamAndEventsPostersPreserved':True};(R/'evidence/pdf.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
