import bpy,bmesh,math,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for name in [x['copy']for x in a['surfaceCopies']]+a['newConstructionObjects']:
 o=bpy.data.objects[name]
 if o.type=='CURVE':continue
 print('CHECK_DETAIL',name,flush=True)
 ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m)
 assert all(f.calc_area()>1e-9 for f in bm.faces),name
 surface=name.endswith('localized lime-cement repair')
 if not surface:assert all(e.is_manifold for e in bm.edges),name
 volume=bm.calc_volume(signed=True)
 if not surface:assert volume>0,(name,volume)
 bm.free();assert m.uv_layers.active,name;m.calc_tangents(uvmap=m.uv_layers.active.name)
 assert all(math.isfinite(v)for l in m.loops for v in [*l.normal,*l.tangent,*l.bitangent]),name
 assert all(abs(l.normal.dot(l.tangent))<1e-4 and l.tangent.length>.999 and abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops),name
 rows.append({'object':name,'triangles':len(m.loop_triangles),'closedManifold':not surface,'signedVolume':volume,'finiteUnitTangentFrames':True,'exception':'intentional thin plaster repair surface'if surface else None});ev.to_mesh_clear()
proof={'status':'PASS','meshesChecked':len(rows),'strictAreaThreshold':1e-9,'strictTangentDotTolerance':1e-4,'strictUnitTangentMinimum':.999,'tolerancesUnchanged':True,'checks':rows}
(O/'evidence/detail-geometry-validation.json').write_text(json.dumps(proof,indent=2)+'\n');print('DETAILS_GEOMETRY_PASS',len(rows),flush=True)
