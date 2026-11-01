import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
P=O/'inputs/Rev11-original.blend';assert hashlib.sha256(P.read_bytes()).hexdigest()=='b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd'
signature=json.loads(json.dumps(snapshot(P)));source=json.loads((O/'baseline/evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='REV11');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();core=s.objects[source['newMeshes'][0]];v=[core.matrix_basis@p.co for p in core.data.vertices];tree=BVHTree.FromPolygons(v,[tuple(p.vertices)for p in core.data.polygons]);rows=[]
def point(h,u,d,z):
 c=sum(h['alongM'])/2;f=h['frontM'];e=h['edge'];return Vector((-f-d,c+u,z))if e=='left'else Vector((f+d,c-u,z))if e=='right'else Vector((c-u,f-d,z))if e=='front'else Vector((c+u,f+d,z))
for h in source['houses']:
 q=point(h,-h['widthM']*.20,(max(h['setbacksM'])+h['depthM'])/2,h['mainRoofZ']+1);hits=[]
 while q.z>6.8:
  hit=tree.ray_cast(q,Vector((0,0,-1)),q.z-6.8)
  if hit[0]is None:break
  if hit[1].z>.99 and hit[0].z<h['mainRoofZ']-.05:hits.append(hit[0].z)
  q=hit[0]-Vector((0,0,.005))
 levels=sorted({round(z,3)for z in hits});assert len(levels)==h['upperLevels'],(h['id'],levels,h['upperLevels'])
 rows.append({'id':h['id'],'edge':h['edge'],'geometryOwner':core.name,'baseDatumM':7.2,'actualUpperSlabTopZs':levels,'actualCourtResidentialLevels':len(levels),'lowerSupportLevelsExcluded':[.6,3.9],'mainRoofZ':h['mainRoofZ'],'setbacksM':h['setbacksM'],'frontM':h['frontM'],'depthM':h['depthM'],'widthM':h['widthM'],'hasThreeOrMore':len(levels)>=3,'diagnosticColor':'GREEN'if len(levels)>=3 else'RED','roofUtilitiesExcluded':True,'geometryProbeXY':list(q)[:2]})
(O/'evidence/before-storey-survey.json').write_text(json.dumps({'status':'READ_ONLY_MEASURED_BEFORE_AUTHORING','units':'metres, Z up','parcelCount':11,'threeOrMoreBefore':sum(r['hasThreeOrMore']for r in rows),'rows':rows,'existingRearLightwellFailures':'Six nonpublic samples beyond Y48 from Rev11 retained; not claimed fixed.'},indent=2))
(O/'evidence/source-signatures.json').write_text(json.dumps({'objects':signature[0],'environment':signature[1],'materials':signature[2],'worlds':signature[3],'images':signature[4],'memberships':{s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes}},indent=2));print('BEFORE_COUNT_AUDIT',[(r['id'],r['actualCourtResidentialLevels'],r['actualUpperSlabTopZs'])for r in rows],flush=True)
