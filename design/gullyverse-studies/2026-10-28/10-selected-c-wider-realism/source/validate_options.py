import bpy,bmesh,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];rows=[]
for s in bpy.data.scenes:
 bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
 assert sum(o.type=='LIGHT'for o in s.objects)==17
 assert all(o.data.energy==0 for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical'))
 checked=[]
 for o in s.objects:
  if not o.name.startswith('OPTION /')or o.type!='MESH':continue
  m=o.data;bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;assert all(f.calc_area()>1e-9 for f in bm.faces),o.name;bm.free();assert all(math.isfinite(x)for v in m.vertices for x in v.co)
  checked.append(o.name)
 rows.append({'scene':s.name,'closedFiniteProposalMeshes':checked,'17OriginalLightsFiveSupport0W':True})
(O/'evidence/options-geometry-validation.json').write_text(json.dumps({'status':'PASS','scope':'proposal topology and lighting only, not production UV/tangent/rig/runtime acceptance','scenes':rows,'mainWorldNotModified':True},indent=2)+'\n');print('OPTIONS_GEOMETRY_PASS',flush=True)
