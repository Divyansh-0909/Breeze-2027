import bpy,json,hashlib,re,collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=Path('/dev/shm/Gullyverse-Rev15U3-Larger-English-Navigation.blend');expected='db96f8be1c6a1a31df85c9c81b9d81a6181d893b0c4d326c54132ddf1abea107';assert hashlib.sha256(P.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
facades={'L1':{'axis':'y','min':14.,'max':25.2,'top':20.},'L2':{'axis':'y','min':25.2,'max':37.,'top':25.},'L3':{'axis':'y','min':37.,'max':50.,'top':22.},'R1':{'axis':'y','min':14.,'max':27.,'top':22.},'R3':{'axis':'y','min':38.1,'max':50.,'top':25.},'F1':{'axis':'x','min':-28.,'max':-8.3,'top':22.},'F2':{'axis':'x','min':8.3,'max':28.,'top':22.},'B1':{'axis':'x','min':-28.,'max':0.,'top':25.},'B2':{'axis':'x','min':0.,'max':28.,'top':25.}}
def protected(pts):
    return max(p.x for p in pts)>13. and max(p.y for p in pts)>26.7 and min(p.y for p in pts)<38.3
def classify(p,n):
    if p.z<7.15:return None
    if p.x<-14. and 14<=p.y<=50 and n.x>.55:return 'L1' if p.y<25.2 else 'L2' if p.y<37 else 'L3'
    if p.x>14. and 14<=p.y<26.7 and n.x<-.55:return 'R1'
    if p.x>14. and 38.3<p.y<=50 and n.x<-.55:return 'R3'
    if 12.6<=p.y<=14.6 and n.y>.55 and abs(p.x)>8.2:return 'F1' if p.x<0 else 'F2'
    if 48.5<=p.y<=59 and n.y<-.55:return 'B1' if p.x<0 else 'B2'
    return None
def components(me):
    graph=[set() for _ in me.vertices]
    for e in me.edges:a,b=e.vertices;graph[a].add(b);graph[b].add(a)
    unseen=set(range(len(graph)));out=[]
    while unseen:
        start=min(unseen);unseen.remove(start);found={start};stack=[start]
        while stack:
            for i in graph[stack.pop()]:
                if i in unseen:unseen.remove(i);found.add(i);stack.append(i)
        out.append(found)
    return out
windows=[];plans={};wallroles=['mineral concrete','warm grey limewash','faded blue-green plaster','muted ochre plaster','localized render repair']
for ob in s.objects:
    if ob.type!='MESH':continue
    match=re.search(r'/ (L[123]|R[123]|F[12]|B[12]) /',ob.name+' / '+str(ob.get('sourceObjectName','')));house=match.group(1) if match else None
    shell='Existing Events house shell' in ob.name
    if (not house and not shell) or house=='R2':continue
    me=ob.data;world=[ob.matrix_world@v.co for v in me.vertices];nm=ob.matrix_world.to_3x3().inverted().transposed();row={'object':ob.name,'house':house,'wallFaces':[],'frameFaces':[],'glassFaces':[]}
    for f in me.polygons:
        mat=ob.material_slots[f.material_index].material
        if not mat or not any(k in mat.name for k in wallroles):continue
        pts=[world[i] for i in f.vertices]
        if protected(pts):continue
        centre=sum(pts,Vector())/len(pts)
        if max(p.z for p in pts)<7.2:continue
        centre.z=max(centre.z,7.2);normal=(nm@f.normal).normalized();group=classify(centre,normal)
        if group:row['wallFaces'].append([f.index,group])
    mats=' '.join(x.material.name for x in ob.material_slots if x.material)
    if 'dusty non-emissive glazing' in mats or 'muted timber green shutters' in mats:
        for comp in components(me):
            pts=[world[i] for i in sorted(comp)];centre=sum(pts,Vector())/len(pts)
            if protected(pts) or max(p.z for p in pts)<7.45:continue
            if not house:continue
            faces=[f for f in me.polygons if f.vertices[0] in comp];front=max(faces,key=lambda f:f.area);normal=(nm@front.normal).normalized()
            toward=Vector((0,31,centre.z))-centre
            if normal.dot(toward)<0:normal=-normal
            if abs(normal.z)>.15:continue
            tangent=Vector((0,0,1)).cross(normal).normalized();u=[p.dot(tangent) for p in pts];z=[p.z for p in pts];depth=[p.dot(normal) for p in pts]
            if 'glazing' in mats:
                idx=len(windows);windows.append({'id':f'{house}-W{idx+1:02d}','object':ob.name,'house':house,'faces':[f.index for f in faces],'centre':list(centre),'normal':list(normal),'tangent':list(tangent),'uMin':min(u),'uMax':max(u),'zMin':min(z),'zMax':max(z),'depth':max(depth)+.035,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
                row['glassFaces'].extend([f.index,idx] for f in faces)
            else:row['frameFaces'].extend(f.index for f in faces)
    if any(row[k] for k in ['wallFaces','frameFaces','glassFaces']):plans[ob.name]=row
# Sash faces near the eligible glass panes receive worn paint; unrelated upper rails stay as before.
for ob in s.objects:
    if ob.type!='MESH' or not any(x.material and 'aged painted sash' in x.material.name for x in ob.material_slots):continue
    match=re.search(r'/ (L[123]|R[123]|F[12]|B[12]) /',ob.name+' / '+str(ob.get('sourceObjectName','')))
    if not match or match.group(1)=='R2':continue
    house=match.group(1);row=plans.setdefault(ob.name,{'object':ob.name,'house':house,'wallFaces':[],'frameFaces':[],'glassFaces':[]})
    for f in ob.data.polygons:
        p=ob.matrix_world@f.center
        if p.z<7.3:continue
        for w in windows:
            if w['house']!=house:continue
            n=Vector(w['normal']);t=Vector(w['tangent']);u=p.dot(t)
            if w['uMin']-.14<u<w['uMax']+.14 and w['zMin']-.14<p.z<w['zMax']+.14 and abs(p.dot(n)-w['depth'])<.27:
                row['frameFaces'].append(f.index);break
plans={k:v for k,v in plans.items() if any(v[x] for x in ['wallFaces','frameFaces','glassFaces'])}
poster=[o.name for o in s.objects if 'EVENTS clearly labelled placeholder' in o.name];assert len(poster)==8
result={'status':'PASS','source':str(P),'sourceSHA256':expected,'protectedTeamRegion':{'rule':'Reject every face/component whose bounds intersect x>13, 26.7<y<38.3; skip every R2 object entirely, preserving the whole Team house and its upper windows.'},'facades':facades,'objects':list(plans.values()),'windows':windows,'protectedPosters':poster,'preserveAllOriginalMaterials':True}
(R/'source/architecture-plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','objects':len(plans),'wallFaces':sum(len(x['wallFaces']) for x in plans.values()),'frameFaces':sum(len(x['frameFaces']) for x in plans.values()),'glassFaces':sum(len(x['glassFaces']) for x in plans.values()),'windows':len(windows),'facades':sorted({g for row in plans.values() for f,g in row['wallFaces']})}),flush=True)
