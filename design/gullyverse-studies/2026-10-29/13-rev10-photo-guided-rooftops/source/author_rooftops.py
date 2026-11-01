"""Rev10 two photo-informed architectural compositions; no source-scene mutation."""
import bpy,bmesh,json,hashlib,sys,ast,math,os
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];BASE=O/'source/Rev09-Original.blend';assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='3f637b223aff0fd4eb397ae6e51d821ed5de5675cf9707643a1cdf955821ab78'
base=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');old=json.loads((O/'evidence/rev09-authoring.json').read_text());mat=lambda n:bpy.data.materials[n]
cement=mat('WORLD / mineral concrete');lime=mat('WORLD / warm grey limewash');sage=mat('WORLD / faded blue-green plaster');ochre=mat('WORLD / muted ochre plaster');roof=mat('WORLD / continuous roof concrete');steel=mat('PILOT / blackened zinc and aged fixings');zinc=mat('PILOT / folded galvanised sheet');seal=mat('PILOT / bituminous joint and gaskets');glass=mat('WORLD / dusty non-emissive glazing');frame=mat('WORLD / aged painted sash');repair=mat('WORLD / localized render repair');timber=mat('REV09 / muted timber green shutters')
for n in ast.parse((O/'source/geometry_helpers.py').read_text()).body:
 if isinstance(n,ast.FunctionDef):exec(compile(ast.Module(body=[n],type_ignores=[]),'helpers','exec'))
STUDIES={
 'A':[
  ('L1','left',18.8,9.3,17.9,7.4,1,[0],lime,'roof-room'),
  ('L2','left',29.6,10.8,21.9,7.8,3,[0,.6,1.1],sage,'gallery'),
  ('L3','left',40.6,10.1,19.8,8.4,2,[0,1.8],lime,'split'),
  ('R1','right',19.9,11.4,20.4,8.2,2,[0,1.3],ochre,'split'),
  ('R2','right',32.1,10.5,17.8,8.6,1,[0],lime,'roof-room'),
  ('R3','right',42.8,9.6,22.4,7.3,4,[0,0,.4,1.5],sage,'gallery'),
  ('B1','back',-13.2,12.4,51.4,8.0,2,[0,1.0],cement,'split'),
  ('B2','back',.8,13.2,54.2,7.5,3,[0,1.5,2.1],lime,'gallery'),
  ('B3','back',14.5,11.5,50.7,8.4,1,[0],ochre,'roof-room'),
  ('F1','front',-14.7,8.4,12.6,6.7,1,[0],lime,'roof-room'),
  ('F2','front',14.4,8.0,12.3,6.9,2,[0,1.6],sage,'split')],
 'B':[
  ('L1','left',18.5,8.4,18.4,6.2,2,[0,.35],sage,'gallery'),
  ('L2','left',29.8,13.7,19.5,7.3,3,[0,.15,1.6],lime,'gallery'),
  ('L3','left',41.8,9.8,17.8,8.3,2,[0,2.1],ochre,'split'),
  ('R1','right',20.3,10.5,19.6,7.2,3,[0,1.4,1.4],lime,'gallery'),
  ('R2','right',33.3,14.6,18.2,8.1,2,[0,1.0],sage,'gallery'),
  ('R3','right',44.4,6.9,21.7,6.9,4,[0,.3,.3,2],cement,'split'),
  ('B1','back',-13.8,11.8,51.2,7.2,3,[0,1,1],ochre,'gallery'),
  ('B2','back',.1,14.8,52.4,8.0,2,[0,2.2],lime,'gallery'),
  ('B3','back',14.2,10.9,50.5,8.3,4,[0,0,.7,2.0],sage,'split'),
  ('F1','front',-14.7,9.5,12.7,6.2,2,[0,1.0],sage,'split'),
  ('F2','front',14.9,9.4,12.5,6.7,1,[0],ochre,'roof-room')]
}
records=[]
for edition,specs in STUDIES.items():
 s=base.copy();s.name='REV10 '+edition+' / '+('Connected Working Rooftops'if edition=='A'else'Layered Residential Galleries');s['variant']='PHOTO '+edition;s.use_fake_user=True
 for c in list(s.collection.children):s.collection.children.unlink(c)
 for o in list(s.collection.objects):s.collection.objects.unlink(o)
 host=bpy.data.collections.new('REV10 '+edition+' / inherited locked world');s.collection.children.link(host)
 for o in base.objects:
  if o.name not in old['newConstruction']:host.objects.link(o)
 details=bpy.data.collections.new('REV10 '+edition+' / composed neighborhood');s.collection.children.link(details);bpy.context.window.scene=s;s.frame_set(1);parts=[];buckets={};houses=[]
 for idx,(label,edge,center,width,front,depth,levels,setbacks,plaster,typology)in enumerate(specs):
  zone=label;g=7.2;fh=2.85;top=g+levels*fh
  def P(u,d,z):return Vector((-front-d,center+u,z))if edge=='left'else Vector((front+d,center-u,z))if edge=='right'else Vector((center-u,front-d,z))if edge=='front'else Vector((center+u,front+d,z))
  def B(n,u,d,z,w,dd,h,m):box(n,P(u,d,z),(dd,w,h)if edge in['left','right']else(w,dd,h),m,zone)
  def R(n,a,b,r,m,nseg=8):rod(n,P(*a),P(*b),r,m,zone,nseg)
  def rail(u0,u1,d,z,opaque=False):
   if opaque:B('thick repaired roof parapet',(u0+u1)/2,d,z+.45,u1-u0,.20,.90,plaster);B('patched coping',(u0+u1)/2,d,z+.94,u1-u0+.05,.29,.07,cement)
   else:
    for zz in [.18,.95]:R('shared gallery horizontal rail',(u0,d,z+zz),(u1,d,z+zz),.025,steel)
    for j in range(math.ceil((u1-u0)/.22)+1):
     u=u0+j*(u1-u0)/math.ceil((u1-u0)/.22);R('gallery vertical picket',(u,d,z+.12),(u,d,z+.96),.012,steel)
  def pipe(path,r=.033,m=zinc):
   for a,b in zip(path,path[1:]):R('purposeful service connection',a,b,r,m)
  def cloth(u,d,z,w,h,m):
   # Closed thin irregular cloth body, hung beyond the protected walking floor.
   coords=[(u-w/2,z),(u+w/2,z+.015),(u+w*.46,z-h),(u-w*.44,z-h+.04)];verts=[P(x,d+dd,zz)for dd in[-.005,.005]for x,zz in coords];piece('hanging domestic cloth',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,zone,{'reference':'R1/R3 domestic use','notNewArtwork':True})
  # Support mass below fixed roof datum, upper body built as thick partitioned walls.
  B('supported neighborhood podium',0,depth/2,3.60,width,depth,7.20,cement)
  for fl in[3.55,6.99]:B('exterior supporting slab',0,depth/2,fl,width+.1,depth+.1,.22,cement)
  for lev in range(levels):
   fl=g+lev*fh;off=setbacks[lev];back=depth-.14;fw=width-(.8 if lev==levels-1 and idx%3==1 else 0);half=fw/2
   B('load-bearing rear wall',0,back,(fl+fl+fh)/2,fw,.28,fh,plaster)
   for u in[-half+.14,half-.14]:B('shared party return wall',u,(off+back)/2,fl+fh/2,.28,back-off,fh,plaster)
   B('real reinforced floor/slab',0,(off+depth)/2,fl+.045,fw+.05,depth-off+.10,.18,roof)
   # Unequal authored bays: one broad opening plus one smaller casement, not a grid.
   gallery=typology=='gallery'and (lev<levels-1 or edition=='B')
   bays=[(-fw*.24,1.06,True),(fw*.23,1.48 if(idx+lev)%2 else 1.82,False)]
   if fw>12:bays=[(-fw*.32,1.04,True),(-.05,1.76,False),(fw*.31,1.19,True)]
   if typology=='roof-room':bays=[(-fw*.20,1.35,False),(fw*.24,1.05,True)]
   openings=[]
   for j,(u,ww,door)in enumerate(bays):
    u+=.13*(lev%2);z0=fl+.15 if door else fl+.85;z1=fl+2.42;openings.append((u-ww/2,u+ww/2,z0,z1,door))
   cuts=sorted(set([fl,fl+fh]+[z for h in openings for z in h[2:4]]))
   for lo,hi in zip(cuts,cuts[1:]):
    blocked=sorted((a,b)for a,b,z0,z1,_ in openings if z0<(lo+hi)/2<z1);last=-half
    for a,b in blocked+[(half,half)]:
     if a-last>1e-5:B('facade partition / real aperture',(a+last)/2,off+.14,(hi+lo)/2,a-last,.28,hi-lo,plaster)
     last=max(last,b)
   for j,(a,b,z0,z1,door)in enumerate(openings):
    u=(a+b)/2;ww=b-a;h=z1-z0;mid=(z1+z0)/2;inset=.56 if gallery else .30
    B('deep nonemissive door'if door else'deep casement',u,off+inset,mid,ww-.06,.065,h-.06,timber if door else glass)
    for du in[-ww/2,ww/2]:B('thick exposed jamb',u+du,off+.17,mid,.07,.43,h+.10,cement)
    for zz in[z0,z1]:B('sill or lintel',u,off+.17,zz,ww+.12,.43,.085,cement)
    if not door:
     B('unequal window mullion',u+.11,off+inset-.04,mid,.045,.07,h,frame)
     B('horizontal casement member',u,off+inset-.04,mid-.1,ww,.06,.035,frame)
     B('sloping shade slab',u,off-.22,z1+.14,ww+.38,.82,.10,cement)
     if (idx+lev+j)%3==0:B('hinged open shutter leaf',u-ww/2-.22,off-.22,mid,.38,.11,h,timber)
    else:
     for zz in[z0+.13,z1-.14]:B('door rail',u,off+inset-.05,zz,ww-.1,.04,.045,frame)
     R('door pull',(u+.26,off+inset-.10,mid-.12),(u+.26,off+inset-.10,mid+.1),.012,zinc)
   if gallery:
    # Deep walkable residential gallery outside the authoritative visitor floor.
    d=off-.64;B('gallery circulation slab',0,d,fl+.08,fw,1.48,.18,cement);rail(-half+.15,half-.15,off-1.31,fl+.17,False)
    for u in[-half+.18,fw*.09,half-.18]:
     B('gallery upright',u,off-1.15,fl+1.46,.095,.095,2.70,frame)
     B('gallery slab bracket',u,off-.50,fl-.14,.12,1.0,.25,cement)
    if lev==0 or lev==levels-1:B('gallery overhang with thickness',0,off-.54,fl+2.69,fw+.18,1.52,.13,cement)
    if lev==1 or (levels==1):
     for j,(uu,hh)in enumerate([(-fw*.29,.78),(-fw*.19,.59),(fw*.20,.91)]):cloth(uu,off-1.35,fl+1.02,.42 if j!=1 else.63,hh,ochre if j==0 else sage if j==1 else lime)
   # Local repairs follow sills/plinths instead of random material polygons.
   for j,uu in enumerate([-half+.48,half-.48]):
    B('uneven exposed render repair',uu,off-.008,fl+.35+j*.20,.56,.022,.43,repair)
   if lev==0:
    pipe([(-half+.27,off-.12,fl+.25),(-half+.27,off-.12,fl+2.58),(-half+.90,off-.12,fl+2.58)],.025)
    B('domestic service meter',-half+.63,off-.16,fl+1.80,.32,.13,.40,zinc)
   if lev<levels-1 and setbacks[lev+1]>off+.3:
    # Human-scale front terrace exposed by upper-storey setback.
    rail(-half+.1,half-.1,off-.025,fl+fh+.13,idx%2==0)
  B('final concrete roof',0,(setbacks[-1]+depth)/2,top+.11,width+.14,depth-setbacks[-1]+.14,.22,roof)
  for u in[-width/2,width/2]:B('thick side roof parapet',u,(setbacks[-1]+depth)/2,top+.56,.21,depth-setbacks[-1],.79,plaster)
  rail(-width/2,width/2,setbacks[-1]+.08,top+.20,True)
  B('roof rear wall',0,depth-.08,top+.56,width,.22,.79,plaster)
  # Real service tank, ribs and plumbing. No distant unconnected black cylinders.
  if idx in[0,2,4,6,8,9]:
   u=-width*.25;d=depth-1.15;B('tank masonry plinth',u,d,top+.29,1.5,1.5,.25,cement);R('tank body',(u,d,top+.42),(u,d,top+1.62),.59,steel,20)
   for z in[top+.48,top+.78,top+1.08,top+1.38,top+1.60]:R('tank reinforcing rib',(u,d,z-.02),(u,d,z+.02),.615,frame,20)
   R('tank cap',(u,d,top+1.63),(u,d,top+1.69),.24,steel,16);pipe([(u,d,top+.55),(u+.76,d,top+.55),(u+.76,d,top+.20),(u+.76,.30,top+.20),(u+.76,.30,g+.30)])
  if idx in[1,3,6,9]:
   u=width*.23;d=depth-1.50;B('inhabited roof access headroom',u,d,top+1.21,2.30,2.15,2.0,plaster);B('access room roof',u,d,top+2.27,2.52,2.35,.15,roof);B('roof door',u,d-1.10,top+1.15,.9,.07,1.85,timber)
   # Side-mounted access ladder, never in visitor route.
   for du in[-.30,.30]:R('roof access ladder stile',(u+du,d-1.3,top+.27),(u+du,d-1.3,top+2.5),.022,steel)
   for k in range(8):R('roof ladder tread',(u-.3,d-1.3,top+.40+k*.28),(u+.3,d-1.3,top+.40+k*.28),.018,steel)
  # Sparse roof use: washing-line posts + unevenly draped closed cloth forms.
  if idx in[0,4,7]:
   dd=setbacks[-1]+1.3;uu=width*.12
   for du in[-1.25,1.25]:R('washing post',(uu+du,dd,top+.21),(uu+du,dd,top+1.73),.024,steel)
   R('washing line',(uu-1.25,dd,top+1.66),(uu+1.25,dd,top+1.66),.006,seal)
   cloth(uu-.70,dd,top+1.65,.48,.71,sage);cloth(uu+.12,dd,top+1.65,.70,.52,lime);cloth(uu+.77,dd,top+1.65,.39,.84,ochre)
  if idx%2==0:
   u=width*.31;off=setbacks[0];zz=g+2.30;B('AC compressor body',u,off-.33,zz,.87,.50,.54,zinc)
   for j in range(6):B('AC vent rib',u-.30+j*.12,off-.598,zz,.025,.025,.41,steel)
   for du in[-.30,.30]:B('AC mount bracket',u+du,off-.22,zz-.33,.045,.68,.045,steel)
  # Roof-edge cable route with real sag, inside each parcel rather than across sky.
  for k in range(2):
   points=[(-width/2+.18+j*(width-.36)/6,-.16,g+2.52+k*.10-.18*math.sin(math.pi*j/6))for j in range(7)];pipe(points,.008,seal)
  houses.append({'id':label,'edge':edge,'center':center,'widthM':width,'frontM':front,'depthM':depth,'upperLevelsFromCourtyard':levels,'totalApparentStoreys':levels+2,'setbacksM':setbacks,'mainRoofZ':top+.22,'typology':typology,'referenceRoles':['R2','R4']if typology=='roof-room'else['R1','R3','R5']})
 # Connected working terrace wings occupy only the OUTSIDE of the fixed floor.
 for edge,segments in [('left',[(15.0,24.5,7.28),(24.5,36.0,7.58),(36.0,48.2,7.28)]),('right',[(14.7,26.3,7.28),(26.3,38.4,7.28),(38.4,48.4,7.77)])]:
  side=-1 if edge=='left'else 1;zone=edge+' connected service terrace';x=side*18.3
  for j,(lo,hi,z)in enumerate(segments):
   box('connected thick roof extension',(x,(lo+hi)/2,z-.14),(4.6,hi-lo,.28),roof,zone)
   # Edge guard remains beyond X±16, never through signs or crowd.
   box('main floor exterior low parapet',(side*16.22,(lo+hi)/2,7.65),(.24,hi-lo-.18,.76),lime if j!=1 else cement,zone)
   box('worn roof edge coping',(side*16.22,(lo+hi)/2,8.055),(.33,hi-lo-.08,.07),cement,zone)
   box('outside support wall',(side*20.45,(lo+hi)/2,3.52),(.30,hi-lo,7.04),cement,zone)
  # Three terrace risers link the small level difference as roof-service context.
  for k in range(3):box('service terrace stair',(side*18.6,25.0+k*.26,7.30+k*.10),(1.1,.30,.13),cement,zone)
 # Static groups are spatially/materially coherent; all parts remain editable in master.
 names=[]
 for (z,mn),d in buckets.items():
  m=bpy.data.meshes.new('REV10 '+edition+' '+z);m.from_pydata(d['v'],[],d['f']);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(m);bm.free();m.update();o=bpy.data.objects.new('REV10 '+edition+' / '+z+' / '+mn.split(' / ')[-1],m);details.objects.link(o);m.materials.append(bpy.data.materials[mn]);uvmetre(o);names.append(o.name)
 s['crowd']='EXACT PRIOR BLENDER C180';s['architectureProposal']=True;s['lightingChange']=False;s['photoPixelsUsedAsTextures']=False;s['steelRackTable']='PENDING / NO SUBSTITUTION'
 records.append({'edition':edition,'variant':s['variant'],'scene':s.name,'houses':houses,'parts':parts,'newMeshes':names,'removedOnlyFromNewScene':old['newConstruction'],'references':['R1','R2','R3','R4','R5','R6'],'allOriginalCrowdObjectsShared':True})
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.get('variant')=='PHOTO A');bpy.context.scene.frame_set(1);bpy.context.scene.camera=bpy.data.objects['REV09 CAMERA / 02-entry-square'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();dest=Path(os.environ.get('REV10_AUTHOR_OUTPUT',str(Path('/dev/shm/rev10/Gullyverse-Rev10-Photo-Guided-Alternatives.blend'))if Path('/dev/shm/rev10').is_dir()else str(O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend')));bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
link=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend'
if not link.exists():link.symlink_to(dest)
(O/'evidence/authoring.json').write_text(json.dumps({'status':'AUTHORED_PENDING_VALIDATION_AND_USER_CHOICE','baselineSHA256':'3f637b223aff0fd4eb397ae6e51d821ed5de5675cf9707643a1cdf955821ab78','masterSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'masterBytes':dest.stat().st_size,'studies':records,'all13HistoricalScenesPreserved':True,'newImageOrLightOwners':0},indent=2,default=lambda x:list(x)));print('REV10_AUTHORED',dest.stat().st_size,[(r['edition'],len(r['houses']),len(r['newMeshes']))for r in records],flush=True)
