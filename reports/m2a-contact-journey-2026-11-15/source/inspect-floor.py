import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/dev/shm/Breeze-2027-runtime/public/models/gullyverse/locked-rev15z-clean-v2/contact-frontage-baked.blend')
c=json.load(open('/dev/shm/Breeze-2027-runtime/components/gullyverse-runtime/contact-space.json'));t=Vector(c['tangent']);n=Vector(c['normal']);rows=[]
for o in bpy.data.collections['Runtime / contact-frontage'].objects:
 if 'Rooftop slab'not in o.name:continue
 for f in o.data.polygons:
  vs=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
  if max(v.z for v in vs)>7.3 or min(v.z for v in vs)<7.1:continue
  rows.append({'u':[min(v.dot(t)for v in vs),max(v.dot(t)for v in vs)],'depth':[min(v.dot(n)for v in vs),max(v.dot(n)for v in vs)],'z':[min(v.z for v in vs),max(v.z for v in vs)],'normal':list(f.normal)})
print('FLOOR',json.dumps(rows))
