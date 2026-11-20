import bpy,json,hashlib,copy
from pathlib import Path
from mathutils import Vector

O=Path(__file__).resolve().parents[1]
B=O.parent/'team-wall-rev15j1-full-heading-2026-11-10'
P=B/'delivery/Gullyverse-Rev15J1-Full-Heading.blend'
BASE_SHA='8360e4894bcdaa3daffb72b9939a22ccabcc0375694064122ccfca3bb6b9ef3b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==BASE_SHA
bpy.ops.wm.open_mainfile(filepath=str(P))
base=next(s for s in bpy.data.scenes if s.get('variant')=='REV15J1')
history={s.name:tuple(s.objects) for s in bpy.data.scenes}
energies={o.name:o.data.energy for o in base.objects if o.type=='LIGHT'}
s=bpy.data.scenes.new('REV15K / Black Brick Overlapping Team Murals')
s['variant']='REV15K';s.world=base.world;s.frame_start=1;s.frame_end=base.frame_end
for prop in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,prop,getattr(base.view_settings,prop))
for o in base.objects:
 if o.get('artKind') or o.name=='REV15J1 / Team Carousel Controller':continue
 s.collection.objects.link(o)
bpy.context.window.scene=s;s.frame_set(1)
controller=bpy.data.objects.new('REV15K / Team Carousel Controller',None);s.collection.objects.link(controller)
controller['team_index']=0;controller.id_properties_ui('team_index').update(min=0,max=7)

# The same world-space worn masonry texture drives the wall and paint relief.
group=bpy.data.node_groups.new('REV15K / painted brick substrate','ShaderNodeTree')
for name,t in [('Color','NodeSocketColor'),('Normal','NodeSocketVector'),('Height','NodeSocketFloat')]:group.interface.new_socket(name=name,in_out='OUTPUT',socket_type=t)
n=group.nodes;l=group.links;out=n.new('NodeGroupOutput')
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0])
combine=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['Y'],combine.inputs['X']);l.new(sep.outputs['Z'],combine.inputs['Y'])
brick_file=O/'viewer/art/black-painted-brick.png'
brick_image=bpy.data.images.load(str(brick_file));brick_image.name='REV15K / worn black-painted brick albedo';brick_image.colorspace_settings.name='sRGB';brick_image.pack()
height_image=bpy.data.images.load(str(brick_file),check_existing=False);height_image.name='REV15K / brick luminance for relief';height_image.colorspace_settings.name='Non-Color';height_image.pack()
tile_width=2.48;tile_height=tile_width*brick_image.size[1]/brick_image.size[0]
mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1/tile_width,1/tile_height,0);l.new(combine.outputs[0],mapping.inputs[0])
brick=n.new('ShaderNodeTexImage');brick.image=brick_image;brick.extension='REPEAT';l.new(mapping.outputs[0],brick.inputs['Vector'])
height=n.new('ShaderNodeTexImage');height.image=height_image;height.extension='REPEAT';l.new(mapping.outputs[0],height.inputs['Vector'])
gray=n.new('ShaderNodeRGBToBW');l.new(height.outputs['Color'],gray.inputs[0])
normalize=n.new('ShaderNodeMapRange');normalize.clamp=True;normalize.inputs['From Min'].default_value=.02;normalize.inputs['From Max'].default_value=.19;l.new(gray.outputs[0],normalize.inputs['Value'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.007;l.new(normalize.outputs['Result'],bump.inputs['Height'])
l.new(brick.outputs['Color'],out.inputs['Color']);l.new(bump.outputs['Normal'],out.inputs['Normal']);l.new(normalize.outputs['Result'],out.inputs['Height'])

def material(name,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.use_backface_culling=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.91;p.inputs['Specular IOR Level'].default_value=.16;p.inputs['Metallic'].default_value=0
 substrate=n.new('ShaderNodeGroup');substrate.node_tree=group;l.new(substrate.outputs['Normal'],p.inputs['Normal'])
 if image:
  t=n.new('ShaderNodeTexImage');t.image=image;t.extension='CLIP';l.new(t.outputs['Color'],p.inputs['Base Color']);l.new(t.outputs['Alpha'],p.inputs['Alpha']);m.surface_render_method='DITHERED'
 else:l.new(substrate.outputs['Color'],p.inputs['Base Color'])
 return m

def plane(name,x,y,z,w,h,mat):
 vv=[(x,y+w/2,z-h/2),(x,y-w/2,z-h/2),(x,y-w/2,z+h/2),(x,y+w/2,z+h/2)]
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],[(0,1,2,3)]);me.materials.append(mat);uv=me.uv_layers.new()
 uvs=[(0,0),(1,0),(1,1),(0,1)]
 for poly in me.polygons:
  for li in poly.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 me.update();obj=bpy.data.objects.new(name,me);s.collection.objects.link(obj)
 return obj,vv,uvs

wall_mat=material('REV15K / matte black-painted brick')
wall,_,_=plane('REV15K / Team wall black-painted brick finish',15.129,31.445,9.19,8.25,3.98,wall_mat)
wall['finish']='Worn black-painted running-bond masonry; shared world-space luminance-derived relief beneath all mural paint'
baseline=json.loads((B/'evidence/carousel-manifest.json').read_text())
manifest={'version':'REV15K','defaultTeam':0,'order':baseline['order'],'coreSource':BASE_SHA,'facade':baseline['facade'],'brick':{'texture':'art/black-painted-brick.png','tileWidthM':tile_width,'tileHeightM':tile_height,'reliefM':.007,'bumpStrength':.45,'heightRange':[.02,.19],'heightSource':'Luminance-derived from black brick texture, not a scanned height map','origin':[0,0]},'slides':[]}
asset_rows=[]
for i,old in enumerate(baseline['slides']):
 team=old['team'];key=team.replace(' ','-');file=O/'viewer/art'/f'{key}.png'
 im=bpy.data.images.load(str(file));im.name='REV15K / '+team+' complete mural paint';im.alpha_mode='STRAIGHT';im.colorspace_settings.name='sRGB';im.pack()
 aspect=im.size[0]/im.size[1];h=min(3.78,8.05/aspect);w=h*aspect
 ob,vv,uvs=plane('REV15K / '+team+' / overlapping mural composition',15.126,31.445,9.19,w,h,material('REV15K / '+team+' painted brick mural',im))
 people=copy.deepcopy(old.get('people') or [{'name':name,'role':'LEAD'} for name in old['names']])
 for person in people:
  if i:person['role']='LEAD'
 title=team.upper().split(' ') if team in ['Organising Committee','Public Relations','Web Development'] else [team.upper()]
 layout='four-staggered-portraits' if i==0 else 'three-portrait-triangle' if len(people)==3 else 'two-overlapping-portraits'
 ob['artKind']='mural-composition';ob['carouselSlide']=i;ob['team']=team;ob['headingText']=team.upper();ob['titleLines']=json.dumps(title);ob['people']=json.dumps(people);ob['layout']=layout
 for prop in ['hide_render','hide_viewport']:
  driver=ob.driver_add(prop).driver;v=driver.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=controller;v.targets[0].data_path='["team_index"]';driver.expression=f'index != {i}'
 art={'object':ob.name,'kind':'mural-composition','person':None,'position':[15.126,31.445,9.19],'width':w,'height':h,'vertices':vv,'uvs':uvs,'uv':[0,0,1,1],'image':'art/'+file.name}
 manifest['slides'].append({'index':i,'team':team,'headingText':team.upper(),'titleLines':title,'layout':layout,'names':old['names'],'people':people,'art':[art]})
 asset_rows.append({'team':team,'file':'viewer/art/'+file.name,'sha256':sha(file),'bytes':file.stat().st_size,'size':list(im.size),'layout':layout,'titleLines':title,'people':people,'tool':'image_gen.imagegen','inputComposite':'Rev15J1 viewer/art/'+('oc-mural.png' if i==0 else key+'.png')})

data=bpy.data.cameras.new('REV15K / matched laptop review camera');data.lens=22
camera=bpy.data.objects.new(data.name,data);s.collection.objects.link(camera);camera.location=(9.4,31.445,9.25);camera.rotation_euler=(Vector((15.13,31.445,9.25))-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
s['carouselOrder']=json.dumps(manifest['order']);s['initialTeam']='Organising Committee';s['userVisualApproval']='PENDING';s['authorizedChange']='Black painted brick finish; overlapping portrait compositions, large lower foreground one/two-line team names, side handwritten names/roles; other teams LEAD; OC roles preserved.'
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=8;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100
checks={'40HistoricalSceneMembershipsExact':all(tuple(bpy.data.scenes[k].objects)==v for k,v in history.items()),'baseFileUnchanged':sha(P)==BASE_SHA,'originalNonArtShared':all(s.objects.get(o.name)==o for o in base.objects if not o.get('artKind') and o.name!='REV15J1 / Team Carousel Controller'),'allOriginalLightEnergiesExact':all(bpy.data.objects[n].data.energy==e for n,e in energies.items()),'sameWorld':s.world==base.world,'eightTeamsNoCoordinators':len(manifest['order'])==8 and 'Coordinators' not in manifest['order'],'allOtherRolesLead':all(p['role']=='LEAD' for slide in manifest['slides'][1:] for p in slide['people']),'originalOCRolesPreserved':manifest['slides'][0]['people']==baseline['slides'][0]['people'],'threePortraitTriangle':manifest['slides'][6]['layout']=='three-portrait-triangle','threeStackedTwoWordTitles':sum(len(x['titleLines'])==2 for x in manifest['slides'])==3}
for i,slide in enumerate(manifest['slides']):
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'slide{i}Exclusive']=len(active)==1 and active[0]['carouselSlide']==i
assert all(checks.values()),checks
controller['team_index']=0;controller.update_tag();bpy.context.view_layer.update()
(O/'evidence/carousel-manifest.json').write_text(json.dumps(manifest,indent=2));(O/'viewer/carousel.json').write_text(json.dumps(manifest,indent=2));(O/'evidence/art-assets.json').write_text(json.dumps(asset_rows,indent=2))
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
target=O/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
result={'status':'PASS','checks':checks,'baseSHA256':BASE_SHA,'masterSHA256':sha(target),'masterBytes':target.stat().st_size,'sceneCount':len(bpy.data.scenes),'defaultTeam':'Organising Committee','wallMaterial':wall_mat.name,'paintSharesBrickNormal':True,'lightEnergies':energies}
(O/'evidence/blender-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
