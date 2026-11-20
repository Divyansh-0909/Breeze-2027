from pathlib import Path
import json
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

O=Path(__file__).resolve().parents[1]
captures=json.loads((O/'evidence/captures.json').read_text())
assert len(captures)==8
font_root=Path('/usr/share/fonts/truetype/open-sans')
for name,file in [('ReviewRegular','OpenSans-Regular.ttf'),('ReviewBold','OpenSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(font_root/file)))
target=O/'review/Team-Mural-Full-Heading-Laptop-Review.pdf'
w,h=landscape(A4)
pdf=Canvas(str(target),pagesize=(w,h),pageCompression=1)
pdf.setTitle('Gullyverse - Organising Committee - Eight Team Mural Laptop Views')
pdf.setAuthor('Breeze 2027')
gallery=[]
for index,record in enumerate(captures,1):
    pdf.setFillColor(Color(.97,.97,.955));pdf.rect(0,0,w,h,fill=1,stroke=0)
    pdf.setFillColor(Color(.51,.36,.14));pdf.setFont('ReviewBold',9)
    pdf.drawString(24,h-28,'BREEZE 2027 / GULLYVERSE / REV15J1')
    pdf.setFillColor(Color(.12,.15,.17));pdf.setFont('ReviewBold',20)
    pdf.drawString(24,h-56,f'{index:02d} / {record["team"]}')
    pdf.setFillColor(Color(.38,.42,.44));pdf.setFont('ReviewRegular',9)
    pdf.drawString(24,h-72,'Laptop view - 1600 x 900 - Actual Blender scene - 10 November 2026')
    image_width=w-48;image_height=image_width*900/1600
    pdf.drawImage(str(O/record['file']),24,h-82-image_height,width=image_width,height=image_height,preserveAspectRatio=True)
    pdf.setFillColor(Color(.38,.42,.44));pdf.setFont('ReviewRegular',9)
    pdf.drawString(24,33,'Coordinators removed. Organising Committee first. Original reference plaster wall and world lighting retained.')
    pdf.drawRightString(w-24,33,f'{index} / 8')
    pdf.showPage()
    gallery.append(f'<figure><figcaption>{index:02d} / {record["team"]}</figcaption><img src="{record["file"]}" alt="{record["team"]} mural"></figure>')
pdf.save()
(O/'GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Organising Committee first - Team mural</title><style>body{margin:24px;background:#14191d;color:#f7eedb;font:18px system-ui}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}figure{margin:0}figcaption{padding:12px 0}img{display:block;width:100%}@media(max-width:900px){main{grid-template-columns:1fr}}</style><h1>Organising Committee first / Team mural</h1><p>Eight teams. Actual Blender scene renders using the original plaster wall and world lighting.</p><main>'+''.join(gallery)+'</main>')
print(target,target.stat().st_size,'bytes')
