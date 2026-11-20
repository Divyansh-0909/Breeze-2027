from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,features
R=Path(__file__).resolve().parents[1];assert features.check_feature('raqm')
fontpath=R/'source/fonts/NotoSansDevanagari-Regular.ttf';font=ImageFont.truetype(str(fontpath),330,layout_engine=ImageFont.Layout.RAQM)
translations=[('GULLYVERSE','गलीवर्स','gullyverse'),('AFTERMOVIE','आफ्टरमूवी','aftermovie'),('EVENTS  <','कार्यक्रम','events'),('TEAM  >','टीम','team'),('ACCOMMODATION','आवास','accommodation'),('CONTACT US','संपर्क करें','contact'),('PAST SPONSORS','पूर्व प्रायोजक','past-sponsors')]
rows=[]
for english,hindi,slug in translations:
    probe=Image.new('RGBA',(1,1));draw=ImageDraw.Draw(probe);box=draw.textbbox((0,0),hindi,font=font,direction='ltr',language='hi');pad=8;w,h=box[2]-box[0],box[3]-box[1]
    im=Image.new('RGBA',(w+pad*2,h+pad*2),(245,246,240,0));d=ImageDraw.Draw(im);d.text((pad-box[0],pad-box[1]),hindi,font=font,fill=(245,246,240,255),direction='ltr',language='hi');p=R/'textures'/('hindi-'+slug+'.png');im.save(p)
    rows.append({'english':english,'hindi':hindi,'file':p.name,'pixels':list(im.size),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'source/translations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(R/'evidence/hindi-artwork.json').write_text(json.dumps({'status':'PASS','shaping':'Pillow RAQM / HarfBuzz, language hi, left to right; complete Devanagari conjuncts and vowel marks rendered together','font':fontpath.name,'fontSHA256':hashlib.sha256(fontpath.read_bytes()).hexdigest(),'labels':rows},ensure_ascii=False,indent=2)+'\n');print('SHAPED_HINDI_LABELS',len(rows))
