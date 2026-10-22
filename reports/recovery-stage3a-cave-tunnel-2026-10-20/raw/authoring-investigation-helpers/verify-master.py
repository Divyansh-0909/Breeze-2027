import bpy,json
from pathlib import Path
r=Path('/workspace/Breeze-2027-navigation');p=r/'assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend';bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for image in bpy.data.images:
 if image.source=='FILE':rows.append({'name':image.name,'packed':bool(image.packed_file),'exists':Path(bpy.path.abspath(image.filepath)).exists(),'size':list(image.size)})
result={'status':'PASS'if all(x['packed']or x['exists']for x in rows)else'FAIL','openedReadOnly':True,'master':str(p.relative_to(r)),'meshObjects':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}for o in bpy.data.objects if o.type=='MESH'],'linkedImages':rows}
(r/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw/master-accessibility.json').write_text(json.dumps(result,indent=2));print(result)
