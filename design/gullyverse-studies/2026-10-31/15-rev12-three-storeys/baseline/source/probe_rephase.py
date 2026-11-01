import bpy,math,json
m=bpy.data.objects['REV11 / ONE continuous shared-wall structural shell'].data;uv=m.uv_layers.active
for p in m.polygons:
 mat=m.materials[p.material_index];node=next((n for n in mat.node_tree.nodes if n.type=='VECT_MATH'and n.operation=='SCALE'),None);period=1/node.inputs['Scale'].default_value if node else 1
 mean=[sum(uv.data[i].uv[a]for i in p.loop_indices)/len(p.loop_indices)for a in range(2)];off=[math.floor(v/period)*period for v in mean]
 for i in p.loop_indices:uv.data[i].uv=(uv.data[i].uv[0]-off[0],uv.data[i].uv[1]-off[1])
m.calc_tangents(uvmap=uv.name);print('REPHASE_TANGENT',min(l.tangent.length for l in m.loops),sum(l.tangent.length<.999 for l in m.loops))
