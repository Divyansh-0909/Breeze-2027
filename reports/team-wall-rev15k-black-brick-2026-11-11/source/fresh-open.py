import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1]
P=O/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
v=json.loads((O/'evidence/blender-validation.json').read_text())
assert hashlib.sha256(P.read_bytes()).hexdigest()==v['masterSHA256']
bpy.ops.wm.open_mainfile(filepath=str(P))
s=bpy.context.scene;controller=s.objects['REV15K / Team Carousel Controller']
checks={'41Scenes':len(bpy.data.scenes)==41,'activeRev15K':s.get('variant')=='REV15K','defaultOC':controller['team_index']==0,'noLinkedLibraries':len(bpy.data.libraries)==0,'allFileImagesPacked':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'originalLightsRetained':all(bpy.data.objects[n].data.energy==e for n,e in v['lightEnergies'].items())}
for i in range(8):
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'slide{i}Exclusive']=len(active)==1 and active[0]['carouselSlide']==i
assert all(checks.values()),checks
(O/'evidence/fresh-open.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':v['masterSHA256']},indent=2));print(json.dumps(checks),flush=True)
