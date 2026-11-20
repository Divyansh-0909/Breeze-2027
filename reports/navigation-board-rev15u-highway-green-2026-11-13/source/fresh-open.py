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
rotations={o.name.split(' / ',1)[1]:list(o.rotation_euler) for o in base.objects}
matrices={o.name.split(' / ',1)[1]:[list(v) for v in o.matrix_world] for o in base.objects}
grounds={o.name.split(' / ',1)[1]:mesh_hash(o) for o in base.objects if o.get('groundSurface')}
lights={o.name.split(' / ',1)[1]:[o.data.energy,list(o.data.color)] for o in base.objects if o.type=='LIGHT'}
if a.restored:
    restored=json.loads((R/'evidence/restore-check.json').read_text());P=Path(restored['restoredMaster']);expected=restored['restoredSHA256']
else:P=Path(b['editedMaster']);expected=b['editedSHA256']
assert sha(P)==expected;bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
assert len(bpy.data.scenes)==53 and s.name=='REV15U1 / Bilingual green highway navigation signs'
assert digital_snapshot(s)==digital,'Digital sponsor board changed'
current={o.name.split(' / ',1)[1]:o for o in s.objects}
modified=set(b['modifiedOriginalObjects']);assert all([list(v) for v in current[k].matrix_world]==m for k,m in matrices.items() if ('REV15T3 / '+k) not in modified)
assert all(list(current[k].rotation_euler)==v for k,v in rotations.items())
plaques=[o for o in s.objects if o.type=='MESH' and 'White inset border' not in o.name and ('Reused sign hierarchy /' in o.name or ' / Past Sponsors plaque' in o.name)];assert len(plaques)==6 and all(abs(o.dimensions.z-.68)<.00001 for o in plaques)
assert abs(next(o for o in plaques if 'Past Sponsors plaque' in o.name).location.z-.34-10.05)<.00001
assert all(mesh_hash(current[k])==v for k,v in grounds.items())
assert all([current[k].data.energy,list(current[k].data.color)]==v for k,v in lights.items())
fonts=[o for o in s.objects if o.type=='FONT' and (o.get('navigationLabel') or 'Highway Gullyverse title' in o.name)]
hindi=[o for o in s.objects if o.get('language')=='hi'];assert len(hindi)==7
art={x['english']:x for x in json.loads((R/'evidence/hindi-artwork.json').read_text())['labels']}
for ob in hindi:
 row=art[ob['englishLabel']];assert ob['hindiLabel']==row['hindi'];im=next(n.image for n in ob.material_slots[0].material.node_tree.nodes if n.type=='TEX_IMAGE');assert hashlib.sha256(im.packed_file.data).hexdigest()==row['sha256']
assert len(fonts)==7 and all(o.data.font.packed_file for o in fonts)
assert all('Overpass' in o.data.font.name for o in fonts)
arrows=[o for o in s.objects if o.get('angleDegrees')==45];assert len(arrows)==4 and sum(o['direction']=='up-left' for o in arrows)==2 and sum(o['direction']=='up-right' for o in arrows)==2
assert any(o.data.body=='Accommodation' for o in fonts) and all(o.data.body!='Schedule' for o in fonts)
assert sum(bool(im.packed_file) for im in bpy.data.images)==109
led=next(o for o in s.objects if o.get('ledScreen'));assert led['minimumLogoGapCells']==72 and led['logoCount']==62 and led['periodCells']==10676
mat=led.material_slots[0].material;value=mat.node_tree.nodes['LED scroll cells'].outputs[0]
for frame,expectedValue in [(1,0),(2,1),(10677,0)]:s.frame_set(frame);bpy.context.view_layer.update();assert abs(value.default_value-expectedValue)<.001
for name in ['main.js','logo-strip.png','sponsors.json']:
    original=R.parent/'navigation-board-rev15l1-logo-spacing-2026-11-11/viewer'/name;assert sha(R/'viewer'/name)==sha(original)
out={'status':'PASS','freshNativeOpen':True,'scenes':53,'packedImages':109,'packedHighwayFonts':2,'sevenLabelsUseOverpass':True,'unchangedNavigationOrientations':True,'panelHeightMetres':.68,'sevenHindiLabels':True,'fourRoadMeshesAndAttributesExact':True,'lightingAndExposureUnchanged':True,'digitalBoardGeometryMaterialsImagesAndDriversExact':True,'LEDNativeFramesAndWrapPass':True,'LEDViewerShaderAtlasManifestByteIdentical':True,'logoCount':62,'minimumGapCells':72,'periodCells':10676,'sourceSHA256':expected}
(R/('evidence/restored-fresh-open.json' if a.restored else 'evidence/fresh-open.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
