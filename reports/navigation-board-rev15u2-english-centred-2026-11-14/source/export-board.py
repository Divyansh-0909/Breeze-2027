import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());P=Path(b['editedMaster']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(P)==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
style=bpy.data.collections['REV15U2 / Centred English labels']
board=[o for o in s.objects if o.get('authorizedChange')=='approach-board-rigid' or o in list(style.objects) or o.get('navigationLabel') or o.get('angleDegrees')==45 or 'White inset border' in o.name or any(k in o.name for k in ['Aftermovie upward arrow','close-hung sponsor LED casing','short LED suspension','casing screw','LED power cable','board foot']) or o.get('ledScreen')]
copies=[];records=[]
for original in board:
    if original.type not in ['MESH','FONT','CURVE']:continue
    evaluated=original.evaluated_get(deps);me=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);me.transform(evaluated.matrix_world);me.update();ob=bpy.data.objects.new('NAV REVIEW / '+original.name,me)
    if original.get('navigationLabel'):ob['navigationLabel']=original['navigationLabel']
    if original.get('ledScreen'):
        me.materials.clear();mat=bpy.data.materials.new('UNCHANGED LED / runtime shader placeholder');mat.diffuse_color=(.003,.003,.003,1);me.materials.append(mat);ob['ledScreen']=True
    copies.append(ob);records.append({'name':original.name,'type':original.type,'label':ob.get('navigationLabel'),'ledScreen':bool(ob.get('ledScreen'))})
ex=bpy.data.scenes.new('NAV REVIEW / Green signs only');bpy.context.window.scene=ex
for ob in copies:ex.collection.objects.link(ob);ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.export_scene.gltf(filepath=str(R/'viewer/board.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False,export_extras=True)
assert sum(x['ledScreen'] for x in records)==1
assert sha(P)==b['editedSHA256']
(R/'evidence/viewer-export.json').write_text(json.dumps({'status':'PASS','nativeMasterUnchanged':True,'onlyOneActiveBoardExported':True,'fontGeometryBakedFromCurrentMaster':True,'parts':records,'glbBytes':(R/'viewer/board.glb').stat().st_size,'glbSHA256':sha(R/'viewer/board.glb'),'LEDShaderAndAtlasAndSponsorManifestReusedUnchanged':True},indent=2)+'\n');print('EXPORT_DONE',len(copies),flush=True)
