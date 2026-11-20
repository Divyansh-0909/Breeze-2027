import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=Path('/dev/shm/Gullyverse-Rev15R-Indian-Market-Open-Shops-Final.blend');expected=json.loads((R.parent/'open-shops-rev15r-2026-11-13/evidence/build-verification.json').read_text())['editedSHA256'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(P)==expected
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15S / Reference-led realistic shop name boards'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for o in base.objects:
 a=o.copy();a.name='REV15S / '+o.name.removeprefix('REV15R / ')
 if o.type in ['LIGHT','CAMERA']:a.data=o.data.copy()
 s.collection.objects.link(a);copies[o]=a
for o,a in copies.items():
 if o.parent in copies:a.parent=copies[o.parent]
 if a.animation_data:
  for f in a.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15S / independent view');layer.use_pass_z=True
for x in list(s.view_layers):
 if x!=layer:s.view_layers.remove(x)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
assets=bpy.data.collections.new('REV15S / Shop name boards');s.collection.children.link(assets)
def material(name,color,metal=0,rough=.7):
 m=bpy.data.materials.new('REV15S / '+name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
frame=material('blackened metal folded frame',(.055,.065,.064),.64,.67);bolt=material('aged screw and edge metal',(.20,.18,.13),.7,.58);lamp=material('lamp reflector',(.53,.53,.45),.7,.32);diffuser=material('lamp diffuser',(.69,.57,.37));diffuser.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(1,.83,.58,1);diffuser.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=1.7
side=1;Y=0;Z=0;key='';records=[];hidden=[]
def xyz(d,u,z):return(side*(d-.16 if 3.4<d<3.7 else d),Y+u,Z+z)
def new(name,vs,fs,m,uv=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 if uv:
  layer=me.uv_layers.new()
  for loop,co in zip(layer.data,uv):loop.uv=co
 o=bpy.data.objects.new('REV15S / '+key+' / '+name,me);assets.objects.link(o);me.materials.append(m);o['shopId']=key;return o
def box(name,d,u,z,dep,w,h,m):
 vs=[xyz(d+x*dep/2,u+y*w/2,z+zz*h/2) for x,y,zz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];o=new(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m);b=o.modifiers.new('folded edge radius','BEVEL');b.width=.006;b.segments=2;return o
def pipe(name,pts,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*xyz(*v),1)
 o=bpy.data.objects.new('REV15S / '+key+' / '+name,cu);assets.objects.link(o);cu.materials.append(m);o['shopId']=key;return o
def face(name,d,z,w,h,m,bend=False):
 vs=[];fs=[];uv=[];n=24 if bend else 1
 for i in range(n+1):
  u=-w/2+w*i/n;dd=d+(.008*math.sin(i/n*math.pi*2) if bend else 0);vs.extend([xyz(dd,u,z-h/2),xyz(dd,u,z+h/2)])
 for i in range(n):
  fs.append((2*i,2*i+2,2*i+3,2*i+1));a=i/n;b=(i+1)/n
  if side>0:a,b=1-a,1-b
  uv.extend([(a,0),(b,0),(b,1),(a,1)])
 return new(name,vs,fs,m,uv)
def artmat(id,inside=False):
 m=material(id+(' interior paint' if inside else ' aged sign paint'),(.7,.7,.6),.03,.78);nodes=m.node_tree.nodes;links=m.node_tree.links;b=nodes['Principled BSDF'];im=bpy.data.images.load(str(R/('delivery/sign-art/'+id+'-'+('inside.png' if inside else 'face.png'))));im.pack();t=nodes.new('ShaderNodeTexImage');t.image=im;links.new(t.outputs['Color'],b.inputs['Base Color'])
 if not inside:
  rough=bpy.data.images.load(str(R/f'delivery/sign-art/{id}-roughness.png'));rough.colorspace_settings.name='Non-Color';rough.pack();t=nodes.new('ShaderNodeTexImage');t.image=rough;links.new(t.outputs['Color'],b.inputs['Roughness']);bum=nodes.new('ShaderNodeBump');bum.inputs['Strength'].default_value=.08;bum.inputs['Distance'].default_value=.001;links.new(t.outputs['Color'],bum.inputs['Height']);links.new(bum.outputs['Normal'],b.inputs['Normal'])
 return m
shops=[('L25',-1,-25,9.65),('L07',-1,-7,9.8),('L02',-1,2,10.25),('R16',1,-16,9.65),('R07',1,-7,9.8)]
for key,side,Y,Z in shops:
 m=artmat(key);box('sheet backing',3.585,0,0,.055,7.04,1.02,frame);face('bilingual painted fascia',3.545,0,6.94,.94,m,True)
 for zz in [-.497,.497]:box('folded frame rail',3.53,0,zz,.04,7.08,.035,frame)
 for u in [-3.52,3.52]:box('folded frame side',3.53,u,0,.04,.035,1.02,frame)
 for u in [-3.32,-1.1,1.1,3.32]:
  for zz in [-.42,.42]:
   box('washer',3.515,u,zz,.014,.036,.036,bolt);box('screw slot',3.505,u,zz,.004,.022,.004,frame)
 for u in [-2.15,2.15]:
  box('lamp anchor plate',3.62,u,.56,.04,.13,.16,bolt);pipe('curved lamp bracket',[(3.59,u,.6),(3.38,u,.77),(3.08,u,.77),(3.02,u,.56)],.018,frame);box('reflector hood',3.04,u,.52,.22,.36,.10,frame);box('warm lamp face',3.035,u,.465,.16,.28,.012,diffuser)
  data=bpy.data.lights.new('REV15S / '+key+' / sign wash','AREA');data.energy=10;data.color=(1,.84,.64);data.size=.9;ob=bpy.data.objects.new(data.name,data);assets.objects.link(ob);ob.location=xyz(3.02,u,.43);target=Vector(xyz(3.55,u*.7,-.08));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();ob['shopId']=key
 # Preserve the accepted interior: replace only its small category lettering.
 inside=artmat(key,True);insideZ={'L25':8.78,'L07':8.93,'L02':9.38,'R16':8.78,'R07':8.93}[key];face('matching rear shop label',7.90,insideZ-Z,2.46,.285,inside)
 for old,a in copies.items():
  if old.type=='FONT' and old.get('shopId')==key and 'painted ' in old.name and 'CHAI 10' not in old.name:a.hide_render=True;a.hide_viewport=True;hidden.append(old.name)
 records.append({'id':key,'side':side,'y':Y,'boardCentreZ':Z,'width':7.04,'height':1.02,'newSignLights':2,'wattsPerLight':10})
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
for o in assets.objects:o.matrix_world=o.matrix_basis.copy()
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert len([o for o in s.objects if o.get('artKind')])==8;assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
# Everything accepted inside the shop remains shared unchanged, except the label visibility.
assert all(a.data==o.data and list(a.location)==list(o.location) for o,a in copies.items() if o.type=='MESH')
bpy.context.preferences.filepaths.save_version=0;out=Path('/dev/shm/Gullyverse-Rev15S-Realistic-Shop-Name-Boards.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.data.libraries.write(str(R/'delivery/Rev15S-Shop-Board-Additions.blend'),{assets},fake_user=True,compress=True)
proof={'status':'PASS','source':str(P),'sourceSHA256':expected,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'historicalScenesPreserved':len(history),'shops':records,'hiddenInteriorLabels':hidden,'assets':len(assets.objects),'approvedShopMeshDataAndLocationsPreserved':True,'all189CrowdRetained':True,'all8MuralsRetained':True,'productionWebsiteChanged':False};(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');assert sha(P)==expected;print(json.dumps(proof),flush=True)
