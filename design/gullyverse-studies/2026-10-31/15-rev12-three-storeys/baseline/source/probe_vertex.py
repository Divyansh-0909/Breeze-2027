import bpy
m=bpy.data.objects['REV11 / ONE continuous shared-wall structural shell'].data;m.calc_tangents(uvmap=m.uv_layers.active.name)
for p in m.polygons:
 if 19823 in p.vertices:
  print(p.index,list(p.normal),[(list(m.uv_layers.active.data[i].uv),list(m.loops[i].tangent))for i in p.loop_indices])
