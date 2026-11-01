"""Deliberate joined architectural composition. Orthogonal wall/slab union, no Boolean modifier.
Run only on authenticated Rev10 input; never resaves/edits its 15 scenes or data.
"""
import bpy,bmesh,json,math,sys,hashlib,statistics,ast
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()=='d530f164318ac4f736d43159b7eac705ca4233ac78d69fb545c2b71b950da850'
source=next(s for s in bpy.data.scenes if s.get('variant')=='PHOTO A')
arch=json.loads((O/'baseline/evidence/authoring.json').read_text());old=arch['studies'][0]
s=source.copy();s.name='REV11 / Connected Neighborhood +7 percent';s['variant']='REV11';s.use_fake_user=True
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
locked=bpy.data.collections.new('REV11 / original protected site');s.collection.children.link(locked)
for o in source.objects:
 if o.name not in old['newMeshes']:locked.objects.link(o)
details=bpy.data.collections.new('REV11 / joined construction');s.collection.children.link(details);bpy.context.window.scene=s;s.frame_set(1)
m=lambda n:bpy.data.materials[n]
cement=m('WORLD / mineral concrete');lime=m('WORLD / warm grey limewash');sage=m('WORLD / faded blue-green plaster');ochre=m('WORLD / muted ochre plaster');roof=m('WORLD / continuous roof concrete');steel=m('PILOT / blackened zinc and aged fixings');zinc=m('PILOT / folded galvanised sheet');seal=m('PILOT / bituminous joint and gaskets');glass=m('WORLD / dusty non-emissive glazing');frame=m('WORLD / aged painted sash');repair=m('WORLD / localized render repair');timber=m('REV09 / muted timber green shutters')
for node in ast.parse((O/'source/geometry_helpers.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'helper','exec'))
parts=[];buckets={};solid=[];houses=[]
def C(n,loc,dims,mat,zone):
 assert min(dims)>0,(n,dims)
 structural={'continuous foundation body','connected floor structural slab','continuous rear bearing wall','shared party-wall return','real aperture facade','inhabited deep gallery slab','gallery structural upright','gallery ceiling thickness','joined final roof slab','continuous masonry parapet','back roof parapet','inhabited headroom side','headroom rear','headroom front pier','headroom door lintel','headroom roof','stepped exposed terrace roof'}
 if n not in structural:
  box(n,loc,dims,mat,zone);return
 solid.append({'name':n,'location':list(loc),'dimensions':list(dims),'material':mat.name,'zone':zone})
# Rectangular property boundaries abut; visible front offsets and roof heights may differ.
# (label, edge, along min/max, front, outer depth, upper storeys, setbacks, plaster, gallery)
specs=[('L1','left',14,25.2,18.1,9.9,1,[0],lime,False),('L2','left',25.2,37,18.7,9.3,3,[0,.45,1.35],sage,True),('L3','left',37,50,17.9,10.1,2,[0,1.55],lime,False),('R1','right',14,27,18.4,9.6,2,[0,.75],ochre,True),('R2','right',27,38.1,17.8,10.2,1,[0],lime,False),('R3','right',38.1,50,19.0,9.0,3,[0,.4,1.2],sage,True),('B1','back',-28,-9.5,50,9.0,2,[0,.60],cement,False),('B2','back',-9.5,8.2,50,9.0,3,[0,.75,1.65],lime,True),('B3','back',8.2,28,50,9.0,2,[0,1.15],ochre,False),('F1','front',-28,-8.3,14,6.2,1,[0],lime,False),('F2','front',8.3,28,14,5.5,2,[0,1.05],sage,False)]
for idx,(label,edge,lo,hi,front,depth,levels,offsets,plaster,gallery)in enumerate(specs):
 width=hi-lo;center=(lo+hi)/2;half=width/2;zone=label
 def P(u,d,z):return Vector((-front-d,center+u,z))if edge=='left'else Vector((front+d,center-u,z))if edge=='right'else Vector((center-u,front-d,z))if edge=='front'else Vector((center+u,front+d,z))
 def B(n,u,d,z,w,dd,h,mat,core=True):
  (C if core else box)(n,P(u,d,z),(dd,w,h)if edge in ['left','right']else(w,dd,h),mat,zone)
 def R(n,a,b,r,mat,nseg=8):rod(n,P(*a),P(*b),r,mat,zone,nseg)
 def pipe(n,points,r=.027,mat=zinc):
  for a,b in zip(points,points[1:]):R(n,a,b,r,mat)
 def rail(u0,u1,d,z,opaque=False):
  if opaque:B('continuous masonry parapet',(u0+u1)/2,d,z+.49,u1-u0,.22,.98,plaster);B('weathered coping',(u0+u1)/2,d,z+1.015,u1-u0,.30,.07,cement)
  else:
   for zz in [.12,1.04]:R('gallery rail',(u0,d,z+zz),(u1,d,z+zz),.024,steel)
   for j in range(math.ceil((u1-u0)/.28)+1):
    u=u0+j*(u1-u0)/math.ceil((u1-u0)/.28);R('gallery picket',(u,d,z+.12),(u,d,z+1.04),.013,steel)
 B('continuous foundation body',0,depth/2,.30,width,depth,.60,cement)
 floorlevels=[(.60,3.30,0),(3.90,3.30,0)]+[(7.20+lev*3,3.0,offsets[lev])for lev in range(levels)]
 for lev,(fl,fh,off)in enumerate(floorlevels):
  upper=lev>=2;back=depth-.15
  B('connected floor structural slab',0,(off+depth)/2,fl-.10,width,depth-off,.20,roof)
  B('continuous rear bearing wall',0,back,fl+fh/2,width,.30,fh,plaster)
  for u in[-half+.15,half-.15]:B('shared party-wall return',u,(off+back)/2,fl+fh/2,.30,back-off,fh,plaster)
  # Domestic frontage uses 3.5–4.9m bays, not one tiny window on a 20m panel.
  count=max(2,round(width/4.3));centers=[-half+(j+.5)*width/count for j in range(count)]
  # No window/door is authored into a party-wall attachment at an L corner.
  if label in ['F1','F2','B1','B3']:
   def outward_opening(u):
    x=P(u,0,fl).x
    return x>-18.1+1 if label=='F1' else x<18.4-1 if label=='F2' else x>-17.9+1 if label=='B1' else x<19.0-1
   centers=[u for u in centers if outward_opening(u)]
  openings=[]
  for j,u in enumerate(centers):
   door=j==0 or (gallery and j==count-1);ww=1.02 if door else[1.28,1.50,1.66][(idx+j+lev)%3];z0=fl+.10 if door else fl+.90;z1=fl+2.20 if door else fl+2.25
   openings.append((u-ww/2,u+ww/2,z0,z1,door))
  zs=sorted({fl,fl+fh,*[z for r in openings for z in r[2:4]]})
  for z0,z1 in zip(zs,zs[1:]):
   holes=[(a,b)for a,b,bot,top,_ in openings if bot<(z0+z1)/2<top];last=-half
   for a,b in holes+[(half,half)]:
    if a>last:B('real aperture facade',(a+last)/2,off+.15,(z0+z1)/2,a-last,.30,z1-z0,plaster)
    last=max(last,b)
  for j,(a,b,z0,z1,door)in enumerate(openings):
   u=(a+b)/2;ww=b-a;h=z1-z0;mid=(z0+z1)/2;inset=.60 if gallery and upper else .37
   B('nonemissive domestic door'if door else'recessed window glazing',u,off+inset,mid,ww-.06,.065,h-.06,timber if door else glass,False)
   for du in[-ww/2,ww/2]:B('thick jamb',u+du,off+.16,mid,.07,.43,h+.10,cement)
   for z in[z0,z1]:B('lintel and projecting sill',u,off+.16,z,ww+.10,.43,.08,cement)
   if door:
    B('visible threshold',u,off-.13,z0-.04,ww+.18,.56,.08,cement)
    R('door pull',(u+.28,off+inset-.08,mid-.10),(u+.28,off+inset-.08,mid+.10),.012,zinc)
   else:
    B('varied casement mullion',u+(.12 if j%2 else-.16),off+inset-.045,mid,.045,.06,h,frame,False)
    B('casement crossbar',u,off+inset-.045,mid-.08,ww,.06,.035,frame,False)
    if (idx+j+lev)%3!=1:B('deep window chajja',u,off-.21,z1+.14,ww+.24,.84,.10,cement)
    if (idx+j+lev)%4==0:B('partly open timber shutter',u-ww/2-.20,off-.20,mid,.35,.09,h,timber,False)
  if gallery and upper:
   B('inhabited deep gallery slab',0,off-.60,fl-.03,width,1.50,.20,cement)
   rail(-half+.16,half-.16,off-1.30,fl+.08)
   for u in[-half+.18,.1,half-.18]:
    B('gallery structural upright',u,off-1.18,fl+1.40,.12,.12,2.70,frame)
    B('slab knee support',u,off-.45,fl-.26,.14,1.10,.32,cement)
   B('gallery ceiling thickness',0,off-.57,fl+2.78,width,1.48,.14,cement)
  if upper and lev-2<levels-1 and offsets[lev-1]>off+.3:
   nextoff=offsets[lev-1];B('stepped exposed terrace roof',0,(off+nextoff)/2,fl+fh-.10,width,nextoff-off+.30,.20,roof);rail(-half+.15,half-.15,off+.07,fl+fh,idx%2==0)
  # Repairs are restrained at plinths/sills, with larger articulated podium bays below roof.
  for j in range(2):B('local aged plaster patch',-half+.58+j*(width-.95),off-.013,fl+.35+j*.17,.63,.025,.40,repair,False)
  if lev==0:
   for u in[-half+.3,half-.3]:B('lower storey engaged pier',u,off-.08,fl+1.6,.32,.36,3.1,plaster)
 top=7.2+levels*3
 B('joined final roof slab',0,(offsets[-1]+depth)/2,top+.11,width,depth-offsets[-1],.22,roof)
 rail(-half,half,offsets[-1]+.10,top+.22,True)
 B('back roof parapet',0,depth-.11,top+.73,width,.22,1.02,plaster)
 # End parapets are omitted at property joins: one shared party roof seal is authored later.
 u=-width*.22;d=depth-1.25
 if idx in[0,2,4,6,8,9]:
  B('tank support plinth',u,d,top+.35,1.4,1.4,.26,cement)
  R('native domestic water tank',(u,d,top+.49),(u,d,top+1.63),.58,steel,20)
  for zz in[.54,.81,1.08,1.35,1.60]:R('tank rib',(u,d,top+zz-.018),(u,d,top+zz+.018),.60,frame,16)
  R('tank lid',(u,d,top+1.63),(u,d,top+1.69),.26,steel,16)
  pipe('tank supply/return',[(u,d,top+.60),(u+.72,d,top+.60),(u+.72,d,top+.23),(u+.72,.34,top+.23),(u+.72,.34,7.5)])
 if idx in[1,3,7,10]:
  u=width*.24;d=depth-1.4
  # Hollow roof access room, real recessed door, not a solid blank cube.
  for du in[-1.05,1.05]:B('inhabited headroom side',u+du,d,top+1.25,.20,2.15,2.06,plaster)
  B('headroom rear',u,d+1.0,top+1.25,2.30,.20,2.06,plaster)
  for du in[-.80,.80]:B('headroom front pier',u+du,d-1.0,top+1.25,.70,.20,2.06,plaster)
  B('headroom door lintel',u,d-1,top+2.21,2.3,.20,.14,plaster)
  B('headroom roof',u,d,top+2.35,2.50,2.35,.14,roof)
  B('headroom door',u,d-.83,top+1.2,.88,.065,1.94,timber,False)
  for du in[-.29,.29]:R('roof access ladder',(u+du,d-1.30,top+.22),(u+du,d-1.30,top+2.5),.022,steel)
  for k in range(8):R('ladder tread',(u-.29,d-1.30,top+.43+.28*k),(u+.29,d-1.30,top+.43+.28*k),.018,steel)
 # Vertical pipe begins at ground and terminates at coping: connects stories visibly.
 pipe('continuous shared rainwater downpipe',[(-half+.33,.02,.70),(-half+.33,.02,top+.95),(-half+.33,.55,top+.95)],.035)
 if idx in[0,4,7]:
  u=width*.1;d=offsets[-1]+1.35
  for du in[-1.25,1.25]:R('roof washline post',(u+du,d,top+.22),(u+du,d,top+1.73),.025,steel)
  R('washline',(u-1.25,d,top+1.66),(u+1.25,d,top+1.66),.006,seal)
  for j,du in enumerate([-.72,.06,.70]):B('domestic drying cloth',u+du,d,top+1.22,.46 if j!=1 else .62,.012,.74 if j!=1 else.51,[sage,lime,ochre][j],False)
 footprint=([-28,-front],[lo,hi])if edge=='left'else([front,28],[lo,hi])if edge=='right'else([lo,hi],[front,front+depth])if edge=='back'else([lo,hi],[front-depth,front])
 houses.append({'id':label,'edge':edge,'footprint':footprint,'frontM':front,'alongM':[lo,hi],'widthM':width,'depthM':depth,'upperLevels':levels,'floorToFloorUpperM':3.0,'lowerFloorToFloorM':3.3,'mainRoofZ':top+.22,'galleryDepthM':1.5 if gallery else 0,'doorClearM':2.1,'railHeightM':1.04,'parapetM':1.05,'setbacksM':offsets})
# Orthogonal exposed-surface extraction across ALL structural solids, hence no duplicate internal
# party-wall planes. Exact cuts are from authored dimensions; no voxel approximation/noise.
coords=[sorted({round(b['location'][a]+sgn*b['dimensions'][a]/2,2)for b in solid for sgn in[-1,1]})for a in range(3)]
shape=tuple(len(v)-1 for v in coords);print('EXACT_ORTHOGONAL_UNION_GRID',shape,int(np.prod(shape)),flush=True)
materialNames=list(dict.fromkeys(b['material']for b in solid));lookup=[{v:i for i,v in enumerate(c)}for c in coords];cells=np.zeros(shape,dtype=np.uint8)
for b in solid:
 lo=[lookup[a][round(b['location'][a]-b['dimensions'][a]/2,2)]for a in range(3)];hi=[lookup[a][round(b['location'][a]+b['dimensions'][a]/2,2)]for a in range(3)];cells[lo[0]:hi[0],lo[1]:hi[1],lo[2]:hi[2]]=materialNames.index(b['material'])+1
verts=[];faces=[];mats=[];vmap={}
def vertex(key):
 if key not in vmap:vmap[key]=len(verts);verts.append(tuple(key))
 return vmap[key]
# Merge equal-material exposed cells into exact planar rectangles before allocating mesh.
# Split EVERY rectangle edge at all shared surface vertices, eliminating T junctions.
for axis in range(3):
 u=(axis+1)%3;v=(axis+2)%3
 for sign in[-1,1]:
  for plane in range(shape[axis]):
   def slab(at):
    ar=np.take(cells,at,axis=axis)
    # np.take retains ascending other axes; orient as (u,v).
    return ar if u<v else ar.T
   a=slab(plane);neighbor=slab(plane+sign)if 0<=plane+sign<shape[axis]else np.zeros_like(a)
   mask=np.where(neighbor==0,a,0).copy()
   for i in range(mask.shape[0]):
    js=np.flatnonzero(mask[i])
    for j in js:
     mi=int(mask[i,j])
     if not mi:continue
     j1=j+1
     while j1<mask.shape[1] and mask[i,j1]==mi:j1+=1
     i1=i+1
     while i1<mask.shape[0]and np.all(mask[i1,j:j1]==mi):i1+=1
     mask[i:i1,j:j1]=0
     # Bound fan aspect ratio so corner angle weights do not collapse in MikkTSpace.
     u0,u1=coords[u][i],coords[u][i1];v0,v1=coords[v][j],coords[v][j1];du=u1-u0;dv=v1-v0
     nu=max(1,math.ceil(du/(8*dv)));nv=max(1,math.ceil(dv/(8*du)))
     for iu in range(nu):
      for iv in range(nv):
       ks=[]
       for uu,vv in[(u0+du*iu/nu,v0+dv*iv/nv),(u0+du*(iu+1)/nu,v0+dv*iv/nv),(u0+du*(iu+1)/nu,v0+dv*(iv+1)/nv),(u0+du*iu/nu,v0+dv*(iv+1)/nv)]:
        key=[0.,0.,0.];key[axis]=coords[axis][plane+(1 if sign==1 else 0)];key[u]=round(uu,2);key[v]=round(vv,2);ks.append(vertex(tuple(key)))
       faces.append(ks if sign==1 else list(reversed(ks)));mats.append(mi-1)
 print('UNION_AXIS',axis,'rectangles',len(faces),flush=True)
from bisect import bisect_left,bisect_right
lines={}
for key,vi in vmap.items():
 for axis in range(3):
  other=tuple(key[a]for a in range(3)if a!=axis);lines.setdefault((axis,other),[]).append((key[axis],vi))
for k in lines:lines[k].sort()
keys={vi:k for k,vi in vmap.items()}
for fi,f in enumerate(faces):
 outline=[]
 for ia,ib in zip(f,f[1:]+f[:1]):
  a,b=keys[ia],keys[ib];axis=next(i for i in range(3)if a[i]!=b[i]);line=lines[(axis,tuple(a[i]for i in range(3)if i!=axis))];positions=[x[0]for x in line];lo,hi=sorted([a[axis],b[axis]]);segment=line[bisect_left(positions,lo):bisect_right(positions,hi)]
  if a[axis]>b[axis]:segment=list(reversed(segment))
  outline.extend(vi for _,vi in segment[:-1])
 faces[fi]=outline
# Fan each planar rectangle from its interior, keeping all matched boundary vertices.
triangles=[];triangleMats=[]
for f,mi in zip(faces,mats):
 center=tuple((min(verts[i][a]for i in f)+max(verts[i][a]for i in f))/2 for a in range(3));ci=len(verts);verts.append(center)
 for a,b in zip(f,f[1:]+f[:1]):triangles.append((a,b,ci));triangleMats.append(mi)
faces=triangles;mats=triangleMats
mesh=bpy.data.meshes.new('REV11 continuous shared-wall shell');mesh.from_pydata(verts,[],faces);mesh.update()
for name in materialNames:mesh.materials.append(bpy.data.materials[name])
for p,mi in zip(mesh.polygons,mats):p.material_index=mi
bm=bmesh.new();bm.from_mesh(mesh);assert all(e.is_manifold for e in bm.edges),'Authored union has edge/corner-only contact; repair shapes'
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
obj=bpy.data.objects.new('REV11 / ONE continuous shared-wall structural shell',mesh);details.objects.link(obj);uvmetre(obj);new=[obj.name]
for (zone,mn),b in buckets.items():
 mesh=bpy.data.meshes.new('REV11 details '+zone);mesh.from_pydata(b['v'],[],b['f']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(mesh);bm.free();mesh.update();obj=bpy.data.objects.new('REV11 / '+zone+' / '+mn.split(' / ')[-1],mesh);details.objects.link(obj);mesh.materials.append(bpy.data.materials[mn]);uvmetre(obj);new.append(obj.name)
# Height-only duplicates retain original data/UV/materials and world XY/yaw; source is unchanged.
actors=json.loads((O/'evidence/before-survey.json').read_text())['actors'];scaleRecords=[]
def crowd(target,factor,label):
 co=bpy.data.collections.new('REV11 crowd '+label);target.collection.children.link(co);records=[]
 for actor in actors:
  foot=actor['bounds'][0][2];T=Matrix.Translation((0,0,foot))@Matrix.Diagonal((1,1,factor,1))@Matrix.Translation((0,0,-foot));names=[]
  for n in actor['objects']:
   ob=bpy.data.objects[n]
   # Remove shared original actor link only from this new scene's inherited collection.
   if n in locked.objects and target==s:locked.objects.unlink(ob)
   clone=ob.copy();clone.name='REV11 '+label+' / '+n
   if factor!=1:
    clone.data=ob.data.copy();W=np.array(ob.matrix_basis,dtype=np.float64);TT=np.eye(4);TT[2,2]=factor;TT[2,3]=foot*(1-factor);local=np.linalg.inv(W)@TT@W
    for va,vb in zip(ob.data.vertices,clone.data.vertices):vb.co=(local@np.array([*va.co,1.0]))[:3]
    clone.data.update()
   clone['actorSource']=n;clone['heightOnlyFactor']=factor;co.objects.link(clone);names.append(clone.name)
  records.append({'label':actor['label'],'sourceObjects':actor['objects'],'objects':names,'foot':actor['foot'],'anchorZ':foot,'heightOnlyFactor':factor,'oldHeightM':actor['heightM'],'newHeightM':actor['heightM']*factor,'worldXYAndYawUnchanged':True})
 return records,co
rows,cc=crowd(s,1.07,'H07');scaleRecords.append({'variant':'REV11','factor':1.07,'actors':rows});s['proposalOnly']=True;s['sourceIdentity']='REV10 A with selected B gallery-depth construction';s['selectedByUser']=False
for factor,label in[(1.0,'H00'),(1.06,'H06'),(1.09,'H09')]:
 c=s.copy();c.name='REV11 CONTROL / Crowd '+label;c['variant']='REV11 '+label;c.use_fake_user=True;c.collection.children.unlink(cc);rows,co=crowd(c,factor,label);scaleRecords.append({'variant':c['variant'],'factor':factor,'actors':rows})
bpy.context.window.scene=s;s.camera=bpy.data.objects['REV09 CAMERA / 02-entry-square'];s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();dest=O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
result={'status':'AUTHORED_PENDING_STRICT_VALIDATION_AND_VISUAL_REVIEW','masterSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'masterBytes':dest.stat().st_size,'baselineSHA256':'d530f164318ac4f736d43159b7eac705ca4233ac78d69fb545c2b71b950da850','scene':s.name,'variant':'REV11','newMeshes':new,'removedOnlyFromNewScenes':old['newMeshes'],'houses':houses,'structuralParts':solid,'detailParts':parts,'crowdVariants':scaleRecords,'orthogonalUnionExactCuts':{'shape':shape,'surfaceFacesBeforeDissolve':len(faces),'vertexCountBeforeDissolve':len(verts),'oneSharedWallShell':True,'BooleanModifierUsed':False},'newMaterialsImagesLights':0,'screenFloorRouteGeometryUnchanged':True,'entryOpeningM':16.6,'proposedHeightFactor':1.07,'historical15ScenesUnchanged':True}
(O/'evidence/authoring.json').write_text(json.dumps(result,indent=2,default=lambda v:list(v))+'\n');print('REV11_AUTHORED',result['masterSHA256'],result['masterBytes'],flush=True)
