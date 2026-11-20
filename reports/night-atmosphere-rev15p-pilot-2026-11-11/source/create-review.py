from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1]
W,H=1190.55,841.89
out=R/'review/Gullyverse-Rev15P-Night-Pilot-Review.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Gullyverse Rev15P — isolated night atmosphere pilot')
def heading(title,sub):
 c.setFillColor(HexColor('#121c25'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#f0ddbc'));c.setFont('Helvetica-Bold',22);c.drawString(28,H-36,title);c.setFont('Helvetica',10);c.setFillColor(HexColor('#c8cdce'));c.drawString(28,H-55,sub)
def panel(name,label,x,y,w=551,h=344):
 p=R/'renders'/name;c.setFillColor(HexColor('#f0ddbc'));c.setFont('Helvetica',11);c.drawString(x,y+h+7,label);c.drawImage(ImageReader(str(p)),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
for key in ['far','middle','near']:
 heading('GULLYVERSE / '+key.upper()+' COMPARISON','Rev15P isolated pilot • 11 November 2026 • same camera position, target, lens and 1440 × 900 frame across Blender and browser')
 panel(f'blender-baseline-{key}.png','Original Rev15O / native Blender',28,408)
 panel(f'blender-pilot-{key}.png','Rev15P / native Blender night pilot',611,408)
 panel(f'browser-clear-{key}.png','Browser control / fog off, pilot lighting',28,28)
 panel(f'browser-desktop-{key}.png','Browser pilot / fog on',611,28)
 c.showPage()
heading('MOBILE VIEW / ACCESSIBLE DIRECTIONS','390 × 844 CSS pixels • CPU emulation and software rendering • not a physical phone or thermal certification')
for i,key in enumerate(['far','middle','near']):
 p=R/'renders'/f'browser-mobile-emulated-{key}.png';c.drawImage(ImageReader(str(p)),28+i*280,72,width=258,height=558,preserveAspectRatio=True,mask='auto');c.setFont('Helvetica-Bold',13);c.setFillColor(HexColor('#f0ddbc'));c.drawString(28+i*280,654,key.upper())
c.drawImage(ImageReader(str(R/'renders/browser-mobile-emulated-with-ui.png')),890,72,width=258,height=558,preserveAspectRatio=True,mask='auto');c.setFont('Helvetica-Bold',13);c.drawString(890,654,'CONTROLS / DIRECTIONS');c.showPage()
d=json.loads((R/'evidence/browser-performance.json').read_text())
heading('MEASUREMENTS / LIMITS','SwiftShader software renderer in Chromium • synchronous GPU-completed frame benchmark • three renders per view; low-sample diagnostic only')
y=H-100;c.setFont('Helvetica-Bold',12);c.setFillColor(HexColor('#f0ddbc'));c.drawString(28,y,'Profile / camera');c.drawString(260,y,'FPS');c.drawString(340,y,'Frame p50 / p95 / p99 ms');c.drawString(600,y,'CPU p50 / p95 / p99 ms');c.drawString(865,y,'GPU p50 / p95 / p99 ms');y-=28
def values(s):return ' / '.join(f'{s.get(k):.1f}' if s and s.get(k) is not None else 'unmeasured' for k in ['p50Ms','p95Ms','p99Ms'])
for profile in d['profiles']:
 for row in profile['measures']:
  c.setFont('Helvetica',11);c.setFillColor(HexColor('#d5dbdd'));c.drawString(28,y,profile['profile']+' / '+row['view']);c.drawString(260,y,f'{row["frames"]["sustainedFPS"]:.2f}' if row['frames']['sustainedFPS'] else 'n/a');c.drawString(340,y,values(row['frames']));c.drawString(600,y,values(row['cpuRenderSubmission']));c.drawString(865,y,values(row['gpu']));y-=25
y-=20
notes=[
 'The ~60 FPS desktop and >=30 FPS mobile goals are not met on this cloud software renderer. Hardware/physical-phone results remain unmeasured.',
 'No production integration, commits, pushes, deployment or Drive writes. Rev15O remains authoritative; this isolated pilot needs visual review.',
 'Plain GLB is the viewer default. Draco decodes but changes the triangle count and remains an experimental test option.',
 'The browser is a material/lighting prototype. Its PBR response differs from Blender; only ground static light/shadow maps are baked.',
 'The source has 18 shop fronts, 13 closed and five authored open. Geometry is preserved; three warm light pools identify the selectively active shops.',
 'The original world-projected graffiti coordinates and alpha artwork are preserved in the web conversion; fine enamel grain is approximated.',
 'KTX2/Basis encoding is not delivered: no encoder is installed. Browser compressed-format support alone is not an encoded asset test.',
 'Full native master: 46 scenes, including all 45 source scenes and all 189 people. Source and pilot hashes are recorded in the preservation report.',
 'See REPORT.md and evidence/browser-performance.json for transferred bytes, draw calls, texture estimates, sample counts and complete test conditions.'
]
c.setFont('Helvetica',11)
for line in notes:
 c.setFillColor(HexColor('#c8cdce'));c.drawString(28,y,line);y-=26
c.save();print(out)
items=[]
for key in ['far','middle','near']:
 for prefix,title in [('blender-baseline','Original Rev15O'),('blender-pilot','Blender pilot'),('browser-desktop','Browser pilot'),('browser-clear','Browser fog off')]:items.append(f'<figure><img loading="lazy" src="../renders/{prefix}-{key}.png"><figcaption>{key} · {title}</figcaption></figure>')
(R/'review/GALLERY.html').write_text('<!doctype html><meta charset="utf-8"><title>Gullyverse night pilot</title><style>body{background:#121c25;color:#f0ddbc;font:16px system-ui;margin:30px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}figure{margin:0}img{width:100%}figcaption{margin:10px 0}</style><h1>Gullyverse / Rev15P night pilot</h1><p>Isolated experiment. Rev15O remains authoritative. Browser performance goals are not met in software rendering.</p><div class="grid">'+''.join(items)+'</div>')
