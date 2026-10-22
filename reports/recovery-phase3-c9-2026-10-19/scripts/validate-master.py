from pathlib import Path
import bpy,json,hashlib
root=Path.cwd();path=root/'assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend'
before=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path))
contract=json.loads(bpy.data.texts['RECOVERY_C9_CONTRACT'].as_string());objects=[]
for level in range(3):
 ob=bpy.data.objects[f'C9_Wall_15_LOD{level}'];assert len(ob.data.polygons)==contract['LODs'][level]['triangles'];assert len(ob.data.uv_layers)==2
 objects.append({'name':ob.name,'triangles':len(ob.data.polygons),'UVs':[u.name for u in ob.data.uv_layers],'material':ob.data.materials[0].name})
images=[{'name':im.name,'width':im.size[0],'height':im.size[1],'packed':bool(im.packed_file),'source':im.source}for im in bpy.data.images if im.source=='FILE']
assert images and all(im['packed']for im in images)
assert bpy.data.objects.get('C9_Native_High_Unique_Uniform_0_9')and bpy.data.objects.get('coastal_cliff_01_LOD0')
assert before==hashlib.sha256(path.read_bytes()).hexdigest()
result={'status':'PASS','masterSHA256':before,'bytes':path.stat().st_size,'runtimeObjects':objects,'packedImages':images,'missingLinkedImages':0,'originalNativeSourceIncluded':True,'highAuthoringMeshIncluded':True,'openedReadOnlyNoSave':True,'Blender':bpy.app.version_string}
(root/'reports/recovery-phase3-c9-2026-10-19/raw/master-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('MASTER_READ_ONLY PASS',len(images),'packed images')
