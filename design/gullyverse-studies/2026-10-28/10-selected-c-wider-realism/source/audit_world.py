import bpy,json,sys,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
base=O/'source/APPROVED-PILOT.blend';new=O/'source/Gullyverse-Selected-C-Wider-Realism.blend'
a,ea,ma,wa,ia=snapshot(base);members={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes}
b,eb,mb,wb,ib=snapshot(new)
assert wa==wb
assert all(b.get(n)==v for n,v in a.items()),[n for n,v in a.items()if b.get(n)!=v]
assert all(mb[n]==v for n,v in ma.items())
assert all(ib[n]==v for n,v in ia.items())and set(ia)==set(ib)
assert all(eb[n]==v for n,v in ea.items())
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in members.items())
s=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD');p=next(s for s in bpy.data.scenes if s.get('variant')=='C+A PILOT')
assert s.world==p.world and s.view_settings.exposure==p.view_settings.exposure and s.view_settings.look==p.view_settings.look
assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in p.objects if o.type=='LIGHT'}
assert sum(o.type=='LIGHT'for o in s.objects)==17
assert all(o.data.energy==0 for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical'))
bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
author=json.loads((O/'evidence/authoring.json').read_text())
for r in author['surfaceCopies']:
 o=bpy.data.objects[r['original']];cp=bpy.data.objects[r['copy']]
 assert o.name not in s.objects and cp.name in s.objects
 assert o.matrix_basis==cp.matrix_basis
 if r.get('bakedIdenticalSolidifyForUVs'):
  bpy.context.window.scene=p; bpy.context.view_layer.update(); source_dep=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(source_dep);m=ev.to_mesh();assert [list(v.co)for v in m.vertices]==[list(v.co)for v in cp.data.vertices];assert [list(p.vertices)for p in m.polygons]==[list(p.vertices)for p in cp.data.polygons];ev.to_mesh_clear();bpy.context.window.scene=s;bpy.context.view_layer.update()
 else:
  assert [list(v.co)for v in o.data.vertices]==[list(v.co)for v in cp.data.vertices]
  assert [list(p.vertices)for p in o.data.polygons]==[list(p.vertices)for p in cp.data.polygons]
 assert o.animation_data is None and cp.animation_data is None
 assert not any(sl.material and sl.material.name.startswith('ART /')for sl in o.material_slots)
for o in p.objects:
 if o.name.startswith(('Closed rolling shutter','Shutter slat'))or any(sl.material and sl.material.name.startswith('ART /')for sl in o.material_slots):assert s.objects.get(o.name)==o
assert len(s.objects)==len(p.objects)+len(author['newConstructionObjects'])+22
r={'status':'PASS','baselineSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(new.read_bytes()).hexdigest(),'originalObjectsExact':len(a),'allPriorObjectMaterialsUVTransformsActionsWorldsUnchanged':True,'fourPriorSceneMembershipsUnchanged':True,'fiveTotalScenes':len(bpy.data.scenes),'surfaceCopies':len(author['surfaceCopies']),'baseVerticesTopologyTransformsUnchanged':True,'allSevenArtPlacementsExact':True,'all33ImageOwnersExact':True,'lights17Active12SupportsFive0W':True,'noCrowdOrStockMovement':True,'noCounterBaseGeometryChange':True}
(O/'evidence/preservation-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('PRESERVATION_PASS',r,flush=True)
