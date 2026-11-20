import bpy,json,hashlib,math,argparse,sys,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];U3=R.parent/'navigation-board-rev15u3-larger-english-text-2026-11-14';plan=json.loads((R/'source/architecture-plan.json').read_text());pres=runpy.run_path(str(R/'source/preservation.py'));snapshot=pres['snapshot']
ap=argparse.ArgumentParser();ap.add_argument('--base',default=plan['source']);ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15V-Weathered-Cypher-Houses.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);out=Path(a.output);assert not out.exists(),'Existing output preserved.';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();fingerprint=runpy.run_path(str(U3/'source/scene-fingerprint.py'))['fingerprint'];basefp=fingerprint(base);assert basefp['sha256']==json.loads((U3/'evidence/native-scene-fingerprint.json').read_text())['sha256'];protected_before=snapshot(base,plan,'REV15U3 / ')
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15V / Weathered cypher houses and windows';s['variant']='REV15V'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
    ob=old.copy();ob.name='REV15V / '+old.name.removeprefix('REV15U3 / ')
    if old.type=='CAMERA':ob.data=old.data.copy()
    s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
    if old.parent in copies:ob.parent=copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15V / independent view')
for l in list(s.view_layers):
    if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
assets=bpy.data.collections.new('REV15V / Cypher architecture update');s.collection.children.link(assets)
images={};texture_hashes={r['file']:r['sha256'] for r in json.loads((R/'evidence/material-authoring.json').read_text())['files']}
def image(name,noncolor=False):
    if name not in images:
        assert sha(R/'textures'/name)==texture_hashes[name];im=bpy.data.images.load(str(R/'textures'/name));im.colorspace_settings.name='Non-Color' if noncolor else 'sRGB';im.pack();assert hashlib.sha256(im.packed_file.data).hexdigest()==texture_hashes[name];images[name]=im
    return images[name]
def material(name,base=(.3,.3,.3),rough=.8,metal=0):
    m=bpy.data.materials.new('REV15V / '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*base,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def textured(name,color,rough=None,normal=None,repeat=False,metal=0):
    m=material(name,metal=metal);nd=m.node_tree.nodes;lk=m.node_tree.links;p=nd.get('Principled BSDF');p.inputs['Specular IOR Level'].default_value=.23;uv=nd.new('ShaderNodeUVMap');uv.uv_map='REV15VFacadeUV'
    def tex(file,noncolor=False):
        t=nd.new('ShaderNodeTexImage');t.image=image(file,noncolor);t.extension='REPEAT' if repeat else 'EXTEND';lk.new(uv.outputs['UV'],t.inputs['Vector']);return t
    lk.new(tex(color).outputs['Color'],p.inputs['Base Color'])
    if rough:lk.new(tex(rough,True).outputs['Color'],p.inputs['Roughness'])
    if normal:
        n=nd.new('ShaderNodeNormalMap');n.uv_map='REV15VFacadeUV';n.inputs['Strength'].default_value=.78;lk.new(tex(normal,True).outputs['Color'],n.inputs['Color']);lk.new(n.outputs['Normal'],p.inputs['Normal'])
    return m
facade_mats={g:textured(g+' weathered limewash and masonry',g+'-color.jpg',g+'-rough.png',g+'-normal.jpg') for g in sorted({g for row in plan['objects'] for _,g in row['wallFaces']})}
sash=textured('Chipped pale sash paint','sash-paint.jpg',repeat=True);shutter=textured('Worn green timber shutter paint','shutter-paint.jpg',repeat=True);glass=textured('Dirt-fringed reflective glazing','glass-color.jpg','glass-rough.png',metal=.16);gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Coat Weight'].default_value=.55;gp.inputs['Coat Roughness'].default_value=.12;gp.inputs['IOR'].default_value=1.45
metal=material('Dark aged window grille steel',(.024,.032,.028),.58,.62);fixing=material('Oxidised grille fixings',(.085,.052,.025),.83,.35);concrete=material('Weathered sill and rain hood edges',(.29,.275,.24),.91)
modified=[]
for row in plan['objects']:
    old=base.objects[row['object']];ob=copies[old];me=old.data.copy();bindings=[slot.material for slot in old.material_slots];ob.data=me
    for i,mat in enumerate(bindings):me.materials[i]=mat;ob.material_slots[i].link='DATA'
    oldactive=me.uv_layers.active_index;uv=me.uv_layers.new(name='REV15VFacadeUV');slots={}
    def assign(face,mat):
        if mat.name not in slots:slots[mat.name]=len(me.materials);me.materials.append(mat)
        face.material_index=slots[mat.name]
    for fi,group in row['wallFaces']:
        f=me.polygons[fi];assign(f,facade_mats[group]);cfg=plan['facades'][group]
        for li in f.loop_indices:
            p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;u=(p.x if cfg['axis']=='x' else p.y);uv.data[li].uv=((u-cfg['min'])/(cfg['max']-cfg['min']),(p.z-7.2)/(cfg['top']-7.2))
    frame_mat=shutter if 'timber' in old.name else sash
    nm=ob.matrix_world.to_3x3().inverted().transposed()
    for fi in row['frameFaces']:
        f=me.polygons[fi];assign(f,frame_mat);n=(nm@f.normal).normalized()
        for li in f.loop_indices:
            p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(p.x/.35,p.y/.35) if abs(n.z)>.6 else (p.y/.35,p.z/.35) if abs(n.x)>abs(n.y) else (p.x/.35,p.z/.35)
    for fi,wi in row['glassFaces']:
        f=me.polygons[fi];assign(f,glass);w=plan['windows'][wi];t=Vector(w['tangent'])
        for li in f.loop_indices:
            p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.dot(t)-w['uMin'])/(w['uMax']-w['uMin']),(p.z-w['zMin'])/(w['zMax']-w['zMin']))
    me.uv_layers.active_index=oldactive;assets.objects.link(ob);modified.append(old.name)
def team_intersection(points):return max(p[0] for p in points)>13 and max(p[1] for p in points)>26.7 and min(p[1] for p in points)<38.3
batches={};counts={'grilles':0,'sills':0,'hoods':0,'rods':0,'fixings':0,'skippedProtectedParts':0}
def add(house,vs,fs,mi):
    if team_intersection(vs):counts['skippedProtectedParts']+=1;return False
    batch=batches.setdefault(house,{'vs':[],'fs':[],'mi':[]});start=len(batch['vs']);batch['vs'].extend(vs);batch['fs'].extend(tuple(start+i for i in f) for f in fs);batch['mi'].extend([mi]*len(fs));return True
def box(house,w,u,z,d,width,height,depth,mi):
    t=Vector(w['tangent']);n=Vector(w['normal']);vs=[tuple(t*(u+a*width/2)+n*(d+b*depth/2)+Vector((0,0,z+c*height/2))) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return add(house,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mi)
def rod(house,start,end,r=.007):
    a=Vector(start);b=Vector(end);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1))) if abs(axis.z)<.9 else axis.cross(Vector((1,0,0)));u.normalize();v=axis.cross(u);vs=[]
    for centre in [a,b]:
        for j in range(8):vs.append(tuple(centre+r*(math.cos(j*math.tau/8)*u+math.sin(j*math.tau/8)*v)))
    fs=[tuple(reversed(range(8))),tuple(range(8,16))]+[(j,(j+1)%8,(j+1)%8+8,j+8) for j in range(8)]
    if add(house,vs,fs,0):counts['rods']+=1
for index,w in enumerate(plan['windows']):
    width=w['uMax']-w['uMin'];height=w['zMax']-w['zMin'];house=w['house'];u=(w['uMax']+w['uMin'])/2;z=(w['zMax']+w['zMin'])/2;d=w['depth'];t=Vector(w['tangent']);n=Vector(w['normal'])
    if width<.5 or height<.6:continue
    point=lambda a,b:tuple(t*a+n*d+Vector((0,0,b)))
    if w['zMax']<13 or index%2==0:
        bars=max(3,round(width/.17));spacing=width/(bars+1)
        for j in range(1,bars+1):uu=w['uMin']+j*spacing;rod(house,point(uu,w['zMin']+.035),point(uu,w['zMax']-.035))
        for q in [.34,.68]:zz=w['zMin']+height*q;rod(house,point(w['uMin']+.035,zz),point(w['uMax']-.035,zz),.006)
        counts['grilles']+=1
        for uu in [w['uMin']+.04,w['uMax']-.04]:
            for zz in [w['zMin']+.04,w['zMax']-.04]:
                if box(house,w,uu,zz,d,.035,.035,.008,1):counts['fixings']+=1
    if box(house,w,u,w['zMin']-.06,d-.025,width+.16,.075,.18,2):counts['sills']+=1
    if w['zMin']>10.5 and index%3==0:
        if box(house,w,u,w['zMax']+.12,d+.065,width+.28,.075,.40,2):counts['hoods']+=1
added=[]
for house,batch in batches.items():
    me=bpy.data.meshes.new('REV15V / '+house+' window detail batch');me.from_pydata(batch['vs'],[],batch['fs']);me.update()
    for mat in [metal,fixing,concrete]:me.materials.append(mat)
    for f,i in zip(me.polygons,batch['mi']):f.material_index=i
    ob=bpy.data.objects.new(me.name,me);assets.objects.link(ob);ob['architectureHouse']=house;added.append(ob.name)
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert all(list(old.matrix_world)==list(ob.matrix_world) for old,ob in copies.items())
assert all(old.data==ob.data for old,ob in copies.items() if old.name not in modified and old.type!='CAMERA')
assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items())
assert fingerprint(base)['sha256']==basefp['sha256'],'Original U3 scene changed'
protected_after=snapshot(s,plan,'REV15V / ');assert protected_after==protected_before,'Protected geometry, original face materials, Team, posters, lights or navigation changed'
fp=fingerprint(s);fp.pop('data')
if a.restore:assert fp['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
if a.restore:result={'status':'PASS','restoredMaster':str(out),'restoredBytes':out.stat().st_size,'restoredSHA256':sha(out),'sceneFingerprintSHA256':fp['sha256'],'method':'Actual rebuild from restored U3 and the authored facade maps/plan, with exact active-scene fingerprint and protected-region snapshot match'};(R/'evidence/restore-check.json').write_text(json.dumps(result,indent=2)+'\n')
else:
    # The compact changed-surface native library is written by export.py.
    result={'status':'PASS','scene':s.name,'source':a.base,'sourceSHA256':sha(a.base),'sourceSceneFingerprint':basefp['sha256'],'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scenes':len(bpy.data.scenes),'historicalScenesPreserved':len(history),'modifiedObjects':modified,'newObjects':added,'windows':len(plan['windows']),'details':counts,'originalWallAndWindowGeometryUnchanged':True,'protectedSnapshot':protected_before,'TeamBuildingAndAllMuralsUnchanged':True,'allEightEventsPostersUnchanged':True,'navigationCrowdRoadAndLightsUnchanged':True,'productionWebsiteChanged':False};(R/'evidence/build-verification.json').write_text(json.dumps(result,indent=2)+'\n');(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n')
print(json.dumps({'status':'PASS','restore':a.restore,'modifiedObjects':len(modified),'windows':len(plan['windows']),'details':counts,'TeamAndEventsPostersPreserved':True}),flush=True)
