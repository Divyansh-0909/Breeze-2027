import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(b['editedMaster'])==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();contact=list(next(c for c in s.collection.children if c.name=='REV15Z / Wide Contact window').objects);accommodation=[o for o in s.objects if o.get('accommodationPart')];assert len(accommodation)==4
delta=bpy.data.collections.new('REV15Z / Wide window and restored Accommodation recovery')
for o in contact+accommodation:delta.objects.link(o)
native=R/'delivery/Rev15Z-Contact-and-Accommodation-Component.blend';bpy.data.libraries.write(str(native),{delta},fake_user=True,compress=True)
outputs={}
for key,objects,file in [('contact',contact,'Rev15Z-Wide-Contact-Window.glb'),('accommodation',accommodation,'Rev15Z-Restored-Accommodation.glb')]:
 ex=bpy.data.scenes.new('REV15Z / '+key+' private component');bpy.context.window.scene=ex
 for old in objects:
  ob=old.copy();ob.data=old.data.copy();ex.collection.objects.link(ob);ob.select_set(True);bpy.context.view_layer.objects.active=ob
  if ob.type=='FONT':bpy.ops.object.convert(target='MESH')
 glb=R/'delivery'/file;bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_active_scene=True,export_apply=True,export_animations=False,export_extras=True,export_lights=True);outputs[key]={'file':glb.name,'bytes':glb.stat().st_size,'sha256':sha(glb)}
assert sha(b['editedMaster'])==b['editedSHA256'];result={'status':'PASS','native':{'file':native.name,'bytes':native.stat().st_size,'sha256':sha(native)},'runtime':outputs,'scope':'Contact and Accommodation are separate runtime components. Replace the entire old Y Contact collection and old Accommodation bindings; do not append duplicates. Native full-world source reconstruction is tested separately. Full-world website integration/baking remains pending.'};(R/'evidence/export.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
