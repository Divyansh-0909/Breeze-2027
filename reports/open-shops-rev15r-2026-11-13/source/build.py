import bpy,math,random,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];repo=R.parents[1];random.seed(270113)
P=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)=='f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682'
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes}
s=base.copy();s.name='REV15R / Reference-led open market shops'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={};promoted=0
for o in base.objects:
 a=o.copy();a.name='REV15R / '+o.name.removeprefix('REV15P / ')
 if o.type in ['LIGHT','CAMERA']:a.data=o.data.copy()
 if o.type=='MESH' and o.data.name.startswith('REV13A shared'):
  a.data=bpy.data.meshes[o.get('LOD0',o.data.name.rsplit('LOD',1)[0]+'LOD0')];a['reviewLOD']=0;promoted+=a.data!=o.data
 s.collection.objects.link(a);copies[o]=a
for o,a in copies.items():
 if o.parent in copies:a.parent=copies[o.parent]
 if a.animation_data:
  for f in a.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15R / independent view');layer.use_pass_z=True
for x in list(s.view_layers):
 if x!=layer:s.view_layers.remove(x)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
events=next(o for o in base.objects if o.type=='LIGHT' and 'REV15N / Poster wall gentle spill' in o.name)
team=copies[next(o for o in base.objects if o.type=='LIGHT' and 'REV15 / Poster wall gentle spill' in o.name)];team.data=events.data.copy();team.location=(13.906,31.445,11.53);team['matchedSource']=events.name
assets=bpy.data.collections.new('REV15R / Open shop additions');s.collection.children.link(assets)
def mat(name,c,rough=.8,metal=0):
 m=bpy.data.materials.new('REV15R / '+name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def worn(name,c,rough=.8,metal=0):
 m=mat(name,c,rough,metal);n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=28;noise.inputs['Detail'].default_value=2;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*.48 for v in c),1);r.color_ramp.elements[1].color=(*c,1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],b.inputs['Base Color']);bum=n.new('ShaderNodeBump');bum.inputs['Strength'].default_value=.18;bum.inputs['Distance'].default_value=.016;l.new(noise.outputs['Fac'],bum.inputs['Height']);l.new(bum.outputs['Normal'],b.inputs['Normal']);return m
steel=mat('brushed utensil steel',(.55,.58,.60),.29,.62);black=mat('blackened iron',(.023,.029,.027),.78,.3);wood=worn('handled wooden shelves',(.24,.14,.07));blue=worn('worn petrol enamel',(.035,.17,.19));cream=worn('old cream paint',(.55,.49,.35));sack=worn('woven jute',(.39,.30,.17));grain=mat('loose grain',(.6,.43,.16));green=mat('bottle glass',(.045,.21,.09),.22,.08);rubber=mat('rubber cable',(.018,.02,.018));white=mat('ceramic cup',(.78,.76,.66),.4);paper=mat('old paper',(.58,.49,.33));jarbody=mat('tinted jar',(.25,.30,.23),.23,.08);red=mat('painted lid',(.38,.045,.025),.45);warm=mat('warm tube',(.86,.74,.54));warm.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(1,.79,.55,1);warm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=2
packs=[]
for i in range(8):
 m=mat('original packet '+str(i),(.8,.7,.5),.6);im=bpy.data.images.load(str(R/f'delivery/labels/pack-{i}.png'));im.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);packs.append(m)
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');font.pack()
records=[];current=None;side=1;Y=0;Z=0
def xyz(d,u,z):return (side*(3.85+d),Y+u,Z+z-(.16 if d<0 else 0))
def track(o,name,m=None):
 o.name=f'REV15R / {current} / {name}';o['shopId']=current;o['referenceAuthored']=True
 for c in list(o.users_collection):c.objects.unlink(o)
 assets.objects.link(o)
 if m:o.data.materials.clear();o.data.materials.append(m)
 return o
def box(name,d,u,z,dep,w,h,m,bev=0):
 vs=[(x*dep/2,y*w/2,z*h/2) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.update();o=bpy.data.objects.new(name,me);o.location=xyz(d,u,z);assets.objects.link(o);track(o,name,m)
 if bev:
  b=o.modifiers.new('soft worn edges','BEVEL');b.width=bev;b.segments=2
 return o
def cylinder(name,d,u,z,r,h,m):
 vs=[(r*math.cos(i*math.tau/16),r*math.sin(i*math.tau/16),zz) for zz in [-h/2,h/2] for i in range(16)];fs=[(i,(i+1)%16,(i+1)%16+16,i+16) for i in range(16)]+[tuple(reversed(range(16))),tuple(range(16,32))];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);o.location=xyz(d,u,z);assets.objects.link(o);track(o,name,m)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def sphere(name,d,u,z,scale,m):
 vs=[(math.sin(j*math.pi/8)*math.cos(i*math.tau/16),math.sin(j*math.pi/8)*math.sin(i*math.tau/16),math.cos(j*math.pi/8)) for j in range(9) for i in range(16)];fs=[(j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i) for j in range(8) for i in range(16)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);o.location=xyz(d,u,z);o.scale=scale;assets.objects.link(o);track(o,name,m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def pipe(name,points,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*xyz(*v),1)
 o=bpy.data.objects.new(name,cu);assets.objects.link(o);return track(o,name,m)
def panel(name,d,u,z,w,h,m):
 vs=[xyz(d,u-w/2,z-h/2),xyz(d,u+w/2,z-h/2),xyz(d,u+w/2,z+h/2),xyz(d,u-w/2,z+h/2)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new()
 for a,b in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)] if side<0 else [(1,0),(0,0),(0,1),(1,1)]):a.uv=b
 o=bpy.data.objects.new(name,me);assets.objects.link(o);return track(o,name,m)
def text(body,d,u,z,size=.09,m=white):
 cu=bpy.data.curves.new(body,'FONT');cu.body=body;cu.font=font;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0008;o=bpy.data.objects.new(body,cu);assets.objects.link(o);o.location=xyz(d,u,z);o.rotation_euler=(Vector((-side,0,0))).to_track_quat('Z','Y').to_euler();return track(o,'painted '+body,m)
def packet(d,u,z,i,w=.22,h=.31):
 box('packet body',d+.025,u,z,.055,w,h,packs[i],.008);panel('printed packet',d-.008,u,z,w*.95,h*.96,packs[i])
def bottle(d,u,z,color=green):
 cylinder('returnable bottle',d,u,z+.13,.055,.26,color);cylinder('bottle neck',d,u,z+.29,.025,.11,color);cylinder('crown cap',d,u,z+.35,.027,.02,red)
def jar(d,u,z):
 cylinder('stock jar',d,u,z+.18,.13,.36,jarbody);cylinder('jar contents',d,u,z+.14,.124,.25,grain);cylinder('red jar lid',d,u,z+.37,.14,.045,red);panel('jar paper ticket',d-.132,u,z+.19,.13,.07,paper)
def kettle(d,u,z):
 sphere('tea kettle belly',d,u,z+.18,(.23,.23,.19),steel);cylinder('kettle lid',d,u,z+.34,.15,.025,steel);sphere('lid knob',d,u,z+.38,(.035,.035,.035),black)
 pipe('kettle spout',[(d,u+.13,z+.17),(d,u+.33,z+.22),(d,u+.41,z+.39)],.045,steel)
 pipe('arched kettle handle',[(d,u-.18,z+.27),(d,u-.18,z+.53),(d,u+.18,z+.53),(d,u+.18,z+.27)],.024,black)
def crate(d,u,z):
 box('crate floor',d,u,z+.025,.55,.58,.05,wood)
 for v in [-.27,.27]:
  for zz in [.09,.21,.33]:box('crate side slat',d,u+v,z+zz,.55,.035,.075,wood)
 for dd in [-.25,.25]:
  for zz in [.09,.21,.33]:box('crate end slat',d+dd,u,z+zz,.035,.58,.075,wood)
 for a in [-.13,.13]:
  for b in [-.16,0,.16]:bottle(d+a,u+b,z+.04)
shops=[('L25',-1,-25,6.06,'Kirana provisions',0),('L07',-1,-7,6.21,'Chai and biscuits',1),('L02',-1,2,6.66,'Household essentials',2),('R16',1,-16,6.06,'Mobile repair',3),('R07',1,-7,6.21,'Snacks and cold drinks',4)]
hidden=[];modified=[]
for key,side,Y,Z,title,kind in shops:
 current=key;start=len(assets.objects)
 for old,a in copies.items():
  if old.type!='MESH':continue
  centre=old.matrix_world@Vector((0,0,0))
  if 'Dry goods carton' in old.name and side*centre.x>4.3 and abs(centre.y-Y)<3.2:
   a.hide_render=True;a.hide_viewport=True;hidden.append(old.name)
  if old.name.startswith('REV15P / Shop warm interior') and abs(centre.y-Y)<.2 and side*centre.x>7:
   a.material_slots[0].link='OBJECT';a.material_slots[0].material=[blue,blue,cream,blue,cream][kind];modified.append(old.name)
 # Back wall stock racks: the previous empty brown plane is now a working shop wall.
 for u in [-2.9,-.95,.95,2.9]:box('steel rack upright',4.05,u,1.4,.045,.045,2.65,black)
 for row,z in enumerate([.42,1.02,1.62,2.22]):
  box('stock shelf',3.94,0,z,.52,5.8,.055,wood)
  for col in range(17):
   u=-2.7+col*.333
   if kind==3:
    packet(3.64,u,z+.19,7,w=.24,h=.32)
   elif (col+row)%5==0:bottle(3.89,u,z+.03)
   else:packet(3.64+random.uniform(0,.035),u,z+.21,(col+row*2+kind)%7,w=.25,h=.36)
 # High hanging strips and their support wire; retain a clear centre view.
 pipe('sachet support wire',[(.22,-2.95,2.78),(.22,0,2.72),(.22,2.95,2.78)],.007,black)
 for col,u in enumerate([-2.7,-2.35,-2,-1.65,1.6,1.95,2.3,2.65]):
  pipe('packet strip cord',[(.24,u,2.78),(.28,u,1.69 if col%2 else 1.94)],.004,black)
  for row in range(3+(col%2)):
   packet(.24+row*.012,u,2.58-row*.25,(col+kind)%5,w=.23,h=.23)
 # Small backed boards and hand painted categories on each rear wall.
 box('category board',4.10,0,2.72,.04,2.5,.28,black);text(title.upper(),4.072,0,2.72,.12)
 # Visible under-shelf practical, a local source rather than global exposure change.
 box('shelf tube diffuser',2.7,0,2.86,.06,2.8,.055,warm)
 d=bpy.data.lights.new('REV15R / '+key+' / shelf practical','AREA');d.energy=55;d.color=(1,.79,.55);d.shape='RECTANGLE';d.size=3;d.size_y=1.5;o=bpy.data.objects.new(d.name,d);assets.objects.link(o);o.location=xyz(2.65,0,2.78);o['shopId']=key
 # Counter goods fit the existing counter's upper surface.
 if kind in [0,2,4]:
  for u in [-1.15,-.72,-.29]:jar(-.55,u,1.39)
  box('balance base',-.5,.7,1.43,.35,.4,.08,blue);box('balance display',-.38,.7,1.63,.16,.21,.20,black);box('scale pan',-.52,.7,1.51,.4,.46,.035,steel)
  for u in [-2.4,2.4]:
   sphere('filled gunny sack',1.2,u,.32,(.34,.31,.42),sack);cylinder('sack rolled mouth',1.2,u,.63,.28,.06,sack);cylinder('exposed rice',1.2,u,.67,.245,.02,grain)
  crate(.55,2.5,.03)
  for i in range(4):box('uneven reserve carton',3.3,-2.3,.16+i*.28,.45,.55,.25,paper,.015)
 if kind==1:
  box('blue tea counter apron',-1.074,0,.69,.025,3.04,1.12,blue);box('steel counter sheet',-.57,0,1.39,1.0,3.18,.035,steel)
  kettle(-.55,-.7,1.43);cylinder('tea urn',-.45,.38,1.68,.18,.48,steel);cylinder('urn lid',-.45,.38,1.93,.19,.04,steel)
  for u in [1.0,1.31]:jar(-.55,u,1.43)
  box('glass washing tray',-.67,-1.28,1.43,.32,.45,.045,steel)
  for i in range(6):cylinder('chai glass',-.67+(i%2)*.12,-1.42+(i//2)*.13,1.52,.045,.14,white)
  for i in range(4):cylinder('stacked saucers',-.4,.85,1.45+i*.015,.10,.018,white)
  box('tea menu board',3.62,-1.5,2.5,.04,1.05,.48,black);text('CHAI 10   BISCUITS 5',3.59,-1.5,2.5,.07)
 if kind==3:
  box('repair mat',-.57,0,1.4,.72,1.5,.025,blue)
  for u in [-.5,-.2,.15]:box('phone awaiting repair',-.62,u,1.43,.13,.21,.018,black,.008)
  box('parts tray',-.4,.68,1.46,.28,.36,.06,steel);box('soldering station',-.35,1.15,1.51,.32,.32,.18,black)
  pipe('soldering lead',[(-.35,1.15,1.55),(-.68,.9,1.46),(-.55,.5,1.45)],.009,rubber)
  pipe('bench lamp arm',[(-.1,-1.2,1.4),(-.1,-1.2,2.0),(-.5,-1.2,2.22)],.018,steel);sphere('bench lamp shade',-.5,-1.2,2.19,(.13,.13,.07),cream)
  for u in [-2.5,-1.85,1.85,2.5]:
   pipe('hanging cable loop',[(3.56+.02*math.sin(i*math.pi/12),u+.16*math.sin(i*math.pi/12),2.45-.28*(1-math.cos(i*math.pi/12))) for i in range(25)],.015,rubber)
  for u in [-1.5,0,1.5]:box('small parts drawers',3.7,u,.7,.4,.9,.8,cream,.01)
 if kind==4:
  for i in range(5):bottle(-.5,.25+i*.2,1.4)
  crate(1.1,-2.4,.03)
  box('small cooler case',2.9,2.4,.65,.65,.7,1.25,cream,.02);panel('cooler dark door',2.56,2.4,.78,.54,.85,blue)
 records.append({'id':key,'title':title,'side':side,'y':Y,'floor':Z,'newObjects':len(assets.objects)-start,'referenceFiles':[0,1,2] if kind in [0,2,4] else [3,4] if kind==1 else [5]})
 print('SHOP_READY',key,len(assets.objects),flush=True)
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
for o in assets.objects:
 o.matrix_world=o.matrix_basis.copy()
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
assert len([o for o in s.objects if o.get('artKind')])==8
checks=[]
for o in assets.objects:
 if o.type not in ['MESH','CURVE','FONT']:continue
 if o.type=='CURVE':
  pts=[o.matrix_world@Vector(p.co[:3]) for sp in o.data.splines for p in sp.points];minimum=min(abs(p.x) for p in pts)-o.data.bevel_depth*max(o.scale)
 else:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];minimum=min(abs(p.x) for p in pts)
 checks.append(minimum)
assert min(checks)>=2.75,min(checks)
assert all(o.data.energy==0 for o in s.objects if o.type=='LIGHT' and 'Rev05B shop interior practical' in o.name)
bpy.context.preferences.filepaths.save_version=0;out=Path('/dev/shm/Gullyverse-Rev15R-Indian-Market-Open-Shops-Final.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.data.libraries.write(str(R/'delivery/Rev15R-Open-Shop-Additions-Final.blend'),{assets},fake_user=True,compress=True)
proof={'status':'PASS','sourceMaster':str(P),'sourceSHA256':sha(P),'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'historicalScenesPreserved':len(history),'newScene':s.name,'shopCount':5,'shops':records,'hiddenGenericCartons':hidden,'repaintedBackPanels':modified,'assetObjects':len(assets.objects),'all189CrowdRetained':True,'crowdPromotedToOriginalLOD0':promoted,'teamLightMatchedToEvents':True,'all8MuralSlidesRetained':True,'minimumAssetAbsX':min(checks),'centralLaneUntouched':True,'optionalRev05BSupportsStillOff':True,'newShopPracticalWatts':55,'referencePhotosAsRuntimeTextures':False,'productionWebsiteChanged':False}
(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('BUILD_DONE',json.dumps({k:v for k,v in proof.items() if k not in ['hiddenGenericCartons','shops','repaintedBackPanels']}),flush=True)
