"""Authorized Rev05B: genuine shop cavities and dense-center static crowd. No website changes."""
import bpy,json,math,random,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from shop_recess import make_recess,SHOPS,floor
assert '--rev05b-authorized' in sys.argv
baseline=O/'source/baseline/Rev05A.blend'
assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='b143dc873b9566217301119f97cf349a73db58d7fdc1591c451e2daf7000ee8c'
assert Path(bpy.data.filepath)==baseline
objects=list(bpy.data.objects);shelves=[o for o in objects if o.name.startswith('Shop stock shelf')];items=[o for o in objects if o.name.startswith('Dry goods carton')]
assert len(shelves)==45 and len(items)==180
architecture=[];assemblies=[];moved=[]
for side,cy,index in SHOPS:
    g=floor(cy);building=bpy.data.objects[f'Building / {side} / {index}']
    trim=min([o for o in objects if o.name.startswith('Shop recess')and o.location.x*side>0],key=lambda o:abs(o.location.y-cy))
    back=min([o for o in objects if o.name.startswith('Shop warm interior')and o.location.x*side>0],key=lambda o:abs(o.location.y-cy))
    architecture.extend([make_recess(building,side,cy,g),make_recess(trim,side,cy,g,True)])
    old=back.matrix_basis.copy();back.location.x=side*8.32
    architecture.append({'object':back.name,'oldBasis':[list(r)for r in old],'newBasis':[list(r)for r in back.matrix_basis],'backLining':True})
    for bank,(dy,depth,wall)in enumerate([(-2.3,5.5,-1),(0,7.25,-1),(2.3,6.35,1)]):
        old_y=cy+dy;stock=[o for o in shelves if o.location.x*side>0 and abs(o.location.y-old_y)<.01]
        cargo=[o for o in items if o.location.x*side>0 and abs(o.location.y-old_y)<.71]
        assert len(stock)==3 and len(cargo)==12
        pivot=Vector((side*3.83,old_y,g));new=Vector((side*depth,cy+wall*2.78,g))
        rigid=Matrix.Translation(new)@Matrix.Rotation(side*wall*math.pi/2,4,'Z')@Matrix.Translation(-pivot)
        names=[]
        for obj in stock+cargo:
            before=obj.matrix_basis.copy();obj.matrix_basis=rigid@before;obj.update_tag(refresh={'OBJECT'})
            moved.append({'object':obj.name,'shop':[side,cy],'bank':bank,'before':[list(r)for r in before],'after':[list(r)for r in obj.matrix_basis]});names.append(obj.name)
        assemblies.append({'shop':[side,cy],'bank':bank,'sideWallY':cy+wall*2.78,'rigidMatrix':[list(r)for r in rigid],'objects':names})
assert len(moved)==225
lights=[]
for side,cy,index in SHOPS:
    name=f'Rev05B shop interior practical {side} {cy}'
    light=bpy.data.lights.new(name,'AREA');light.shape='RECTANGLE';light.size=3;light.size_y=3.8;light.energy=45;light.color=(1,.78,.57);light.use_shadow=True
    obj=bpy.data.objects.new(name,light);bpy.data.collections['00_SHARED_SITE_ARCHITECTURE'].objects.link(obj);obj.location=(side*6.1,cy,floor(cy)+2.72)
    lights.append({'name':name,'position':list(obj.location),'watts':45,'shadow':True,'scope':'Interior only; authorized readability exception, no visible replacement fixture or global/street lighting edit.'})

prior=json.loads((O/'source/baseline/organic-crowd-authoring.json').read_text())['actors']
bylabel={r['label']:r for r in prior};shared=[r for r in prior if r['role']=='shared organic audience'];assert len(shared)==144
target_names={n for r in prior for n in r['objects']}
def hull(points):
    pts=sorted(set((round(float(x),7),round(float(y),7))for x,y in points))
    def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lo=[];hi=[]
    for p in pts:
        while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]
def separated(a,b,gap=.10):
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
            if length<1e-9:continue
            nx=-dy/length;ny=dx/length;aa=[x*nx+y*ny for x,y in a];bb=[x*nx+y*ny for x,y in b]
            if max(aa)+gap<=min(bb)or max(bb)+gap<=min(aa):return True
    return False
def canonical(row):
    inverse=(Matrix.Translation(row['foot'])@Matrix.Rotation(row['yawRadians'],4,'Z')@Matrix.Diagonal((row['widthScale'],row['widthScale'],row['heightScale'],1))).inverted()
    parts=[bpy.data.objects[n]for n in row['objects']];matrices={o.name:inverse@o.matrix_basis for o in parts};points=[matrices[o.name]@v.co for o in parts for v in o.data.vertices]
    return parts,matrices,points
templates={r['label']:canonical(r)for r in prior}
pv=[];pf=[]
for obj in bpy.data.objects:
    if obj.type!='MESH'or obj.name in target_names or obj.name.startswith(('Bounded lane haze','Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron')):continue
    assert obj.parent is None
    off=len(pv);pv.extend(obj.matrix_basis@v.co for v in obj.data.vertices);pf.extend(tuple(off+i for i in p.vertices)for p in obj.data.polygons)
props=BVHTree.FromPolygons(pv,pf)
SEED=2026102506;rng=random.Random(SEED);accepted=[];records=[];changed=[];added=[];attempts=0
common=bpy.data.collections['03_SHARED_NEUTRAL_CROWD_PROXIES'];cloths=[bpy.data.materials['Crowd clothing '+str(i)]for i in range(5)]
anchors={'board':[(-3,24.5),(2.7,26)],'transition':[(-3.8,29.4),(4.6,30.1),(.6,31.2)],'middle':[(-5.1,34.5),(4.8,35.1),(-1.5,35.7),(1.7,34.7)],'dense':[(-5.7,39.7),(-1.5,41.2),(2.1,39.4),(6.5,40.2),(.2,38.5)],'left_wing':[(-12,34.6),(-10.4,39.3),(-13.2,42)],'right_wing':[(10.9,33.9),(12.9,38.7),(11.9,42.5)]}
limits={'board':(-5.5,5.5,23.8,27.4),'transition':(-8.5,8.5,28,32.5),'middle':(-10.5,10.5,32.5,37.6),'dense':(-10.8,10.8,37.3,43.2),'left_wing':(-14.3,-9.4,31.7,43.6),'right_wing':(9.4,14.3,31.4,43.6)}
def candidate(role):
    lo,hi,near,far=limits[role]
    if rng.random()<.58:
        ax,ay=rng.choice(anchors[role]);return rng.gauss(ax,1.05 if'wing'in role else 1.6),rng.gauss(ay,.95 if'wing'in role else 1.3)
    return rng.uniform(lo,hi),rng.uniform(near,far)
def compose(label,template,role,is_new=False):
    global attempts
    parts,matrices,points=templates[template];lo,hi,near,far=limits[role]
    for trial in range(60000):
        attempts+=1;x,y=candidate(role)
        if not(lo<=x<=hi and near<=y<=far):continue
        yaw=math.atan2(x,45.8-y)+math.radians(rng.uniform(-12,12));width=rng.uniform(.94,1.07);height=rng.uniform(.96,1.11)
        linear=Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((width,width,height,1));transform=Matrix.Translation((x,y,7.2))@linear
        shape=hull([(linear@p).xy for p in points]);footprint=[(px+x,py+y)for px,py in shape]
        if any(abs(px)>14.75 or py<23.4 or py>44.2 for px,py in footprint):continue
        # Exact straight walk ends at Y=36.5. Keep a narrow physical capsule buffer,
        # then allow the crowd to occupy the complete center in front of that endpoint.
        if min(py for px,py in footprint)<36.95 and not(all(px>=.45 for px,py in footprint)or all(px<=-.45 for px,py in footprint)):continue
        if role=='board'and any(abs(px)<1.4 for px,py in footprint):continue
        if not all(separated(footprint,r['footprint'])for r in accepted):continue
        verts=[];faces=[]
        for obj in parts:
            off=len(verts);m=transform@matrices[obj.name];verts.extend(m@v.co for v in obj.data.vertices);faces.extend(tuple(off+i for i in p.vertices)for p in obj.data.polygons)
        if BVHTree.FromPolygons(verts,faces).overlap(props):continue
        break
    else:raise RuntimeError('No safe placement for '+label+' / '+role)
    names=[]
    for original in parts:
        if is_new:
            obj=original.copy();obj.name=label+' '+original.name[len(template)+1:];common.objects.link(obj);added.append(obj.name)
            for slot in obj.material_slots:
                if slot.material and slot.material.name.startswith('Crowd clothing '):slot.link='OBJECT';slot.material=rng.choice(cloths)
        else:obj=original;changed.append(obj.name)
        obj.matrix_basis=transform@matrices[original.name];obj.update_tag(refresh={'OBJECT'});names.append(obj.name)
    row={'label':label,'sourceTemplate':template,'role':role,'foot':[x,y,7.2],'yawRadians':yaw,'widthScale':width,'heightScale':height,'viewAngleVariationDegrees':math.degrees(yaw-math.atan2(x,45.8-y)),'footprint':footprint,'objects':names};records.append(row);accepted.append(row)
roles=['board']*6+['transition']*14+['middle']*36+['dense']*92+['left_wing']*14+['right_wing']*14
assert len(roles)==176
for i,role in enumerate(roles):
    existing=i<144;row=shared[i]if existing else rng.choice(shared);label=row['label']if existing else'Rev05B audience %03d'%i
    compose(label,row['label'],role,not existing)
for row in prior:
    if row in shared:continue
    compose(row['label'],row['label'],'dense')
from diagnostic_cameras import add_cameras
diagnostics=add_cameras()
for scene in bpy.data.scenes:
    scene['rev05b_status']='OPEN_SHOPS_AND_DENSE_CENTER_STATIC_CROWD';scene['rev05_shelf_status']='IMPLEMENTED_REV05B_USER_EXCEPTION'
    bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0
master=O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend';bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
result={'status':'AUTHORED','seed':SEED,'attempts':attempts,'baselineSHA256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'oldAudienceCounts':{'A':144,'B':152,'C':148},'newAudienceCounts':{'A':176,'B':184,'C':180},'actors':records,'changedExistingCrowdParts':changed,'addedCrowdParts':added,'bodyFootprintGapM':.10,'straightWalkEndY':36.5,'narrowPassageBodyBoundaryX':.45,'centralGapEndsAtY':36.95,'staticCenterFillNoParting':True,'architecture':architecture,'assemblies':assemblies,'shelfAndItemTransforms':moved,'newLights':lights,'newDiagnostics':diagnostics,'newTextureImages':[],'removedObjects':[],'bannerStillAbsent':bpy.data.objects.get('Festival takeover banner')is None,'cavityDepthM':4.4,'depthReason':'3.8m draft left insufficient doorway capsule clearance; original external bounds unchanged.'}
(O/'evidence/rev05b-authoring.json').write_text(json.dumps(result,indent=2)+'\n');print('REV05B_AUTHORED',result['newAudienceCounts'],'attempts',attempts,flush=True)
