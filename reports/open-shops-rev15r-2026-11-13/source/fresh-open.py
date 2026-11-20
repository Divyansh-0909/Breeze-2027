import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=json.loads((R/'evidence/build-verification.json').read_text());bpy.ops.wm.open_mainfile(filepath=p['editedMaster']);s=bpy.context.scene;assert s.name==p['newScene'];s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();assets=bpy.data.collections['REV15R / Open shop additions'];minimum=100;bad=[]
for o in assets.objects:
 if o.type not in ['MESH','CURVE','FONT']:continue
 ev=o.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,depsgraph=deps)
 if len(me.vertices):
  lo=min(abs((ev.matrix_world@v.co).x) for v in me.vertices);minimum=min(minimum,lo)
  if lo<2.75:bad.append({'name':o.name,'minimumAbsX':lo})
 bpy.data.meshes.remove(me)
assert not bad,bad
assert all(o.name in bpy.context.view_layer.objects for o in assets.objects)
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
assert all(o.data.name.endswith('LOD0') for o in s.objects if o.type=='MESH' and o.data.name.startswith('REV13A shared'))
assert len([o for o in s.objects if o.get('artKind')])==8
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
proof={'status':'PASS','freshNativeOpen':True,'objectsInCurrentViewLayer':len(assets.objects),'evaluatedMeshMinimumAbsX':minimum,'centralLaneClear':True,'packedImages':sum(bool(im.packed_file) for im in bpy.data.images),'all189CrowdAtOriginalLOD0':True,'eightMuralSlidesRetained':True,'sourceMasterSHA256':hashlib.sha256(Path(p['sourceMaster']).read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(Path(p['editedMaster']).read_bytes()).hexdigest()};assert proof['sourceMasterSHA256']==p['sourceSHA256'];assert proof['masterSHA256']==p['editedSHA256'];(R/'evidence/fresh-open.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
