import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(O/'delivery/Gullyverse-Rev15J1-Full-Heading.blend'))
s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15J1')
bpy.context.window.scene=s
controller=s.objects['REV15J1 / Team Carousel Controller']
order=json.loads(s['carouselOrder'])
checks={'40Scenes':len(bpy.data.scenes)==40,'original39ScenesRetained':len([s for s in bpy.data.scenes if s.get('variant')!='REV15J1'])==39,'defaultOC':int(controller['team_index'])==0 and order[0]=='Organising Committee','eightTeamsNoCoordinators':len(order)==8 and 'Coordinators' not in order,'noLinkedLibraries':len(bpy.data.libraries)==0,'allFileImagesPacked':all(im.packed_file for im in bpy.data.images if im.source=='FILE')}
for i in range(8):
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update()
 active=[o for o in s.objects if o.get('artKind') and not o.hide_render]
 checks[f'slide{i}Exclusive']=bool(active) and all(o['carouselSlide']==i for o in active)
result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks}
(O/'evidence/fresh-open.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2),flush=True)
assert all(checks.values())
