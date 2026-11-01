import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1]
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and any(x in o.name.lower()for x in ['wall','parapet','building /','shutter','recess']):
  p=[o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'name':o.name,'location':list(o.location),'scale':list(o.scale),'bounds':[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]})
cams=[{'name':o.name,'position':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens}for o in bpy.data.objects if o.type=='CAMERA']
mats={m.name:{'nodes':[(n.name,n.bl_idname,[(s.name,list(s.default_value)if hasattr(s.default_value,'__len__')and not isinstance(s.default_value,str)else s.default_value)for s in n.inputs if hasattr(s,'default_value')])for n in m.node_tree.nodes]}for m in bpy.data.materials if any(x in m.name.lower()for x in ['shutter','plaster','concrete','brick'])and m.node_tree}
img=bpy.data.images.load(str(O/'source/originals/ritviz.jpeg'));sample=list(img.pixels[:24]);bpy.data.images.remove(img)
(O/'evidence/baseline-scene-probe.json').write_text(json.dumps({'surfaces':rows,'cameras':cams,'materials':mats,'sampleImageFloats':sample},indent=2)+'\n');print('PROBE_DONE',len(rows))
