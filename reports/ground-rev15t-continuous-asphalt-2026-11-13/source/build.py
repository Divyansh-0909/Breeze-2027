import bpy,json,hashlib,math,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'source/road-layout.json').read_text());random.seed(cfg['seed'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=Path(cfg['masterInput']);assert sha(P)==cfg['inputSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes}
source_state={o.name:{'data':o.data,'matrix':[list(r) for r in o.matrix_world],'hidden':o.hide_render} for o in base.objects}
s=base.copy();s.name='REV15T / Continuous asphalt gully and cypher'
for co in list(s.collection.children):s.collection.children.unlink(co)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for o in base.objects:
 a=o.copy();a.name='REV15T / '+o.name.removeprefix('REV15S / ')
 if o.type in ['LIGHT','CAMERA']:a.data=o.data.copy()
 s.collection.objects.link(a);copies[o]=a
for o,a in copies.items():
 if o.parent in copies:a.parent=copies[o.parent]
 if a.animation_data:
  for f in a.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15T / independent view')
for x in list(s.view_layers):
 if x!=layer:s.view_layers.remove(x)
bpy.context.window.view_layer=layer;layer.use_pass_z=True
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
assets=bpy.data.collections.new('REV15T / Asphalt road and edge details');s.collection.children.link(assets)
cx,cy=cfg['circle']['centre'];crowd=[o for o in base.objects if o.type=='MESH' and o.data.name.startswith('REV13A shared')]
feet=[o.matrix_world.translation.copy() for o in crowd];holes=[];omitted=[]
for h in cfg['holes']:
 if any(((p.x-h['x'])/h['rx'])**2+((p.y-h['y'])/h['ry'])**2<2.1 for p in feet):omitted.append(h['id']);continue
 assert abs(h['x'])-h['rx']*1.18>cfg['centralClearHalfWidth'] or h['y']>14
 assert math.hypot(h['x']-cx,h['y']-cy)-max(h['rx'],h['ry'])*1.18>cfg['circle']['clearRadius']
 holes.append(h)
def depression(x,y):
 d=0
 for h in holes:
  dx=(x-h['x'])/h['rx'];dy=(y-h['y'])/h['ry'];a=math.atan2(dy,dx);q=math.hypot(dx,dy)/(1+.10*math.sin(a*5+h['phase'])+.065*math.cos(a*9-h['phase']))
  if q<1:d=max(d,h['depth']*(1-q*q)**.64)
 return d
def grade(y):
 return 6.0 if y<=-10 else 6+.05*(y+10) if y<14 else 7.2
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.new('REV15T / '+name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
road=mat('Reference-authored worn asphalt',(.07,.07,.066));nd=road.node_tree.nodes;lk=road.node_tree.links;b=nd['Principled BSDF']
uv=nd.new('ShaderNodeUVMap');uv.uv_map='RoadWorldUV'
for file,socket,noncolor in [('road-world-color.png','Base Color',False),('road-world-roughness.png','Roughness',True)]:
 im=bpy.data.images.load(str(R/'textures'/file));im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';im.pack();t=nd.new('ShaderNodeTexImage');t.image=im;t.interpolation='Linear';lk.new(uv.outputs['UV'],t.inputs['Vector']);lk.new(t.outputs['Color'],b.inputs[socket])
im=bpy.data.images.load(str(R/'textures/asphalt-2m-normal.png'));im.colorspace_settings.name='Non-Color';im.pack();u=nd.new('ShaderNodeUVMap');u.uv_map='RoadDetailUV';t=nd.new('ShaderNodeTexImage');t.image=im;t.extension='REPEAT';lk.new(u.outputs['UV'],t.inputs['Vector']);n=nd.new('ShaderNodeNormalMap');n.uv_map='RoadDetailUV';n.inputs['Strength'].default_value=.8;lk.new(t.outputs['Color'],n.inputs['Color']);lk.new(n.outputs['Normal'],b.inputs['Normal'])
road['authoringMetres']=True;road['detailTileMetres']=2
shoulder=mat('unchanged structural floor edge',(.15,.14,.12),.92)
steel=mat('weathered drain iron',(.055,.058,.05),.72,.65);recess=mat('dark grate recess',(.012,.014,.012),.94);gravelmat=[mat('loose aggregate '+str(i),c,.94) for i,c in enumerate([(.16,.13,.09),(.21,.19,.15),(.10,.09,.07)])]
water=mat('shallow settled water',(.037,.034,.025),.15);wb=water.node_tree.nodes['Principled BSDF'];wb.inputs['IOR'].default_value=1.333;wb.inputs['Coat Weight'].default_value=.3;wb.inputs['Coat Roughness'].default_value=.11
def mesh(name,verts,faces,mats,indices=None,roadUV=False):
 me=bpy.data.meshes.new('REV15T / '+name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('REV15T / '+name,me);assets.objects.link(o)
 for m in mats:me.materials.append(m)
 if indices:
  for p,i in zip(me.polygons,indices):p.material_index=i
 if roadUV:
  globalUV=me.uv_layers.new(name='RoadWorldUV');detailUV=me.uv_layers.new(name='RoadDetailUV')
  for lp in me.loops:
   p=me.vertices[lp.vertex_index].co;globalUV.data[lp.index].uv=((p.x+16)/32,(p.y+30)/78);detailUV.data[lp.index].uv=(p.x/2,p.y/2)
  me.uv_layers.active=globalUV
 return o
ground=[];hidden=[];floorproof=[]
keys=['Lane flat / 6.8m clear','Accessible ramp / 1 to 20','Flared ramp apron','Rooftop slab / 32m x 40m']
for key in keys:
 old=next(o for o in base.objects if key in o.name and o.type=='MESH');a=copies[old];a.hide_render=True;a.hide_viewport=True;a['navigationBaselineOnly']=True;hidden.append(a.name)
 ovs=[old.matrix_world@v.co for v in old.data.vertices];verts=[];faces=[];indices=[];cache={};edgepaths={};topfaces=[]
 def vi(p):
  key=tuple(round(float(v),6) for v in p)
  if key not in cache:cache[key]=len(verts);verts.append(tuple(p))
  return cache[key]
 maxw=max(p.x for p in ovs)-min(p.x for p in ovs);step=.10 if key.startswith('Lane flat') else (.19 if maxw<10 else .28);nx=max(1,math.ceil(maxw/step))
 for f in old.data.polygons:
  normal=old.matrix_world.to_3x3()@f.normal
  if normal.z<.9:continue
  pts=[ovs[i] for i in f.vertices];assert len(pts)==4
  bot=sorted(sorted(pts,key=lambda p:p.y)[:2],key=lambda p:p.x);top=sorted(sorted(pts,key=lambda p:p.y)[2:],key=lambda p:p.x);p00,p10=bot;p01,p11=top
  ny=max(1,math.ceil(max((p01-p00).length,(p11-p10).length)/step))
  grid=[]
  for j in range(ny+1):
   vv=j/ny;row=[]
   for i in range(nx+1):
    uu=i/nx;p=p00*(1-uu)*(1-vv)+p10*uu*(1-vv)+p01*(1-uu)*vv+p11*uu*vv;p.z-=depression(p.x,p.y);row.append(vi(p))
   grid.append(row)
  for j in range(ny):
   for i in range(nx):faces.append((grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]));indices.append(0)
  # Store exact edge subdivisions so original side faces join the new top.
  for p,q,path in [(p00,p10,grid[0]),(p10,p11,[row[-1] for row in grid]),(p11,p01,list(reversed(grid[-1]))),(p01,p00,list(reversed([row[0] for row in grid])))]:
   kp,kq=tuple(round(float(v),6) for v in p),tuple(round(float(v),6) for v in q);edgepaths[(kp,kq)]=path;edgepaths[(kq,kp)]=list(reversed(path))
 for f in old.data.polygons:
  if (old.matrix_world.to_3x3()@f.normal).z>=.9:continue
  ids=list(f.vertices);poly=[]
  for i,vid in enumerate(ids):
   p,q=ovs[vid],ovs[ids[(i+1)%len(ids)]];kp,kq=tuple(round(float(v),6) for v in p),tuple(round(float(v),6) for v in q)
   path=edgepaths.get((kp,kq));poly.extend(path[:-1] if path else [vi(p)])
  faces.append(tuple(poly));indices.append(1)
 o=mesh(key+' / asphalt replacement',verts,faces,[road,shoulder],indices,True);o['groundSurface']=True;o['navigationSourceObject']=a.name;o['gradePreserved']=True;o['collisionPolicy']='Retain original smooth navigation shell';ground.append(o)
 # Every original footprint boundary vertex must remain at its original height.
 for p in ovs:
  if any(abs(v[0]-p.x)<1e-5 and abs(v[1]-p.y)<1e-5 and abs(v[2]-p.z)<1e-5 for v in verts):continue
  raise AssertionError(('Original boundary moved',key,list(p)))
 floorproof.append({'name':key,'original':old.name,'replacement':o.name,'vertices':len(verts),'faces':len(faces),'originalBoundaryVerticesRetained':len(ovs),'bounds':[[min(v[i] for v in verts) for i in range(3)],[max(v[i] for v in verts) for i in range(3)]]})
# The ring is painted flush in the shared world map, replacing raised block arcs.
arcs=[]
for old,a in copies.items():
 if 'Cypher chalk arc' in old.name:a.hide_render=True;a.hide_viewport=True;arcs.append(a.name)
def box_geometry(vs,fs,x,y,z,w,l,h):
 start=len(vs);vs.extend([(x+u*w/2,y+v*l/2,z+q*h/2) for u,v,q in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]])
 fs.extend([tuple(start+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])
# Three nearly flush drain covers sit outside the walking strip.
grates=[]
for i,(x,y,w,l) in enumerate([(-3.2,-16.3,.36,.65),(3.2,-1.4,.36,.65),(-11.5,35.7,.48,.76)]):
 z=grade(y);vs=[];fs=[];ids=[]
 # Each bar follows the existing grade over its short footprint.
 for yy in [-l/2,l/2]:
  n=len(fs);box_geometry(vs,fs,x,y+yy,grade(y+yy)+.005,w,.025,.012);ids.extend([0]*(len(fs)-n))
 for xx in [-w/2,w/2]:
  n=len(fs);box_geometry(vs,fs,x+xx,y,z+.003,.025,l,.012);ids.extend([0]*(len(fs)-n))
 n=len(fs);box_geometry(vs,fs,x,y,z-.004,w*.88,l*.88,.012);ids.extend([1]*(len(fs)-n))
 for j in range(8):
  yy=-l*.40+j*l*.8/7;n=len(fs);box_geometry(vs,fs,x,y+yy,grade(y+yy)+.005,w*.86,.018,.012);ids.extend([0]*(len(fs)-n))
 o=mesh('nearly flush drain '+str(i+1),vs,fs,[steel,recess],ids);o['maxRiseMetres']=.011;grates.append(o)
# Low, sparse loose aggregate at broken rims; one batched mesh.
vs=[];fs=[];mi=[];stones=0
for h in holes:
 for i in range(15):
  a=random.uniform(0,math.tau);r=random.uniform(.94,1.16);x=h['x']+math.cos(a)*h['rx']*r;y=h['y']+math.sin(a)*h['ry']*r
  if abs(x)<1.4 or math.hypot(x-cx,y-cy)<4.65:continue
  z=grade(y)-depression(x,y)+.003;rr=random.uniform(.012,.036);start=len(vs);vs.extend([(x-rr,y,z),(x,y-rr*.7,z),(x+rr,y,z),(x,y+rr*.8,z),(x+rr*.1,y,z+rr*.48)])
  fs.extend([tuple(start+j for j in f) for f in [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]]);mi.extend([i%3]*5);stones+=1
mesh('batched loose aggregate',vs,fs,gravelmat,mi)
ponds=[]
for h in holes:
 if not h['puddle']:continue
 z=grade(h['y'])-h['depth']*.48;pts=[(h['x'],h['y'],z)]
 for j in range(40):
  a=math.tau*j/40;rr=.43*(1+.08*math.sin(a*5+h['phase']));pts.append((h['x']+math.cos(a)*h['rx']*rr,h['y']+math.sin(a)*h['ry']*rr,z))
 fs=[(0,1+j,1+(j+1)%40) for j in range(40)];o=mesh('shallow damp pocket '+h['id'],pts,fs,[water]);o['defectId']=h['id'];ponds.append(o)
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert len(crowd)==189 and len([o for o in s.objects if o.get('artKind')])==8
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert all(o.data is st['data'] and [list(r) for r in o.matrix_world]==st['matrix'] and o.hide_render==st['hidden'] for o in base.objects for st in [source_state[o.name]])
assert all(o.data is a.data for o,a in copies.items() if o.type=='MESH')
for y in [-30,-18,-10,-5,0,5,9,14,22,25,35,48]:
 for x in [-1.4,0,1.4]:assert depression(x,y)==0
for i in range(25):
 a=i*math.tau/25
 for rr in [0,2,4.5]:assert depression(cx+math.cos(a)*rr,cy+math.sin(a)*rr)==0
bpy.context.preferences.filepaths.save_version=0;out=Path(cfg['masterOutput']);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.data.libraries.write(str(R/'delivery/Rev15T-Asphalt-Ground-Additions.blend'),{assets},fake_user=True,compress=True)
proof={'status':'PASS','scene':s.name,'source':str(P),'sourceSHA256':sha(P),'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'historicalScenesPreserved':len(history),'floors':floorproof,'newObjects':len(assets.objects),'holes':holes,'omittedToProtectCrowdFeet':omitted,'repairPatches':len(cfg['patches']),'puddles':len(ponds),'looseAggregatePieces':stones,'drainCovers':len(grates),'paintedCircle':cfg['circle'],'oldRaisedArcObjectsHidden':len(arcs),'all189CrowdRetained':True,'all8MuralsRetained':True,'sourceSceneObjectsAndDataUnchanged':True,'shopsAndSignsUnchanged':True,'lightingUnchanged':True,'centralMovementStripAndCircleFlat':True,'rampGradeAndOriginalBoundariesPreserved':True,'publicWebsiteChanged':False}
assert proof['sourceSHA256']==cfg['inputSHA256'];(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('BUILD_DONE',json.dumps({k:v for k,v in proof.items() if k not in ['holes','floors']}),flush=True)
