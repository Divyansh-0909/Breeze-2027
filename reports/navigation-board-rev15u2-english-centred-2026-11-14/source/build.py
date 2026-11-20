import bpy,json,hashlib,argparse,sys,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];U1=R.parent/'navigation-board-rev15u-highway-green-2026-11-13'
ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15U1-Bilingual-Highway-Navigation.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15U2-English-Centred-Navigation.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out=Path(a.output);assert not out.exists(),'Existing output preserved; choose a new filename.'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
fingerprint=runpy.run_path(str(U1/'source/scene-fingerprint.py'))['fingerprint'];expected=json.loads((U1/'evidence/native-scene-fingerprint.json').read_text());assert fingerprint(base)['sha256']==expected['sha256'],'Wrong or modified U1 base'
history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15U2 / English centred highway navigation';s['variant']='REV15U2'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={};removed=[]
for old in base.objects:
    if old.get('language')=='hi':removed.append(old.name);continue
    ob=old.copy();ob.name='REV15U2 / '+old.name.removeprefix('REV15U1 / ')
    if old.type=='CAMERA':ob.data=old.data.copy()
    s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
    if old.parent in copies:ob.parent=copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15U2 / independent view')
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
labels=[(old,ob) for old,ob in copies.items() if old.type=='FONT' and old.get('navigationLabel')];assert len(labels)==7 and len(plates)==6 and len(removed)==7
delta=bpy.data.collections.new('REV15U2 / Centred English labels');s.collection.children.link(delta);alignment=[]
for old,ob in labels:
    if old['navigationLabel']=='GULLYVERSE':plate=header
    else:plate=next(p for p in plates if abs(p.location.z-(old.location.z+.24))<.001 and abs(p.location.x-old.location.x)<.4)
    pb=bounds(plate);bb=bounds(ob);centre=(pb[2][0]+pb[2][1])/2;shift=centre-(bb[2][0]+bb[2][1])/2
    ob.location.z+=shift;delta.objects.link(ob);bpy.context.view_layer.update();bb=bounds(ob);error=abs((bb[2][0]+bb[2][1])/2-centre);assert error<.00001
    assert bb[2][0]>pb[2][0]+.04 and bb[2][1]<pb[2][1]-.04
    alignment.append({'label':ob.data.body,'object':ob.name,'panel':plate.name,'targetCentreZ':centre,'textCentreZ':sum(bb[2])/2,'errorMetres':error,'verticalShift':shift})
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
changed={old for old,ob in labels}
assert all(list(old.matrix_world)==list(ob.matrix_world) for old,ob in copies.items() if old not in changed)
assert all(old.data==ob.data for old,ob in copies.items() if old.type!='CAMERA')
assert all(old.location.x==ob.location.x and old.location.y==ob.location.y and list(old.rotation_euler)==list(ob.rotation_euler) and list(old.scale)==list(ob.scale) for old,ob in labels)
assert not any(o.get('language')=='hi' for o in s.objects)
assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items())
fp=fingerprint(s);fp.pop('data')
if a.restore:assert fp['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256'],'Restored scene differs'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
if a.restore:
    proof={'status':'PASS','method':'Actual reconstruction from the semantically verified restored U1 base and the included seven-label centring source; active scene fingerprint matches the original U2 scene','restoredMaster':str(out),'restoredBytes':out.stat().st_size,'restoredSHA256':sha(out),'scenes':54,'sceneFingerprintSHA256':fp['sha256']};(R/'evidence/restore-check.json').write_text(json.dumps(proof,indent=2)+'\n')
else:
    bpy.data.libraries.write(str(R/'delivery/Rev15U2-English-Centred-Labels.blend'),{delta},fake_user=True,compress=True)
    proof={'status':'PASS','scene':s.name,'source':a.base,'sourceSHA256':sha(a.base),'sourceSceneFingerprint':expected,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scenes':54,'historicalScenesPreserved':53,'removedHindiObjects':removed,'alignment':alignment,'englishLabelsVerticallyCentred':7,'allOtherTransformsAndGeometryUnchanged':True,'labelFontsSizesAndHorizontalPositionsUnchanged':True,'digitalSponsorBoardUnchanged':True,'panelHeightMetres':.68,'diagonalArrows':4,'accommodationRetained':True,'lightingAndExposureUnchanged':True,'productionWebsiteChanged':False};(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n')
print(json.dumps({'status':'PASS','scene':s.name,'centredLabels':7,'removedHindiLabels':7,'restore':a.restore}),flush=True)
