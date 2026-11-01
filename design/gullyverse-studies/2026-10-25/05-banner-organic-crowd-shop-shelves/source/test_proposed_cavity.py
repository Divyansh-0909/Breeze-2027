import bpy,json,sys,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('prepared_recess',p/'source/prepare_shop_interior.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for name,through in [('Building / -1 / 0',False),('Shop recess',True)]:
 old=bpy.data.objects[name];dummy=bpy.data.objects.new('DIAGNOSTIC_ONLY_'+name,old.data.copy());dummy.matrix_basis=old.matrix_basis.copy();rows.append(m.make_recess(dummy,-1,-25,6,through))
(p/'evidence/proposed-recess-mesh-math-test.json').write_text(json.dumps({'status':'PASS_ON_UNLINKED_DIAGNOSTIC_COPIES_ONLY','appliedToCandidate':False,'userExceptionPending':True,'meshes':rows},indent=2)+'\n');print('PROPOSED_RECESS_TOPOLOGY_VALID',[(r['newVertices'],r['faces'])for r in rows])
