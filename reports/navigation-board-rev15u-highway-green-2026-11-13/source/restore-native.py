import bpy,json,hashlib,argparse,sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];T=R.parent/'ground-rev15t3-rebuilt-potholes-2026-11-13'
ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--delta',default=str(R/'delivery/Rev15U1-Bilingual-Highway-Sign-Styling.blend'));ap.add_argument('--output',required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output);assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
basefp=runpy.run_path(str(T/'source/scene-fingerprint.py'))['fingerprint'](base)
assert basefp['sha256']==json.loads((T/'evidence/native-scene-fingerprint.json').read_text())['sha256'],'Wrong or modified T3 base'
proof=json.loads((R/'evidence/build-verification.json').read_text());skip=set(proof['modifiedOriginalObjects']);s=base.copy();s.name='REV15U1 / Bilingual green highway navigation signs';s['variant']='REV15U1'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
    if old.name in skip:continue
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
with bpy.data.libraries.load(a.delta,link=False) as (src,dst):dst.collections=['REV15U1 / Highway sign styling delta']
s.collection.children.link(dst.collections[0])
for ob in dst.collections[0].objects:
    assert ob.parent is None
    loc=ob.location.copy();rot=ob.rotation_euler.copy();sc=ob.scale.copy()
    ob.matrix_world=ob.matrix_basis.copy()
    ob.location=loc;ob.rotation_euler=rot;ob.scale=sc
layer=s.view_layers.new('REV15U1 / independent view')
for l in list(s.view_layers):
    if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
s.camera=copies[base.camera]
bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
actual=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'](s);expected=json.loads((R/'evidence/native-scene-fingerprint.json').read_text());assert actual['sha256']==expected['sha256'],'Restored active scene differs'
assert len(bpy.data.scenes)==53
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
result={'status':'PASS','method':'Semantically verified complete T3 base plus packed U style delta; active geometry, UVs, vertex colours, material assignments, transforms, visibility, fonts and lights match original U master','restoredMaster':str(out),'restoredBytes':out.stat().st_size,'restoredSHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'sceneFingerprintSHA256':actual['sha256'],'scenes':53}
(R/'evidence/restore-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
