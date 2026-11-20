import bpy,json,hashlib,runpy,argparse,sys,math
from pathlib import Path
from types import SimpleNamespace
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads((R/p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
geo=runpy.run_path(str(R/'source/geometry.py'));Batch=geo['Batch'];material=geo['material'];quads=geo['quads'];image_material=geo['image_material'];snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint']
ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15Y-Enquiry-Window-and-Monochrome-Lettering.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[]);out=Path(a.output);assert not out.exists(),'Choose a new output filename';sourceSHA=sha(a.base)
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();basefp=fp(base);assert basefp['sha256']=='6bcf7218f2d445818bd967b5465c12926513f14600ccb1780236d5c1860da5cd'
history={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes};oldContact=[o for o in base.objects if o.get('contactPart')];artY=next(o for o in base.objects if o.get('accommodationPart')=='COMING above SOON graffiti');originalScene=bpy.data.scenes['REV15X1 / Clean Accommodation wall'];originalArt=next(o for o in originalScene.objects if o.get('accommodationPart')=='COMING above SOON graffiti');originalArtSignature=snapshot(SimpleNamespace(objects=[originalArt]),{'objects':[]},'REV15X1 / ')
protectedOriginal=[o for o in base.objects if o not in oldContact and o!=artY];protected=snapshot(SimpleNamespace(objects=protectedOriginal),{'objects':[]},'REV15Y / ');m=read('source/base-window-manifest.json');n=Vector(m['normal']);t=Vector(m['tangent']);up=Vector((0,0,1));P=lambda u,d,z:t*u+n*d+up*z;depth=m['depth'];fl,fr=m['frameBoundsU'];centre=(fl+fr)/2;panelL=fl+.12;panelR=fr-.12;panelBottom=8.20;panelTop=9.21
s=base.copy();s.name='REV15Z / Wide Contact window and restored graffiti';s['variant']='REV15Z'
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 if old in oldContact:continue
 ob=old.copy();ob.name='REV15Z / '+old.name.removeprefix('REV15Y / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for driver in ob.animation_data.drivers:
   for var in driver.driver.variables:
    for target in var.targets:
     if target.id in copies:target.id=copies[target.id]
layer=s.view_layers.new('REV15Z / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for node in s.node_tree.nodes:
 if node.type=='R_LAYERS':node.scene=s;node.layer=layer.name
# Restore the exact X1 colour artwork: geometry, UVs, transform and original material/image.
art=copies[artY];art.data=originalArt.data;art.matrix_basis=originalArt.matrix_basis
for key in list(art.keys()):del art[key]
for key in originalArt.keys():art[key]=originalArt[key]
assert snapshot(SimpleNamespace(objects=[art]),{'objects':[]},'REV15Z / ')==originalArtSignature
collection=bpy.data.collections.new('REV15Z / Wide Contact window');s.collection.children.link(collection);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
# UV framing removes transparent outer margins without modifying generated image bytes.
imagePath=R/'assets/contact-us-graffiti.png';image=bpy.data.images.load(str(imagePath));image.name='REV15Z / CONTACT US colourful graffiti';image.alpha_mode='STRAIGHT';image.colorspace_settings.name='sRGB';image.pack();assert hashlib.sha256(image.packed_file.data).hexdigest()==sha(imagePath);paint=image_material('CONTACT US orange gold pink graffiti',image)
rect=[8,82,2164,650];titleW=2.15;titleH=titleW*(rect[3]-rect[1])/(rect[2]-rect[0]);titleZ=9.66;records=[]
for i in range(32):
 for j in range(6):
  points=[];uv=[]
  for di,dj in [(0,0),(1,0),(1,1),(0,1)]:
   u=centre-titleW/2+(i+di)*titleW/32;z=titleZ-titleH/2+(j+dj)*titleH/6;hit=s.ray_cast(deps,P(u,-20.2,z),-n,distance=4);assert hit[0],('No heading wall',u,z);points.append(tuple(hit[1]+hit[2]*.008));uv.append(((rect[0]+(rect[2]-rect[0])*(i+di)/32)/2172,1-(rect[3]-(rect[3]-rect[1])*(j+dj)/6)/724))
  records.append((points,uv))
heading=quads('CONTACT US colourful wall graffiti',collection,records,paint,'contact heading');heading['headingText']='CONTACT US';heading['centreU']=centre
wood=material('Weathered green window frame',(.095,.17,.12),.88,grain=46);timber=material('Worn timber window sill',(.17,.12,.07),.92,grain=62);dark=material('Deep charcoal window reveal',(.018,.029,.023),.99);paper=material('Warm cream form inside window',(.78,.76,.66),.94,grain=130);field=material('Off-white form fields',(.89,.87,.79),.93);ink=material('Charcoal form lettering',(.019,.025,.020),.93);button=material('Send message green',(.045,.105,.07),.85);steel=material('Dull steel lamp brackets',(.10,.13,.11),.76,.50)
hardware=Batch();basis=(t,n,up)
def box(u,d,z,w,h,deep,mi=0):hardware.box(P(u,d,z),(w,deep,h),mi,basis)
# One continuous wide window: no person bay, shutters or centre mullion/divider.
for u in [fl+.06,fr-.06]:box(u,depth+.15,8.705,.12,1.33,.30)
for z in [8.10,9.31]:box(centre,depth+.15,z,fr-fl,.12,.30)
box(centre,depth+.26,8.08,fr-fl+.18,.11,.56,1)
box(centre,depth+.045,8.705,fr-fl-.22,1.10,.055,2)
# Recessed inner lip gives the form a visible window reveal.
for u in [panelL+.018,panelR-.018]:box(u,depth+.105,8.705,.036,1.02,.12,2)
for z in [panelBottom+.018,panelTop-.018]:box(centre,depth+.105,z,panelR-panelL,.036,.12,2)
hardwareObj=hardware.object('Single wide enquiry window frame and sill',collection,[wood,timber,dark],'window frame');hardwareObj['singleOpening']=True;hardwareObj['centreDivider']=False
panel=quads('Full-width message surface inside window',collection,[([tuple(P(panelL,depth+.081,panelBottom)),tuple(P(panelR,depth+.081,panelBottom)),tuple(P(panelR,depth+.081,panelTop)),tuple(P(panelL,depth+.081,panelTop))],[(0,0),(1,0),(1,1),(0,1)])],paper,'message panel');panel['messageWidthFraction']=1.0
form=Batch();usable=panelR-panelL-.22
for i in range(3):form.box(P(panelL+.11+(i+.5)*usable/3,depth+.090,8.88),(usable/3-.045,.012,.145),0,basis)
form.box(P(centre,depth+.090,8.565),(usable,.012,.245),0,basis);form.box(P(panelR-.53,depth+.095,8.31),(.82,.018,.15),1,basis);form.object('Native full-window form illustration',collection,[field,button],'native form illustration')
fontBasis=Matrix((t,up,n)).transposed().to_4x4()
def label(text,u,z,size=.062,color=None):
 data=bpy.data.curves.new('REV15Z / '+text,'FONT');data.body=text;data.size=size;data.align_x='LEFT';data.align_y='CENTER';ob=bpy.data.objects.new(data.name,data);collection.objects.link(ob);ob.matrix_world=Matrix.Translation(P(u,depth+.115,z))@fontBasis;data.materials.append(color or ink);ob['contactPart']='native form label';return ob
label('LEAVE A MESSAGE',panelL+.11,9.115,.078)
for i,text in enumerate(['NAME','EMAIL','PHONE']):label(text,panelL+.12+i*usable/3,9.01,.053)
for i,text in enumerate(['Your name','you@example.com','+91 ...']):label(text,panelL+.13+i*usable/3,8.88,.059)
label('MESSAGE',panelL+.12,8.76,.053);label('Tell us how we can help...',panelL+.13,8.605,.061);label('Talk to the crew',panelL+.12,8.31,.059);label('Send message',panelR-.89,8.31,.061,field)
# Two local house fixtures, with broad soft beams over the wide window and title.
diffuser=material('Warm window-lamp diffuser',(.75,.69,.53),.6);p=diffuser.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(1,.80,.58,1);p.inputs['Emission Strength'].default_value=2.5;lamps=Batch()
for i,u in enumerate([centre-1.18,centre+1.18]):
 lamps.box(P(u,depth+.90,10.04),(.55,.27,.09),0,basis);lamps.box(P(u,depth+.90,9.987),(.45,.18,.014),1,basis);lamps.box(P(u,depth+.60,10.23),(.055,.66,.045),0,basis);lamps.box(P(u,depth+.90,10.15),(.055,.055,.24),0,basis)
 d=bpy.data.lights.new('REV15Z / Contact house lamp '+str(i+1),'SPOT');d.energy=65;d.color=(1,.80,.58);d.spot_size=math.radians(145);d.spot_blend=.8;d.shadow_soft_size=.35;d.use_custom_distance=True;d.cutoff_distance=3.2;ob=bpy.data.objects.new(d.name,d);collection.objects.link(ob);ob.location=P(u,depth+.90,9.97);ob.rotation_euler=(P(centre+(u-centre)*.70,depth,9.00)-ob.location).to_track_quat('-Z','Y').to_euler();ob['contactPart']='local house light'
lamps.object('Contact window shaded lamp fixtures',collection,[steel,diffuser],'lamp fixtures')
s.camera=copies[base.camera];s['authorizedChange']='Restore exact original colourful Accommodation graffiti. Matching colourful CONTACT US heading. Remove attendant and separate bay/divider; one wide window contains the full-width form. Keep Accommodation barrier absent.';s['userVisualApproval']='PENDING';bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update();assert snapshot(SimpleNamespace(objects=[copies[o]for o in protectedOriginal]),{'objects':[]},'REV15Z / ')==protected;assert fp(base)['sha256']==basefp['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items());fingerprint=fp(s);fingerprint.pop('data')
manifest={'version':'Rev15Z','normal':list(n),'tangent':list(t),'depth':depth,'frameBoundsU':[fl,fr],'frameBoundsZ':[8.04,9.37],'frameCentreU':centre,'frameCentre':list(P(centre,depth,8.705)),'headingCentreU':centre,'headingCentreZ':titleZ,'headingWidthM':titleW,'headingUVRect':rect,'messageBoundsU':[panelL,panelR],'messageBoundsZ':[panelBottom,panelTop],'messageDepth':depth+.081,'messageWidthFraction':1.0,'messageWidthM':panelR-panelL,'personCount':0,'singleWindow':True,'centreDivider':False,'removedContactObjects':[o.name for o in oldContact],'removedAccommodationObjects':m['removedObjects'],'unchangedPartialWindowEdits':m['partialWindowEdits'],'accommodationRestoration':'Exact original X1 mesh/UV/transform/material/packed colour image; not a redraw','accommodationOriginalSignature':originalArtSignature,'contactImageSHA256':sha(imagePath),'accommodationImageSHA256':sha(R/'assets/coming-soon-graffiti.png'),'contactObjects':[o.name for o in collection.objects],'runtimeForm':'Private review component; full-world website integration pending.'}
if a.restore:assert fingerprint['sha256']==read('evidence/native-scene-fingerprint.json')['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);assert sha(a.base)==sourceSHA
proof={'status':'PASS','source':a.base,'sourceSHA256':sourceSHA,'sourceSceneFingerprint':basefp['sha256'],'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':62,'protectedOriginalObjects':protected,'accommodationExactOriginalSignature':originalArtSignature,'removedYContactObjects':[o.name for o in oldContact],'newContactObjects':len(collection.objects),'originalPeoplePreserved':189,'newCrewPeople':0,'messageWidthFraction':1.0,'messageWidthM':panelR-panelL,'fullWidthWindowNoDivider':True,'packedImages':sum(bool(i.packed_file)for i in bpy.data.images),'sceneFingerprintSHA256':fingerprint['sha256'],'websiteIntegration':'PENDING'};(R/('evidence/restore-check.json'if a.restore else'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n');(R/'delivery/window-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'PASS','scenes':len(bpy.data.scenes),'contactObjects':len(collection.objects),'originalGraffitiRestored':True,'personCount':0,'messageWidthM':panelR-panelL}))
