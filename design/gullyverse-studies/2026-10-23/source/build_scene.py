import bpy,math,json,sys,os,hashlib,time,random
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];A=O/'assets';bpy.ops.wm.read_factory_settings(use_empty=True)
# METRES / X right / Y forward / Z up. All variants share these exact objects.
shared=bpy.data.collections.new('00_SHARED_SITE_ARCHITECTURE');bpy.context.scene.collection.children.link(shared);C=shared
records=[];cameras={};image_cache={}
def mat(name,color,rough=.8,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
def image(path):
 path=str(A/path)
 if path not in image_cache:image_cache[path]=bpy.data.images.load(path)
 return image_cache[path]
def texmat(name,file,rough=.8,emit=0):
 m=mat(name,(.7,.7,.7),rough);n=m.node_tree.nodes;t=n.new('ShaderNodeTexImage');t.image=image(file);p=n.get('Principled BSDF');m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if emit:m.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=emit
 return m
def plaster(name,family,color):
 m=mat(name,color,.9);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');co=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.28;l.new(co.outputs['Object'],mapping.inputs[0]);t=n.new('ShaderNodeTexImage');t.image=image(family+'-basecolor.jpg');t.projection='BOX';t.projection_blend=.2;l.new(mapping.outputs['Vector'],t.inputs['Vector']);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.48;mix.inputs[2].default_value=(*color,1);l.new(t.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color']);return m
stone=plaster('CC0 / scuffed cement / matte structural concrete','scuffed_cement',(.65,.66,.61));cream=plaster('CC0 / worn plaster / muted limewash','worn_plaster_wall',(.72,.66,.5));teal=plaster('CC0 / worn plaster / aged petrol paint','worn_plaster_wall',(.22,.42,.42));dust=mat('Dry lane dust',(.19,.19,.17),.98);slab=mat('Deck concrete',(.34,.35,.31));rust=mat('Aged steel',(.17,.18,.17),.66,.35);wood=mat('Worn wood',(.25,.17,.11));dark=mat('Shutter charcoal',(.11,.14,.14),.83);shutter=mat('Galvanised faded shutter',(.3,.33,.31),.75,.15);glass=mat('Dark blue window',(.07,.12,.16),.4,.12);ochre=mat('Ochre paint',(.52,.35,.17));terracotta=mat('Muted rust paint',(.4,.2,.15));paper=mat('Paper backing',(.68,.63,.5));warm=mat('Warm practical diffuser',(1,.68,.33),.5,emit=4);black=mat('Water tank rubber',(.035,.045,.05));cloths=[mat('Crowd clothing '+str(i),c,.95)for i,c in enumerate([(.06,.08,.095),(.2,.23,.23),(.3,.24,.2),(.27,.31,.3),(.12,.16,.2)])];skin=mat('Neutral shaded crowd proxy skin',(.21,.15,.11),.96)
def move(o,name,material):
 for col in list(o.users_collection):col.objects.unlink(o)
 C.objects.link(o);o.name=name
 if material:o.data.materials.append(material)
 return o
def cube(name,loc,scale,material,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object,name,material);o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  mod=o.modifiers.new('Small authored edge radius','BEVEL');mod.width=bev;mod.segments=1;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,r,depth,material,verts=12):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);return move(bpy.context.object,name,material)
def rod(name,p,q,r=.025,material=rust,verts=8):
 mid=(Vector(p)+Vector(q))*.5;o=cyl(name,mid,r,(Vector(q)-Vector(p)).length,material,verts);o.rotation_euler=(Vector(q)-Vector(p)).to_track_quat('Z','Y').to_euler();return o
def wire(name,points,r=.012,material=rust):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=r;curve.bevel_resolution=0;s=curve.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,curve);C.objects.link(o);o.data.materials.append(material);return o
def text(name,body,loc,size=.3,material=paper,rotation=(math.pi/2,0,0),align='CENTER'):
 curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.align_x=align;curve.size=size;curve.extrude=.001;o=bpy.data.objects.new(name,curve);C.objects.link(o);o.location=loc;o.rotation_euler=rotation;curve.materials.append(material);return o
def panel(name,file,loc,w,h,facing='front',emission=.08):
 m=texmat(name+' / raster paint',file,.9,emission);bpy.ops.mesh.primitive_plane_add(size=1,location=loc);o=move(bpy.context.object,name,m);o.scale=(w,h,1)
 # Plane local X/Y forms image right/up. Front looks toward -Y.
 o.rotation_euler=(math.pi/2,0,0)if facing=='front'else(math.pi/2,0,-math.pi/2 if facing=='right'else math.pi/2)
 return o
def area(name,loc,target,power,color,size=3):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
def mesh(name,verts,faces,material):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);C.objects.link(o);d.materials.append(material);return o
# Structural podium and accessible ramp. No stairs or elevator on visitor route.
cube('Podium / supported market base',(0,-12,2.8),(23,38,5.6),stone)
for x in [-12,-4,4,12]:
 for y in [10,26,43]:cube('Roof structural column',(x,y,3.4),(.65,.65,6.8),stone)
cube('Rooftop slab / 32m x 40m',(0,31,7.02),(32,34,.36),slab)
cube('Lane flat / 6.8m clear',(0,-20,5.87),(7.2,20,.26),dust)
mesh('Accessible ramp / 1 to 20', [(-3.6,-10,6),(3.6,-10,6),(3.6,5,6.75),(-3.6,5,6.75)],[(0,1,2,3)],dust)
# Flared apron continues at the same gentle slope into the roof-side bypass.
mesh('Flared ramp apron', [(-8,5,floor(5)),(8,5,floor(5)),(8,14,7.2),(-8,14,7.2)],[(0,1,2,3)],dust)
for x in [-15.85,15.85]:cube('Continuous rooftop parapet',(x,31,7.75),(.3,34,1.1),stone)
cube('Rear screen parapet',(0,47.8,7.75),(32,.3,1.1),stone)
for x in [-12,12]:cube('Entry parapet return',(x,14.15,7.75),(7.4,.3,1.1),stone)
# Main foreground buildings: deliberate alternating open and shuttered shops.
shopkeys=['chai','kirana','repair','tailor','general','books'];shops=[]
for side in [-1,1]:
 for i,y in enumerate([-25,-16,-7,2]):
  z=floor(y);height=[9.2,7.4,10.5,8.2][(i+(side==1))%4];wall=[cream,teal,stone,cream][(i+(side==1))%4];x=side*7.6
  cube(f'Building / {side} / {i}',(x,y,z+height/2),(7.2,8.5,height),wall,.05)
  # Projecting shopfront is a recessed opening surrounded by masonry, not a dark painted rectangle.
  front=side*3.98;open_=(i+(side==1))%3!=1
  cube('Shop recess',(front,y,z+1.58),(.28,6.9,3.16),dark)
  for by in [y-3.65,y+3.65]:cube('Shop pier',(front-side*.1,by,z+1.8),(.7,.45,3.6),wall)
  cube('Shop lintel',(front-side*.15,y,z+3.45),(.72,7.7,.45),wall)
  key=shopkeys[(i+(3 if side==1 else 0))%6]
  panel('Hand-painted '+key,'shop-'+key+'.jpg',(front-side*.4,y,z+3.65),7,.95,'right'if side==-1 else'left')
  cube('Shop canopy',(front-side*.63,y,z+3.05),(1.6,7.35,.1),[teal,terracotta,ochre][i%3])
  for by in [y-3.2,y+3.2]:rod('Awning stay',(front,by,z+3.7),(front-side*1.1,by,z+3.08),.025)
  if open_:
   cube('Shop warm interior',(front+side*.14,y,z+1.3),(.11,6.2,2.45),wood)
   for yy in [y-2.3,y,y+2.3]:
    for zz in [z+.5,z+1.25,z+2.0]:
     cube('Shop stock shelf',(front-side*.15,yy,zz),(.5,1.65,.08),paper)
     for k in range(4):cube('Dry goods carton',(front-side*.34,yy-.6+k*.4,zz+.22),(.35,.3,.36),[ochre,cream,teal][k%3])
   cube('Counter',(front-side*.7,y,z+.64),(1,3.3,1.28),wood)
   cube('Practical shop tube',(front-side*.6,y,z+2.8),(.08,1.15,.065),warm)
   shops.append({'position':[front-side*.65,y,z+2.7],'target':[0,y,z+1.6]})
  else:
   cube('Closed rolling shutter',(front-side*.19,y,z+1.4),(.12,6.9,2.8),shutter)
   for zz in range(18):cube('Shutter slat',(front-side*.28,y,z+.12+zz*.15),(.045,6.85,.023),dark)
   rod('Shutter latch',(front-side*.33,y-.4,z+.65),(front-side*.33,y+.4,z+.65),.035)
  # Balcony, shaded apartment windows and irregular added service pipes.
  balcony_z=z+4.65;cube('Cantilever balcony',(front-side*.5,y,balcony_z),(1.45,7.3,.17),slab)
  for yy in [y-2.9,y-.9,y+1.2,y+2.9]:
   cube('Window opening',(front-side*.12,yy,balcony_z+1.55),(.14,1.25,1.75),glass)
   cube('Window sill',(front-side*.27,yy,balcony_z+.66),(.45,1.45,.13),slab)
  rod('Balcony top rail',(front-side*1.12,y-3.5,balcony_z+1),(front-side*1.12,y+3.5,balcony_z+1),.025)
  for j in range(15):rod('Balcony picket',(front-side*1.12,y-3.45+j*.49,balcony_z+.08),(front-side*1.12,y-3.45+j*.49,balcony_z+1),.016)
  wire('Drain pipe',[(front-side*.3,y+3.5,z+.1),(front-side*.3,y+3.5,z+height-.3)],.055)
  cube('AC unit',(front-side*.3,y-2.5,balcony_z+2.7),(.6,.9,.6),shutter)
  for j in range(5):cube('AC louvre',(front-side*.61,y-2.5,balcony_z+2.49+j*.08),(.03,.8,.02),dark)
  # Stacked crates are kept at the edge of the lane, away from its clear central 4.2m.
  for j in range(2):cube('Store-edge crate',(side*3.05,y+2.8,z+.2+j*.39),(.52,.6,.38),wood)
  if i%2==0:cyl('Planter',(side*3.15,y-3,z+.3),.24,.6,terracotta)
# Overhead cables sag between buildings, not a neon canopy.
for y in [-22,-11,0]:
 for j in range(3):wire('Lane electrical service cable',[(-4,y,12.3+j*.14),(-2,y+.3,11.65+j*.14),(0,y+.45,11.4+j*.14),(2,y+.3,11.7+j*.14),(4,y,12.5+j*.14)],.013)
# Scooters: clear recognizable proxy silhouettes with wheels/seat/mirrors.
for side,y in [(-1,-20),(1,-10),(-1,-1)]:
 x=side*3.05;z=floor(y);cube('Parked scooter body',(x,y,z+.56),(.56,1.35,.54),[teal,ochre][side==1],.12);cube('Scooter seat',(x,y-.05,z+.91),(.47,.7,.12),black,.05)
 for yy in [y-.55,y+.6]:
  o=cyl('Scooter tyre',(x,yy,z+.28),.28,.15,black,16);o.rotation_euler[1]=math.pi/2
 rod('Scooter steering',(x,y+.5,z+.5),(x,y+.6,z+1.2),.055);rod('Scooter bars',(x-.35,y+.6,z+1.22),(x+.35,y+.6,z+1.22),.028)
 for dx in [-.32,.32]:rod('Mirror stem',(x+dx,y+.6,z+1.22),(x+dx,y+.6,z+1.5),.012);cube('Scooter mirror',(x+dx,y+.6,z+1.5),(.15,.06,.1),glass)
# Architecturally motivated screen occluder and inhabited upper terrace.
cube('Roof service room / reveal occluder',(.25,14.4,9.45),(9.2,5.6,4.5),cream,.04)
cube('Service roof cap',(.25,14.4,11.81),(9.55,5.95,.22),slab)
cyl('Service black water tank',(.6,14.6,12.65),1.15,1.45,black,24)
for z in [12.2,12.5,12.8,13.1]:cyl('Tank reinforcing rib',(.6,14.6,z),1.18,.045,black,24)
# Distinct nearby skyline: terraces, parapets, tanks; no named-city imitation.
for i,(x,y,w,d,h)in enumerate([(-25,-18,10,14,15),(24,-8,11,17,19),(-26,18,12,16,18),(27,28,14,18,23),(-20,52,11,12,16),(0,62,14,14,22),(19,57,10,15,19)]):
 cube('Neighbor mid-rise '+str(i),(x,y,h/2-1),(w,d,h),[stone,cream,teal][i%3])
 for z in [3,6.2,9.4,12.6,15.8]:
  if z>h-2:continue
  for j in range(4):
   xx=x-w*.35+j*w*.23;cube('Neighbor window',(xx,y-d/2-.02,z),(1.25,.05,1.7),glass)
 cube('Neighbor parapet',(x,y-d/2,h-.5),(w,.25,.9),slab);cyl('Neighbor water tank',(x+2,y,h+.1),.8,1.2,black,16)
# Team right / Events left. Actual authorized portraits; event art visibly proxy.
team=bpy.data.collections.new('01_SHARED_TEAM_RIGHT_AND_EVENTS_LEFT');C=team
for x in [-15,15]:cube('Destination plaster wall',(x,29,8.95),(.35,12,3.5),cream)
for i in range(8):
 yy=25.1+(i%4)*2.12;zz=8.3+(i//4)*1.38
 panel('TEAM authorized portrait '+str(i),f'team-{i:02}.jpg',(14.8,yy,zz),.94,1.28,'right')
for i in range(8):
 yy=25.1+(i%4)*2.12;zz=8.3+(i//4)*1.38
 panel('EVENTS clearly labelled placeholder '+str(i),f'event-{i%4:02}.jpg',(-14.8,yy,zz),.94,1.28,'left')
text('TEAM destination heading','TEAM / THE CREW',(14.77,29,10.92),.4,rotation=(math.pi/2,0,math.pi/2))
text('EVENTS destination heading','EVENTS / POSTER STUDY',(-14.77,29,10.92),.37,rotation=(math.pi/2,0,-math.pi/2))
# Reuse existing navigation hero raster. Structure is conceptually resized, not an unchanged imported scaffold.
signs=bpy.data.collections.new('02_SHARED_NAVIGATION_LANDMARK');C=signs
sx,sy,sz=5.6,20,7.2
for x in [-3.2,3.2]:
 rod('Navigation upright',(sx+x,sy,sz),(sx+x,sy,sz+6.1),.065);cube('Navigation base',(sx+x,sy,sz+.13),(.65,.8,.26),stone)
rod('Navigation top beam',(sx-3.2,sy,sz+6.1),(sx+3.2,sy,sz+6.1),.07)
panel('EXISTING GULLYVERSE hero raster','existing-gullyverse-board.png',(sx,sy-.1,sz+5),4.8,1.152,emission=.15)
for dx in [-1.8,1.8]:rod('Navigation header suspension',(sx+dx,sy,sz+6.1),(sx+dx,sy,sz+5.5),.015)
for body,x,z,w in [('EVENTS  <',sx-1.65,sz+3.9,3),('TEAM  >',sx+1.65,sz+3.9,3),('PAST SPONSORS',sx-1.65,sz+3.12,3),('CONTACT US',sx+1.65,sz+3.12,3),('AFTERMOVIE  ^',sx,sz+2.35,4)]:
 cube('Reused sign hierarchy / '+body,(x,sy,z),(w,.14,.55),dark,.035);text('Navigation / '+body,body,(x,sy-.09,z-.13),.26,paper)
# Rooftop cypher, intentionally clear center and a single digital screen on a parapet.
C=shared
# A worn thin ground circle; not a stage or raised platform.
for j in range(48):
 a=j*math.tau/48;b=(j+.62)*math.tau/48;rod('Cypher chalk arc',(4.3*math.cos(a)-6,25+4.3*math.sin(a),7.215),(4.3*math.cos(b)-6,25+4.3*math.sin(b),7.215),.016,paper,4)
cube('DJ tabletop at cypher edge',(-10.9,22.8,8.2),(2.2,.8,.09),wood)
for xx in [-11.7,-10.1]:rod('DJ table leg',(xx,22.8,7.2),(xx,22.8,8.17),.035)
for xx in [-11.45,-10.4]:cyl('Turntable platter',(xx,22.8,8.29),.23,.06,black,24)
# Existing 3-panel digital-screen proportions at uniform 0.65 concept scale.
scale=.65;cw,ch,sw,sh,gap=[x*scale for x in [13.6,9.2,4,7.2,.4]];screen_z=7.2+1.4+ch/2
for name,x,w,h in [('center',0,cw,ch),('left',-(cw/2+gap+sw/2),sw,sh),('right',cw/2+gap+sw/2,sw,sh)]:
 cube('Screen slim rear casing / '+name,(x,45.9,screen_z),(w+.12,.28,h+.12),dark)
 # Each panel uses the existing video poster frame as a single private concept still, not playback.
 panel('Existing Aftermovie / '+name,'existing-aftermovie-frame.jpg',(x,45.72,screen_z),w,h,emission=1.7)
 for dx in [-w*.36,w*.36]:cube('Parapet screen support / '+name,(x+dx,46.02,8),(.1,.1,1.6),rust)
# Crowd proxies: no invented faces, no motion capture or runtime claims.
crowd=bpy.data.collections.new('03_SHARED_NEUTRAL_CROWD_PROXIES');C=crowd;human_records=[]
def person(name,x,y,z=7.2,pose=0,index=0):
 h=1.62+(index%5)*.045;m=cloths[index%len(cloths)];hip=z+.85;shoulder=z+1.34
 for dx in [-.105,.105]:rod(name+' trouser',(x+dx,y,z+.09),(x+dx,y,hip),.09,m,7)
 # Tapered torso with visible shoulder/waist hierarchy.
 bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=.19,radius2=.255,depth=.55,location=(x,y,z+1.13));move(bpy.context.object,name+' shirt',m)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.145,location=(x,y,z+h-.145));o=move(bpy.context.object,name+' head',skin);o.scale=(.92,.95,1.15)
 for side in [-1,1]:
  root=(x+side*.23,y,shoulder);elbow=(x+side*.31,y+.02,z+1.03);hand=(x+side*.22,y+.12,z+.91)
  if pose==1 and side==1:elbow=(x+.34,y,z+1.62);hand=(x+.25,y+.02,z+1.97)
  if pose==2:elbow=(x+side*.34,y,z+1.18);hand=(x+side*.09,y+.16,z+1.12)
  rod(name+' sleeve',root,elbow,.065,m,7);rod(name+' forearm',elbow,hand,.046,skin,7)
 human_records.append({'name':name,'x':x,'y':y,'radius':.39,'top':z+h})
for row,y in enumerate([28.7,31.6,34.5,37.4,40.3,42.3]):
 for j,x in enumerate([-10,-7.6,-5.2,-2.8,2.8,5.2,7.6,10]):person('Audience %02d_%02d'%(row,j),x+(.22 if row%2 else 0),y+(.15 if j%2 else 0),pose=(j+row)%3,index=j+row)
for i,(x,y)in enumerate([(-6.9,18.8),(-7.8,20),(-9.5,26),(-10,29.5),(-7.2,22.3),(-4.2,24)]):person('Cypher silhouette '+str(i),x,y,pose=i%3,index=i+3)
for i,(x,y)in enumerate([(1.9,7.8),(2.9,8.8),(1.7,9.8)]):person('Distant lane crowd glimpse '+str(i),x,y,z=floor(y),pose=i%3,index=i+1)
# Cameras are one linked collection, identical matrices/lenses for all A/B/C scenes.
rig=bpy.data.collections.new('04_SHARED_CAMERA_RIG');C=rig
camera_specs=[('01-landing',(0,-27,7.72),(-1.2,13,9.5),32),('02-lane-walk',(0,-11,floor(-11)+1.72),(-2.8,12,9.2),30),('03-opening',(-6.1,12,8.82),(-1,29,9),25),('04-hub',(-.6,20,8.92),(1.5,32,10),22),('05-team',(8.8,26.2,8.92),(14.8,28.6,8.95),30),('06-events',(-8.8,26.2,8.92),(-14.8,28.6,8.95),30),('07-cutscene-begin',(0,25.2,8.92),(0,45.8,10.5),30),('08-cutscene-mid',(-.7,30.7,9.12),(0,45.8,10.8),30),('09-screen-reveal',(0,36.5,9.62),(0,45.8,11.35),25),('10-screen-watch',(-11.4,35.2,9.25),(0,45.8,11.4),26),('11-overhead',(1,16,91),(1,16,0),35),('12-mobile-landing',(0,-27,7.72),(-1.2,13,9.5),32)]
for name,pos,target,lens in camera_specs:
 data=bpy.data.cameras.new(name);data.lens=lens;data.sensor_width=36;data.clip_start=.08;data.clip_end=250;o=bpy.data.objects.new(name,data);C.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras[name]=o
 if 'overhead'in name:data.type='ORTHO';data.ortho_scale=89;o.rotation_euler=(0,0,0);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 records.append({'id':name,'position':pos,'target':target,'lensMM':lens,'sensorWidthMM':36,'cameraToWorld':[list(row)for row in o.matrix_world],'type':data.type,'orthoScale':data.ortho_scale})
# A true editable 20-second camera path. Rendered keyframe animatic is separately labelled.
data=bpy.data.cameras.new('13-CROWD-MOVE-20s');data.lens=29;cam=bpy.data.objects.new('13-CROWD-MOVE-20s',data);C.objects.link(cam)
path=[]
for frame,pos,target in [(1,(0,25.2,8.92),(0,45.8,10.5)),(120,(-.45,28.2,9),(0,45.8,10.7)),(240,(-.7,30.7,9.12),(0,45.8,10.8)),(360,(.45,33.3,9.4),(0,45.8,11.1)),(480,(0,36.5,9.62),(0,45.8,11.35))]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_euler',frame=frame);path.append({'frame':frame,'position':pos,'target':target})
for fc in cam.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
cameras['13-CROWD-MOVE-20s']=cam
# Variant layers add removable art direction, never different routes or screen coordinates.
scenes=[];variants={}
for code,title,power,tint in [('A','Grounded Indian Neighborhood',1500,(1,.78,.53)),('B','Festival Heavy Block',2400,(1,.65,.38)),('C','Balanced Neighborhood Cypher',1900,(1,.76,.5))]:
 scene=bpy.data.scenes.new(code+' / '+title);scenes.append(scene)
 for coll in [shared,team,signs,crowd,rig]:scene.collection.children.link(coll)
 C=bpy.data.collections.new('10_'+code+'_LIGHTING_AND_PRACTICALS');scene.collection.children.link(C)
 world=bpy.data.worlds.new(code+' night');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.065,.095,.15,1);world.node_tree.nodes['Background'].inputs[1].default_value=.3;scene.world=world
 area('Moon / broad cool night key',(0,-5,31),(0,8,7),2300,(.48,.63,1),24)
 area('Rooftop ambient spill',(0,29,20),(0,29,7),power,(.62,.74,1),21)
 for i,p in enumerate(shops):area('Warm open-shop spill '+str(i),p['position'],p['target'],145 if code=='A'else 200,tint,2.2)
 for x in [-14,14]:
  cube('Wall practical casing',(x,28.5,11.5),(.35,.5,.12),rust);cube('Wall practical diffuser',(x,28.5,11.41),(.28,.4,.04),warm);area('Poster wall gentle spill',(x,28.5,11.3),(x,28.5,8),180,tint,3)
 area('Soft screen spill',(0,44.8,11.5),(0,34,8.3),650 if code=='A'else 1050,(.67,.76,1),7)
 area('Signboard practical',(5.6,18.9,13.2),(5.6,20,10),130,(1,.85,.64),3)
 # Local haze is a design volume only; website atmosphere is untouched.
 vol=bpy.data.materials.new(code+' subtle distance haze');vol.use_nodes=True;n=vol.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.004;v.inputs['Color'].default_value=(.55,.61,.68,1);v.inputs['Anisotropy'].default_value=.12;vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume']);cube('Bounded lane haze',(0,1,13),(32,65,20),vol)
 art=bpy.data.collections.new('11_'+code+'_FESTIVAL_GRAPHICS_AND_PROPS');scene.collection.children.link(art);C=art
 if code in ['B','C']:
  panel('Restrained rooftop wall graphic','graphic-cypher.jpg',(-14.76,37.4,9),3.8,1.58,'left',.04)
  panel('Street wayfinding paste-up','graphic-wayfinding.jpg',(-2.665,12.4,9.1),2.6,1.08,'left',.04)
 if code=='B':
  panel('Festival takeover banner','graphic-festival.jpg',(0,-3,11.5),6.2,2.58)
  for y in [-18,-1,24]:
   pts=[]
   for j in range(9):
    x=-3.4+j*.85;z=12.2-.7*math.sin(j/8*math.pi);pts.append((x,y,z));cyl('Small warm festival practical',(x,y,z-.05),.035,.1,warm,6)
   wire('Festival practical cable',pts,.009)
  for i in range(8):person('Festival extra '+str(i),(-1 if i%2 else 1)*(11.8+(i%3)*.3),26+i*2,pose=i%3,index=i)
 if code=='C':
  panel('Small festival lane poster','graphic-festival.jpg',(3.57,-8,8.7),1.15,.48,'left',.02)
  for i in range(4):person('Balanced extra '+str(i),12.1,29+i*3,pose=i%3,index=i+1)
 scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.volume_bounces=0;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.fps=24;scene.frame_start=1;scene.frame_end=480;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.7;scene.camera=cameras['01-landing'];scene.frame_set(1)
 scene['concept_only']='No runtime code, navigation, collision, performance or physical-build certification.';scene['variant']=code;variants[code]={'scene':scene.name,'title':title,'changed':'Lighting power/temperature, temporary festival graphics, secondary crowd density. Shared site/routes/cameras/screen/poster-wall positions unchanged.'}
# Remove initial empty scene; pack every image and use relative filenames.
for scene in list(bpy.data.scenes):
 if scene not in scenes:bpy.data.scenes.remove(scene)
bpy.context.window.scene=scenes[2]
for img in bpy.data.images:
 if img.source=='FILE':img.pack()
(O/'source/camera-guide.json').write_text(json.dumps({'coordinateConvention':'Blender metres, X right, Y forward, Z up','rig':records,'crowdMove':path,'variants':variants,'proposedNavigation':{'laneWidthM':6.8,'minimumIntendedClearWidthM':3,'rampRiseM':1.2,'rampRunM':24,'rampSlope':'1:20','landingDeckZ':6,'roofDeckZ':7.2,'roofDimensionsM':[32,34],'hub':[0,22,7.2],'teamRight':[15,29,7.2],'eventsLeft':[-15,29,7.2],'screen':[0,45.8,screen_z],'signboardCenter':[sx,sy,sz],'screenNativePanelDimensionsM':[13.6,9.2,4,7.2,.4],'screenUniformConceptScale':.65}},indent=2))
# Scene-side evidence: actual mesh counts, shared datablocks and visibility ray occlusion.
stats=[]
for scene in scenes:
 deps=bpy.context.evaluated_depsgraph_get();meshes=[o for o in scene.objects if o.type=='MESH'];triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons);stats.append({'variant':scene['variant'],'scene':scene.name,'meshObjects':len(meshes),'rawMeshTriangles':triangles,'curvesAndTextObjects':sum(o.type in ['CURVE','FONT']for o in scene.objects),'lights':sum(o.type=='LIGHT'for o in scene.objects),'sharedArchitectureObjectCount':len(shared.objects),'packedImages':len([i for i in bpy.data.images if i.packed_file])})
(O/'evidence/scene-budget.json').write_text(json.dumps(stats,indent=2));(O/'evidence/crowd-proxy-centres.json').write_text(json.dumps(human_records,indent=2));
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/Gullyverse-Lane-Rooftop-ABC.blend'),compress=True);print('MASTER_SAVED',len(bpy.data.objects),len(bpy.data.images),flush=True)
