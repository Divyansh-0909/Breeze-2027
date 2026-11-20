import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Matrix,Vector
from array import array
O=Path(__file__).resolve().parents[1];B=O.parent/'crowd-rev15m-aftermovie-models-2026-11-11';P=B/'delivery/Gullyverse-Rev15M-Consistent-Crowd.blend';EXPECTED='87a35df28f750a5a4b2a27aa4a6c2b2ef8476bb7940db90d2badc1e284bf54cc'
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def geometry_sha(mesh):
 a=array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',a);return hashlib.sha256(a.tobytes()).hexdigest()
assert sha(P)==EXPECTED;bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene;assert base['variant']=='REV15M'
history={s.name:tuple(o.name for o in s.objects) for s in bpy.data.scenes};baseline=json.loads((O/'evidence/wall-baseline.json').read_text());baseline={r['name']:r for r in baseline}
house='REV15F / continuous house shell / flush R2 Team facade';repairs='REV15 / REV12 / L2 / localized render repair';painted={house,repairs}
removed={'REV15 / PILOT / Destination plaster wall','REV15 / PILOT / destination foot skirting'}|{o.name for o in base.objects if o.name.startswith('REV15 / PILOT / poster mounting batten')};assert len(removed)==7
posters=[base.objects[f'REV15 / EVENTS clearly labelled placeholder {i}'] for i in range(8)];centres=[]
for o in posters:centres.append(Vector(tuple(sum(b)/2 for b in baseline[o.name]['bounds'])))
columns=[28.30,29.35,32.75,33.80];rows=[7.88,9.00];targets=[Vector((-15.85,columns[i%4],rows[i//4])) for i in range(8)]
posterParts=[o for o in base.objects if (o.name.startswith('REV15 / EVENTS clearly labelled placeholder') or o.name.startswith('REV15 / PILOT / poster')) and o.name not in removed];assert len(posterParts)==72
transforms={}
for ob in posterParts:
 bbox=baseline[ob.name]['bounds'];centre=Vector(tuple(sum(b)/2 for b in bbox));index=min(range(8),key=lambda i:(centre-centres[i]).length_squared);transforms[ob.name]=Matrix.Translation(targets[index])@Matrix.Diagonal((.78,.78,.78,1))@Matrix.Translation(-centres[index]);
heading='REV15 / EVENTS destination heading';headingCentre=Vector(tuple(sum(b)/2 for b in baseline[heading]['bounds']));transforms[heading]=Matrix.Translation(Vector((-15.8245,28.825,9.65)))@Matrix.Diagonal((.8,.8,.8,1))@Matrix.Translation(-headingCentre)
lightNames=['REV15 / Wall practical casing.004','REV15 / Wall practical diffuser.004','REV15 / Poster wall gentle spill.004']
for name in lightNames:transforms[name]=Matrix.Translation(Vector((-2.85,2.6,-1.35)))
s=base.copy();s.name='REV15N / Events on Existing House Wall';s['variant']='REV15N';assert s.collection!=base.collection
for c in list(s.collection.children):s.collection.children.unlink(c)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob)
bpy.context.window.scene=s
if s.use_nodes:
 for n in s.node_tree.nodes:
  if n.type=='R_LAYERS':n.scene=s
oldController=base.objects['REV15M / Team Carousel Controller'];controller=oldController.copy();controller.name='REV15N / Team Carousel Controller';s.collection.objects.link(controller);controller['team_index']=0
group=bpy.data.node_groups['REV15K / painted brick substrate'];palette=[(0,(.095,.075,.055,1)),(.18,(.18,.145,.11,1)),(.48,(.29,.245,.19,1)),(.82,(.43,.37,.29,1)),(1,(.54,.47,.38,1))]
def wall_material(original):
 m=original.copy();m.name='REV15N / warm house brick over '+original.name;n=m.node_tree.nodes;l=m.node_tree.links;out=next(a for a in n if a.type=='OUTPUT_MATERIAL');old=out.inputs['Surface'].links[0].from_socket
 substrate=n.new('ShaderNodeGroup');substrate.node_tree=group;substrate.label='Same masonry scale and relief as Team wall'
 ramp=n.new('ShaderNodeValToRGB');ramp.name='REV15N / warm greige masonry palette';ramp.color_ramp.interpolation='EASE'
 for i,(position,color) in enumerate(palette):
  e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(position);e.position=position;e.color=color
 l.new(substrate.outputs['Height'],ramp.inputs[0]);p=n.new('ShaderNodeBsdfPrincipled');p.inputs['Roughness'].default_value=.91;p.inputs['Specular IOR Level'].default_value=.16;l.new(ramp.outputs['Color'],p.inputs['Base Color']);l.new(substrate.outputs['Normal'],p.inputs['Normal'])
 geo=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');normal=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],xyz.inputs[0]);l.new(geo.outputs['Normal'],normal.inputs[0])
 def op(operation,a,b):
  v=n.new('ShaderNodeMath');v.operation=operation
  for i,val in enumerate([a,b]):
   if isinstance(val,(int,float)):v.inputs[i].default_value=val
   else:l.new(val,v.inputs[i])
  return v.outputs[0]
 bounds=[('X',-16.4,-14.8),('Y',25.2,37.0),('Z',7.199,9.82)];masks=[]
 for axis,low,high in bounds:masks.extend([op('GREATER_THAN',xyz.outputs[axis],low),op('LESS_THAN',xyz.outputs[axis],high)])
 masks.append(op('GREATER_THAN',normal.outputs['X'],.85));mask=masks[0]
 for a in masks[1:]:mask=op('MULTIPLY',mask,a)
 mix=n.new('ShaderNodeMixShader');mix.name='REV15N / only the existing Events house facade';l.new(mask,mix.inputs[0]);l.new(old,mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);return m
copies={};shared=[];geometry={};matNames=[]
for ob in base.objects:
 if ob.name in removed or ob==oldController:continue
 if ob.get('artKind'):
  a=ob.copy();a.name=ob.name.replace('REV15M /','REV15N /',1);a.animation_data_clear();s.collection.objects.link(a)
  for prop in ['hide_render','hide_viewport']:
   d=a.driver_add(prop).driver;v=d.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=controller;v.targets[0].data_path='["team_index"]';d.expression=f'index != {a["carouselSlide"]}'
 elif ob.name in painted:
  a=ob.copy();a.data=ob.data.copy();a.name='REV15N / '+('Existing Events house shell' if ob.name==house else 'Events house render repairs');s.collection.objects.link(a);copies[ob.name]=a;geometry[ob.name]=geometry_sha(ob.data)
  for i,mat in enumerate(a.data.materials):
   if mat.name in ['WORLD / mineral concrete','WORLD / warm grey limewash','WORLD / faded blue-green plaster','WORLD / muted ochre plaster','WORLD / localized render repair']:
    new=wall_material(mat);a.data.materials[i]=new;matNames.append(new.name)
 elif ob.name in transforms:
  a=ob.copy();a.name='REV15N / '+ob.name.removeprefix('REV15 / ');s.collection.objects.link(a);a.matrix_world=transforms[ob.name]@ob.matrix_world;copies[ob.name]=a
  if ob.name==heading:a.data=ob.data.copy();a.data.body='EVENTS'
 else:s.collection.objects.link(ob);shared.append(ob)
layer=s.view_layers.new('REV15N / Current world')
for old in list(s.view_layers):
 if old!=layer:s.view_layers.remove(old)
bpy.context.window.view_layer=layer
if s.use_nodes:
 for n in s.node_tree.nodes:
  if n.type=='R_LAYERS':n.layer=layer.name
s.frame_set(1);layer.update()
checks={'all43HistoricalSceneMembershipsExact':all(tuple(o.name for o in bpy.data.scenes[name].objects)==objects for name,objects in history.items()),'existingHouseGeometryExact':all(geometry_sha(copies[name].data)==value for name,value in geometry.items()),'noSeparateEventsWall':not any(name in s.objects for name in removed),'noNewWallGeometry':sum(o.type=='MESH' for o in s.objects)==sum(o.type=='MESH' for o in base.objects)-7,'sameTeamMasonryGroup':all(any(n.type=='GROUP' and n.node_tree==group for n in bpy.data.materials[name].node_tree.nodes) for name in matNames),'all189CrowdObjectsShared':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in shared)==189,'allUnrelatedObjectsShared':all(s.objects[o.name]==o for o in shared),'TeamBlackWallUnchanged':s.objects['REV15K / Team wall black-painted brick finish']==base.objects['REV15K / Team wall black-painted brick finish'],'allEightPosterImagesRetained':all(copies[p.name].data==p.data for p in posters),'wallLightPowerUnchanged':copies[lightNames[2]].data==base.objects[lightNames[2]].data,'sameWorldAndColorManagement':s.world==base.world and s.view_settings.view_transform==base.view_settings.view_transform,'LEDRetained':s.frame_end==10676 and s.objects['REV15L / animated sponsor LED face']['minimumLogoGapCells']==72}
for i,p in enumerate(posters):
 a=copies[p.name];world=[a.matrix_world@v.co for v in a.data.vertices];centre=sum(world,Vector())/len(world);checks[f'poster{i}MountedOnHouse']=abs(centre.x+15.85)<.0001 and abs(centre.y-targets[i].y)<.0001 and abs(centre.z-targets[i].z)<.0001
for index in range(8):
 controller['team_index']=index;controller.update_tag();layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'mural{index}Exclusive']=len(active)==1 and active[0]['carouselSlide']==index
controller['team_index']=0;controller.update_tag();layer.update();assert all(checks.values()),checks
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;target=O/'delivery/Gullyverse-Rev15N-Events-House-Wall.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True);checks['baseMasterUnchanged']=sha(P)==EXPECTED
manifest={'version':'REV15N','design':'Use only the existing L2 house facade at Events beside the cypher; no black wall or separate plaster display','existingHouseObject':copies[house].name,'houseGeometrySHA256':geometry[house],'facadeBounds':{'x':[-16.4,-14.8],'y':[25.2,37.0],'z':[7.199,9.82]},'worldNormalXMinimum':.85,'palette':palette,'masonryGroup':group.name,'removedFromCurrentScene':sorted(removed),'mountedPosters':[copies[p.name].name for p in posters],'posterCentres':[list(v) for v in targets],'posterUniformScale':.78,'movedObjects':{old:new.name for old,new in copies.items() if old in transforms},'paintedObjects':[copies[n].name for n in painted],'materials':matNames,'architecturalOpenings':'Existing windows, doors, frames, rails and upper stories retained'}
(O/'evidence/wall-manifest.json').write_text(json.dumps(manifest,indent=2));(O/'evidence/blender-validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':sha(target),'masterBytes':target.stat().st_size,'baseSHA256':EXPECTED,'sceneCount':len(bpy.data.scenes)},indent=2));print('EVENTS HOUSE WALL SAVED',flush=True)
