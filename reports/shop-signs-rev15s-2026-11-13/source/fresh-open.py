import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=json.loads((R/'evidence/build-verification.json').read_text());bpy.ops.wm.open_mainfile(filepath=p['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();assets=bpy.data.collections['REV15S / Shop name boards'];minimum=100
for o in assets.objects:
 if o.type not in ['MESH','CURVE']:continue
 ev=o.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,depsgraph=deps)
 if len(me.vertices):minimum=min(minimum,min(abs((ev.matrix_world@v.co).x) for v in me.vertices))
 bpy.data.meshes.remove(me)
assert minimum>2.75;assert all(o.name in bpy.context.view_layer.objects for o in assets.objects);assert all(im.packed_file for im in bpy.data.images if im.source=='FILE');assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189;assert len([o for o in s.objects if o.get('artKind')])==8
d={'status':'PASS','freshNativeOpen':True,'sourceSHA256':hashlib.sha256(Path(p['source']).read_bytes()).hexdigest(),'editedSHA256':hashlib.sha256(Path(p['editedMaster']).read_bytes()).hexdigest(),'newAssets':len(assets.objects),'minimumAssetAbsX':minimum,'packedImages':sum(bool(im.packed_file) for im in bpy.data.images),'crowdCount':189,'muralStates':8,'shopInteriorsPreserved':p['approvedShopMeshDataAndLocationsPreserved']};assert d['sourceSHA256']==p['sourceSHA256'] and d['editedSHA256']==p['editedSHA256'];(R/'evidence/fresh-open.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
