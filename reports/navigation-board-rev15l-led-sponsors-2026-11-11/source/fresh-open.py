import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15L-Navigation-LED.blend';v=json.loads((O/'evidence/blender-validation.json').read_text());assert hashlib.sha256(P.read_bytes()).hexdigest()==v['masterSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
logos=json.loads((O/'evidence/sponsors.json').read_text());controller=s.objects['REV15L / Team Carousel Controller'];old=bpy.data.objects['REV15K / Team Carousel Controller'];old_index=old['team_index']
checks={'42Scenes':len(bpy.data.scenes)==42,'activeREV15L':s.get('variant')=='REV15L','defaultOC':controller['team_index']==0,'noLinkedLibraries':len(bpy.data.libraries)==0,'allFileImagesPacked':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'allLogosInPeriod':s.frame_end==logos['periodCells']}
node=s.objects['REV15L / animated sponsor LED face'].data.materials[0].node_tree.nodes['LED scroll cells']
for frame,expected in [(1,0),(2,1),(logos['periodCells']+1,0)]:s.frame_set(frame);bpy.context.view_layer.update();checks[f'loopFrame{frame}']=abs(node.outputs[0].default_value-expected)<1e-5
for i in range(8):controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{i}Exclusive']=len(active)==1 and active[0]['carouselSlide']==i
checks['previousMuralControllerIndependent']=old['team_index']==old_index
assert all(checks.values()),checks
(O/'evidence/fresh-open.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':v['masterSHA256']},indent=2));print(json.dumps(checks),flush=True)
