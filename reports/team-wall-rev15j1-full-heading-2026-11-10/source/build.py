import bpy,copy,hashlib,json,os
from pathlib import Path

O=Path(__file__).resolve().parents[1]
P=Path(os.environ.get('TEAM_WALL_BASE',str(O.parent/'team-wall-rev15j-2026-11-10/delivery/Gullyverse-Rev15J-OC-First.blend')))
BASE_SHA='0a67481232bd52e9aedc2637564a71d3cbce6d8fb55c2464b860172bbc02d9f0'
assert hashlib.sha256(P.read_bytes()).hexdigest()==BASE_SHA
bpy.ops.wm.open_mainfile(filepath=str(P))
base=next(s for s in bpy.data.scenes if s.get('variant')=='REV15J')
history={s.name:tuple(s.objects) for s in bpy.data.scenes}
s=bpy.data.scenes.new('REV15J1 / Organising Committee Full Heading')
s['variant']='REV15J1';s.world=base.world;s.camera=base.camera
for prop in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,prop,getattr(base.view_settings,prop))
s.frame_start,s.frame_end=base.frame_start,base.frame_end;s.render.fps=base.render.fps
bpy.context.window.scene=s;s.frame_set(1)
c=bpy.data.objects.new('REV15J1 / Team Carousel Controller',None);s.collection.objects.link(c)
c['team_index']=0;c.id_properties_ui('team_index').update(min=0,max=7)
m=json.loads((O.parent/'team-wall-rev15j-2026-11-10/evidence/carousel-manifest.json').read_text())
m=copy.deepcopy(m);m.update(version='REV15J1',coreSource=BASE_SHA)
lookup={a['object']:a for slide in m['slides'] for a in slide['art']}
spec=json.loads((O/'evidence/heading-art.json').read_text())
image=bpy.data.images.load(str(O/'viewer/art/organising-committee-heading.png'));image.name='REV15J1 / Organising Committee heading';image.colorspace_settings.name='sRGB';image.alpha_mode='STRAIGHT';image.pack()
mat=bpy.data.materials.new('REV15J1 / full Organising Committee heading');mat.use_nodes=True;mat.surface_render_method='DITHERED';mat.use_backface_culling=True
p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.88;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.15
t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;t.extension='CLIP';mat.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha'])
changed=[]
for obj in base.objects:
 if obj.name=='REV15J / Team Carousel Controller':continue
 if not obj.get('artKind'):s.collection.objects.link(obj);continue
 n=obj.copy();n.name=obj.name.replace('REV15J /','REV15J1 /',1);s.collection.objects.link(n);n.animation_data_clear()
 for prop in ['hide_render','hide_viewport']:
  driver=n.driver_add(prop).driver;var=driver.variables.new();var.name='index';var.type='SINGLE_PROP';var.targets[0].id=c;var.targets[0].data_path='["team_index"]';driver.expression=f'index != {obj["carouselSlide"]}'
 a=lookup[obj.name];a['object']=n.name
 if obj['carouselSlide']==0 and obj['artKind']=='heading':
  h=.72;w=h*spec['aspect'];assert w<7.45
  x,y,z=a['position'];vv=[(x,y+w/2,z-h/2),(x,y-w/2,z-h/2),(x,y-w/2,z+h/2),(x,y+w/2,z+h/2)]
  u0,v0,u1,v1=spec['uv'];uvs=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
  n.data=obj.data.copy()
  for vertex,co in zip(n.data.vertices,vv):vertex.co=co
  n.data.materials.clear();n.data.materials.append(mat)
  for poly in n.data.polygons:
   for li in poly.loop_indices:n.data.uv_layers.active.data[li].uv=uvs[n.data.loops[li].vertex_index]
  n.data.update();n.data.calc_tangents()
  n['headingText']='ORGANISING COMMITTEE'
  a.update(width=w,height=h,vertices=vv,uv=spec['uv'],uvs=uvs,image='viewer/art/organising-committee-heading.png')
  changed.append(n.name)
m['slides'][0]['headingText']='ORGANISING COMMITTEE'
s['carouselOrder']=json.dumps(m['order']);s['initialTeam']='Organising Committee';s['headingText']='ORGANISING COMMITTEE';s['userVisualApproval']='PENDING';s['authorizedChange']='Replace abbreviated OC heading with full Organising Committee in the existing graffiti family; all other art and wall retained.'
c.update_tag();bpy.context.view_layer.update()
checks={'39HistoricalScenesExact':all(tuple(bpy.data.scenes[k].objects)==v for k,v in history.items()),'oneHeadingChanged':len(changed)==1,'wallAndNonArtExact':all(s.objects.get(o.name)==o for o in base.objects if not o.get('artKind') and o.name!='REV15J / Team Carousel Controller'),'otherArtMeshesExact':all(o.data==base.objects[o.name.replace('REV15J1 /','REV15J /',1)].data for o in s.objects if o.get('artKind') and o.name not in changed),'eightTeamsNoCoordinators':len(m['order'])==8 and 'Coordinators' not in m['order'],'fullHeadingText':m['slides'][0]['headingText']=='ORGANISING COMMITTEE','headingNativeAspectAndHeight':abs(w/h-spec['aspect'])<1e-8 and h==.72,'sameWorldLighting':s.world==base.world}
for i,slide in enumerate(m['slides']):
 c['team_index']=i;c.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'slide{i}Exclusive']=len(active)==len(slide['art']) and all(o['carouselSlide']==i for o in active)
assert all(checks.values()),checks
c['team_index']=0;c.update_tag();bpy.context.view_layer.update()
(O/'evidence/carousel-manifest.json').write_text(json.dumps(m,indent=2))
web=copy.deepcopy(m)
for slide in web['slides']:
 for a in slide['art']:a['image']='art/'+Path(a['image']).name
(O/'viewer/carousel.json').write_text(json.dumps(web,indent=2))
ui=bpy.data.texts.load(str(O/'source/carousel_controls.py'));ui.name='team_wall_rev15j1_controls.py'
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=8;bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
target=O/'delivery/Gullyverse-Rev15J1-Full-Heading.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
result={'status':'PASS','checks':checks,'baseSHA256':BASE_SHA,'masterSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'masterBytes':target.stat().st_size,'sceneCount':len(bpy.data.scenes),'headingWidthM':w,'headingHeightM':h}
(O/'evidence/blender-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
