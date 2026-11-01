from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
import json,hashlib,shutil,random
ROOT=Path('/workspace/Breeze-2027-wip-push');OUT=Path(__file__).resolve().parents[1];A=OUT/'assets';A.mkdir(exist_ok=True);sources=[]
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';S='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';H='/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf'
def font(n,kind=F):return ImageFont.truetype(kind,n)
def label(im,text,y,size=60,fill='#e9dfbd',kind=F):
 d=ImageDraw.Draw(im);b=d.textbbox((0,0),text,font=font(size,kind));d.text(((im.width-(b[2]-b[0]))/2,y),text,font=font(size,kind),fill=fill)
def save(im,name,origin,license):
 p=A/name;im.save(p);sources.append(dict(file='assets/'+name,origin=origin,license=license,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
shops=[('chai','चाय • नाश्ता','CHAI / NASHTA','#ac9c75','#312a23'),('kirana','किराना स्टोर','KIRANA / DAILY NEEDS','#d5c9a7','#21403f'),('repair','मोबाइल रिपेयर','MOBILE REPAIR','#274b5a','#dfcc98'),('tailor','सिलाई सेंटर','SILAI / ALTERATIONS','#8a6159','#e4cdb3'),('general','जनरल स्टोर','GENERAL STORE','#73877d','#e8dcc0'),('books','कॉपी • किताबें','BOOKS / STATIONERY','#c5ba9d','#273537')]
for key,hi,en,bg,ink in shops:
 im=Image.new('RGB',(1200,300),bg);d=ImageDraw.Draw(im);d.rectangle((12,12,1188,288),outline=ink,width=5);label(im,hi,27,90,ink,H);label(im,en,180,49,ink);rng=random.Random(key)
 for i in range(350):
  x=rng.randrange(1200);y=rng.randrange(300);d.line((x,y,x+rng.randrange(2,12),y),fill=bg,width=2)
 save(im,'shop-'+key+'.jpg','Original fictional generic shop signage authored for this concept; no named real street/business copied.','Project-authored concept graphics; DejaVu/Noto font licenses included.')
people=[('Aparna Balakrishnan','Chairperson','Aparna.jpeg'),('Bhavya Besoya','Co-Chairperson','bhavya.jpeg'),('Vedant Dubey','Administrator','vedant.jpeg'),('Jhalak Gupta','Administrator','jhalak.jpeg'),('Navya Sharma','Marketing Lead','Navya_Sharma.jpg'),('Nithya Pasupuleti','PR Lead','Nithya.jpeg'),('Khushwant Singh','Web Dev Lead','Khushwant.jpg'),('Shrijita Guha','Design Lead','Srijita.jpeg')]
for i,(name,role,file)in enumerate(people):
 im=Image.new('RGB',(600,820),'#d4c6a4');d=ImageDraw.Draw(im);d.rectangle((18,18,582,802),outline='#292b29',width=6);label(im,'THE CREW',28,68,'#292b29');label(im,'PEOPLE BEHIND THE NOISE',117,21,'#47423a');photo=ImageOps.fit(Image.open(ROOT/'public'/file).convert('RGB'),(490,470));photo=ImageOps.colorize(ImageOps.grayscale(photo),'#252c2a','#cfc5ab');im.paste(photo,(55,166));
 words=name.split();label(im,' '.join(words[:-1]).upper(),655,32,'#292b29');label(im,words[-1].upper(),696,32,'#292b29');label(im,role.upper(),753,22,'#655343');save(im,f'team-{i:02}.jpg','Existing authorized website team roster and public/'+file+'; wanted-style typographic treatment, no criminal implication.','Existing project portrait rights retained; new layout project-authored.')
for i,col in enumerate(['#c3533e','#c5a34b','#6e8b86','#525e7a']):
 im=Image.new('RGB',(600,820),'#d9cfb8');d=ImageDraw.Draw(im);d.rectangle((25,25,575,795),outline='#292c2d',width=5);d.ellipse((70,180,530,640),outline=col,width=55);d.line((40,620,550,245),fill=col,width=35);label(im,'BREEZE 2027',52,54,'#292c2d');label(im,'EVENTS',302,88,'#24282a');label(im,'POSTER STUDY',412,39,'#24282a');label(im,'EVENT ART PROXY',700,34,'#913628');label(im,'PLACEHOLDER / NOT FINAL ART',755,20,'#292c2d');save(im,f'event-{i:02}.jpg','Neutral event poster placeholder; no invented official event/lineup announcement.','Original project-authored temporary graphics.')
for key,title,sub,bg,fg in [('festival','GULLYVERSE','LANE TO CYPHER / BREEZE 2027','#b44432','#f0ddaa'),('cypher','MAKE SOME SPACE','CYPHER / WATCH / REPEAT','#254b4a','#dfd0a6'),('wayfinding','ROOFTOP AHEAD','KEEP THE LANE CLEAR','#d6c69f','#303b38')]:
 im=Image.new('RGB',(1200,500),bg);label(im,title,145,75,fg);label(im,sub,305,35,fg);save(im,'graphic-'+key+'.jpg','Original festival concept typography, distinct from missing artist graffiti.','Project-authored temporary concept artwork.')
# Selected source maps are included as actual payloads, not external paths.
manifest=json.load(open(ROOT/'assets-source/gullyverse/canal-material-study/provenance-manifest.json'))
for family in ['scuffed_cement','worn_plaster_wall']:
 for file in ['basecolor.jpg','normal.png']:
  src=ROOT/'public/models/gullyverse/canal-material-study'/family/file;p=A/(family+'-'+file);shutil.copyfile(src,p);sources.append(dict(file='assets/'+p.name,origin='Existing verified Poly Haven '+family+' 2K runtime derivative; official source specification in material-provenance.json.',license='CC0 1.0',bytes=p.stat().st_size,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
shutil.copyfile(ROOT/'assets-source/gullyverse/canal-material-study/provenance-manifest.json',A/'material-provenance.json');shutil.copyfile('/usr/share/doc/fonts-noto-core/copyright',A/'Noto-OFL.txt')
# Raster graphics embed glyphs. No existing project font binaries are redistributed.
(A/'GRAPHICS-LICENSES.txt').write_text('Concept graphics are authored in this task. Noto uses SIL Open Font License (see Noto-OFL.txt). DejaVu font license: https://dejavu-fonts.github.io/License.html . Existing project portraits/video/navigation raster retain project rights and are included for this private authorized design study; no new third-party redistribution rights are claimed.\n')
(A/'asset-provenance.json').write_text(json.dumps({'assets':sources,'peopleRoster':people,'notes':'No artist graffiti invented. Human bodies in Blender are neutral low-poly crowd proxies. Existing video frame and nav raster recorded separately after extraction.'},indent=2));print('Prepared',len(sources),'assets')
