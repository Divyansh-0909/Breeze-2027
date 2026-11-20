"""Restore T3 from the complete verified T2 master plus the packed road delta."""
import bpy, json, hashlib, argparse, sys, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--delta',default=str(R/'delivery/Rev15T3-Rebuilt-Potholes-Additions.blend'));ap.add_argument('--output',required=True)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output)
assert not out.exists(),'Choose a new output filename; existing files are preserved.'
assert hashlib.sha256(Path(a.base).read_bytes()).hexdigest()=='33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb'
bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;history=len(bpy.data.scenes)
s=base.copy();s.name='REV15T3 / Rebuilt broken asphalt potholes'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
    if old.get('groundSurface') or 'nearly flush drain' in old.name or 'REV15T2 / edge pool' in old.name:continue
    ob=old.copy();ob.name='REV15T3 / '+old.name.removeprefix('REV15T2 / ')
    if old.type in ['LIGHT','CAMERA']:ob.data=old.data.copy()
    if 'batched loose aggregate' in old.name or 'shallow damp pocket' in old.name:ob.hide_render=True;ob.hide_viewport=True
    s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
    if old.parent in copies:ob.parent=copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15T3 / independent view')
for l in list(s.view_layers):
    if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
images={hashlib.sha256(im.packed_file.data).hexdigest():im for im in bpy.data.images if im.packed_file}
before=set(bpy.data.images)
with bpy.data.libraries.load(a.delta,link=False) as (src,dst):dst.collections=['REV15T3 / Restored road defects and edge water']
s.collection.children.link(dst.collections[0])
for im in list(bpy.data.images):
    if im in before or not im.packed_file:continue
    old=images.get(hashlib.sha256(im.packed_file.data).hexdigest())
    if old:im.user_remap(old);bpy.data.images.remove(im)
s.camera=copies[base.camera];s['paintedCypherCircle']=False
bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
actual=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'](s)
expected=json.loads((R/'evidence/native-scene-fingerprint.json').read_text())
assert actual['sha256']==expected['sha256'],'Restored active scene differs in geometry, UVs, vertex colours, materials, visibility, transforms or lighting.'
assert len(bpy.data.scenes)==52 and history==51
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
proof={'status':'PASS','method':'Complete verified T2 base plus packed T3 road delta; active-scene fingerprint matches original T3 geometry, UVs, colours, materials, transforms, visibility and lights','scenes':52,'activeSceneSHA256':actual['sha256'],'restoredMaster':str(out),'restoredBytes':out.stat().st_size,'restoredSHA256':hashlib.sha256(out.read_bytes()).hexdigest()}
(R/'evidence/restore-check.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
