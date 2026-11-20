from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1];B=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11';d=json.loads((R/'evidence/browser-comparison.json').read_text());cases={(x['profile'],x['version']):x for x in d['results']};W,H=1190.55,841.89;out=R/'review/Gullyverse-Rev15P2-Browser-Night-Review.pdf';c=canvas.Canvas(str(out),pagesize=(W,H));c.setTitle('Gullyverse Rev15P2 — night lighting and browser optimization')
def heading(title,sub):
 c.setFillColor(HexColor('#121c25'));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#f0ddbc'));c.setFont('Helvetica-Bold',22);c.drawString(28,H-35,title);c.setFont('Helvetica',10);c.setFillColor(HexColor('#c8cdce'));c.drawString(28,H-54,sub)
def panel(file,label,x,y,w=551,h=344):
 c.setFillColor(HexColor('#f0ddbc'));c.setFont('Helvetica',11);c.drawString(x,y+h+7,label);c.drawImage(ImageReader(str(file)),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def lines(text,x,y,size=12,gap=25):
 c.setFont('Helvetica',size);c.setFillColor(HexColor('#d0d6d8'))
 for line in text:c.drawString(x,y,line);y-=gap
for index,key in enumerate(['far','middle','near']):
 heading('GULLYVERSE / '+key.upper()+' NIGHT VIEW','12 November 2026 · Native reference, previous browser and updated browser · matching camera, lens and 1440 × 900 frame')
 panel(B/'renders'/f'blender-pilot-{key}.png','Native Blender night reference',28,408);panel(R/'renders'/f'desktop-baseline-{key}.png','Previous browser / Rev15P',611,408);panel(R/'renders'/f'desktop-updated-{key}.png','Updated browser / Rev15P2',28,28)
 old=cases['desktop','baseline']['measures'][index];new=cases['desktop','updated']['measures'][index];reduction=(1-new['completedRenderReadback']['meanMs']/old['completedRenderReadback']['meanMs'])*100
 lines(['Baked light and shadow on the static scene.','Corrected floor lightmap coordinates.','Native damp roughness; one floor-highlight light.','Original geometry, text and artwork retained.','Original quarry movement and transitions untouched.','',f'Desktop test render cost: {reduction:.0f}% lower.',f"Before {old['completedRenderReadback']['meanMs']:.0f} ms / after {new['completedRenderReadback']['meanMs']:.0f} ms.",'Cloud SwiftShader; five measured renders per view.','Readback cost is included; this is not display FPS.','Physical hardware and phones remain unmeasured.'],625,356,size=12,gap=25)
 c.showPage()
heading('MOBILE COMPARISON / SAME CAMERAS','390 × 844 CSS pixels · render DPR 0.85 · CPU emulation 4× · software rendering, not physical-phone certification')
for i,key in enumerate(['far','middle','near']):
 panel(R/'renders'/f'mobile-emulated-baseline-{key}.png','Before / '+key,28+i*195,64,w=176,h=380);panel(R/'renders'/f'mobile-emulated-updated-{key}.png','Updated / '+key,614+i*185,64,w=176,h=380)
lines(['The original scene positions and routes are retained. The browser lighting is cheaper; the physical site has not been changed.','Reduced-motion pause, HTML festival directions, one canvas, LED fog and explicit ground UV1 bindings pass.'],28,695,size=13,gap=29);c.showPage()
heading('MEASURED COST / PRESERVATION','Identical baseline and updated harness · two warm-up and five measured renders · one-pixel GPU readback forces completion')
cols=[28,310,455,600,755,910];labels=['Profile / view','Before ms','Updated ms','Reduction','CPU updated p50','Draw calls']
for x,label in zip(cols,labels):c.setFillColor(HexColor('#f0ddbc'));c.setFont('Helvetica-Bold',12);c.drawString(x,H-100,label)
y=H-132
for profile in ['desktop','mobile-emulated']:
 for i,key in enumerate(['far','middle','near']):
  old=cases[profile,'baseline']['measures'][i];new=cases[profile,'updated']['measures'][i];a=old['completedRenderReadback']['meanMs'];b=new['completedRenderReadback']['meanMs'];row=[profile+' / '+key,f'{a:.1f}',f'{b:.1f}',f'{(1-b/a)*100:.0f}%',f"{new['cpuSubmission']['p50Ms']:.1f} ms",str(new['stats']['drawCalls'])]
  for x,value in zip(cols,row):c.setFont('Helvetica',11);c.setFillColor(HexColor('#d0d6d8'));c.drawString(x,y,value)
  y-=26
lines(['The asset fell from 23.78 MB to 16.70 MB. All 447,269 triangles and base artwork image bytes are retained.','Static geometry uses baked diffuse lighting; four ground meshes retain one live specular-only light for damp highlights.','The new higher-resolution floor maps slightly increase the fair texture-source estimate: about 145.5 MB to 149.7 MB.','This estimate is not driver VRAM. GPU timer results are unmeasured when no valid non-disjoint query completes.','Five-render tail percentiles are descriptive only. Full timing samples and p50/p95/p99 are in the technical report.','The desktop ~60 FPS and mobile >=30 FPS goals are not certified; this software renderer remains below those goals.','Original quarry movement, entrance/exit transitions and walking routes are untouched. No production route was edited.','Rev15O and the packed Rev15P master remain unchanged. This is an isolated pilot update, with a verified recovery package.','Remaining limits: static shadow assumptions, approximate view-dependent metal response, and unmeasured physical-device performance.'],28,y-35,size=11,gap=27)
c.save();print(out)
