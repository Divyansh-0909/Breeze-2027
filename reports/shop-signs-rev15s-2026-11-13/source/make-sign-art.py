from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,math
R=Path(__file__).resolve().parents[1];P=R/'delivery/sign-art';P.mkdir(exist_ok=True);rng=np.random.default_rng(151113)
dev=str(R/'source/fonts/NotoSansDevanagari-Bold.ttf');serif=str(R/'source/fonts/NotoSerifDevanagari-Bold.ttf');latin=str(R/'source/fonts/DejaVuSansCondensed-Bold.ttf')
specs=[('L25','किराना स्टोर','KIRANA PROVISIONS','GRAINS  /  SPICES  /  DAILY NEEDS',(218,208,164),(139,35,31),(37,82,91)),('L07','नुक्कड़ चाय','CHAI & BISCUITS','FRESH CHAI  /  BISCUITS  /  EVERY DAY',(205,161,66),(99,31,27),(87,44,26)),('L02','जनरल स्टोर','HOUSEHOLD ESSENTIALS','SOAP  /  GRAIN  /  EVERYDAY SUPPLIES',(37,80,94),(235,211,151),(207,149,66)),('R16','मोबाइल रिपेयर','MOBILE REPAIR','REPAIRS  /  CABLES  /  ACCESSORIES',(218,215,191),(33,57,90),(161,47,37)),('R07','नाश्ता और ठंडे पेय','SNACKS & COLD DRINKS','BISCUITS  /  SNACKS  /  COLD DRINKS',(143,169,139),(122,38,31),(33,69,72))]
W,H=2560,384
def fitted(text,font,maxsize,width):
 for size in range(maxsize,25,-2):
  f=ImageFont.truetype(font,size)
  if f.getbbox(text)[2]<width:return f
 return f
def lettering(im,text,xy,font,fill,shadow=(48,40,29),outline=1):
 d=ImageDraw.Draw(im);x,y=xy;d.text((x+4,y+5),text,font=font,anchor='mm',fill=shadow,language='hi');d.text((x,y),text,font=font,anchor='mm',fill=fill,stroke_width=outline,stroke_fill=fill,language='hi')
for i,(key,hi,en,footer,bg,ink,trim) in enumerate(specs):
 im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im);d.rectangle((15,13,W-16,H-14),outline=trim,width=10);d.rectangle((33,29,W-34,H-30),outline=trim,width=2)
 lettering(im,hi,(W/2,131),fitted(hi,serif if i in [0,4] else dev,137,2140),ink)
 d.rectangle((198,215,W-198,300),fill=trim);lettering(im,en,(W/2,254),fitted(en,latin,74,2050),(237,224,180),outline=0)
 d.text((W/2,335),footer,font=ImageFont.truetype(latin,28),fill=ink,anchor='mm')
 # Small original line drawings echo the photographed painted illustrations.
 for x in [110,W-110]:
  if i==1:
   d.rounded_rectangle((x-47,111,x+38,168),radius=10,outline=ink,width=7);d.arc((x+20,116,x+66,158),270,90,fill=ink,width=7);d.line((x-55,179,x+51,179),fill=ink,width=6)
   for dx in [-20,4,28]:d.arc((x+dx-8,70,x+dx+8,115),80,265,fill=ink,width=4)
  elif i==3:
   d.rounded_rectangle((x-33,82,x+33,184),radius=9,outline=ink,width=6);d.line((x-18,98,x+18,98),fill=ink,width=3);d.ellipse((x-5,169,x+5,179),outline=ink,width=2)
  else:
   d.rectangle((x-37,101,x+37,176),outline=ink,width=5);d.line((x-37,116,x+37,116),fill=ink,width=4);d.line((x-32,164,x+32,164),fill=ink,width=3)
 # Controlled wear: variable paint fade, very small chips, and rain marks near edges.
 arr=np.array(im).astype(np.float32);noise=rng.normal(0,1.25,(H,W,1));x=np.linspace(0,1,W)[None,:,None];y=np.linspace(0,1,H)[:,None,None];arr=arr*(.965+.03*np.sin(x*4.8+i))+noise;edge=np.minimum(np.arange(H),np.arange(H)[::-1])[:,None];wear=rng.random((H,W))<(np.maximum(0,(25-edge))/25*.035+.00065);arr[wear]=np.array((104,89,68));im=Image.fromarray(np.clip(arr,0,255).astype('uint8'));d=ImageDraw.Draw(im)
 for sx in [65,900,1660,2494]:
  d.line([(sx,21),(sx+int(rng.integers(-3,4)),45)],fill=(148,119,84),width=2);d.line([(sx,H-26),(sx+2,H-43)],fill=(151,130,95),width=1)
 im.quantize(colors=256).save(P/f'{key}-face.png',optimize=True)
 rough=np.clip(181+rng.normal(0,8,(H,W)),0,255).astype('uint8');Image.fromarray(rough).quantize(colors=32).save(P/f'{key}-roughness.png',optimize=True)
 mini=Image.new('RGB',(1200,168),bg);md=ImageDraw.Draw(mini);md.rectangle((7,7,1192,160),outline=trim,width=5);lettering(mini,en,(600,80),fitted(en,latin,69,1100),ink,outline=0);mini.save(P/f'{key}-inside.png',optimize=True)
(R/'evidence/sign-art-specs.json').write_text(json.dumps([{'id':s[0],'hindi':s[1],'english':s[2],'descriptor':s[3]} for s in specs],ensure_ascii=False,indent=2));print('Five original bilingual fascia designs and five matching interior labels')
