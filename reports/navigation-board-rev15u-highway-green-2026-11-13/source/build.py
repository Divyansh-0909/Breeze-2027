import bpy,json,hashlib,math,argparse,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15T3-Rebuilt-Potholes.blend');ap.add_argument('--expected-sha256',default='09fa6d949d4b45c8a44dc5d465ba1ee1795ad695976ce1311de9375d711d416b');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15U1-Bilingual-Highway-Navigation.blend')
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();P=Path(a.base);assert sha(P)==a.expected_sha256
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes}
s=base.copy();s.name='REV15U1 / Bilingual green highway navigation signs';s['variant']='REV15U1'
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s;copies={}
for old in base.objects:
    ob=old.copy();ob.name='REV15U1 / '+old.name.removeprefix('REV15T3 / ')
    if old.type=='CAMERA':ob.data=old.data.copy()
    s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
    if old.parent in copies:ob.parent=copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15U1 / independent view')
for l in list(s.view_layers):
    if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
style=bpy.data.collections.new('REV15U1 / Highway sign styling delta');s.collection.children.link(style)
medium=bpy.data.fonts.load(str(R/'source/fonts/Overpass-Medium.otf'));bold=bpy.data.fonts.load(str(R/'source/fonts/Overpass-SemiBold.otf'))
def rgb(hex):
    a=[int(hex[i:i+2],16)/255 for i in [0,2,4]]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
def material(name,color,rough):
    m=bpy.data.materials.new('REV15U1 / '+name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*rgb(color),1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=0;b.inputs['Coat Weight'].default_value=.12;return m
green=material('Road sign green / 087655','087655',.44);white=material('Reflective white border and lettering','F5F6F0',.38)
modified=[];new=[];records=[];translations={x['english']:x for x in json.loads((R/'source/translations.json').read_text())}
def edit_material(old,ob,mat):
    ob.data=old.data.copy();ob.data.materials.clear();ob.data.materials.append(mat)
    style.objects.link(ob);modified.append(old.name)
def bounds(ob):
    pts=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def mesh(name,vs,fs,mat):
    me=bpy.data.meshes.new('REV15U1 / '+name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();ob=bpy.data.objects.new(me.name,me);style.objects.link(ob);new.append(ob);return ob
def outline(cx,cz,w,h,r):
    pts=[]
    for x,z,start in [(cx+w/2-r,cz+h/2-r,0),(cx-w/2+r,cz+h/2-r,90),(cx-w/2+r,cz-h/2+r,180),(cx+w/2-r,cz-h/2+r,270)]:
        for j in range(7):
            a=math.radians(start+j*90/6);pts.append((x+math.cos(a)*r,z+math.sin(a)*r))
    return pts
def border(ob):
    b=bounds(ob);cx=sum(b[0])/2;cz=sum(b[2])/2;w=b[0][1]-b[0][0]-.095;h=b[2][1]-b[2][0]-.095;t=.017 if h>.8 else .012
    outer=outline(cx,cz,w,h,.035);inner=outline(cx,cz,w-2*t,h-2*t,.023);n=len(outer);y=b[1][0]-.004
    vs=[(x,y,z) for x,z in outer+inner];fs=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    return mesh('White inset border / '+ob.name.removeprefix('REV15U1 / '),vs,fs,white)
plates=[];header=None;fonts=[]
for old,ob in copies.items():
    if old.type=='MESH' and ('Reused sign hierarchy /' in old.name or ' / Past Sponsors plaque' in old.name):
        edit_material(old,ob,green);ob.scale.z*=.68/.55
        if 'Past Sponsors plaque' in old.name:ob.location.z+=(.68-.55)/2
        
        if old.get('proposedDestination'):
            ob.pop('proposedDestination',None);ob['confirmedDestination']='Accommodation'
        bpy.context.view_layer.update();plates.append(ob);border(ob)
    elif 'EXISTING GULLYVERSE hero raster' in old.name:
        edit_material(old,ob,green);header=ob;border(ob);ob['navigationLabel']='GULLYVERSE'
    elif old.type=='FONT' and (' / Navigation / ' in old.name or ' / Past Sponsors label' in old.name):
        ob.data=old.data.copy();ob.data.font=medium;ob.data.materials.clear();ob.data.materials.append(white)
        label='ACCOMMODATION' if old.data.body=='SCHEDULE' else old.data.body;ob['navigationLabel']=label;ob.data.body=label.replace('  <','').replace('  >','').title();ob.data.size=.28;ob.data.extrude=.001;ob.data.bevel_depth=0
        centre=old.location.z+.13+((.68-.55)/2 if 'Past Sponsors label' in old.name else 0);ob.location.z=centre-.24
        
        if label in ['EVENTS  <','ACCOMMODATION']:ob.location.x=-1.38
        if label in ['TEAM  >','CONTACT US']:ob.location.x=1.40
        if old.get('proposedDestination'):ob.pop('proposedDestination',None);ob['confirmedDestination']='Accommodation'
        bpy.context.view_layer.update()
        if ob.dimensions.x>1.95:ob.data.size*=1.95/ob.dimensions.x
        style.objects.link(ob);modified.append(old.name);fonts.append(ob)
    elif ' / Aftermovie upward arrow' in old.name:
        edit_material(old,ob,white)
assert len(plates)==6 and len(fonts)==6 and header is not None
h=bounds(header);cx=sum(h[0])/2;cz=sum(h[2])/2
data=bpy.data.curves.new('REV15U1 / Highway Gullyverse title','FONT');data.body='GULLYVERSE';data.font=bold;data.size=.48;data.align_x='CENTER';data.extrude=.001;data.materials.append(white)
ob=bpy.data.objects.new(data.name,data);style.objects.link(ob);new.append(ob);ob.location=(cx,h[1][0]-.013,cz-.29);ob.rotation_euler=(math.pi/2,0,0);ob['navigationLabel']='GULLYVERSE'

def hindi_label(key,cx,cz,y,height):
    row=translations[key];im=bpy.data.images.load(str(R/'textures'/row['file']));im.pack();width=height*row['pixels'][0]/row['pixels'][1]
    mat=bpy.data.materials.new('REV15U1 / Shaped Hindi / '+key);mat.use_nodes=True;nd=mat.node_tree.nodes;lk=mat.node_tree.links;p=nd.get('Principled BSDF');p.inputs['Roughness'].default_value=.38;p.inputs['Coat Weight'].default_value=.12;tex=nd.new('ShaderNodeTexImage');tex.image=im;lk.new(tex.outputs['Color'],p.inputs['Base Color']);lk.new(tex.outputs['Alpha'],p.inputs['Alpha']);mat.surface_render_method='DITHERED'
    ob=mesh('Hindi / '+key,[(cx-width/2,y,cz-height/2),(cx+width/2,y,cz-height/2),(cx+width/2,y,cz+height/2),(cx-width/2,y,cz+height/2)],[(0,1,2,3)],mat)
    uv=ob.data.uv_layers.new(name='LabelUV');coords=[(0,0),(1,0),(1,1),(0,1)]
    for lp in ob.data.loops:uv.data[lp.index].uv=coords[lp.vertex_index]
    ob['language']='hi';ob['hindiLabel']=row['hindi'];ob['englishLabel']=key;return ob
hindi_label('GULLYVERSE',cx,cz+.245,h[1][0]-.014,.32)
for font in fonts:hindi_label(font['navigationLabel'],font.location.x,font.location.z+.24+.13,font.location.y-.001,.205)

for label,x,z,sign in [('Events',-2.72,11.90,-1),('Team',2.72,11.90,1),('Accommodation',-2.72,11.12,-1),('Contact Us',2.72,11.12,1)]:
    y=10.905;pts=[(-.15,0),(-.025,.115),(-.025,.039),(.15,.039),(.15,-.039),(-.025,-.039),(-.025,-.115)]
    angle=sign*math.pi/4;vs=[(x+u*(-sign)*math.cos(angle)-v*math.sin(angle),y,z+u*(-sign)*math.sin(angle)+v*math.cos(angle)) for u,v in pts];ob=mesh(label+' white diagonal arrow',vs,[tuple(range(7))],white);ob['direction']='up-left' if sign<0 else 'up-right';ob['angleDegrees']=45
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert all(list(old.matrix_world)==list(ob.matrix_world) for old,ob in copies.items() if old.name not in modified),'Unrelated transform changed'
assert all(list(old.rotation_euler)==list(ob.rotation_euler) for old,ob in copies.items()),'Orientation changed'
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert all(old.data==ob.data for old,ob in copies.items() if old.type=='MESH' and old.name not in modified),'Unrelated geometry changed'
assert all(old.data.energy==ob.data.energy and list(old.data.color)==list(ob.data.color) for old,ob in copies.items() if old.type=='LIGHT')
digital=[old for old in base.objects if any(k in old.name for k in ['LED','casing screw','LED power cable']) or old.get('ledScreen')]
assert all(old.data==copies[old].data and list(old.matrix_world)==list(copies[old].matrix_world) for old in digital)
led=next(old for old in digital if old.get('ledScreen'));assert led.data==copies[led].data and led['periodCells']==10676 and led['logoCount']==62 and led['minimumLogoGapCells']==72
for font in fonts:
    plate=next(p for p in plates if abs(p.location.z-(font.location.z+.24))<.01 and (abs(p.location.x-font.location.x)<.3 or 'Aftermovie' in font.data.body))
    bb,pb=bounds(font),bounds(plate);assert bb[0][0]>pb[0][0]+.06 and bb[0][1]<pb[0][1]-.06 and bb[2][0]>pb[2][0] and bb[2][1]<pb[2][1],font.name
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;out=Path(a.output);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.data.libraries.write(str(R/'delivery/Rev15U1-Bilingual-Highway-Sign-Styling.blend'),{style},fake_user=True,compress=True)
proof={'status':'PASS','scene':s.name,'source':str(P),'sourceSHA256':a.expected_sha256,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scenes':len(bpy.data.scenes),'historicalScenesPreserved':len(history),'modifiedOriginalObjects':modified,'newStyleObjects':[o.name for o in new],'originalNavigationOrientationsUnchanged':True,'panelHeightMetres':.68,'pastSponsorsPlaqueGrowsUpward':True,'bilingual':['hi','en'],'newHindiLabels':7,'diagonalDestinationArrows':4,'accommodationReplacesSchedule':True,'unrelatedGeometryAndRoadDefectsUnchanged':True,'font':'Overpass Medium and SemiBold','greenHex':'087655','whiteHex':'F5F6F0','sixPlaquesAndHeaderStyled':True,'digitalBoardObjectsUnchanged':[o.name for o in digital],'digitalBoardMeshMaterialAndAnimationSharedWithBase':True,'logoCount':62,'periodCells':10676,'minimumLogoGapCells':72,'lightingAndExposureUnchanged':True,'productionWebsiteChanged':False}
(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');assert sha(P)==a.expected_sha256;print('GREEN_BOARD_DONE',json.dumps({k:proof[k] for k in ['editedSHA256','scenes','originalNavigationOrientationsUnchanged','sixPlaquesAndHeaderStyled','digitalBoardMeshMaterialAndAnimationSharedWithBase']}),flush=True)
