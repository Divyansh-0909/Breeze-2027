import bpy,json,re
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'navigation-board-rev15l1-logo-spacing-2026-11-11/delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();rows=json.loads((O/'evidence/population-parts.json').read_text());groups={}
for r in rows:
 m=re.match(r'^(REV15 / Cypher silhouette \d+|Distant lane crowd glimpse \d+) ',r['name'])
 if m:groups.setdefault(m.group(1),[]).append(r)
output=[]
for key,parts in sorted(groups.items()):
 head=next(r for r in parts if r['name']==key+' head');x,y=head['loc'][:2];feet=min(r['bounds'][2][0] for r in parts);top=head['bounds'][2][1];hits=[]
 for ob in s.objects:
  if ob.type!='MESH' or ob.data.name.startswith('REV13A shared') or re.match(r'^(REV15 / Cypher silhouette \d+|Distant lane crowd glimpse \d+) ',ob.name):continue
  points=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  if min(p.x for p in points)>x or max(p.x for p in points)<x or min(p.y for p in points)>y or max(p.y for p in points)<y:continue
  inv=ob.matrix_world.inverted_safe();origin=inv@Vector((x,y,feet+.32));direction=inv.to_3x3()@Vector((0,0,-1));hit,loc,normal,index=ob.ray_cast(origin,direction.normalized())
  if hit:
   world=ob.matrix_world@loc
   if feet-.3<world.z<feet+.3:hits.append({'object':ob.name,'z':world.z,'normalZ':(ob.matrix_world.to_3x3()@normal).normalized().z})
 hits=[h for h in hits if h['normalZ']>.7];hits.sort(key=lambda h:abs(h['z']-feet));output.append({'proxy':key,'parts':[r['name'] for r in parts],'anchor':[x,y],'originalFeet':feet,'standingHeight':top-feet,'ground':hits})
(O/'evidence/replacement-plan.json').write_text(json.dumps(output,indent=2));print(json.dumps(output),flush=True)
