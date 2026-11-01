import bpy,json,math,random,hashlib,re
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1]
OLD=Path(bpy.data.filepath)
assert hashlib.sha256(OLD.read_bytes()).hexdigest()=='6041c26ac21fd990f14e2dae0fbe2cad15c21739f045d8cf56b7b8439a9e239a'
SEED=2026102505;rng=random.Random(SEED)
BASE=O/'source/baseline'
prior=json.loads((BASE/'evidence/crowd-composition.json').read_text())['people']
bylabel={p['label']:p for p in prior}
base_labels=sorted(p['label']for p in prior if p['label'].startswith('Audience '))
assert len(base_labels)==48
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
def canonical(label):
    row=bylabel[label];theta=math.radians(row['angleDeg']);origin=Vector(row['foot'])
    objects=sorted([o for o in bpy.data.objects if o.name.startswith(label+' ')],key=lambda o:o.name)
    assert len(objects)==8 and all(o.parent is None for o in objects)
    matrices={o.name:Matrix.Rotation(-theta,4,'Z')@Matrix.Translation(-origin)@o.matrix_basis for o in objects}
    points=[matrices[o.name]@v.co for o in objects for v in o.data.vertices]
    floor=min(p.z for p in points)
    matrices={name:Matrix.Translation((0,0,-floor))@m for name,m in matrices.items()}
    points=[Vector((p.x,p.y,p.z-floor))for p in points]
    return objects,matrices,points
templates={label:canonical(label)for label in bylabel}
banner=bpy.data.objects.get('Festival takeover banner');assert banner is not None
assert any(n.type=='TEX_IMAGE'and n.image and n.image.name=='graphic-festival.jpg'for m in banner.data.materials for n in m.node_tree.nodes)
banner_record={'name':banner.name,'collections':[c.name for c in banner.users_collection],'basis':[list(r)for r in banner.matrix_basis],'dedicatedSupports':[],'removedOnlyThisPlane':True,'smallCPosterPreserved':bpy.data.objects.get('Small festival lane poster')is not None}
bpy.data.objects.remove(banner,do_unlink=True)
common=bpy.data.collections['03_SHARED_NEUTRAL_CROWD_PROXIES']
cloths=[bpy.data.materials['Crowd clothing '+str(i)]for i in range(5)]
anchors=[(-9.2,36),(-5.1,35),(5.9,34.4),(10.3,37.7),(-6.1,40.8),(5.9,40.5),(-10.7,41.4),(10.4,42.2),(-3.8,38.1),(3.8,37.2)]
accepted=[];records=[];changed=[];created=[];attempts=0
def candidate():
    if rng.random()<.66:
        ax,ay=rng.choice(anchors);return rng.gauss(ax,1.6),rng.gauss(ay,1.35)
    r=math.sqrt(rng.uniform(5.7**2,14.25**2));theta=rng.uniform(-math.radians(85),math.radians(85))
    return r*math.sin(theta),45.8-r*math.cos(theta)
def compose(label,template,role,collection,is_new=False):
    global attempts
    objects,matrices,points=templates[template]
    for attempt in range(60000):
        attempts+=1;x,y=candidate();radius=math.hypot(x,45.8-y)
        if radius<5.7 or radius>14.25 or abs(x)<2.05 or abs(x)>14.4 or y<30.75 or y>44.7:continue
        theta=math.atan2(x,45.8-y)+math.radians(rng.uniform(-11,11))
        width=rng.uniform(.92,1.08);height=rng.uniform(.96,1.12)
        linear=Matrix.Rotation(theta,4,'Z')@Matrix.Diagonal((width,width,height,1))
        shape=hull([(linear@p).xy for p in points]);footprint=[(px+x,py+y)for px,py in shape]
        if min(abs(px)for px,py in footprint)<1.65:continue
        if any(abs(px)>14.75 or py<30.5 or py>45.1 for px,py in footprint):continue
        if not all(separated(footprint,old['footprint'],.10)for old in accepted):continue
        break
    else:raise RuntimeError('Could not fit actor without body-footprint overlap: '+label)
    transform=Matrix.Translation((x,y,7.2))@linear;made=[]
    for original in objects:
        part=original.name[len(template)+1:]
        if is_new:
            obj=original.copy();obj.name=label+' '+part;collection.objects.link(obj);created.append(obj.name)
            for slot in obj.material_slots:
                if slot.material and slot.material.name.startswith('Crowd clothing '):slot.link='OBJECT';slot.material=rng.choice(cloths)
        else:obj=original;changed.append(obj.name)
        obj.matrix_basis=transform@matrices[original.name];obj.update_tag(refresh={'OBJECT'});made.append(obj.name)
    row={'label':label,'sourceTemplate':template,'role':role,'foot':[x,y,7.2],'yawRadians':theta,'viewAngleVariationDegrees':math.degrees(theta-math.atan2(x,45.8-y)),'widthScale':width,'heightScale':height,'footprint':footprint,'objects':made}
    accepted.append(row);records.append(row)
for i in range(144):
    existing=i<48;template=base_labels[i%48]if existing else rng.choice(base_labels)
    label=base_labels[i]if existing else'Organic audience %03d'%i
    compose(label,template,'shared organic audience',common,not existing)
for prefix,count,variant in [('Festival extra ',8,'B'),('Balanced extra ',4,'C')]:
    collection=bpy.data.collections['11_'+variant+'_FESTIVAL_GRAPHICS_AND_PROPS']
    for i in range(count):compose(prefix+str(i),prefix+str(i),'variant extras',collection)
for s in bpy.data.scenes:
    bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0
master=O/'source/Gullyverse-Organic-Crowd-No-Banner-Intermediate.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
result={'status':'AUTHORED','seed':SEED,'attempts':attempts,'sharedAudienceCount':144,'oldAudienceCounts':{'A':48,'B':56,'C':52},'newAudienceCounts':{'A':144,'B':152,'C':148},'bodyFootprintGapM':.10,'protectedCentralHalfWidthM':1.65,'removedBanner':banner_record,'changedExistingCrowdParts':changed,'addedCrowdParts':created,'actors':records,'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'baselineSHA256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'note':'Actual projected body hulls, not only foot centers, determine every rejection. Source geometry is linked/reused; new clothing overrides are object-owned.'}
(O/'evidence/organic-crowd-authoring.json').write_text(json.dumps(result,indent=2)+'\n');print('ORGANIC_CROWD_AUTHORED',result['newAudienceCounts'],'attempts',attempts,flush=True)
