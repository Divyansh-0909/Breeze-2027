import bpy,bmesh,json,hashlib,runpy,math,argparse,sys
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=read('source/plan.json');geo=runpy.run_path(str(R/'source/geometry.py'));Batch=geo['Batch'];material=geo['material'];quads=geo['quads'];image_material=geo['image_material'];snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'];face_sig=runpy.run_path(str(R/'source/face-preservation.py'))['faces_signature'];ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15X1-Accommodation-Clean-Wall.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15Y-Enquiry-Window-and-Monochrome-Lettering.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);out=Path(a.output);assert not out.exists(),'Choose a new output filename';sourceSHA=sha(a.base);bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();basefp=fp(base);assert basefp['sha256']=='4852c39dc337c366fe2be41bac4b34b4f1f8019a29a9a20bac6d8350bd51f6b7';history={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes};removed=set(plan['removedAccommodationBarrierObjects']);edits={row['object']:row for row in plan['windowEdits']};mural=next(o for o in base.objects if o.get('accommodationPart')=='COMING above SOON graffiti');excluded=removed|set(edits)|{mural.name};protected=snapshot(SimpleNamespace(objects=[o for o in base.objects if o.name not in excluded]),{'objects':[]},'REV15X1 / ');face_before={name:face_sig(base.objects[name],row['removeFaces'])for name,row in edits.items()};n=Vector(plan['normal']);t=Vector(plan['tangent']);up=Vector((0,0,1));u0=plan['openCentreU'];leftWidth=plan['personWidthM'];rightWidth=plan['messageWidthM'];gap=plan['dividerWidthM'];boardLeft=u0+leftWidth/2+gap;boardRight=boardLeft+rightWidth;frameLeft=u0-leftWidth/2-.10;frameRight=boardRight+.10;frameU=(frameLeft+frameRight)/2;depth=plan['contact']['frontDepth'];P=lambda u,d,z:t*u+n*d+up*z
# Project the title onto the existing house surface before adding any props.
deps=bpy.context.evaluated_depsgraph_get();titleW=1.75;titleH=250/980*titleW;titleZ=9.73;titleRecords=[]
def atlas_uv(rect):
 x0,y0,x1,y1=rect;return[(x0/1024,1-y1/1536),(x1/1024,1-y1/1536),(x1/1024,1-y0/1536),(x0/1024,1-y0/1536)]
rect=plan['lettering']['contactPixels'];x0,y0,x1,y1=rect
for i in range(24):
 for j in range(4):
  points=[];uv=[]
  for du,dz in [(0,0),(1,0),(1,1),(0,1)]:
   uu=frameU-titleW/2+(i+du)*titleW/24;zz=titleZ-titleH/2+(j+dz)*titleH/4;hit=base.ray_cast(deps,P(uu,-20.2,zz),-n,distance=4);assert hit[0],('No heading host',uu,zz);points.append(tuple(hit[1]+hit[2]*.006));uv.append(((x0+(x1-x0)*(i+du)/24)/1024,1-(y1-(y1-y0)*(j+dz)/4)/1536))
  titleRecords.append((points,uv))
s=base.copy();s.name='REV15Y / Enquiry window and monochrome graffiti';s['variant']='REV15Y'
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 if old.name in removed:continue
 ob=old.copy();ob.name='REV15Y / '+old.name.removeprefix('REV15X1 / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for driver in ob.animation_data.drivers:
   for var in driver.driver.variables:
    for target in var.targets:
     if target.id in copies:target.id=copies[target.id]
layer=s.view_layers.new('REV15Y / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for node in s.node_tree.nodes:
 if node.type=='R_LAYERS':node.scene=s;node.layer=layer.name
changed=[]
for name,row in edits.items():
 old=base.objects[name];ob=copies[old];me=old.data.copy();ob.data=me;attr=me.attributes.new('REV15YSourceFace','INT','FACE')
 for i,v in enumerate(attr.data):v.value=i
 bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();targets=[bm.faces[i]for i in row['removeFaces']];bmesh.ops.delete(bm,geom=targets,context='FACES');bm.to_mesh(me);bm.free();me.update();assert face_sig(ob)==face_before[name],('Non-target window face changed',name);changed.append(ob)
collection=bpy.data.collections.new('REV15Y / Enquiry window');s.collection.children.link(collection);atlasPath=R/'assets/brush-lettering-atlas.png';atlas=bpy.data.images.load(str(atlasPath));atlas.name='REV15Y / White brush CONTACT US COMING SOON';atlas.alpha_mode='STRAIGHT';atlas.colorspace_settings.name='sRGB';atlas.pack();assert hashlib.sha256(atlas.packed_file.data).hexdigest()==sha(atlasPath);paint=image_material('White brush lettering with charcoal edging',atlas);title=quads('CONTACT US centred house paint',collection,titleRecords,paint,'contact heading');title['headingText']='CONTACT US';title['centreU']=frameU
# Two texture regions remove the generous atlas gap while keeping equal letter height.
art=copies[mural];records=[]
for text,rect,w,z in [('COMING',plan['lettering']['comingPixels'],2.30,9.13),('SOON',plan['lettering']['soonPixels'],2.30*710/980,8.32)]:
 h=w*(rect[3]-rect[1])/(rect[2]-rect[0]);x=-12.015;y=14.009;points=[(x+w/2,y,z-h/2),(x-w/2,y,z-h/2),(x-w/2,y,z+h/2),(x+w/2,y,z+h/2)];records.append((points,atlas_uv(rect)))
temp=quads('Accommodation brush paint data',collection,records,paint,'temporary');art.data=temp.data;bpy.data.objects.remove(temp,do_unlink=True);art['letteringStyle']='White dry-brush names/roles style';art['textLines']=json.dumps(['COMING','SOON']);art['atlasSHA256']=sha(atlasPath)
wood=material('Worn green painted timber',(.095,.17,.12),.88,grain=46);timber=material('Aged timber sill',(.17,.12,.07),.92,grain=62);steel=material('Dull corrugated galvanised shade',(.15,.18,.16),.73,.55,grain=96);inner=material('Deep shaded room',(.017,.028,.022),.99);paper=material('Warm off-white message panel',(.78,.76,.66),.94,grain=130);field=material('Off-white form fields',(.89,.87,.79),.93);ink=material('Charcoal form lettering',(.019,.025,.020),.93);border=material('Soft dark green field edges',(.14,.20,.16),.92);button=material('Send message green',(.045,.105,.07),.85)
hardware=Batch();basis=(t,n,up)
def box(u,d,z,w,h,deep,mi=0):hardware.box(P(u,d,z),(w,deep,h),mi,basis)
# A continuous enquiry frontage spans the open person bay and wider message panel.
for u in [frameLeft+.06,frameRight-.06,boardLeft-.055]:box(u,depth+.06,8.79,.12,1.42,.14)
for z in [8.10,9.47]:box(frameU,depth+.06,z,frameRight-frameLeft,.12,.14)
box(frameU,depth+.19,8.09,frameRight-frameLeft+.18,.11,.53,1)
box(u0,plan['window']['depth']-.55,8.78,leftWidth+1.0,1.7,.04,3)
# Left shutter stands open beside the person bay.
for z in [8.28,8.52,8.76,9.00,9.24]:box(frameLeft-.16,depth+.12,z,.23,.18,.055,0)
box((boardLeft+boardRight)/2,depth+.025,8.79,rightWidth,1.22,.08,4)
panel=quads('Wide message-panel surface',collection,[([tuple(P(boardLeft+.065,depth+.075,8.21)),tuple(P(boardRight-.065,depth+.075,8.21)),tuple(P(boardRight-.065,depth+.075,9.37)),tuple(P(boardLeft+.065,depth+.075,9.37))],[(0,0),(1,0),(1,1),(0,1)])],paper,'message panel');panel['messageWidthFraction']=rightWidth/(leftWidth+rightWidth+gap)
# Native visual fields; runtime HTML replaces these labels/boxes in the private interaction preview.
form=Batch()
for i in range(3):
 uu=boardLeft+.12+(i+.5)*(rightWidth-.24)/3;form.box(P(uu,depth+.088,9.055),((rightWidth-.34)/3,.014,.16),0,basis)
form.box(P((boardLeft+boardRight)/2,depth+.088,8.65),(rightWidth-.24,.014,.34),0,basis);form.box(P(boardRight-.53,depth+.094,8.34),(.82,.018,.16),1,basis);formObj=form.object('Native message-field illustration',collection,[field,button],'native form illustration')
labels=[];fontBasis=Matrix((t,up,n)).transposed().to_4x4()
def label(text,u,z,size=.067,color=None):
 data=bpy.data.curves.new('REV15Y / '+text,'FONT');data.body=text;data.size=size;data.align_x='LEFT';data.align_y='CENTER';ob=bpy.data.objects.new(data.name,data);collection.objects.link(ob);ob.matrix_world=Matrix.Translation(P(u,depth+.112,z))@fontBasis;data.materials.append(color or ink);ob['contactPart']='native form label';labels.append(ob);return ob
label('LEAVE A MESSAGE',boardLeft+.12,9.285,.090)
for i,text in enumerate(['NAME','EMAIL','PHONE']):label(text,boardLeft+.14+i*(rightWidth-.24)/3,9.18,.058)
label('Your name',boardLeft+.15,9.055,.062);label('you@example.com',boardLeft+.15+(rightWidth-.24)/3,9.055,.057);label('+91 ...',boardLeft+.15+2*(rightWidth-.24)/3,9.055,.062);label('MESSAGE',boardLeft+.14,8.91,.058);label('Tell us how we can help...',boardLeft+.15,8.71,.064);label('Talk to the crew',boardLeft+.14,8.34,.063);label('Send message',boardRight-.89,8.34,.065,field)
hardwareObj=hardware.object('Enquiry timber frame and counter',collection,[wood,timber,steel,inner,paper],'window frame')
roof=Batch();width=frameRight-frameLeft+.28
for i in range(42):
 u=frameU-width/2+(i+.5)*width/42;roof.box(P(u,depth+.36,10.28+.018*(i%2)),(width/42+.004,.78,.035),0,basis)
roofObj=roof.object('Small corrugated house shade',collection,[steel],'corrugated shade')
# One additional crew person, copied from the approved Aftermovie character geometry.
choice=plan['actorChoices'][0];source=base.objects[choice['object']];me=source.data.copy();person=bpy.data.objects.new('REV15Y / Crew member peeking from left',me);collection.objects.link(person);floor=7.2;personU=u0-.30;personD=plan['contact']['personDepth']
for v in me.vertices:
 local=v.co.copy();w=max(0,min(1,(local.z-1.25)/.5));local.x-=.14*w;local.y+=.07*w;v.co=P(personU,personD,floor)+(-t)*local.x+n*local.y+up*local.z
me.update();person['contactPart']='attendant';person['sourceActorMesh']=source.data.name;person['sourceActorObject']=source.name;person['pose']='Standing inside the actual opening, leaning from its visual left';iris={i for f in me.polygons if 'iris'in person.material_slots[f.material_index].material.name for i in f.vertices};eye=sum((me.vertices[i].co for i in iris),Vector())/len(iris)
lampMaterial=material('Warm shaded lamp diffuser',(.75,.69,.53),.60);p=lampMaterial.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.80,.58,1);p.inputs['Emission Strength'].default_value=2.5;lamps=Batch()
for i,u in enumerate([frameU-1.18,frameU+1.18]):
 lamps.box(P(u,depth+.90,10.04),(.55,.27,.09),0,basis);lamps.box(P(u,depth+.90,9.987),(.45,.18,.014),1,basis);lamps.box(P(u,depth+.60,10.23),(.055,.66,.045),0,basis);lamps.box(P(u,depth+.90,10.15),(.055,.055,.24),0,basis);d=bpy.data.lights.new('REV15Y / Contact house lamp '+str(i+1),'SPOT');d.energy=90;d.color=(1,.80,.58);d.spot_size=math.radians(120);d.spot_blend=.66;d.shadow_soft_size=.15;d.use_custom_distance=True;d.cutoff_distance=3.2;ob=bpy.data.objects.new(d.name,d);collection.objects.link(ob);ob.location=P(u,depth+.90,9.97);ob.rotation_euler=(P(frameU+(u-frameU)*.35,depth,9.20)-ob.location).to_track_quat('-Z','Y').to_euler();ob['contactPart']='local house light'
lamps.object('Contact shaded lamp fixtures',collection,[steel,lampMaterial],'lamp fixtures');d=bpy.data.lights.new('REV15Y / Soft light inside enquiry window','POINT');d.energy=9;d.color=(1,.86,.68);d.shadow_soft_size=.16;d.use_shadow=False;d.use_custom_distance=True;d.cutoff_distance=1.3;ob=bpy.data.objects.new(d.name,d);collection.objects.link(ob);ob.location=P(u0,plan['window']['depth']-.08,9.20);ob['contactPart']='interior window light'
s.camera=copies[base.camera];s['authorizedChange']='Approved enquiry-window Contact place: crew person left, wide message panel right, centred white brush CONTACT US heading. Accommodation white COMING/SOON and complete low barrier/coping removal.';s['userVisualApproval']='PENDING';bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update();assert snapshot(SimpleNamespace(objects=[copies[o]for o in base.objects if o.name not in excluded]),{'objects':[]},'REV15Y / ')==protected;assert fp(base)['sha256']==basefp['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items());fingerprint=fp(s);fingerprint.pop('data')
manifest={'version':'Rev15Y','normal':list(n),'tangent':list(t),'depth':depth,'frameBoundsU':[frameLeft,frameRight],'frameBoundsZ':[8.04,9.53],'frameCentreU':frameU,'frameCentre':list(P(frameU,depth,8.85)),'headingCentreU':frameU,'headingCentreZ':titleZ,'personEye':list(eye),'personCentreU':personU,'messageBoundsU':[boardLeft+.065,boardRight-.065],'messageBoundsZ':[8.21,9.37],'messageDepth':depth+.075,'messageWidthFraction':rightWidth/(leftWidth+rightWidth+gap),'removedObjects':sorted(removed),'partialWindowEdits':edits,'accommodationLines':['COMING','SOON'],'letteringAtlasSHA256':sha(atlasPath),'contactObjects':[o.name for o in collection.objects],'runtimeForm':'Isolated review component; full-world website integration remains pending.'}
if a.restore:assert fingerprint['sha256']==read('evidence/native-scene-fingerprint.json')['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);assert sha(a.base)==sourceSHA;proof={'status':'PASS','source':a.base,'sourceSHA256':sourceSHA,'sourceSceneFingerprint':basefp['sha256'],'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':61,'originalProtectedObjects':protected,'partialWindowProtectedFaces':face_before,'removedAccommodationBarrierObjects':sorted(removed),'changedWindowObjects':[o.name for o in changed],'changedMural':art.name,'newContactObjects':len(collection.objects),'sourceCrowdPreserved':189,'newCrewPeople':1,'messageWidthFraction':manifest['messageWidthFraction'],'personEye':list(eye),'headerCentred':True,'monochromeImagePacked':True,'packedImages':sum(bool(i.packed_file)for i in bpy.data.images),'sceneFingerprintSHA256':fingerprint['sha256'],'websiteIntegration':'PENDING'};(R/('evidence/restore-check.json'if a.restore else'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n');(R/'delivery/window-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'PASS','scenes':len(bpy.data.scenes),'contactObjects':len(collection.objects),'barrierPartsRemoved':len(removed),'messageFraction':manifest['messageWidthFraction']}))
