import bpy,json,hashlib,array
from pathlib import Path
O=Path(__file__).resolve().parents[1];
def val(v):
    if isinstance(v,(str,int,float,bool))or v is None:return v
    if hasattr(v,'name'):return v.name
    try:return[val(x)for x in v]
    except TypeError:return str(v)
def nodes(t):
    if not t:return None
    return {'nodes':[{'name':n.name,'type':n.bl_idname,'properties':{p.identifier:val(getattr(n,p.identifier))for p in n.bl_rna.properties if p.type in {'BOOLEAN','INT','FLOAT','ENUM','STRING'}and p.identifier not in {'rna_type','name','label','select','location','dimensions','width','height','color'}},'image':n.image.name if hasattr(n,'image')and n.image else None,'inputs':[(s.name,val(s.default_value))for s in n.inputs if hasattr(s,'default_value')]}for n in t.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in t.links]}
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));objects={}
    for o in bpy.data.objects:
        h=hashlib.sha256();bounds=None
        if o.type=='MESH':
            co=array.array('f',[0.0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',co);h.update(co.tobytes());h.update(json.dumps([list(p.vertices)for p in o.data.polygons]).encode())
            for uv in o.data.uv_layers:
                co=array.array('f',[0.0])*(len(uv.data)*2);uv.data.foreach_get('uv',co);h.update(co.tobytes())
            p=[o.matrix_basis@v.co for v in o.data.vertices];bounds=[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)]if p else None
        if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,list(o.data.color),o.data.size if o.data.type=='AREA'else None,o.data.use_shadow)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.sensor_width,o.data.ortho_scale,o.data.clip_start,o.data.clip_end)).encode())
        if o.type=='FONT':h.update(o.data.body.encode())
        action=None
        if o.animation_data and o.animation_data.action:action=[{'path':c.data_path,'index':c.array_index,'keys':[(list(p.co),p.interpolation)for p in c.keyframe_points]}for c in o.animation_data.action.fcurves]
        objects[o.name]={'type':o.type,'basis':[list(r)for r in o.matrix_basis],'dataHash':h.hexdigest(),'materials':[s.material.name if s.material else None for s in o.material_slots],'action':action,'bounds':bounds}
    environment={s.name:{'world':s.world.name,'exposure':s.view_settings.exposure,'transform':s.view_settings.view_transform,'look':s.view_settings.look,'fps':s.render.fps,'range':[s.frame_start,s.frame_end]}for s in bpy.data.scenes}
    materials={m.name:{'diffuse':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness,'nodes':nodes(m.node_tree)}for m in bpy.data.materials}
    worlds={w.name:{'color':list(w.color),'nodes':nodes(w.node_tree)}for w in bpy.data.worlds}
    images={i.name:{'size':list(i.size),'colorSpace':i.colorspace_settings.name,'packedSHA256':hashlib.sha256(i.packed_file.data).hexdigest()if i.packed_file else None}for i in bpy.data.images if i.type=='IMAGE'}
    return objects,environment,materials,worlds,images
