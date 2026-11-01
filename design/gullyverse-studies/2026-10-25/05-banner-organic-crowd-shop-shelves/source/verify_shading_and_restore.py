"""Read-only restored-master checks; writes receipt outside the restored member tree."""
import bpy,json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1]
def value(v):
    if isinstance(v,(str,int,float,bool))or v is None:return v
    if hasattr(v,'name'):return {'datablock':v.name}
    try:return [value(x)for x in v]
    except TypeError:return str(v)
def tree(t):
    if not t:return None
    return {'nodes':[{ 'name':n.name,'type':n.bl_idname,'properties':{p.identifier:value(getattr(n,p.identifier))for p in n.bl_rna.properties if p.type in {'BOOLEAN','INT','FLOAT','ENUM','STRING'}and p.identifier not in {'rna_type','name','label','select','location','dimensions','width','height','color'}},'image':n.image.name if hasattr(n,'image')and n.image else None,'inputs':[(s.name,value(s.default_value))for s in n.inputs if hasattr(s,'default_value')]}for n in t.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in t.links]}
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    return {'materials':{m.name:{'diffuse':list(m.diffuse_color),'metallic':m.metallic,'roughness':m.roughness,'useNodes':m.use_nodes,'nodes':tree(m.node_tree)}for m in bpy.data.materials},'worlds':{w.name:{'color':list(w.color),'nodes':tree(w.node_tree)}for w in bpy.data.worlds},'images':{i.name:{'packed':bool(i.packed_file),'size':list(i.size),'colorspace':i.colorspace_settings.name,'sha256':hashlib.sha256(i.packed_file.data).hexdigest()if i.packed_file else None}for i in bpy.data.images if i.type=='IMAGE'}}
base=snapshot(O/'source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend')
review=O/'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend'
candidate=snapshot(review)
retired=set(base['materials'])-set(candidate['materials'])
assert retired=={'Festival takeover banner / raster paint'},retired
assert not(set(candidate['materials'])-set(base['materials']))
# Blender retires the removed plane's now-unreferenced material on save.
# Its complete original remains in the protected baseline. All surviving shading is exact.
base['materials'].pop('Festival takeover banner / raster paint')
if base!=candidate:
    differences=[]
    def compare(a,b,path=''):
        if type(a)!=type(b):differences.append({'path':path,'before':str(a)[:400],'after':str(b)[:400]});return
        if isinstance(a,dict):
            for k in sorted(set(a)|set(b)):
                if k not in a or k not in b:differences.append({'path':path+'/'+k,'before':str(a.get(k))[:400],'after':str(b.get(k))[:400]})
                else:compare(a[k],b[k],path+'/'+k)
        elif isinstance(a,list):
            if len(a)!=len(b):differences.append({'path':path,'beforeLen':len(a),'afterLen':len(b)})
            for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
        elif a!=b:differences.append({'path':path,'before':a,'after':b})
    compare(base,candidate)
    (O/'evidence/shading-difference-diagnostic.json').write_text(json.dumps(differences,indent=2)+'\n')
    print('DIFFERENCES',differences[:10],flush=True)
assert base==candidate,'material/world/image contents differ; see diagnostic'
assert len(bpy.data.scenes)==3
assert len(candidate['images'])==24 and all(i['packed']for i in candidate['images'].values())
assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
assert len([x for x in bpy.data.objects if x.type=='CAMERA'])==24
assert 'Festival takeover banner'not in bpy.data.objects
for name in ['Existing Aftermovie / center','Existing Aftermovie / left','Existing Aftermovie / right','EXISTING GULLYVERSE hero raster','Small festival lane poster']:assert name in bpy.data.objects
for scene in bpy.data.scenes:
    assert scene['rev05_shelf_status']=='PENDING_USER_ARCHITECTURE_EXCEPTION'
    assert scene.frame_end==960
result={'status':'PASS','masterSHA256':hashlib.sha256(review.read_bytes()).hexdigest(),'sceneCount':3,'packedImages':24,'externalFontDependency':False,'survivingMaterialsAndNodesIdentical':True,'retiredUnreferencedMaterial':sorted(retired),'worldsAndNodesIdentical':True,'packedImagePayloadsAndColorSpacesIdentical':True,'originalCamerasPlusEightDiagnostics':24,'bannerAbsent':True,'screenBoardAndSmallPosterPreserved':True,'phaseStatus':'PARTIAL_SHOP_EXCEPTION_PENDING','shopInteriorApplied':False,'path':str(review)}
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else []
out=Path(args[0])if args else O/'evidence/shading-and-restored-master.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print('READ_ONLY_RESTORE_AND_SHADING_PASS',flush=True)
