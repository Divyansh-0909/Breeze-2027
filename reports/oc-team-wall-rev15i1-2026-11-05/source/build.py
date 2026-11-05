import bpy,json,hashlib,copy,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O/'inputs/Rev15I-authentic.blend';BASE='2aac6fa545137e2357334a5c5ff9adbd806f197a3b45f5ea4ff6fb28787a362d';assert hashlib.sha256(P.read_bytes()).hexdigest()==BASE
bpy.ops.wm.open_mainfile(filepath=str(P));base=next(s for s in bpy.data.scenes if s.get('variant')=='REV15I');s=bpy.data.scenes.new('REV15I1 / Wider OC Names / Team Carousel');s['variant']='REV15I1';s.world=base.world
for p in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,p,getattr(base.view_settings,p))
s.frame_start=base.frame_start;s.frame_end=base.frame_end;s.render.fps=base.render.fps;s.camera=base.camera;bpy.context.window.scene=s;s.frame_set(1)
c=bpy.data.objects.new('REV15I1 / Team Carousel Controller',None);s.collection.objects.link(c);c['team_index']=0;c.id_properties_ui('team_index').update(min=0,max=8)
m=json.load(open(O/'inputs/baseline-carousel.json'));new=copy.deepcopy(m);new['version']='REV15I1';new['coreSource']=BASE;regions=json.load(open(O/'evidence/name-regions.json'));oc=new['slides'][1];target=.90*oc['muralWidthM']/4;changes=[]
im=bpy.data.images.load(str(O/'inputs/wider-oc-names.png'));im.name='REV15I1 / wider OC name graffiti';im.colorspace_settings.name='sRGB';im.alpha_mode='STRAIGHT';im.pack();mat=bpy.data.materials.new('REV15I1 / wider black-ivory OC names');mat.use_nodes=True;mat.surface_render_method='DITHERED';mat.use_backface_culling=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.88;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.15;p.inputs['Emission Strength'].default_value=0;t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;t.extension='CLIP';mat.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha'])
lookup={a['object']:a for slide in new['slides']for a in slide['art']}
for o in base.objects:
 if o.name=='REV15I / Team Carousel Controller':continue
 if not o.get('artKind'):s.collection.objects.link(o);continue
 n=o.copy();n.name=o.name.replace('REV15I /','REV15I1 /',1);s.collection.objects.link(n);n.animation_data_clear();a=lookup[o.name];a['object']=n.name
 for prop in ['hide_render','hide_viewport']:
  d=n.driver_add(prop).driver;v=d.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=c;v.targets[0].data_path='["team_index"]';d.expression=f'index != {o["carouselSlide"]}'
 if o.get('carouselSlide')==1 and o.get('artKind')=='lead-name':
  r=regions[a['person']];w=target;h=w/r['aspect'];z=7.70;cy=a['position'][1];x=a['position'][0];assert z+h<oc['muralBottomZ']+.5*oc['muralHeightM'];vv=[(x,cy+w/2,z),(x,cy-w/2,z),(x,cy-w/2,z+h),(x,cy+w/2,z+h)];me=o.data.copy();n.data=me
  for v,q in zip(me.vertices,vv):v.co=q
  me.materials.clear();me.materials.append(mat);u0,v0,u1,v1=r['uv'];uvs=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
  for poly in me.polygons:
   for li in poly.loop_indices:me.uv_layers.active.data[li].uv=uvs[me.loops[li].vertex_index]
  me.update();me.calc_tangents();changes.append({'person':a['person'],'oldWidthM':a['width'],'newWidthM':w,'heightM':h,'portraitShareWidthM':oc['muralWidthM']/4,'widthRatio':.90,'growth':w/a['width']});a.update(width=w,height=h,position=[x,cy,z+h/2],vertices=vv,uv=r['uv'],uvs=uvs,image='inputs/wider-oc-names.png')
 else:a['image']='viewer/art/'+Path(a['image']).name
s['carouselOrder']=json.dumps(new['order']);s['initialTeam']='Coordinators';s['authorizedChange']='Only four OC name images, UVs and sizes; 90 percent of each portrait share';s['websiteUnmodified']=True;s['userVisualApproval']='PENDING';s['OCNameWidthRatio']=.90
oc['nameWidthRatio']=.90;oc.pop('fullNameBlockHeightM',None);oc.pop('singleNameHeightM',None);oc['nameSizing']='90% portrait share width; native image aspect';(O/'evidence/carousel-manifest.json').write_text(json.dumps(new,indent=2));(O/'evidence/name-widths.json').write_text(json.dumps(changes,indent=2));web=copy.deepcopy(new)
for slide in web['slides']:
 for a in slide['art']:
  src=O/a['image'];dest=O/'viewer/art'/src.name
  if src.resolve()!=dest.resolve():shutil.copy2(src,dest)
  a['image']='art/'+dest.name
(O/'viewer/carousel.json').write_text(json.dumps(web,indent=2));ui=bpy.data.texts.load(str(O/'source/carousel_controls.py'));ui.name='oc_wider_name_controls.py';c['team_index']=0;c.update_tag();bpy.context.view_layer.update();s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=4;bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend'),compress=True);print('SAVED',len(bpy.data.scenes),'scenes; 4 widened names',changes,flush=True)
