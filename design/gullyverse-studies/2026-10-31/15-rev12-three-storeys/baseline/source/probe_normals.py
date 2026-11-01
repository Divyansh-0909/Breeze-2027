import bpy
m=bpy.data.objects['REV11 / ONE continuous shared-wall structural shell'].data;m.calc_tangents(uvmap=m.uv_layers.active.name)
print('LOOPNORMAL',min(l.normal.length for l in m.loops),'SMOOTH',sum(p.use_smooth for p in m.polygons))
for p in m.polygons:
 if any(m.loops[i].tangent.length<.999 for i in p.loop_indices):
  print('BADFACE',p.index,'loopnormals',[list(m.loops[i].normal)for i in p.loop_indices],'vertex',[m.loops[i].vertex_index for i in p.loop_indices]);break
