from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'delivery/labels';P.mkdir(exist_ok=True)
labels=[('SNACKS','#c85c25'),('SPICES','#a63127'),('BISCUITS','#ba932e'),('TEA','#236959'),('SOAP','#527a92'),('RICE','#bdac80'),('DAL','#bca23c'),('USB / CABLE','#284654')]
for i,(name,col) in enumerate(labels):
 im=Image.new('RGB',(192,256),col);d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
 d.rectangle((8,9,183,246),outline='#e1ce96',width=3)
 for y in [13,18,23,230,235,240]:d.line((10,y,182,y),fill='#dabd8a',width=2)
 d.rounded_rectangle((19,63,173,122),radius=5,fill='#efe3bd');d.text((96,90),name,font=font,fill='#26302b',anchor='mm')
 d.ellipse((61,142,131,201),fill='#e1b557',outline='#f3d795',width=4);d.text((96,158),'DAILY',font=small,fill='#473a25',anchor='mt');d.text((96,177),'FRESH',font=small,fill='#473a25',anchor='mt');d.text((96,211),'10 / 20',font=small,fill='#f5edda',anchor='mm');im.save(P/f'pack-{i}.png')
print('8 original unbranded package labels')
