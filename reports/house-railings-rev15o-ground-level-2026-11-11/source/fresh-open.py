import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O/'delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend';V=json.loads((O/'evidence/blender-validation.json').read_text());M=json.loads((O/'evidence/rail-manifest.json').read_text())
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def face_sha(mesh):
 rows=[]
 for p in mesh.polygons:
  coords=tuple(sorted(tuple(round(float(c),6) for c in mesh.vertices[i].co) for i in p.vertices));rows.append((p.material_index,bool(p.use_smooth),coords))
 return hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest()
assert sha(P)==V['masterSHA256'];bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();base=next(x for x in bpy.data.scenes if x.get('variant')=='REV15N');controller=s.objects['REV15O / Team Carousel Controller'];old=base.objects['REV15N / Team Carousel Controller'];oldIndex=old['team_index']
checks={'45Scenes':len(bpy.data.scenes)==45,'activeRev15O':s['variant']=='REV15O','allImagesPacked':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'noLinkedLibraries':len(bpy.data.libraries)==0,'defaultOC':controller['team_index']==0,'all189CrowdRetained':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189,'EventsHouseAndBrickShared':s.objects['REV15N / Existing Events house shell']==base.objects['REV15N / Existing Events house shell'],'TeamBlackWallShared':s.objects['REV15K / Team wall black-painted brick finish']==base.objects['REV15K / Team wall black-painted brick finish'],'all204RailPiecesRemoved':sum(r['removedComponents'] for r in M['records'])==204}
for r in M['records']:
 o=s.objects[r['object']];checks['retainedFacesExact / '+o.name]=face_sha(o.data)==r['retainedFaceSHA256'];checks['noLowRailGeometry / '+o.name]=min((o.matrix_world@v.co).z for v in o.data.vertices)>8.36;checks['visible / '+o.name]=o.visible_get();checks['sourceRailMeshAbsent / '+o.name]=r['sourceObject'] not in s.objects
node=s.objects['REV15L / animated sponsor LED face'].data.materials[0].node_tree.nodes['LED scroll cells']
for frame,value in [(1,0),(2,1),(10677,0)]:s.frame_set(frame);bpy.context.view_layer.update();checks[f'LEDLoop{frame}']=abs(node.outputs[0].default_value-value)<1e-5
for index in range(8):
 controller['team_index']=index;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{index}Exclusive']=len(active)==1 and active[0]['carouselSlide']==index
checks['previousControllerIndependent']=old['team_index']==oldIndex;assert all(checks.values()),checks
(O/'evidence/fresh-open.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':V['masterSHA256']},indent=2));print('FRESH RAILING CHECKS PASS',flush=True)
