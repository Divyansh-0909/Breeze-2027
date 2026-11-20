import hashlib,json,runpy
from pathlib import Path
material_signature=runpy.run_path(str(Path(__file__).with_name('preservation.py')))['material_signature']
def faces_signature(ob,removed=()):
 me=ob.data;attr=me.attributes.get('REV15YSourceFace');rows=[];cache={}
 for f in me.polygons:
  index=attr.data[f.index].value if attr else f.index
  if index in removed:continue
  loops=[]
  for li in f.loop_indices:
   vi=me.loops[li].vertex_index;p=me.vertices[vi].co
   colors=[]
   for ca in me.color_attributes:
    if ca.domain in ['POINT','CORNER']:colors.append([ca.name,list(ca.data[vi if ca.domain=='POINT'else li].color)])
   loops.append([list(p),[[uv.name,list(uv.data[li].uv)]for uv in me.uv_layers],colors])
  mat=ob.material_slots[f.material_index].material;rows.append([index,loops,material_signature(mat,cache),f.use_smooth])
 rows.sort(key=lambda x:x[0]);return {'faces':len(rows),'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
