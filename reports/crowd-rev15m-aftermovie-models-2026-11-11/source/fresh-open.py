import bpy,json,hashlib,re
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';V=json.loads((O/'evidence/blender-validation.json').read_text());R=json.loads((O/'evidence/replacements.json').read_text())
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
assert sha(P)==V['masterSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();base=next(x for x in bpy.data.scenes if x.get('variant')=='REV15L1');controller=s.objects['REV15M / Team Carousel Controller'];old=base.objects['REV15L / Team Carousel Controller'];oldIndex=old['team_index']
checks={'43Scenes':len(bpy.data.scenes)==43,'activeRev15M':s['variant']=='REV15M','allImagesPacked':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'noLinkedLibraries':len(bpy.data.libraries)==0,'original180AudienceRetained':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') and not o.name.startswith('REV15M /') for o in s.objects)==180,'nineReplacementModels':len(R)==9,'noOldProxyParts':not any(re.match(r'^(REV15 / Cypher silhouette \d+|Distant lane crowd glimpse \d+) ',o.name) for o in s.objects),'independentCompositor':s.node_tree!=base.node_tree,'defaultOC':controller['team_index']==0}
for r in R:
 ob=s.objects[r['object']];z=min((ob.matrix_world@v.co).z for v in ob.data.vertices);checks['ground / '+ob.name]=abs(z-r['footZ'])<1e-4;checks['visible / '+ob.name]=ob.visible_get();checks['sourceMesh / '+ob.name]=ob.data.name==r['mesh']
node=s.objects['REV15L / animated sponsor LED face'].data.materials[0].node_tree.nodes['LED scroll cells']
for frame,value in [(1,0),(2,1),(10677,0)]:s.frame_set(frame);bpy.context.view_layer.update();checks[f'LEDLoop{frame}']=abs(node.outputs[0].default_value-value)<1e-5
for index in range(8):
 controller['team_index']=index;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{index}Exclusive']=len(active)==1 and active[0]['carouselSlide']==index
checks['previousControllerIndependent']=old['team_index']==oldIndex;assert all(checks.values()),checks
(O/'evidence/fresh-open.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':V['masterSHA256']},indent=2));print('FRESH OPEN CHECKS PASS',flush=True)
