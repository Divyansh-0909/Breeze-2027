import bpy,json,hashlib
from pathlib import Path
from array import array
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15N-Events-House-Wall.blend';V=json.loads((O/'evidence/blender-validation.json').read_text());M=json.loads((O/'evidence/wall-manifest.json').read_text())
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def geometry_sha(mesh):
 a=array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert sha(P)==V['masterSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();base=next(x for x in bpy.data.scenes if x.get('variant')=='REV15M');controller=s.objects['REV15N / Team Carousel Controller'];old=base.objects['REV15M / Team Carousel Controller'];indexBefore=old['team_index']
checks={'44Scenes':len(bpy.data.scenes)==44,'activeRev15N':s['variant']=='REV15N','allImagesPacked':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'noLinkedLibraries':len(bpy.data.libraries)==0,'sameExistingHouseGeometry':geometry_sha(s.objects[M['existingHouseObject']].data)==M['houseGeometrySHA256'],'noFreestandingDisplay':all(name not in s.objects for name in M['removedFromCurrentScene']),'all189CrowdRetained':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189,'defaultOC':controller['team_index']==0,'TeamBlackWallRetained':s.objects['REV15K / Team wall black-painted brick finish']==base.objects['REV15K / Team wall black-painted brick finish'],'onlyLowerHouseFacade':M['facadeBounds']['z']==[7.199,9.82]}
openings=json.loads((O/'evidence/house-openings.json').read_text())
for i,name in enumerate(M['mountedPosters']):
 ob=s.objects[name];v=[ob.matrix_world@p.co for p in ob.data.vertices];centre=sum(v,Vector())/len(v);target=Vector(M['posterCentres'][i]);checks[f'poster{i}AtHouseSurface']=(centre-target).length<.0001;checks[f'poster{i}Visible']=ob.visible_get();ymin,ymax=min(p.y for p in v),max(p.y for p in v);checks[f'poster{i}ClearOfOpenings']=all(ymax<r['bounds'][1][0]-.05 or ymin>r['bounds'][1][1]+.05 for r in openings);checks[f'poster{i}BelowBalconyBeam']=max(p.z for p in v)<9.82
for name in M['materials']:
 mat=bpy.data.materials[name];ramp=mat.node_tree.nodes['REV15N / warm greige masonry palette'];checks['nonBlackPalette / '+name]=min(sum(e.color[:3]) for e in ramp.color_ramp.elements)>.2
node=s.objects['REV15L / animated sponsor LED face'].data.materials[0].node_tree.nodes['LED scroll cells']
for frame,value in [(1,0),(2,1),(10677,0)]:s.frame_set(frame);bpy.context.view_layer.update();checks[f'LEDLoop{frame}']=abs(node.outputs[0].default_value-value)<1e-5
for index in range(8):
 controller['team_index']=index;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{index}Exclusive']=len(active)==1 and active[0]['carouselSlide']==index
checks['previousControllerIndependent']=old['team_index']==indexBefore;assert all(checks.values()),checks
(O/'evidence/fresh-open.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':V['masterSHA256']},indent=2));print('FRESH HOUSE-WALL CHECKS PASS',flush=True)
