import json, math, shutil
from pathlib import Path

O=Path(__file__).resolve().parents[1]
R=O.parents[1]
inv=json.loads((O/'evidence/inventory.json').read_text())
author=json.loads((O/'evidence/house-authoring-reference.json').read_text())
camera_by_name={c['name']:c for c in inv['cameras']}
poses=[]
def add(id,title,section,mode='inspection',scene='full',camera=None,position=None,target=None,lens=24,ortho=None,viewport=None,notes='',reuse=None):
    row={'id':id,'title':title,'section':section,'lighting':mode,'scene':scene,'viewport':viewport or [1280,720],'notes':notes,'file':'renders/'+id+'.png'}
    if camera:row['sourceCamera']=camera;row['camera']=camera_by_name[camera]
    else:row.update(position=position,target=target,lens=lens,ortho=ortho)
    if reuse:row['reuse']=reuse
    poses.append(row)

add('01-night-lane','Market lane / arrival','Night overview','original',camera='WORLD REVIEW / 01-lane-entry')
add('02-night-arrival','Approach, navigation board and courtyard entry','Night overview','original',position=[0,0,9.2],target=[0,21,10.5],lens=20)
add('03-night-courtyard','Screen, crowd and surrounding houses','Night overview','original',camera='REV09 CAMERA / 04-front')
add('04-night-reverse','Courtyard / looking back toward the market','Night overview','original',camera='REV09 CAMERA / 05-back')
add('05-night-team','Organising Committee mural / current wall','Night overview','original',position=[9.4,31.445,9.25],target=[15.13,31.445,9.25],lens=22,viewport=[1600,900],reuse='../team-wall-rev15j1-full-heading-2026-11-10/renders/01-organising-committee-laptop.png')
add('06-night-events','Events wall and house context','Night overview','original',position=[-8,30.5,9.3],target=[-15.9,31.1,10.0],lens=23)
add('07-plan','Whole environment / top plan','Layout',scene='full',position=[0,12,100],target=[0,12,0],ortho=114,notes='Top view rotated to fit the complete lane and courtyard into one frame.')
poses[-1]['roll']=math.pi/2
add('08-aerial','Whole environment / elevated overview','Layout',position=[66,-65,68],target=[0,12,9],ortho=140)

shops=[('L25','Left shop / lane -25 m',-1,-25,'21-shop-left-25','31-shop-inside-1'),('L07','Left shop / lane -7 m',-1,-7,'22-shop-left-7','32-shop-inside-2'),('L02','Left shop / lane +2 m',-1,2,'23-shop-left2','33-shop-inside-3'),('R16','Right shop / lane -16 m',1,-16,'24-shop-right-16','34-shop-inside-4'),('R07','Right shop / lane -7 m',1,-7,'25-shop-right-7','35-shop-inside-5')]
for i,(key,title,side,y,front,inside) in enumerate(shops):
    add(f'{9+i*2:02d}-shop-{key}-open',title+' / open frontage','Open shops',camera=front,notes='Current modelled open state; original counter, stock and recess geometry.')
    add(f'{10+i*2:02d}-shop-{key}-inside',title+' / interior and stock','Open shops',camera=inside,notes='Interior inspection using additional review lighting. Existing optional shop supports remain at 0 W.')
for i,(key,label) in enumerate([('chaar-diwari','Chaar Diwari'),('ritviz','Ritviz'),('neha-kakkar','Neha Kakkar')]):
    add(f'{19+i*2:02d}-shutter-{key}',label+' / closed shutter frontage','Closed shops and shutters',camera='ART-'+key+'-front',notes='Existing closed facade; no invented open/close animation.')
    add(f'{20+i*2:02d}-shutter-{key}-grooves',label+' / slats, grooves and paint detail','Closed shops and shutters',camera='ART-'+key+'-grazing')

for i,h in enumerate(author['houses']):
    edge=h['edge'];front=h['frontM'];a,b=h['alongM'];center=(a+b)/2
    house_objects=[o for o in inv['objects'] if f'/ REV12 / {h["id"]} /' in o['name']]
    low=.3
    high=max([h['mainRoofZ']+h['parapetM']]+[o['max'][2] for o in house_objects])+.8
    z=(low+high)/2
    if edge=='left':target=[-front*.85,center,z];position=[target[0]+21,center,z];width=h['widthM']
    elif edge=='right':target=[front*.85,center,z];position=[target[0]-21,center,z];width=h['widthM']
    elif edge=='back':target=[center*.85,front,z];position=[target[0],front-1.4,z];width=h['widthM']*.85
    else:target=[center*.85,front,z];position=[target[0],front+1.4,z];width=h['widthM']*.85
    height=high-low
    scale=max(height,width/(1000/1400))*1.10
    add(f'{25+i:02d}-house-{h["id"]}',f'House {h["id"]} / {edge} courtyard facade','Houses',scene='architecture',position=position,target=target,ortho=scale,viewport=[1000,1400],notes=f'{h["upperLevels"]} upper storeys plus lower podium levels. Architecture-only view removes crowd, screen and free artwork to expose the original wall, doors and windows.')
    poses[-1]['house']=h['id']
    if edge in ['front','back']:
        poses[-1]['nearClip']=1.34
        poses[-1]['notes']+=' Foreground buildings are clipped close to the facade plane for this inspection; projecting details may be cut at that plane.'

for i,(side,pos,target,scale) in enumerate([('west',[-75,32,13],[0,32,13],65),('east',[75,32,13],[0,32,13],65),('north',[0,105,13],[0,32,13],62),('south',[0,-55,13],[0,32,13],62)]):
    add(f'{36+i:02d}-exterior-{side}',f'Outer houses / {side} elevation','Exterior walls',scene='architecture',position=pos,target=target,ortho=scale,notes='Complete connected house shell, including the lower podium levels. Architecture-only inspection.')

add('40-windows-left','Left houses / window frames and shutters','Architectural details',scene='architecture',position=[-8,31,14.5],target=[-16.3,31,14.5],lens=38)
add('41-windows-right','Right houses / windows, frames and deep reveals','Architectural details',scene='architecture',position=[8,32.5,14.5],target=[16,32.5,14.5],lens=38)
add('42-balcony-door','Balcony, upper door and supported gallery','Architectural details',scene='architecture',position=[-8,29,15.5],target=[-16.8,30,15.3],lens=30)
add('43-roof-left','Left roofline / tanks, parapets and utility details','Roofs and services',scene='architecture',position=[-7,22,29],target=[-20,28,20],lens=25)
add('44-roof-right','Right roofline / stair access and utilities','Roofs and services',scene='architecture',position=[8,33,30],target=[21,38,21],lens=25)
add('45-stair-access','Roof stair headhouse, access door and landing','Roofs and services',scene='architecture',position=[-16.6,31,26.3],target=[-20.4,34.2,23.5],lens=32)
add('46-house-junction','House corner / joined walls and floor edges','Architectural details',scene='architecture',position=[-7,35,14],target=[-17,37,14],lens=32)
for i,(name,title) in enumerate([('ART-wall-pier-left','Market / left plaster pier artwork'),('ART-wall-pier-right','Market / right pier and wall artwork'),('ART-wall-return-left','Courtyard / left return wall artwork'),('ART-wall-return-right','Courtyard / right return wall artwork')]):
    add(f'{47+i:02d}-wall-art-{i+1}',title,'Wall finishes and artwork',camera=name)
add('51-floor-drain','Shop threshold, lane floor and drainage','Small details',position=[-1.8,-28.8,7.6],target=[-3.6,-28.65,6.03],lens=28)
add('52-sign-canopy','Shop sign, canopy edge and conduit','Small details',camera='LOOKDEV / 06-sign-and-conduit')

assert len({p['id'] for p in poses})==len(poses)
plan={'version':'FULL-ENVIRONMENT-REVIEW-20261111','masterSHA256':inv['masterSHA256'],'scene':inv['scene'],'shopStates':'Five existing open shops; three existing closed artist shutters. No new alternate states are authored.','houseCount':len(author['houses']),'houses':author['houses'],'poses':poses}
(O/'evidence/capture-plan.json').write_text(json.dumps(plan,indent=2))
for p in poses:
    if p.get('reuse'):
        source=(O/p['reuse']).resolve();shutil.copy2(source,O/p['file'])
print('PLANNED',len(poses),'views;',len(shops),'open shops;',len(author['houses']),'houses')
