"""Private selected C+A world pass. Data API avoids slow operator/depsgraph churn."""
import bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];BASE=O/'source/APPROVED-PILOT.blend'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='3ba2b0056a9cd12bc0fefaa9a503df0fe12539467d46a01c7fd0a91fa2124202'
src=next(s for s in bpy.data.scenes if s.get('variant')=='C+A PILOT')
s=src.copy();s.name='SELECTED C+A / Wider Neighborhood Realism';s['variant']='C+A WORLD';s.use_fake_user=True
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
hosts=bpy.data.collections.new('WORLD / inherited pilot and isolated finishes');s.collection.children.link(hosts)
for o in src.objects:hosts.objects.link(o)
details=bpy.data.collections.new('WORLD / grouped construction');s.collection.children.link(details)
bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
copies=[];parts=[];buckets={};skipped=[];zones={}
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
def uvmetre(o):
 m=o.data;uv=m.uv_layers.get('PILOT_world_metres')or m.uv_layers.new(name='PILOT_world_metres')
 for p in m.polygons:
  n=(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized();a=max(range(3),key=lambda i:abs(n[i]));sgn=1 if n[a]>0 else -1
  for li in p.loop_indices:
   v=o.matrix_world@m.vertices[m.loops[li].vertex_index].co
   uv.data[li].uv=(v.y*sgn,v.z)if a==0 else(-v.x*sgn,v.z)if a==1 else(v.x*sgn,v.y)
 m.uv_layers.active=uv;uv.active_render=True
def clone(o,mat):
 cp=o.copy();cp.name='WORLD / '+o.name;cp.data=o.data.copy();hosts.objects.unlink(o);hosts.objects.link(cp)
 cp['worldOriginalObject']=o.name;cp['pilotOriginalObject']=o.get('pilotOriginalObject',o.name)
 # Exact base topology/transforms retained. Disable only known bad inherited cavity bevel.
 disabled=[]
 if o.name.startswith(('Building /','Shop recess')):
  for mod in list(cp.modifiers):
   if mod.type=='BEVEL':disabled.append(mod.name);cp.modifiers.remove(mod)
 if cp.type=='MESH':uvmetre(cp)
 assert len(cp.material_slots)==1;cp.material_slots[0].link='OBJECT';cp.material_slots[0].material=mat
 copies.append({'original':o.name,'copy':cp.name,'semantic':cp['pilotOriginalObject'],'material':mat.name,'disabledLegacyBevels':disabled});return cp
def simple(name,col,rough=.88,metal=0):
 m=bpy.data.materials.new('WORLD / '+name);m.use_nodes=True;m.diffuse_color=(*col,1);b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
def finish(name,family,col,amount=.32,strength=.24):
 m=simple(name,col);t=m.node_tree;b=t.nodes.get('Principled BSDF')
 uv=t.nodes.new('ShaderNodeUVMap');uv.uv_map='PILOT_world_metres';scale=t.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/(1.8 if family=='worn_plaster_wall'else 1.62);t.links.new(uv.outputs[0],scale.inputs[0])
 def tex(im):
  n=t.nodes.new('ShaderNodeTexImage');n.image=im;t.links.new(scale.outputs[0],n.inputs[0]);return n
 a=tex(bpy.data.images[family+'-basecolor.jpg']);mx=t.nodes.new('ShaderNodeMixRGB');mx.inputs[0].default_value=amount;mx.inputs[1].default_value=(*col,1);t.links.new(a.outputs[0],mx.inputs[2]);t.links.new(mx.outputs[0],b.inputs['Base Color'])
 n=tex(bpy.data.images['PILOT / '+family+' / normal 1024']);nm=t.nodes.new('ShaderNodeNormalMap');nm.uv_map='PILOT_world_metres';nm.inputs['Strength'].default_value=strength;t.links.new(n.outputs[0],nm.inputs['Color']);t.links.new(nm.outputs[0],b.inputs['Normal'])
 r=tex(bpy.data.images['PILOT / '+family+' / roughness 1024']);q=t.nodes.new('ShaderNodeMath');q.operation='MULTIPLY_ADD';q.inputs[1].default_value=.20;q.inputs[2].default_value=.74;t.links.new(r.outputs[0],q.inputs[0]);t.links.new(q.outputs[0],b.inputs['Roughness']);m['sourceFamily']=family;return m
steel=bpy.data.materials['PILOT / blackened zinc and aged fixings'];zinc=bpy.data.materials['PILOT / folded galvanised sheet'];seal=bpy.data.materials['PILOT / bituminous joint and gaskets'];wood=bpy.data.materials['PILOT / worn plywood edge']
cement=finish('mineral concrete','scuffed_cement',(.34,.34,.30));lime=finish('warm grey limewash','worn_plaster_wall',(.31,.30,.255));sage=finish('faded blue-green plaster','worn_plaster_wall',(.20,.275,.265));ochre=finish('muted ochre plaster','worn_plaster_wall',(.33,.285,.205),.30)
roofmat=finish('continuous roof concrete','scuffed_cement',(.235,.25,.235),.25,.23);lane=finish('compacted cement dust','scuffed_cement',(.225,.212,.18),.21,.16);repair=finish('localized render repair','worn_plaster_wall',(.36,.34,.285),.16)
frame=simple('aged painted sash',(.11,.14,.135),.75,.3);glass=simple('dusty non-emissive glazing',(.048,.075,.083),.64,.08)
stock=[bpy.data.materials['PILOT / generic dry goods print '+str(i)]for i in range(4)]
def piece(name,v,f,mat,zone,metadata):
 bucket=buckets.setdefault((zone,mat.name),{'v':[],'f':[]});off=len(bucket['v']);bucket['v'].extend(v);bucket['f'].extend(tuple(off+j for j in p)for p in f)
 parts.append({'name':name,'zone':zone,'material':mat.name,**metadata})
def box(name,loc,dims,mat,zone):
 x,y,z=loc;a,b,c=[d/2 for d in dims];v=[(x+sx*a,y+sy*b,z+sz*c)for sx,sy,sz in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 piece(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,zone,{'location':loc,'dimensions':dims})
def rod(name,a,b,r,mat,zone,n=6):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1))if abs(d.z)<.9 else Vector((1,0,0))).normalized();w=d.cross(u);v=[list(p+r*(math.cos(2*math.pi*j/n)*u+math.sin(2*math.pi*j/n)*w))for p in[a,b]for j in range(n)]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)]
 piece(name,v,f,mat,zone,{'ends':[list(a),list(b)],'radiusM':r})
for k,(side,cy,idx)in enumerate([(-1,-7,2),(-1,2,3),(1,-25,0),(1,-16,1),(1,-7,2),(1,2,3)]):
 zone=f'bay {side:+d} Y{cy:+d}';g=floor(cy);material=[cement,lime,sage,cement,lime,ochre][k];building=bpy.data.objects[f'Building / {side} / {idx}'];open_=not(side==1 and cy in[-25,2])
 if any(sl.material and sl.material.name.startswith('ART /')for sl in building.material_slots):skipped.append(building.name)
 else:clone(building,material)
 for prefix in['Shop pier','Shop lintel','Shop recess','Shop canopy']:
  for o in[o for o in src.objects if o.name.startswith(prefix)and o.location.x*side>0 and abs(o.location.y-cy)<4]:
   if any(sl.material and sl.material.name.startswith('ART /')for sl in o.material_slots):skipped.append(o.name);continue
   clone(o,steel if prefix=='Shop recess'else zinc if prefix=='Shop canopy'else material)
 for dy in[-3.1,3.1]:box('returned opening frame',(side*3.8,cy+dy,g+1.49),(.07,.065,2.98),zinc,zone)
 box('rolling steel housing',(side*3.8,cy,g+3.105),(.15,6.26,.18),zinc,zone);box('sign folded tray',(side*3.63,cy,g+3.65),(.045,7.04,.98),steel,zone)
 for dy in[-3.08,3.08]:rod('sign stand-off',(side*3.95,cy+dy,g+3.66),(side*3.59,cy+dy,g+3.66),.019,zinc,zone)
 box('folded awning drip',(side*2.53,cy,g+3.055),(.035,7.36,.105 if k%2 else .145),zinc,zone)
 for j in range(3+k%3):box('awning standing seam',(side*3.33,cy-2.8+j*5.6/(2+k%3),g+3.11),(1.57,.025,.025),zinc,zone)
 if open_:box('thin threshold',(side*3.98,cy,g+.017),(.18,6.12,.003),zinc,zone)
 yy=cy+(3.34 if k%2 else -3.34);rod('electrical riser',(side*3.50,yy,g+.2),(side*3.50,yy,g+4.35),.018,zinc,zone);box('junction enclosure',(side*3.48,yy,g+3.95),(.12,.23,.32),steel,zone)
 for dy in[-3.7,3.7]:box('curb return',(side*3.49,cy+dy,g+.035),(.15,.55,.07),cement,zone)
 if building.name not in skipped:box('local plaster repair',(side*3.515,cy+(-3.68 if k%2 else 3.68),g+.25),(.02,.30,.46+.08*(k%3)),repair,zone)
 zones[zone]={'shop':[side,cy],'open':open_,'variant':k}
for j,o in enumerate([o for o in src.objects if o.name.startswith('Window opening')]):
 side=1 if o.location.x>0 else -1;y,z=o.location.y,o.location.z;zone='upper street '+str(side);clone(o,glass)
 for dy in[-.659,.659]:box('deep window jamb',(side*3.765,y+dy,z),(.13,.075,1.86),cement,zone)
 for dz in[-.908,.908]:box('window head-sill return',(side*3.765,y,z+dz),(.16,1.39,.075),cement,zone)
 box('mullion',(side*3.718,y,z),(.042,.045,1.73),frame,zone)
 for dy in[-.594,.594]:box('painted window sash',(side*3.716,y+dy,z),(.035,.045,1.74),frame,zone)
 if j%3!=1:
  for dy in[-.4,0,.4]:rod('practical grille',(side*3.665,y+dy,z-.81),(side*3.665,y+dy,z+.81),.012,steel,zone)
for o in list(src.objects):
 if o.name.startswith(('Cantilever balcony','Window sill')):clone(o,cement)
for side in[-1,1]:
 for idx,cy in enumerate([-25,-16,-7,2]):
  o=bpy.data.objects[f'Building / {side} / {idx}'];top=max((o.matrix_world@v.co).z for v in o.data.vertices);zone=f'upper bay {side} {idx}';box('crown slab return',(side*3.96,cy,top-.13),(.17,8.42,.18),cement,zone)
  for dy in[-4.20,4.20]:box('vertical joint',(side*3.985,cy+dy,(top+10.7)/2),(.035,.035,max(.14,top-10.7)),seal,zone)
  for zz in[11,min(top-.4,13.2)]:box('rainpipe saddle',(side*3.66,cy+3.5,zz),(.14,.12,.065),zinc,zone)
for j,o in enumerate([o for o in src.objects if o.name.startswith('Dry goods carton')]):
 cp=clone(o,stock[j%4]);uv=cp.data.uv_layers.get('PILOT_carton_faces')or cp.data.uv_layers.new(name='PILOT_carton_faces')
 for p in cp.data.polygons:
  a=max(range(3),key=lambda a:abs(p.normal[a]));axes=[i for i in range(3)if i!=a];co=[cp.data.vertices[v].co for v in p.vertices];lo=[min(v[i]for v in co)for i in axes];hi=[max(v[i]for v in co)for i in axes]
  for li in p.loop_indices:
   v=cp.data.vertices[cp.data.loops[li].vertex_index].co;q=[(v[i]-l)/(h-l)for i,l,h in zip(axes,lo,hi)]
   if(a==0 and p.normal[a]<0)or(a==1 and p.normal[a]>0):q[0]=1-q[0]
   uv.data[li].uv=q
for o in list(src.objects):
 if o.name.startswith(('Shop stock shelf','Counter')):clone(o,wood)
for k,o in enumerate([o for o in src.objects if o.get('pilotOriginalObject',o.name).startswith('Counter')]):
 side=1 if o.location.x>0 else -1;cy=o.location.y;g=floor(cy);zone=f'counter finish {side} {cy}'
 for yy in[cy-1.50,cy,cy+1.50]:box('front stile',(side*2.778,yy,g+.62),(.016,.055,1.19),frame,zone)
 for zz in[g+.07,g+1.20]:box('applied counter edge',(side*2.777,cy,zz),(.018,3.18,.045),zinc if k%2 else wood,zone)
 box('replaceable worktop lip',(side*3.28,cy,g+1.287),(.98,3.26,.014),zinc if k in[1,3]else wood,zone)
for o in list(src.objects):
 if o.name.startswith(('Lane flat','Accessible ramp','Flared ramp apron')):clone(o,lane)
roof=next(o for o in src.objects if o.get('pilotOriginalObject',o.name)=='Rooftop slab / 32m x 40m');clone(roof,roofmat)
for o in list(src.objects):
 if o.name.startswith(('Continuous rooftop parapet','Rear screen parapet','Sloped apron parapet')):clone(o,cement)
for side in[-1,1]:
 zone='roof perimeter '+str(side)
 for j in range(16):
  yy=14.05+(j+.5)*33.7/16;box('parapet coping',(side*15.85,yy,8.337),(.39,33.7/16-.009,.074),cement,zone)
  if j<15:box('coping joint',(side*15.85,yy+33.7/32,8.34),(.39,.009,.065),seal,zone)
 for yy in[18.7,37.5,45.9]:box('scupper sleeve',(side*15.67,yy,7.30),(.08,.28,.12),zinc,zone);rod('external downpipe',(side*16.07,yy,7.28),(side*16.07,yy,6.3),.035,zinc,zone)
 for yy in[26,32.7,39.4,46.1]:box('mineral edge skirting',(side*15.67,yy,7.29),(.035,6.6,.16),cement,zone)
for j in range(15):box('rear coping',(-15.9+(j+.5)*31.8/15,47.8,8.337),(31.8/15-.009,.39,.074),cement,'rear parapet')
t=roofmat.node_tree;b=t.nodes.get('Principled BSDF');g=t.nodes.new('ShaderNodeNewGeometry');sep=t.nodes.new('ShaderNodeSeparateXYZ');t.links.new(g.outputs['Position'],sep.inputs[0])
def mathn(op,a,b):
 n=t.nodes.new('ShaderNodeMath');n.operation=op
 for i,v in enumerate([a,b]):
  if hasattr(v,'node'):t.links.new(v,n.inputs[i])
  else:n.inputs[i].default_value=v
 return n.outputs[0]
bands=[mathn('LESS_THAN',mathn('FLOORED_MODULO',sep.outputs[ax],4.2),.006)for ax in['X','Y']];mask=mathn('MAXIMUM',*bands);mx=t.nodes.new('ShaderNodeMixRGB');mx.inputs[2].default_value=(.062,.068,.062,1);t.links.new(b.inputs['Base Color'].links[0].from_socket,mx.inputs[1]);t.links.new(mask,mx.inputs[0]);t.links.new(mx.outputs[0],b.inputs['Base Color'])
for k,o in enumerate([o for o in src.objects if o.name.startswith('Neighbor mid-rise')]):
 clone(o,[lime,sage,cement,ochre][k%4]);zone='background '+str(k);cy=o.location.y-o.dimensions.y/2;x=o.location.x;width=o.dimensions.x;top=o.location.z+o.dimensions.z/2
 for zz in[6.9,10.1,13.3,16.5]:
  if zz<top-.2:box('floor band',(x,cy-.045,zz),(width,.10,.13),cement,zone)
 for xx in[x-width/2+.16,x+width/2-.16]:box('facade return',(xx,cy-.04,top/2),(.22,.10,top),cement,zone)
 for w in[w for w in src.objects if w.name.startswith('Neighbor window')and abs(w.location.y-(cy-.02))<.05 and abs(w.location.x-x)<width/2]:
  xx,yy,zz=w.location;wx=w.dimensions.x/2+.045;hz=w.dimensions.z/2+.045
  for dx in[-wx,wx]:box('background window jamb',(xx+dx,yy-.055,zz),(.07,.11,hz*2+.06),frame,zone)
  for dz in[-hz,hz]:box('background window head-sill',(xx,yy-.055,zz+dz),(wx*2,.16,.07),cement,zone)
merged=[]
for(zone,mat),d in buckets.items():
 m=bpy.data.meshes.new('WORLD static '+zone);m.from_pydata(d['v'],[],d['f']);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();m.update()
 o=bpy.data.objects.new('WORLD static / '+zone+' / '+mat.split(' / ')[-1],m);details.objects.link(o);m.materials.append(bpy.data.materials[mat]);uvmetre(o);merged.append(o.name)
s['supportOffLocked']=True;s['approvedGraffitiLocked']=True;s['crowdProposalsApplied']=False;s['artReviewStatus']='PRIVATE_WORLD_USER_REVIEW_PENDING';s.camera=src.camera
sys.path.insert(0,str(O/'source'));from world_cameras import add
add(s);bpy.context.view_layer.update()
assert sum(o.type=='LIGHT'for o in s.objects)==17 and sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();master=O/'source/Gullyverse-Selected-C-Wider-Realism.blend';bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
r={'status':'AUTHORED_PENDING_VISUAL_REVIEW','baselineSHA256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'masterBytes':master.stat().st_size,'surfaceCopies':copies,'newConstructionObjects':merged,'authoredParts':parts,'partsBeforeStaticGrouping':len(parts),'staticGroups':len(merged),'newShopBays':zones,'approvedArtHostsSkipped':skipped,'newImages':0,'noNewLights':True,'websiteChanges':False}
(O/'evidence/authoring.json').write_text(json.dumps(r,indent=2)+'\n');print('WORLD_AUTHORED',len(copies),len(parts),len(merged),flush=True)
