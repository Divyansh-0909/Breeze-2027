import bpy, hashlib, json, re
from array import array
def fingerprint(scene):
    rows=[]; cache={}
    for o in sorted(scene.objects,key=lambda x:x.name):
        # Newly linked parented gate objects can retain an unevaluated identity
        # matrix until reopening. Compose their authored transforms explicitly.
        matrix=o.matrix_world
        if o.get('entryGatePart')=='hinge axis' or o.get('streetLampPart'):matrix=o.matrix_basis
        elif o.parent and o.parent.get('entryGatePart')=='hinge axis':matrix=o.parent.matrix_basis@o.matrix_parent_inverse@o.matrix_basis
        row={'name':o.name,'type':o.type,'matrix':[list(r) for r in matrix],
             'hidden':o.hide_render,'viewportHidden':o.hide_viewport,'parent':o.parent.name if o.parent else None}
        if o.type=='MESH':
            m=o.data
            if m.as_pointer() not in cache:
                h=hashlib.sha256()
                for coll,field,typecode,n in [(m.vertices,'co','f',len(m.vertices)*3),(m.loops,'vertex_index','i',len(m.loops)),(m.polygons,'loop_total','i',len(m.polygons)),(m.polygons,'material_index','i',len(m.polygons))]:
                    buf=array(typecode,[0])*n;coll.foreach_get(field,buf);h.update(buf.tobytes())
                for uv in m.uv_layers:
                    buf=array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',buf);h.update(uv.name.encode());h.update(buf.tobytes())
                for attr in m.color_attributes:
                    buf=array('f',[0])*(len(attr.data)*4);attr.data.foreach_get('color',buf);h.update(attr.name.encode());h.update(buf.tobytes())
                cache[m.as_pointer()]=h.hexdigest()
            row['meshSHA256']=cache[m.as_pointer()]
            row['materials']=[re.sub(r'\.\d{3}$','',x.material.name) if x.material else None for x in o.material_slots]
        if o.type=='FONT':row['font']=[o.data.body,o.data.size,o.data.align_x,o.data.align_y,o.data.extrude,o.data.bevel_depth,hashlib.sha256(o.data.font.packed_file.data).hexdigest() if o.data.font.packed_file else o.data.font.name]
        if o.type=='LIGHT':row['light']=[o.data.type,o.data.energy,list(o.data.color)]
        rows.append(row)
    data={'objects':rows,'world':scene.world.name,'exposure':scene.view_settings.exposure,'rayReflections':scene.eevee.use_raytracing}
    return {'sha256':hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest(),'objects':len(rows),'data':data}
