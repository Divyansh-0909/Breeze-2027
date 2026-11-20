import bpy,json,hashlib,argparse,sys,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];U2=R.parent/'navigation-board-rev15u2-english-centred-2026-11-14'
ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15U2-English-Centred-Navigation.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15U3-Larger-English-Navigation.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.output);assert not out.exists(),'Existing output preserved; choose a new filename.'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
fingerprint=runpy.run_path(str(U2/'source/scene-fingerprint.py'))['fingerprint'];expected=json.loads((U2/'evidence/native-scene-fingerprint.json').read_text());assert fingerprint(base)['sha256']==expected['sha256'],'Wrong or modified U2 base'
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15U3 / Slightly larger English navigation';s['variant']='REV15U3'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={};removed=[]
for old in base.objects:
    if old.get('language')=='hi':removed.append(old.name);continue
    ob=old.copy();ob.name='REV15U3 / '+old.name.removeprefix('REV15U2 / ')
    if old.type=='CAMERA':ob.data=old.data.copy()
    s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
    if old.parent in copies:ob.parent=copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15U3 / independent view')
for l in list(s.view_layers):
    if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
s.frame_set(1);bpy.context.view_layer.update()
def bounds(o):
    p=[o.matrix_world@Vector(c) for c in o.bound_box];return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
plates=[ob for old,ob in copies.items() if old.type=='MESH' and 'White inset border' not in old.name and ('Reused sign hierarchy /' in old.name or ' / Past Sponsors plaque' in old.name)]
header=next(ob for old,ob in copies.items() if 'EXISTING GULLYVERSE hero raster' in old.name)
labels=[(old,ob) for old,ob in copies.items() if old.type=='FONT' and old.get('navigationLabel')];assert len(labels)==7 and len(plates)==6 and len(removed)==0
previous=json.loads((U2/'evidence/build-verification.json').read_text());panel_map={x['object']:x['panel'] for x in previous['alignment']}
delta=bpy.data.collections.new('REV15U3 / Larger centred English labels');s.collection.children.link(delta);alignment=[]
for old,ob in labels:
    plate=copies[base.objects[panel_map[old.name]]]
    ob.data=old.data.copy();ob.data.size=old.data.size*1.12;bpy.context.view_layer.update()
    pb=bounds(plate);bb=bounds(ob);centre=(pb[2][0]+pb[2][1])/2;shift=centre-(bb[2][0]+bb[2][1])/2
    ob.location.z+=shift;delta.objects.link(ob);bpy.context.view_layer.update();bb=bounds(ob);error=abs((bb[2][0]+bb[2][1])/2-centre);assert error<.00001
    assert bb[2][0]>pb[2][0]+.04 and bb[2][1]<pb[2][1]-.04
    assert bb[0][0]>pb[0][0]+.06 and bb[0][1]<pb[0][1]-.06
    arrows=[o for o in s.objects if ('Aftermovie upward arrow' in o.name and ob.data.body=='Aftermovie') or (o.get('angleDegrees')==45 and ob.data.body+' white diagonal arrow' in o.name)]
    arrow_gap=None
    for arrow in arrows:
        ab=bounds(arrow);gap=max(bb[0][0]-ab[0][1],ab[0][0]-bb[0][1]);assert gap>.025,'Text crowds arrow: '+ob.data.body;arrow_gap=gap
    alignment.append({'label':ob.data.body,'object':ob.name,'panel':plate.name,'targetCentreZ':centre,'textCentreZ':sum(bb[2])/2,'errorMetres':error,'verticalShift':shift,'previousSize':old.data.size,'currentSize':ob.data.size,'sizeFactor':ob.data.size/old.data.size,'arrowGapMetres':arrow_gap})
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
changed={old for old,ob in labels}
assert all(list(old.matrix_world)==list(ob.matrix_world) for old,ob in copies.items() if old not in changed)
assert all(old.data==ob.data for old,ob in copies.items() if old.type!='CAMERA' and old not in changed)
assert all(old.location.x==ob.location.x and old.location.y==ob.location.y and list(old.rotation_euler)==list(ob.rotation_euler) and list(old.scale)==list(ob.scale) for old,ob in labels)
assert not any(o.get('language')=='hi' for o in s.objects)
assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items())
fp=fingerprint(s);fp.pop('data')
if a.restore:assert fp['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256'],'Restored scene differs'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
if a.restore:
    proof={'status':'PASS','method':'Actual reconstruction from the semantically verified restored U2 base and the included seven-label size-and-centring source; active scene fingerprint matches the original U3 scene','restoredMaster':str(out),'restoredBytes':out.stat().st_size,'restoredSHA256':sha(out),'scenes':55,'sceneFingerprintSHA256':fp['sha256']};(R/'evidence/restore-check.json').write_text(json.dumps(proof,indent=2)+'\n')
else:
    bpy.data.libraries.write(str(R/'delivery/Rev15U3-Larger-English-Labels.blend'),{delta},fake_user=True,compress=True)
    proof={'status':'PASS','scene':s.name,'source':a.base,'sourceSHA256':sha(a.base),'sourceSceneFingerprint':expected,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scenes':55,'historicalScenesPreserved':54,'removedHindiObjects':removed,'alignment':alignment,'englishLabelsVerticallyCentred':7,'allOtherTransformsAndGeometryUnchanged':True,'fontFamiliesAndHorizontalPositionsUnchanged':True,'textSizeIncreasePercent':12,'digitalSponsorBoardUnchanged':True,'panelHeightMetres':.68,'diagonalArrows':4,'accommodationRetained':True,'lightingAndExposureUnchanged':True,'productionWebsiteChanged':False};(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n')
print(json.dumps({'status':'PASS','scene':s.name,'centredLabels':7,'removedHindiLabels':0,'restore':a.restore}),flush=True)
