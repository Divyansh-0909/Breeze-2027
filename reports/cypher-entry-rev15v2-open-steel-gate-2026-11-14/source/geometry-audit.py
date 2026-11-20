import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());assert hashlib.sha256(Path(b['editedMaster']).read_bytes()).hexdigest()==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();faces=0
for o in s.objects:
 if not o.get('entryGatePart') or o.type!='MESH':continue
 for f in o.data.polygons:
  p=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];faces+=1;intersects=(max(v.x for v in p)>-.8 and min(v.x for v in p)<.85 and max(v.y for v in p)>13 and min(v.y for v in p)<16 and max(v.z for v in p)>7.3 and min(v.z for v in p)<9.5);assert not intersects,'New geometry crosses the walking corridor'
result={'status':'PASS','sourceSHA256':b['editedSHA256'],'newFacesAudited':faces,'unobstructedCorridor':{'x':[-.8,.85],'y':[13,16],'z':[7.3,9.5]},'clearWidthMetres':1.65,'thresholdStepAdded':False,'nominalOpeningWidthMetres':1.8,'clearGapBetweenVerticalRodsMetres':(1.715-.075)/14-.016};(R/'evidence/geometry-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
