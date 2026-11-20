import bpy,json,re,collections
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O.parent/'navigation-board-rev15l1-logo-spacing-2026-11-11/delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();rows=[];heads=[]
for o in s.objects:
 if o.type!='MESH':continue
 mats=[m.name if m else '' for m in o.data.materials]
 if any(re.search('crowd|skin|hair|cloth|trouser|sneaker',m,re.I) for m in mats):
  r={'name':o.name,'data':o.data.name,'loc':list(o.matrix_world.translation),'rot':list(o.rotation_euler),'dim':list(o.dimensions),'parent':o.parent.name if o.parent else None,'verts':len(o.data.vertices),'materials':mats,'bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)]};rows.append(r)
  if 'head' in o.name.lower():heads.append(r)
(O/'evidence/population-parts.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'matchedMeshes':len(rows),'proxyHeads':[{k:r[k] for k in ['name','loc','dim','parent']} for r in heads],'otherNonREV15Names':[r['name'] for r in rows if not r['name'].startswith('REV15 /')]},indent=2),flush=True)
