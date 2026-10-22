from pathlib import Path
import bpy,json
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(Path('public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb').resolve()))
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 for name in [u.name for u in o.data.uv_layers]:
  o.data.calc_tangents(uvmap=name);bad={l.index for l in o.data.loops if l.tangent.length<.99}
  for p in o.data.polygons:
   if set(p.loop_indices)&bad:rows.append(dict(mesh=o.name,uv=name,face=p.index,positions=[list(o.data.vertices[i].co)for i in p.vertices],badLoops=list(set(p.loop_indices)&bad),normals=[list(o.data.corner_normals[i].vector)for i in p.loop_indices],geometricNormal=list(p.normal)))
Path('reports/recovery-quarry-fidelity-2026-10-19/raw/actual-bad-tangent-faces.json').write_text(json.dumps(rows,indent=2));print(rows)
