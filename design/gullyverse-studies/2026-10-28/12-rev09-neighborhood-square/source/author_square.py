"""Private Rev09 courtyard. Deliberately composed housing; no website mutation."""
import bpy,bmesh,json,hashlib,math,ast,sys,shutil,tempfile,os
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];cfg=json.loads((O/'source/BASELINE.json').read_text());assert hashlib.sha256(Path(os.environ.get('GULLYVERSE_BASELINE_OVERRIDE',cfg['path'])).read_bytes()).hexdigest()==cfg['sha256']
base=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE ARCH')
def copy_scene(name,variant):
 s=base.copy();s.name=name;s['variant']=variant;s.use_fake_user=True
 for c in list(s.collection.children):s.collection.children.unlink(c)
 for o in list(s.collection.objects):s.collection.objects.unlink(o)
 c=bpy.data.collections.new(variant+' / inherited');s.collection.children.link(c)
 for o in base.objects:c.objects.link(o)
 return s,c
before,_=copy_scene('REV09 CONTROL / Rev08 Architecture + Previous Crowd','SQUARE BEFORE');s,host=copy_scene('REV09 / Multi-Storey Square + Previous Crowd','SQUARE C180');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();details=bpy.data.collections.new('REV09 / residential perimeter');s.collection.children.link(details)
# Local visual replacements only; source objects/data remain intact in all archives.
removed=[]
for o in list(s.objects):
 sem=o.get('pilotOriginalObject',o.name);remove=False
 if sem.startswith('Neighbor mid-rise'):remove=int(sem.rsplit(' ',1)[1])>=2
 if sem.startswith(('Neighbor window','Neighbor parapet','Neighbor water tank'))and o.location.y>=9.9:remove=True
 if o.name.startswith('WORLD static / background ')and any(o.name.startswith('WORLD static / background '+str(k)+' /')for k in range(2,7)):remove=True
 if o.name.startswith(('REV08 / terrace service room','REV08 / rear access roof','REV08 / roof water service')):remove=True
 if sem.startswith('Continuous rooftop parapet'):remove=True
 # The old side coping is replaced by real house fronts; keep all structural decks/drains.
 if o.name.startswith('WORLD static / roof perimeter '):remove=True
 if remove:host.objects.unlink(o);removed.append(o.name)
parts=[];buckets={}
for n in ast.parse((O/'source/geometry_helpers.py').read_text()).body:
 if isinstance(n,ast.FunctionDef):exec(compile(ast.Module(body=[n],type_ignores=[]),str(O/'source/geometry_helpers.py'),'exec'))
cement=bpy.data.materials['WORLD / mineral concrete'];lime=bpy.data.materials['WORLD / warm grey limewash'];sage=bpy.data.materials['WORLD / faded blue-green plaster'];ochre=bpy.data.materials['WORLD / muted ochre plaster'];roof=bpy.data.materials['WORLD / continuous roof concrete'];seal=bpy.data.materials['PILOT / bituminous joint and gaskets'];steel=bpy.data.materials['PILOT / blackened zinc and aged fixings'];zinc=bpy.data.materials['PILOT / folded galvanised sheet'];glass=bpy.data.materials['WORLD / dusty non-emissive glazing'];frame=bpy.data.materials['WORLD / aged painted sash'];repair=bpy.data.materials['WORLD / localized render repair']
warm=glass.copy();warm.name='REV09 / dusty amber glass - NON EMISSIVE';warm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.155,.065,1);warm['emissionAdded']=False
shutter=frame.copy();shutter.name='REV09 / muted timber green shutters';shutter.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.075,.12,.105,1);shutter.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.05
HOUSE_SPECS=[
 ('L1','left',18.45,7.80,16.55,3,5.3,lime),('L2','left',27.65,10.10,16.65,4,5.2,ochre),('L3','left',36.50,7.10,16.90,2,5.1,sage),('L4','left',44.12,7.70,16.45,3,5.5,lime),
 ('R1','right',19.12,9.40,16.65,2,5.3,ochre),('R2','right',28.76,9.34,16.55,3,5.5,lime),('R3','right',37.64,8.02,16.85,5,5.2,sage),('R4','right',44.90,6.08,16.50,3,5.4,cement),
 ('B1','back',-17.08,9.54,49.25,3,5.4,ochre),('B2','back',-8.12,7.94,49.55,4,5.1,lime),('B3','back',.08,8.08,49.20,4,5.5,sage),('B4','back',8.34,7.98,49.50,2,5.1,cement),('B5','back',17.12,9.18,49.25,3,5.4,lime),
 ('F1','front',-12.16,7.12,13.65,2,5.0,lime),('F2','front',12.16,7.12,13.65,3,5.0,sage)]
houses=[];window_records=[];balcony_records=[]
for index,(label,edge,center,width,front,levels,depth,mat)in enumerate(HOUSE_SPECS):
 zone='house '+label;g=7.2;fh=3.1;top=g+levels*fh
 def P(u,d,z):
  return Vector((-front-d,center+u,z))if edge=='left'else Vector((front+d,center-u,z))if edge=='right'else Vector((center-u,front-d,z))if edge=='front'else Vector((center+u,front+d,z))
 def B(name,u,d,z,wu,dd,h,material):
  # Generic local cuboid with an orientation-preserving site transform.
  loc=P(u,d,z);dims=(dd,wu,h)if edge in['left','right']else(wu,dd,h);box(name,loc,dims,material,zone)
 def R(name,a,b,r,material,n=6):rod(name,P(*a),P(*b),r,material,zone,n)
 # Grounded support/body and genuine floor/roof slabs. No main-floor displacement.
 B('house podium support',0,depth/2,3.60,width,depth,7.20,mat)
 for z in[3.3,6.96]:B('podium RC band',0,depth/2,z,width+.04,depth+.04,.20,cement)
 B('rear wall',0,depth-.13,(g+top)/2,width,.26,top-g,mat)
 for u in[-width/2+.13,width/2-.13]:B('party wall',u,depth/2,(g+top)/2,.26,depth,top-g,mat)
 # Openings are modelled by wall partition, not placed onto a solid front cube.
 bays=3 if width>8.4 else 2;centers=[-width*.29+j*width*.58/(bays-1)for j in range(bays)]
 for level in range(levels):
  fl=g+level*fh;B('floor slab',0,depth/2,fl+.05,width+.06,depth+.06,.18,cement)
  balcony=level>0 and(level+index)%3==1;bal_u=centers[(index+level)%bays]
  holes=[]
  for j,u in enumerate(centers):
   isdoor=(level==0 and j==(index%bays))or(balcony and abs(u-bal_u)<.01)
   ww=(1.02 if level==0 else 1.32)if isdoor else(1.25 if(index+j)%3 else 1.44)
   z0=fl+.15 if isdoor else fl+.88;z1=fl+2.43 if isdoor else fl+2.35
   holes.append((u-ww/2,u+ww/2,z0,z1,isdoor))
  cuts=sorted(set([fl,fl+fh]+[v for h in holes for v in h[2:4]]))
  for lo,hi in zip(cuts,cuts[1:]):
   mid=(lo+hi)/2;blocked=sorted((a,b)for a,b,z0,z1,_ in holes if z0<mid<z1);last=-width/2
   for a,b in blocked+[(width/2,width/2)]:
    if a>last+.0001:B('front wall pier/spandrel',(a+last)/2,.13,(lo+hi)/2,a-last,.26,hi-lo,mat)
    last=max(last,b)
  for j,(a,b,z0,z1,isdoor)in enumerate(holes):
   u=(a+b)/2;ww=b-a;hh=z1-z0;mid=(z0+z1)/2
   pane=frame if isdoor else warm if(index+level*2+j)%11==0 else glass
   B('recessed house door'if isdoor else'recessed window glazing',u,.30,mid,ww-.04,.045,hh-.04,pane)
   for dx in[-ww/2,ww/2]:B('opening jamb',u+dx,.115,mid,.07,.37,hh+.11,cement)
   for zz in[z0,z1]:B('opening head/sill',u,.10,zz,ww+.1,.40,.07,cement)
   if not isdoor:
    B('painted center mullion',u,.252,mid,.045,.045,hh,frame)
    for dz in[-hh*.21,hh*.21]:B('casement transom',u,.25,mid+dz,ww-.08,.045,.025,frame)
    B('weathered projecting chhajja',u,-.20,z1+.16,ww+.30,.66,.10,cement)
    if(index+j+level)%4==1:
     B('folded timber shutter',u+ww/2+.17,-.10,mid,.27,.085,hh,shutter)
     for z in[z0+.18,z1-.18]:B('shutter hinge',u+ww/2+.025,-.11,z,.05,.12,.045,steel)
   else:
    B('door threshold',u,-.05,z0-.025,ww+.12,.45,.05,cement)
    R('door handle',(u+.30,.263,mid-.1),(u+.30,.263,mid+.14),.013,zinc)
   window_records.append({'house':label,'level':level,'localOpening':[a,b,z0,z1],'door':isdoor,'position':list(P(u,0,mid)),'material':pane.name,'nonEmissive':True})
  if balcony:
   bw=min(width-.6,3.25+(index%2)*.35);u=max(-width/2+bw/2+.16,min(width/2-bw/2-.16,bal_u));zz=fl+.08
   B('cantilever balcony slab',u,-.60,zz,bw,1.36,.19,cement)
   R('front balcony top rail',(u-bw/2,-1.22,zz+1.14),(u+bw/2,-1.22,zz+1.14),.027,steel)
   R('front balcony lower rail',(u-bw/2,-1.22,zz+.22),(u+bw/2,-1.22,zz+.22),.018,steel)
   for x in range(math.ceil(bw/.17)+1):
    uu=u-bw/2+x*bw/math.ceil(bw/.17);R('balcony baluster',(uu,-1.22,zz+.21),(uu,-1.22,zz+1.14),.013,steel)
   for du in[-bw/2,bw/2]:R('balcony return rail',(u+du,-1.22,zz+1.14),(u+du,0,zz+1.14),.027,steel)
   if level==1 and index%2==0:B('balcony shade canopy',u,-.58,zz+2.69,bw+.20,1.55,.08,zinc)
   balcony_records.append({'house':label,'level':level,'width':bw,'projectionM':1.28,'center':list(P(u,-.6,zz)),'publicFloorIntrusion':False})
  # RC edge/subtle repair follows construction and weather exposure.
  B('front concrete floor return',0,-.025,fl+fh-.10,width+.08,.34,.15,cement)
  if(level+index)%2==0:B('localized lime repair',width/2-.45,-.018,fl+.58,.45,.025,.62,repair)
 # Flat roofs have parapet thickness and real spatially varied silhouettes.
 B('main roof slab',0,depth/2,top+.10,width+.20,depth+.20,.20,roof)
 for u in[-width/2,width/2]:B('roof side parapet',u,depth/2,top+.51,.18,depth,.62,mat)
 B('roof front parapet',0,.08,top+.51,width,.18,.62,mat);B('roof rear parapet',0,depth-.08,top+.51,width,.18,.62,mat)
 B('roof coping',0,.08,top+.85,width+.10,.27,.08,cement)
 if levels<=3 and index%3==0:
  u=width*.20;d=depth*.63;B('roof access room',u,d,top+1.13,2.15,1.60,2.05,mat);B('access room roof',u,d,top+2.20,2.35,1.80,.15,roof);B('roof access door',u,d-.83,top+1.02,.88,.04,1.85,frame)
 if index%3==1:
  u=-width*.28;d=depth*.63;B('tank plinth',u,d,top+.26,1.60,1.60,.22,cement);R('water tank',(u,d,top+.37),(u,d,top+1.60),.62,steel,20)
  for z in[top+.47,top+.76,top+1.05,top+1.34,top+1.58]:R('tank rib',(u,d,z-.018),(u,d,z+.018),.644,frame,20)
  R('tank lid',(u,d,top+1.60),(u,d,top+1.67),.29,steel,16)
 # Grounded, purposeful utility details rather than random clutter.
 up=width/2-.25
 R('rainwater pipe',(up,-.10,g+.1),(up,-.10,top+.16),.035,zinc)
 for lv in range(levels):B('rainwater saddle',up,-.085,g+lv*fh+.55,.14,.16,.045,steel)
 for k in range(3):R('facade utility wire',(-width/2,-.13,g+2.68+k*.07),(width/2,-.13,g+2.68+k*.07),.009,seal)
 # Compressors are closed authored bodies with grilles; no floating brand plates.
 if index%2==0:
  uu=width*.32;zz=g+fh+2.38;B('AC outdoor unit',uu,-.32,zz,.85,.52,.55,zinc)
  for j in range(7):B('AC grille slat',uu-.32+j*.106,-.594,zz,.024,.02,.43,frame)
  for du in[-.29,.29]:B('AC support bracket',uu+du,-.25,zz-.34,.045,.65,.045,steel)
 # End facing lane: modeled opening-like recessed window assembly below its coping.
 if index in[0,4]:
  for lv in range(levels):
   y=center-width/2-.02 if edge=='left'else center-width/2-.02;x=(-front-depth*.50)if edge=='left'else front+depth*.50;zz=g+lv*fh+1.65
   box('lane-facing inset casement',(x,y,zz),(1.55,.06,1.45),glass,zone)
   for dx in[-.82,.82]:box('lane casement jamb',(x+dx,y-.025,zz),(.07,.17,1.59),cement,zone)
   for dz in[-.76,.76]:box('lane casement sill',(x,y-.04,zz+dz),(1.71,.22,.07),cement,zone)
 houses.append({'id':label,'edge':edge,'center':center,'frontSetbackCoordinate':front,'frontageM':width,'depthM':depth,'courtyardDatumM':g,'storeyHeightM':fh,'courtyardFacingStoreys':levels,'mainRoofM':top+.20,'parapetTopM':top+.89,'material':mat.name,'footprintWorld':[list(P(u,d,0))for u,d in[(-width/2,0),(width/2,0),(width/2,depth),(-width/2,depth)]],'originalMainFloorUnchanged':True})
new=[]
for(zone,material),d in buckets.items():
 m=bpy.data.meshes.new('REV09 '+zone);m.from_pydata(d['v'],[],d['f']);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(m);bm.free();m.update();o=bpy.data.objects.new('REV09 / '+zone+' / '+material.split(' / ')[-1],m);details.objects.link(o);m.materials.append(bpy.data.materials[material]);uvmetre(o);new.append(o.name)
s['selectedCrowd']='EXACT PRIOR BLENDER C180';s['optionalSupportLightsW']=0;s['newLightOwners']=0;s['windowEmissionAdded']=False;s['publicMainFloorMoved']=False;s['steelFurnitureIdentity']='PENDING - NO SUBSTITUTION'
sys.path.insert(0,str(O/'source'));from square_cameras import add
for sc in[before,s]:add(sc)
bpy.context.window.scene=s;s.frame_set(1);s.camera=bpy.data.objects['REV09 CAMERA / 02-entry-square'];bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();dest=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend'
# Staging avoids requiring a second full master on the nearly-full persistent disk.
stage=Path('/dev/shm/rev09')if Path('/dev/shm/rev09').is_dir()else Path(tempfile.mkdtemp(prefix='gullyverse-rev09-'));temporary=stage/'author-candidate.blend';bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True);shutil.copyfile(temporary,dest);assert hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(temporary.read_bytes()).digest()
r={'status':'AUTHORED_PENDING_CHECKS_AND_ART_REVIEW','baselineSHA256':cfg['sha256'],'masterSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'masterBytes':dest.stat().st_size,'selectedCrowd':'EXACT PRIOR BLENDER C180','removedOnlyFromNewScene':removed,'newConstruction':new,'parts':parts,'houses':houses,'openings':window_records,'balconies':balcony_records,'all33ImagesReused':True,'noNewPhysicalOrEmissiveLighting':True,'websiteUnchanged':True}
(O/'evidence/authoring.json').write_text(json.dumps(r,indent=2,default=lambda v:list(v)));print('REV09_AUTHORED',len(houses),len(parts),len(new),dest.stat().st_size,flush=True)
