import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];rows=[]
for variant,metadata in [('REV11','baseline/evidence/authoring.json'),('REV12','evidence/authoring.json')]:
 d=json.loads((O/metadata).read_text());s=next(s for s in bpy.data.scenes if s.get('variant')==variant);o=s.objects[d['newMeshes'][0]];m=o.data;m.calc_loop_triangles();bins={'horizontalUp':0,'horizontalDown':0,'vertical':0};areas={};
 for t in m.loop_triangles:
  n=t.normal;key='horizontalUp'if n.z>.99 else'horizontalDown'if n.z<-.99 else'vertical';bins[key]+=1
  if abs(n.z)>.99:
   zz=round(sum((o.matrix_basis@m.vertices[i].co).z for i in t.vertices)/3,3);entry=areas.setdefault(str(zz),{'upAreaM2':0.,'downAreaM2':0.,'triangles':0});entry['upAreaM2'if n.z>0 else'downAreaM2']+=t.area;entry['triangles']+=1
 rows.append({'variant':variant,'primaryClosedShellTriangles':len(m.loop_triangles),'triangleOrientationBreakdown':bins,'actualHorizontalPlateAndCopingSurfacesByWorldZ':areas,'note':'Horizontal totals include true roof/floor surfaces, slab undersides and exposed coping; junction extraction shares them, so they are not an additive author-box estimate.'})
out={'status':'MEASURED_ACTUAL_CORE_GEOMETRY','rows':rows,'deltaPrimaryShell':rows[1]['primaryClosedShellTriangles']-rows[0]['primaryClosedShellTriangles'],'deltaHorizontalTriangles':sum(rows[1]['triangleOrientationBreakdown'][k]-rows[0]['triangleOrientationBreakdown'][k]for k in['horizontalUp','horizontalDown'])};(O/'evidence/structure-triangle-cost.json').write_text(json.dumps(out,indent=2));print('STRUCTURAL_COST',out['deltaPrimaryShell'],out['deltaHorizontalTriangles'])
