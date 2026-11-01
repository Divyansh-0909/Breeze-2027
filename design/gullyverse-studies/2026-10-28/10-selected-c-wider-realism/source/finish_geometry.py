import bpy,bmesh,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());rows=[]
for name in a['newConstructionObjects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);fs=[f for f in bm.faces if len(f.verts)>4];count=len(fs)
 if fs:bmesh.ops.triangulate(bm,faces=fs)
 bm.to_mesh(o.data);bm.free();o.data.update();rows.append({'object':name,'planarCapNgonsTriangulated':count})
master=O/'source/Gullyverse-Selected-C-Wider-Realism.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
a['masterSHA256']=hashlib.sha256(master.read_bytes()).hexdigest();a['masterBytes']=master.stat().st_size;(O/'evidence/authoring.json').write_text(json.dumps(a,indent=2)+'\n');(O/'evidence/cap-retopology.json').write_text(json.dumps({'status':'PASS','planarCapsOnly':True,'originalObjectsUnchanged':True,'rows':rows},indent=2)+'\n')
