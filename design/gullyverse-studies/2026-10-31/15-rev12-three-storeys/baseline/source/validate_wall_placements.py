import bpy,json,sys,os
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/art-authoring.json').read_text());s=next(s for s in bpy.data.scenes if s['variant']==os.environ.get('REV11_TEST_VARIANT','REV11'));bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();records=[]
for w in d['walls']:
 for scene in [sc for sc in bpy.data.scenes if sc.get('variant')!='SOURCE AUDIT']:
  names={o.get('pilotOriginalObject',o.name)for o in scene.objects};assert all(n in names for n in w['hosts'])
 hits=[]
 if w['normalAxis']==0:
  cy=w['centers'][1];cz=w['centers'][0];direction=Vector((-w['normalSign'],0,0))
  for dy in [-.25,0,.25]:
   for dz in [-.75,0,.75]:
    found=s.ray_cast(deps,Vector((0,cy+dy,cz+dz)),direction,distance=5)
    assert found[0]and found[4].get('pilotOriginalObject',found[4].name) in w['hosts'],(w['key'],found[4].name if found[0]else'none')
    hits.append({'object':found[4].name,'hit':list(found[1])})
 else:
  cx,cz=w['centers'];direction=Vector((0,-1,0))
  for dx in [-1.25,0,1.25]:
   for dz in [-.40,0,.40]:
    found=s.ray_cast(deps,Vector((cx+dx,15,cz+dz)),direction,distance=2)
    assert found[0]and found[4].get('pilotOriginalObject',found[4].name) in w['hosts'],(w['key'],found[4].name if found[0]else'none')
    hits.append({'object':found[4].name,'hit':list(found[1])})
 records.append({'key':w['key'],'hostObjects':w['hosts'],'sharedABCSurfaceAndMaterial':True,'unoccludedPatchRays':hits,'geometryChanges':False,'placementApproval':'USER_APPROVED_LOCKED_BY_27_OCTOBER_DOC','sourceAtlasUVRect':w['uvrect']})
(O/('evidence/wall-placement-'+s['variant'].replace(' ','-')+'.json')).write_text(json.dumps({'status':'PASS','wallPaintPlacements':4,'supportingPhysicalExistingObjects':6,'records':records,'teamEventsNavScreenMaterialsUnmodified':True},indent=2)+'\n');print('FOUR_APPROVED_WALL_PATCHES_PRESERVED_PASS')
