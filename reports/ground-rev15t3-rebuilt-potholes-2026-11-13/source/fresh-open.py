import bpy,json,hashlib,math,argparse,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--restored',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);restored=a.restored
if restored:
 proof=json.loads((R/'evidence/restore-check.json').read_text());b['editedMaster']=proof['restoredMaster'];b['editedSHA256']=proof['restoredSHA256']
assert sha(b['editedMaster'])==b['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();floors=[o for o in s.objects if o.get('groundSurface')];assert len(floors)==4;trees=[BVHTree.FromObject(o,deps) for o in floors]
def hit(x,y):
 points=[p for t in trees for p,_,_,_ in [t.ray_cast(Vector((x,y,25)),Vector((0,0,-1)),50)] if p is not None];return max((p.z for p in points),default=None)
def grade(y):return 6 if y<=-10 else 6+.05*(y+10) if y<14 else 7.2
for y in [-29,-20,-10,-5,0,5,9,14,20,25,35,47]:
 for x in [-1.4,0,1.4]:assert abs(hit(x,y)-grade(y))<.0002
for i in range(64):
 a=math.tau*i/64
 for r in [0,2,4.5]:assert abs(hit(-5.1+math.cos(a)*r,25+math.sin(a)*r)-7.2)<.0002
water=[o for o in s.objects if o.name.startswith('REV15T3 / edge pool ')];assert len(water)==16
for o in water:
 for v in o.data.vertices:
  p=o.matrix_world@v.co;z=hit(p.x,p.y);assert z is not None and 0<p.z-z<.12,(o.name,list(p),z,p.z-z);assert abs(p.x)>1.4;assert math.hypot(p.x+5.1,p.y-25)>4.65
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
assert all(o.hide_render for o in s.objects if 'Cypher chalk arc' in o.name)
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
assert len([o for o in s.objects if o.get('artKind')])==8
assert sha(b['source'])==b['sourceSHA256']

for hole in b['rebuiltPotholes']:
 h=hole['hole'];z=hit(h['x'],h['y']);assert abs(z-(grade(h['y'])-hole['depthMetres']*1.03))<.0003,(h['id'],z)
assert all(o.hide_render for o in s.objects if 'batched loose aggregate' in o.name or 'shallow damp pocket' in o.name)
ponds=[o for o in s.objects if o.name.startswith('REV15T3 / Recessed pothole water ')];assert len(ponds)==4
for o in ponds:
 assert .04 < o['belowRoadMetres'] < .07
 for v in o.data.vertices: assert v.co.z>hit(v.co.x,v.co.y)+.0003,(o.name,list(v.co),hit(v.co.x,v.co.y))
for floor in floors:
 assert all(f.normal.z>-.0001 for f in floor.data.polygons if f.material_index>=2),'Folded fracture face'
out={'status':'PASS','freshNativeOpen':True,'nativeMasterSHA256':b['editedSHA256'],'nativeScenes':len(bpy.data.scenes),'packedImages':sum(bool(im.packed_file) for im in bpy.data.images),'routeGradeChecks':36,'flatCypherChecks':192,'edgePoolVerticesChecked':sum(len(o.data.vertices) for o in water),'edgePoolsInsideFloorAndOutsideProtectedRoute':True,'sourceMasterUnchanged':True,'circleHidden':True,'crowdCount':189,'muralStates':8,'nativeRayReflections':s.eevee.use_raytracing,'rebuiltPotholes':16,'recessedWaterPockets':4,'oldPyramidScatterHidden':True,'noInvertedFractureFaces':True}
(R/('evidence/restored-fresh-open.json' if restored else 'evidence/fresh-open.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
