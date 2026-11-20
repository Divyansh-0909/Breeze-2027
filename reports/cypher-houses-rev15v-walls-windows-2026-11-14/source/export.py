import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());plan=json.loads((R/'source/architecture-plan.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(b['editedMaster'])==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
collection=bpy.data.collections.new('REV15V / Changed architecture surfaces and window details');objects=[];records=[]
for row in plan['objects']:
    old=s.objects[row['object'].replace('REV15U3 / ','REV15V / ',1)];indices=sorted({i for i,g in row['wallFaces']}|set(row['frameFaces'])|{i for i,w in row['glassFaces']});src=old.data
    used=sorted({v for i in indices for v in src.polygons[i].vertices});remap={v:i for i,v in enumerate(used)};vs=[tuple(old.matrix_world@src.vertices[i].co) for i in used];fs=[tuple(remap[v] for v in src.polygons[i].vertices) for i in indices]
    me=bpy.data.meshes.new('REV15V runtime / '+old.name.removeprefix('REV15V / '));me.from_pydata(vs,[],fs);me.update();uv=me.uv_layers.new(name='REV15VFacadeUV');mats={}
    for face,i in zip(me.polygons,indices):
        srcface=src.polygons[i];mat=old.material_slots[srcface.material_index].material
        if mat.name not in mats:mats[mat.name]=len(me.materials);me.materials.append(mat)
        face.material_index=mats[mat.name];face.use_smooth=srcface.use_smooth
        for li,sli in zip(face.loop_indices,srcface.loop_indices):uv.data[li].uv=src.uv_layers['REV15VFacadeUV'].data[sli].uv
    ob=bpy.data.objects.new(me.name,me);ob['changedSurface']=True;ob['sourceObject']=old.name;collection.objects.link(ob);objects.append(ob);records.append({'object':old.name,'changedFaces':len(indices)})
for old in s.objects:
    if not old.get('architectureHouse'):continue
    me=old.data.copy();me.transform(old.matrix_world);ob=bpy.data.objects.new('REV15V runtime / '+old.name.removeprefix('REV15V / '),me);ob['architectureHouse']=old['architectureHouse'];collection.objects.link(ob);objects.append(ob)
for ob in objects:
    for f in ob.data.polygons:
        pts=[ob.data.vertices[i].co for i in f.vertices]
        assert not(max(p.x for p in pts)>13 and max(p.y for p in pts)>26.7 and min(p.y for p in pts)<38.3),'Team geometry entered the architecture export'
bpy.data.libraries.write(str(R/'delivery/Rev15V-Cypher-Houses-Architecture-Update.blend'),{collection},fake_user=True,compress=True)
ex=bpy.data.scenes.new('REV15V runtime / Changed houses only');bpy.context.window.scene=ex;ex.collection.children.link(collection)
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=str(R/'delivery/Rev15V-Cypher-Houses-Architecture.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_extras=True)
assert sha(b['editedMaster'])==b['editedSHA256']
result={'status':'PASS','objects':len(objects),'editedSurfaceObjects':records,'TeamRegionExcludedFromEveryExportedFace':True,'originalMasterUnchanged':True,'runtimeBytes':(R/'delivery/Rev15V-Cypher-Houses-Architecture.glb').stat().st_size,'runtimeSHA256':sha(R/'delivery/Rev15V-Cypher-Houses-Architecture.glb'),'nativeComponentBytes':(R/'delivery/Rev15V-Cypher-Houses-Architecture-Update.blend').stat().st_size,'nativeComponentSHA256':sha(R/'delivery/Rev15V-Cypher-Houses-Architecture-Update.blend'),'scope':'Changed surfaces and new window details only. Full native reconstruction uses the original U3 base and included source/plan; this avoids packaging or replacing Team surfaces.'};(R/'evidence/export.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','objects','runtimeBytes','nativeComponentBytes']}))
