import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];R.joinpath('evidence').mkdir(parents=True,exist_ok=True)
P=Path('/dev/shm/Gullyverse-Rev15S-Realistic-Shop-Name-Boards.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if not any(k in o.name.lower() for k in ['floor','ground','lane flat','ramp','rooftop slab','cypher','circle','drain','paving']):continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box]
 x={'name':o.name,'type':o.type,'bounds':[[min(v[i] for v in bb) for i in range(3)],[max(v[i] for v in bb) for i in range(3)]],'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),'matrix':[list(row) for row in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else [],'properties':{k:str(v) for k,v in o.items()},'hideRender':o.hide_render}
 if o.type=='MESH':x.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),sampleVertices=[list(v.co) for v in o.data.vertices[:10]],sampleFaces=[list(f.vertices) for f in o.data.polygons[:8]])
 rows.append(x)
(R/'evidence/ground-inspection.json').write_text(json.dumps({'scene':s.name,'sourceSHA256':hashlib.sha256(P.read_bytes()).hexdigest(),'objects':rows},indent=2)+'\n')
print(json.dumps({'scene':s.name,'matches':len(rows),'objects':[{'name':x['name'],'bounds':x['bounds'],'materials':x['materials'],'verts':x.get('vertices')} for x in rows]},indent=2),flush=True)
