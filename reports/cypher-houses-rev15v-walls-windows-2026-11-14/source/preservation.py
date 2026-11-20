import bpy,json,hashlib
from array import array
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def material_signature(mat,cache=None):
    cache={} if cache is None else cache
    if not mat:return None
    def tree_sig(tree):
        key=tree.as_pointer()
        if key in cache:return cache[key]
        rows=[]
        for n in tree.nodes:
            inputs=[]
            for socket in n.inputs:
                if not hasattr(socket,'default_value'):continue
                v=socket.default_value
                if hasattr(v,'__len__') and not isinstance(v,str):v=list(v)
                if not isinstance(v,(int,float,str,bool,list,tuple,type(None))):v=getattr(v,'name',str(v))
                inputs.append([socket.identifier,v])
            row=[n.name,n.type,inputs]
            for prop in ['operation','blend_type','uv_map','extension','interpolation']:
                if hasattr(n,prop):row.append([prop,getattr(n,prop)])
            if n.type=='TEX_IMAGE' and n.image:row.append(['image',hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else n.image.filepath])
            if n.type=='GROUP':row.append(['group',tree_sig(n.node_tree)])
            rows.append(row)
        drivers=[(d.data_path,d.driver.expression) for d in tree.animation_data.drivers] if tree.animation_data else []
        result=digest([rows,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links],drivers]);cache[key]=result;return result
    return digest([mat.name,tree_sig(mat.node_tree) if mat.use_nodes else list(mat.diffuse_color),getattr(mat,'surface_render_method',None)])
def geometry_signature(me):
    h=hashlib.sha256()
    for coll,field,typ,n in [(me.vertices,'co','f',len(me.vertices)*3),(me.loops,'vertex_index','i',len(me.loops)),(me.polygons,'loop_total','i',len(me.polygons)),(me.polygons,'use_smooth','b',len(me.polygons))]:
        a=array(typ,[0])*n;coll.foreach_get(field,a);h.update(a.tobytes())
    for uv in me.uv_layers:
        if uv.name=='REV15VFacadeUV':continue
        a=array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(uv.name.encode());h.update(a.tobytes())
    for attr in me.color_attributes:
        a=array('f',[0])*(len(attr.data)*4);attr.data.foreach_get('color',a);h.update(attr.name.encode());h.update(a.tobytes())
    return h.hexdigest()
def snapshot(scene,plan,prefix):
    rows=[];gcache={};mcache={};targets={r['object'].removeprefix('REV15U3 / '):r for r in plan['objects']}
    for ob in scene.objects:
        if not ob.name.startswith(prefix) or ob.get('architectureHouse'):continue
        name=ob.name.removeprefix(prefix)
        row={'name':name,'type':ob.type,'matrix':[list(x) for x in ob.matrix_world],'hidden':ob.hide_render,'viewportHidden':ob.hide_viewport}
        if ob.type=='MESH':
            me=ob.data
            if me.as_pointer() not in gcache:gcache[me.as_pointer()]=geometry_signature(me)
            row['shapeUVColour']=gcache[me.as_pointer()]
            skip=set()
            if name in targets:
                t=targets[name];skip={i for i,g in t['wallFaces']}|set(t['frameFaces'])|{i for i,w in t['glassFaces']}
            mats={i:material_signature(slot.material,mcache) for i,slot in enumerate(ob.material_slots)}
            row['unmodifiedFaceMaterials']=digest([(f.index,mats[f.material_index]) for f in me.polygons if f.index not in skip])
        elif ob.type=='FONT':row['font']=[ob.data.body,ob.data.size,ob.data.font.name]
        elif ob.type=='LIGHT':row['light']=[ob.data.type,ob.data.energy,list(ob.data.color)]
        elif ob.type=='CURVE':row['curve']=[(s.type,[list(p.co) for p in s.points]) for s in ob.data.splines]
        rows.append(row)
    return {'sha256':digest(sorted(rows,key=lambda x:x['name'])),'objects':len(rows)}
