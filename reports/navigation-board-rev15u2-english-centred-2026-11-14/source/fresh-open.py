import bpy,json,hashlib,sys,argparse
from pathlib import Path
from array import array
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--restored',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
def mesh_hash(ob):
    me=ob.data;h=hashlib.sha256()
    for coll,field,typ,n in [(me.vertices,'co','f',len(me.vertices)*3),(me.loops,'vertex_index','i',len(me.loops)),(me.polygons,'material_index','i',len(me.polygons))]:
        v=array(typ,[0])*n;coll.foreach_get(field,v);h.update(v.tobytes())
    for uv in me.uv_layers:
        v=array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',v);h.update(v.tobytes())
    for attr in me.color_attributes:
        v=array('f',[0])*(len(attr.data)*4);attr.data.foreach_get('color',v);h.update(v.tobytes())
    return h.hexdigest()
def material_hash(mat):
    if not mat.use_nodes:return mat.name
    rows=[]
    for n in mat.node_tree.nodes:
        inputs=[]
        for i in n.inputs:
            if hasattr(i,'default_value'):
                v=i.default_value
                if hasattr(v,'__len__') and not isinstance(v,str):v=list(v)
                inputs.append([i.name,v])
        row=[n.name,n.type,inputs]
        if n.type=='TEX_IMAGE':row.append(hashlib.sha256(n.image.packed_file.data).hexdigest())
        rows.append(row)
    drivers=[(d.data_path,d.driver.expression) for d in mat.node_tree.animation_data.drivers] if mat.node_tree.animation_data else []
    return hashlib.sha256(json.dumps([rows,[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links],drivers],sort_keys=True).encode()).hexdigest()
def digital_snapshot(s):
    rows=[]
    for o in s.objects:
        if not (any(k in o.name for k in ['LED','casing screw','LED power cable']) or o.get('ledScreen')):continue
        row={'name':o.name.split(' / ',1)[1],'matrix':[list(v) for v in o.matrix_world],'type':o.type,'properties':dict(o.items())}
        if o.type=='MESH':row['mesh']=mesh_hash(o)
        if o.type=='CURVE':row['curve']=[[[list(p.co) for p in sp.points],sp.type] for sp in o.data.splines]
        if o.type=='LIGHT':row['light']=[o.data.energy,list(o.data.color),o.data.type]
        row['materials']=[material_hash(x.material) for x in o.material_slots if x.material];rows.append(row)
    return sorted(rows,key=lambda x:x['name'])
assert sha(b['source'])==b['sourceSHA256'];bpy.ops.wm.open_mainfile(filepath=b['source']);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();digital=digital_snapshot(base)
matrices={o.name.split(' / ',1)[1]:[list(v) for v in o.matrix_world] for o in base.objects if o.get('language')!='hi' and not(o.type=='FONT' and o.get('navigationLabel'))}
grounds={o.name.split(' / ',1)[1]:mesh_hash(o) for o in base.objects if o.get('groundSurface')}
if a.restored:
 proof=json.loads((R/'evidence/restore-check.json').read_text());P=Path(proof['restoredMaster']);expected=proof['restoredSHA256']
else:P=Path(b['editedMaster']);expected=b['editedSHA256']
assert sha(P)==expected;bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
assert len(bpy.data.scenes)==54 and s.name=='REV15U2 / English centred highway navigation'
assert not any(o.get('language')=='hi' for o in s.objects)
assert digital_snapshot(s)==digital
current={o.name.split(' / ',1)[1]:o for o in s.objects}
assert all([list(v) for v in current[k].matrix_world]==m for k,m in matrices.items())
assert all(mesh_hash(current[k])==v for k,v in grounds.items())
from mathutils import Vector
errors=[]
for row in b['alignment']:
 font=s.objects[row['object']];panel=s.objects[row['panel']];pts=[font.matrix_world@Vector(c) for c in font.bound_box];p=[panel.matrix_world@Vector(c) for c in panel.bound_box];error=abs((min(v.z for v in pts)+max(v.z for v in pts))/2-(min(v.z for v in p)+max(v.z for v in p))/2);assert error<.00001;errors.append(error)
assert len(errors)==7
led=next(o for o in s.objects if o.get('ledScreen'));value=led.material_slots[0].material.node_tree.nodes['LED scroll cells'].outputs[0]
for frame,want in [(1,0),(2,1),(10677,0)]:s.frame_set(frame);bpy.context.view_layer.update();assert abs(value.default_value-want)<.001
U1=R.parent/'navigation-board-rev15u-highway-green-2026-11-13'
for f in ['main.js','logo-strip.png','sponsors.json']:assert sha(R/'viewer'/f)==sha(U1/'viewer'/f)
result={'status':'PASS','freshNativeOpen':True,'scenes':54,'HindiLabelsInActiveScene':0,'centredEnglishLabels':7,'maximumCentringErrorMetres':max(errors),'allNonTextTransformsExact':True,'roadGeometryUVsAndColoursExact':True,'digitalBoardGeometryMaterialsAndDriversExact':True,'nativeLEDWrapPass':True,'LEDViewerShaderAtlasManifestByteIdentical':True,'sourceSHA256':expected}
(R/('evidence/restored-fresh-open.json' if a.restored else 'evidence/fresh-open.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
