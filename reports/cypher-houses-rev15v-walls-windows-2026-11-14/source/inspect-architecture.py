import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15U3-Larger-English-Navigation.blend');s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
    if o.type not in ['MESH','FONT']:continue
    p=[o.matrix_world@Vector(c) for c in o.bound_box];bb=[[min(q[i] for q in p),max(q[i] for q in p)] for i in range(3)]
    if bb[1][1]<14 or bb[1][0]>60 or bb[2][1]<7.2:continue
    if not(any(k in o.name.lower() for k in ['house','window','facade','plaster','repair','pane','sill','glass','grill','lintel','team','poster','events','sash','glazing','timber','mineral','limewash','brick','door','beam']) or o.get('artKind')):continue
    row={'name':o.name,'type':o.type,'data':o.data.name,'bounds':bb,'location':list(o.location),'rotation':list(o.rotation_euler),'props':dict(o.items()),'materials':[m.material.name if m.material else None for m in o.material_slots]}
    if o.type=='MESH':
        row['vertices']=len(o.data.vertices);row['faces']=len(o.data.polygons);row['materialFaceCounts']={str(i):sum(f.material_index==i for f in o.data.polygons) for i in range(len(o.material_slots))};row['UVLayers']=[uv.name for uv in o.data.uv_layers]
    rows.append(row)
(R/'evidence/cypher-baseline.json').write_text(json.dumps(rows,indent=2,default=str)+'\n');print('BASELINE_ROWS',len(rows))

