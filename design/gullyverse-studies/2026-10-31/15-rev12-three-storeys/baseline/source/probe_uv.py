import bpy,json
m=bpy.data.objects['REV11 / ONE continuous shared-wall structural shell'].data;m.calc_tangents(uvmap=m.uv_layers.active.name);bad=[]
for p in m.polygons:
 if any(m.loops[i].tangent.length<.999 for i in p.loop_indices):
  bad.append({'index':p.index,'normal':list(p.normal),'co':[list(m.vertices[m.loops[i].vertex_index].co)for i in p.loop_indices],'uv':[list(m.uv_layers.active.data[i].uv)for i in p.loop_indices],'tangent':[list(m.loops[i].tangent)for i in p.loop_indices]})
print('UVBAD',len(bad));print(json.dumps(bad[:6],indent=1))
