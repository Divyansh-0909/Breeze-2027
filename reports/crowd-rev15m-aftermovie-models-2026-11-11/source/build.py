import bpy,json,hashlib,math,re
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parents[1];B=O.parent/'navigation-board-rev15l1-logo-spacing-2026-11-11';P=B/'delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend'
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
expected='64e464166f0c1bef53c145843399807e6edd95ee3900f5c0de1c04504e09b1ee';assert sha(P)==expected
plan=json.loads((O/'evidence/replacement-plan.json').read_text());bank=json.loads((O/'evidence/reference-bank.json').read_text())['bank'];assert len(plan)==9
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;assert base['variant']=='REV15L1'
history={x.name:sorted(o.name for o in x.objects) for x in bpy.data.scenes};sourceLights={o.name:o.data.energy for o in base.objects if o.type=='LIGHT'}
sources=[o for o in base.objects if o.type=='MESH' and o.data.name.startswith('REV13A shared')];assert len(sources)==180
protected={o.name:(o.data.name,tuple(tuple(v) for v in o.matrix_world)) for o in sources}
removed={n for row in plan for n in row['parts']};assert len(removed)==72
s=base.copy();s.name='REV15M / Aftermovie Characters Throughout';s['variant']='REV15M';assert s.collection!=base.collection
for collection in list(s.collection.children):s.collection.children.unlink(collection)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s
if s.use_nodes:
 for node in s.node_tree.nodes:
  if node.type=='R_LAYERS':node.scene=s
oldController=base.objects['REV15L / Team Carousel Controller'];controller=oldController.copy();controller.name='REV15M / Team Carousel Controller';s.collection.objects.link(controller);controller['team_index']=0
shared=[]
for ob in base.objects:
 if ob.name in removed or ob==oldController:continue
 if ob.get('artKind'):
  n=ob.copy();n.name=ob.name.replace('REV15L /','REV15M /',1);n.animation_data_clear();s.collection.objects.link(n)
  for prop in ['hide_render','hide_viewport']:
   d=n.driver_add(prop).driver;v=d.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=controller;v.targets[0].data_path='["team_index"]';d.expression=f'index != {n["carouselSlide"]}'
 else:s.collection.objects.link(ob);shared.append(ob)
archetypes=['hoodie-tapered-jeans','open-overshirt-wide-trousers','box-tee-straight-jeans','sweatshirt-relaxed-trousers','long-sleeve-cargos','oversized-tee-cargos','overshirt-slim-jeans','cropped-jacket-wide-jeans','sweatshirt-cargos'];preferred=['relaxed','one-hand-pocket','folded-arms','weight-shift','hands-together','phone-record'];replacements=[]
for i,row in enumerate(plan):
 choices=[r for r in bank if r['archetype']==archetypes[i]];desired=['one-hand-pocket','relaxed','folded-arms','hands-together','weight-shift','folded-arms','one-hand-pocket','weight-shift','phone-record'][i];reference=next((r for r in choices if r['pose']==desired),min(choices,key=lambda r:preferred.index(r['pose'])));mesh=bpy.data.meshes[reference['LOD0']];assert len(mesh.vertices)>4000
 ob=bpy.data.objects.new(f'REV15M / {"Lane" if i<3 else "Cypher"} character {i:02d}',mesh);s.collection.objects.link(ob)
 x,y=row['anchor'];surface=row['ground'][0];ground=surface['z'];height=row['standingHeight'];scale=height/(reference['localMaxZ']-reference['localMinZ']);ob.scale=(scale,scale,scale);ob.location=(x,y,ground-reference['localMinZ']*scale)
 ob.rotation_euler.z=[-.10,.13,-.18][i] if i<3 else math.atan2(-(-6.25-x),23.3-y)
 ob.matrix_world=Matrix.Translation(ob.location) @ ob.rotation_euler.to_matrix().to_4x4() @ Matrix.Diagonal((*ob.scale,1.0))
 for key,value in {'crowdStyle':'Existing Aftermovie REV13A','archetype':reference['archetype'],'poseFamily':reference['pose'],'sourceAftermovieObject':reference['object'],'sourceMesh':mesh.name,'originalProxy':row['proxy'],'footZ':ground,'standingHeightM':height,'reviewLOD':0}.items():ob[key]=value
 replacements.append({'object':ob.name,'originalProxy':row['proxy'],'replacedParts':row['parts'],'anchorXY':[x,y],'originalProxyFootZ':row['originalFeet'],'footZ':ground,'groundObject':surface['object'],'heightM':height,'referenceObject':reference['object'],'mesh':mesh.name,'archetype':reference['archetype'],'pose':reference['pose'],'scale':scale,'yaw':ob.rotation_euler.z})
layer=s.view_layers.new('REV15M / Current world')
for previousLayer in list(s.view_layers):
 if previousLayer!=layer:s.view_layers.remove(previousLayer)
bpy.context.window.view_layer=layer
if s.use_nodes:
 for node in s.node_tree.nodes:
  if node.type=='R_LAYERS':node.layer=layer.name
s.frame_set(1);layer.update();checks={'all42HistoricalSceneMembershipsExact':all(sorted(o.name for o in bpy.data.scenes[name].objects)==names for name,names in history.items()),'all72ProxyPartsReplaced':all(n not in s.objects for n in removed),'ninePeopleRetainedAtOriginalXY':all(abs(s.objects[r['object']].location.x-r['anchorXY'][0])<1e-5 and abs(s.objects[r['object']].location.y-r['anchorXY'][1])<1e-5 for r in replacements),'allNewMeshesSharedWithAftermovieLibrary':all(s.objects[r['object']].data==bpy.data.meshes[r['mesh']] for r in replacements),'original180AudienceUnchanged':all(s.objects[n].data.name==data and tuple(tuple(v) for v in s.objects[n].matrix_world)==matrix for n,(data,matrix) in protected.items()),'allUnrelatedObjectsShared':all(s.objects[o.name]==o for o in shared),'originalLightEnergiesExact':all(s.objects[n].data.energy==v for n,v in sourceLights.items()),'LEDGapAndPeriodRetained':s.frame_end==10676 and s.objects['REV15L / animated sponsor LED face']['minimumLogoGapCells']==72,'allFileImagesPacked':all(im.packed_file for im in bpy.data.images if im.source=='FILE')}
for r in replacements:
 ob=s.objects[r['object']];minZ=min((ob.matrix_world@v.co).z for v in ob.data.vertices);checks['feetOnGround / '+ob.name]=abs(minZ-r['footZ'])<1e-4;checks['visible / '+ob.name]=ob.visible_get(view_layer=layer)
for i in range(8):
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{i}Exclusive']=len(active)==1 and active[0]['carouselSlide']==i
controller['team_index']=0;controller.update_tag();bpy.context.view_layer.update();assert all(checks.values()),checks
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;out=O/'delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);checks['baseMasterUnchanged']=sha(P)==expected
(O/'evidence/replacements.json').write_text(json.dumps(replacements,indent=2));(O/'evidence/blender-validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'sceneCount':len(bpy.data.scenes),'activeScene':s.name,'masterSHA256':sha(out),'masterBytes':out.stat().st_size,'baseSHA256':expected,'sourceAudience':180,'replacedPeople':9,'newVisibleCrowd':189},indent=2));print('CONSISTENT CROWD SAVED',flush=True)
