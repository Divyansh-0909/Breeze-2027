import bpy, json, hashlib, runpy, argparse, sys
from pathlib import Path
from types import SimpleNamespace

R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot']
fingerprint=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint']
HOST='REV15C / REV15B / REV15 / Entry parapet return'
LABEL='Accommodation wall label'
ap=argparse.ArgumentParser()
ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15X-Accommodation-Coming-Soon.blend')
ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15X1-Accommodation-Clean-Wall.blend')
ap.add_argument('--restore',action='store_true')
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
out=Path(a.output);assert not out.exists(),'Choose a new output filename.'
source_sha=sha(a.base)
bpy.ops.wm.open_mainfile(filepath=a.base)
base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update()
basefp=fingerprint(base)
assert basefp['sha256']=='8214924dd55d741cd2b5abd5cd66d2aff92b1a82aac5483c014ff1070477ada1'
host=base.objects['REV15X / '+HOST];label=base.objects['REV15X / '+LABEL]
unchanged=[o for o in base.objects if o not in [host,label]]
protected=snapshot(SimpleNamespace(objects=unchanged),{'objects':[]},'REV15X / ')
geometry=host.data;matrix=host.matrix_world.copy()
history={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes}
s=base.copy();s.name='REV15X1 / Clean Accommodation wall';s['variant']='REV15X1'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 if old==label:continue
 ob=old.copy();ob.name='REV15X1 / '+old.name.removeprefix('REV15X / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for driver in ob.animation_data.drivers:
   for var in driver.driver.variables:
    for target in var.targets:
     if target.id in copies:target.id=copies[target.id]
layer=s.view_layers.new('REV15X1 / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
clean=host.material_slots[0].material.copy();clean.name='REV15X1 / Existing parapet without supporting graffiti'
tree=clean.node_tree;bs=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED');bypassed=[]
for key in ['Base Color','Roughness','Metallic']:
 dest=bs.inputs[key];assert len(dest.links)==1
 paint=dest.links[0].from_node
 assert paint.type==('MATH'if key=='Metallic'else'MIX_RGB')
 original=paint.inputs[0 if key=='Metallic'else 1]
 src=original.links[0].from_socket if original.is_linked else None
 value=original.default_value
 if hasattr(value,'__len__'):value=list(value)
 for link in list(dest.links):tree.links.remove(link)
 if src:tree.links.new(src,dest)
 else:dest.default_value=value if key=='Base Color'else(value[0]if isinstance(value,list)else value)
 bypassed.append({'input':key,'removedPaintNode':paint.name,'source':src.node.name if src else value})
# Remove disconnected atlas/projection nodes from this new local material only.
needed=set()
def visit(n):
 if n in needed:return
 needed.add(n)
 for inp in n.inputs:
  for link in inp.links:visit(link.from_node)
for node in tree.nodes:
 if node.type=='OUTPUT_MATERIAL':visit(node)
for node in list(tree.nodes):
 if node not in needed:tree.nodes.remove(node)
assert not any(n.type=='TEX_IMAGE'and n.image and 'supporting pieces'in n.image.name for n in tree.nodes)
updated=copies[host];updated.material_slots[0].link='OBJECT';updated.material_slots[0].material=clean
assert updated.data==geometry and updated.matrix_world==matrix
s.camera=copies[base.camera]
s['authorizedChange']='Remove only the blue-purple supporting graffiti on the left Accommodation parapet and the Accommodation label. Preserve COMING/SOON, wall-mounted light and all other art. Contact integration remains a proposal.'
s['userVisualApproval']='PENDING'
bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer
s.frame_set(1);bpy.context.view_layer.update()
assert snapshot(SimpleNamespace(objects=[copies[o]for o in unchanged]),{'objects':[]},'REV15X1 / ')==protected
assert fingerprint(base)['sha256']==basefp['sha256']
assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items())
fp=fingerprint(s);fp.pop('data')
if a.restore:assert fp['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(a.base)==source_sha
proof={'status':'PASS','source':a.base,'sourceSHA256':source_sha,'sourceSceneFingerprint':basefp['sha256'],'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':60,'removedFromActiveScene':['REV15X / '+LABEL],'materialOnlyChange':{'host':updated.name,'material':clean.name,'channelsRestored':bypassed,'hostMeshDataSharedUnchanged':True},'protectedRemainingObjects':protected,'activeObjects':len(s.objects),'packedImages':sum(bool(i.packed_file)for i in bpy.data.images),'sceneFingerprintSHA256':fp['sha256'],'ComingSoonAndLocalLightPreserved':True,'otherGraffitiPreservedIncludingRightParapet':True,'allGeometryUVsTransformsAndLightsPreserved':True,'ContactUs':'DESIGN_PROPOSAL_ONLY','websiteIntegration':'PENDING'}
(R/('evidence/restore-check.json'if a.restore else'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n')
print(json.dumps({'status':'PASS','scenes':len(bpy.data.scenes),'activeObjects':len(s.objects),'protectedObjects':protected['objects']}))
