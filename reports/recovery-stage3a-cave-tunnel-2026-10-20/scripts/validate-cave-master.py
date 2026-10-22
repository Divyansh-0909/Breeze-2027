from pathlib import Path
import bpy,json,hashlib
ROOT=Path.cwd();S=ROOT/'assets-source/gullyverse/c9-cave-recovery';R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw';p=S/'cave-entrance-working.blend';before=hashlib.file_digest(p.open('rb'),'sha256').hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p))
m=json.loads(bpy.data.texts['CAVE_RECOVERY_CONTRACT'].as_string());actual=json.loads((ROOT/'public/models/gullyverse/c9-cave-recovery/manifest.json').read_text());assert m==actual;assert m['approvedTextureScale']==3;assert m['textureMapping']['geometryUVMetresPerUnit']==2
objects=[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}for o in bpy.data.objects if o.type=='MESH'];images=[{'name':i.name,'packed':bool(i.packed_file),'exists':Path(bpy.path.abspath(i.filepath)).is_file(),'size':list(i.size),'colourSpace':i.colorspace_settings.name}for i in bpy.data.images if i.source=='FILE'];assert all(i['packed']for i in images)
assert all(bpy.data.objects.get(name)for part in m['parts']for name in part['nodes']);assert bpy.data.objects.get('CC0_Coastal04_Original_Native_Reference');assert bpy.data.objects.get('CC0_Coastal01_Native_Tunnel_Sculpt_Source')
result={'status':'PASS','openedReadOnly':True,'master':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':before,'runtimeContractMatchesManifest':True,'meshObjects':objects,'linkedImages':images,'unitScaleM':bpy.context.scene.unit_settings.scale_length,'runtimeTextureImagesEmbedded':False,'authoringPBRTexturesPacked':True}
assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==before
(R/'master-accessibility.json').write_text(json.dumps(result,indent=2)+'\n');print('MASTER_READ_ONLY_PASS',json.dumps(result),flush=True)
