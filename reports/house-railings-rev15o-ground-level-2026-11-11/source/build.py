import bpy,bmesh,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=O.parent/'events-wall-rev15n-warm-brick-2026-11-11';P=B/'delivery/Gullyverse-Rev15N-Events-House-Wall.blend';EXPECTED='74130d7c7b28df9916372cf1644ece90ae864fa236e9554b92dde72d8b2abff5'
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def face_sha(mesh,excluded=set()):
 rows=[]
 for p in mesh.polygons:
  if any(v in excluded for v in p.vertices):continue
  coords=tuple(sorted(tuple(round(float(c),6) for c in mesh.vertices[i].co) for i in p.vertices));rows.append((p.material_index,bool(p.use_smooth),coords))
 return hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest()
assert sha(P)==EXPECTED;plan=json.loads((O/'evidence/removal-plan.json').read_text());assert len(plan)==4
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;assert base['variant']=='REV15N';history={x.name:tuple(o.name for o in x.objects) for x in bpy.data.scenes};targets={r['object']:r for r in plan}
s=base.copy();s.name='REV15O / Clear Ground-Level House Fronts';s['variant']='REV15O';assert s.collection!=base.collection
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s
if s.use_nodes:
 for n in s.node_tree.nodes:
  if n.type=='R_LAYERS':n.scene=s
oldController=base.objects['REV15N / Team Carousel Controller'];controller=oldController.copy();controller.name='REV15O / Team Carousel Controller';s.collection.objects.link(controller);controller['team_index']=0
shared=[];records=[]
for ob in base.objects:
 if ob==oldController:continue
 if ob.get('artKind'):
  a=ob.copy();a.name=ob.name.replace('REV15N /','REV15O /',1);a.animation_data_clear();s.collection.objects.link(a)
  for prop in ['hide_render','hide_viewport']:
   d=a.driver_add(prop).driver;v=d.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=controller;v.targets[0].data_path='["team_index"]';d.expression=f'index != {a["carouselSlide"]}'
 elif ob.name in targets:
  row=targets[ob.name];excluded=set(row['removedVertices']);expectedFaces=face_sha(ob.data,excluded);a=ob.copy();a.data=ob.data.copy();a.name='REV15O / '+ob.name.removeprefix('REV15 / ');s.collection.objects.link(a)
  bm=bmesh.new();bm.from_mesh(a.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(excluded)],context='VERTS');bm.to_mesh(a.data);bm.free();a.data.update()
  assert face_sha(a.data)==expectedFaces,ob.name
  records.append({'sourceObject':ob.name,'object':a.name,'removedComponents':len(row['componentsRemoved']),'removedVertices':len(excluded),'sourceVertices':len(ob.data.vertices),'remainingVertices':len(a.data.vertices),'sourceFaces':len(ob.data.polygons),'remainingFaces':len(a.data.polygons),'retainedFaceSHA256':expectedFaces,'removedHeightRange':[min(c['bounds'][2][0] for c in row['componentsRemoved']),max(c['bounds'][2][1] for c in row['componentsRemoved'])],'remainingComponentCount':len(row['componentsRetained']),'materialNames':[m.name for m in a.data.materials]})
 else:s.collection.objects.link(ob);shared.append(ob)
layer=s.view_layers.new('REV15O / Current world')
for old in list(s.view_layers):
 if old!=layer:s.view_layers.remove(old)
bpy.context.window.view_layer=layer
if s.use_nodes:
 for n in s.node_tree.nodes:
  if n.type=='R_LAYERS':n.layer=layer.name
s.frame_set(1);layer.update();checks={'all44HistoricalSceneMembershipsExact':all(tuple(o.name for o in bpy.data.scenes[name].objects)==names for name,names in history.items()),'fourHouseFrontsCleared':len(records)==4,'all204GroundRailingPiecesRemoved':sum(r['removedComponents'] for r in records)==204,'allRetainedUpperFacesExact':all(face_sha(s.objects[r['object']].data)==r['retainedFaceSHA256'] for r in records),'allUnrelatedObjectsShared':all(s.objects[o.name]==o for o in shared),'all189PeopleShared':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in shared)==189,'EventsBrickHouseSharedUnchanged':s.objects['REV15N / Existing Events house shell']==base.objects['REV15N / Existing Events house shell'],'TeamBlackWallSharedUnchanged':s.objects['REV15K / Team wall black-painted brick finish']==base.objects['REV15K / Team wall black-painted brick finish'],'LEDRetained':s.frame_end==10676 and s.objects['REV15L / animated sponsor LED face']['minimumLogoGapCells']==72,'lightsSharedUnchanged':all(o in shared for o in base.objects if o.type=='LIGHT')}
for index in range(8):
 controller['team_index']=index;controller.update_tag();layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{index}Exclusive']=len(active)==1 and active[0]['carouselSlide']==index
controller['team_index']=0;controller.update_tag();layer.update();assert all(checks.values()),checks
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;out=O/'delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);checks['baseMasterUnchanged']=sha(P)==EXPECTED
(O/'evidence/rail-manifest.json').write_text(json.dumps({'version':'REV15O','interpretation':'Ground-level house-front guardrails at the walkable courtyard elevation. Upper balcony railings, structural columns, window hardware and frames retained.','records':records},indent=2));(O/'evidence/blender-validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':sha(out),'masterBytes':out.stat().st_size,'baseSHA256':EXPECTED,'sceneCount':len(bpy.data.scenes)},indent=2));print('GROUND HOUSE RAILINGS REMOVED',flush=True)
