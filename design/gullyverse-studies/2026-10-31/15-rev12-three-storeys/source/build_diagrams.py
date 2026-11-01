import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parents[1];R=O/'review';d=json.loads((O/'evidence/authoring.json').read_text());q=json.loads((O/'evidence/storey-qa.json').read_text());old=json.loads((O/'evidence/before-storey-survey.json').read_text());F=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);by={h['id']:h for h in d['houses']};before={h['id']:h for h in old['rows']};order=['F1','L1','L2','L3','B1','B2','B3','R3','R2','R1','F2']
for edition in['before','after']:
 im=Image.new('RGB',(1500,1120),'#faf9f6');p=ImageDraw.Draw(im);p.text((30,22),'ALL 11 PARCELS / '+('Rev11 BEFORE: 8 below minimum'if edition=='before'else'Rev12 AFTER: 11/11 have 3+ upper storeys'),font=F(29),fill='#172b36');P=lambda x,y:(750+16*x,1050-16*y);p.rectangle((*P(-16,48),*P(16,14)),outline='#75489b',width=4);p.multiline_text(P(-14,37),'PROTECTED 32 × 34m\n1,088m² / Z7.2m\n180 original C180\n+7% proposal unchanged\n\nOPEN SKY / NO CEILING',font=F(21),fill='#75489b',spacing=9)
 for key in order:
  h=by[key];count=before[key]['actualCourtResidentialLevels']if edition=='before'else d['targetLevels'][key];col='#d67e77'if count<3 else'#a4c3ac';(x0,x1),(y0,y1)=h['footprint'];p.rectangle((*P(x0,y1),*P(x1,y0)),fill=col,outline='#172b36',width=2);pp=P((x0+x1)/2,(y0+y1)/2);p.text((pp[0]-30,pp[1]-23),key+'\n'+str(count)+' levels',font=F(19),fill='#172b36')
 p.text((30,1010),'Red = fewer than 3 REAL occupied-looking levels ABOVE the courtyard; lower supports / roof huts excluded.',font=F(20),fill='#172b36');p.text((30,1060),'16.6m entry clear. Same footprints, all ten shared-body junctions closed. Measured plan, not a render.',font=F(21),fill='#172b36');im.save(R/('storey-plan-'+edition+'.png'))
im=Image.new('RGB',(2200,1380),'#faf9f6');p=ImageDraw.Draw(im);p.text((30,20),'UNROLLED COURTYARD ELEVATION / actual measured slabs, roof huts excluded',font=F(32),fill='#172b36')
for k,edition in enumerate(['before','after']):
 ybase=610+640*k;p.text((30,ybase-500),'REV11 BEFORE'if edition=='before'else'REV12 AFTER',font=F(24),fill='#172b36')
 for i,key in enumerate(order):
  h=by[key];n=before[key]['actualCourtResidentialLevels']if edition=='before'else d['targetLevels'][key];x0=150+i*180;x1=x0+160;roof=before[key]['mainRoofZ']if edition=='before'else h['mainRoofZ'];col='#d67e77'if n<3 else'#a4c3ac';p.rectangle((x0,ybase-(roof-7.2)*27,x1,ybase),fill=col,outline='#172b36',width=3)
  for lev in range(n):
   z=7.2+lev*3;yy=ybase-(z-7.2)*27;p.line((x0,yy,x1,yy),fill='#172b36',width=2);p.text((x0+5,yy-64),f'L{lev+1}: {z:.1f}m',font=F(17),fill='#172b36')
  p.text((x0+5,ybase+12),key+f' / {n}',font=F(22),fill='#172b36');p.text((x0+5,ybase-(roof-7.2)*27-27),f'roof {roof:.2f}',font=F(16),fill='#172b36')
 p.line((100,ybase,2160,ybase),fill='#75489b',width=4);p.text((30,ybase+48),'Z7.2m courtyard datum. Each column is one named parcel; widths diagrammatic, physical counts independently ray-verified.',font=F(20),fill='#172b36')
 # One correctly scaled 1.7m stick figure adjacent to the measured levels.
 xx=112;p.ellipse((xx-6,ybase-1.7*27,xx+6,ybase-1.7*27+12),fill='#172b36');p.line((xx,ybase-1.7*27+12,xx,ybase-14),fill='#172b36',width=3);p.line((xx,ybase-14,xx-7,ybase),fill='#172b36',width=3);p.line((xx,ybase-14,xx+7,ybase),fill='#172b36',width=3)
im.save(R/'all-eleven-storey-elevation.png')
# Numerical schedule available as readable image in addition to machine CSV.
im=Image.new('RGB',(1600,1050),'#faf9f6');p=ImageDraw.Draw(im);p.text((30,20),'HARD STOREY GATE / 11 of 11 PASS',font=F(34),fill='#172b36');headers=['Parcel','Before','After','Physical slab top Z (m)','Main roof','Public-visible'];xs=[35,200,355,510,1150,1350]
for x,t in zip(xs,headers):p.text((x,90),t,font=F(22),fill='#172b36')
for i,key in enumerate(order):
 r=next(r for r in q['rows']if r['parcel']==key);y=155+i*65;vals=[key,str(r['beforeUpperResidentialCount']),str(r['actualIndependentSlabCount']),', '.join(f'{z:.1f}'for z in r['actualSlabTopZs']),f"{r['mainRoofZ']:.2f}",str(r['visibleLevelsFromPublicPositions'])]
 for j,(x,t)in enumerate(zip(xs,vals)):p.text((x,y),t,font=F(23),fill='#b32525'if j==1 and r['beforeUpperResidentialCount']<3 else'#172b36')
p.text((30,925),'3.0m floor pitch; 2.10m nominal doors (~2.06m below trim); 1.5m galleries; 1.05m roof guards.',font=F(23),fill='#172b36');p.text((30,977),'Visibility is from the union of valid public poses. The unchanged screen still masks lower rear floors.',font=F(22),fill='#172b36');im.save(R/'all-eleven-count-schedule.png');print('STOREY_DIAGRAMS_COMPLETE')
