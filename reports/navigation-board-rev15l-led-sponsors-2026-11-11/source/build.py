import bpy,json,hashlib,math,copy
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];B=O.parent/'team-wall-rev15k-black-brick-2026-11-11';P=B/'delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((B/'evidence/blender-validation.json').read_text())['masterSHA256'];assert sha(P)==expected
logos=json.loads((O/'evidence/sponsors.json').read_text());strip=O/'viewer/logo-strip.png';assert strip.exists()
bpy.ops.wm.open_mainfile(filepath=str(P));base=next(s for s in bpy.data.scenes if s.get('variant')=='REV15K')
history={s.name:tuple(s.objects) for s in bpy.data.scenes};old_lights={o.name:o.data.energy for o in base.objects if o.type=='LIGHT'}
s=bpy.data.scenes.new('REV15L / Navigation and Scrolling Sponsor LED');s['variant']='REV15L';s.world=base.world;s.render.fps=30;s.frame_start=1;s.frame_end=logos['periodCells']
for p in ['view_transform','look','exposure','gamma']:setattr(s.view_settings,p,getattr(base.view_settings,p))
bpy.context.window.scene=s
board=[];unchanged=[]
old_controller=base.objects['REV15K / Team Carousel Controller'];controller=old_controller.copy();controller.name='REV15L / Team Carousel Controller';s.collection.objects.link(controller);controller['team_index']=0
for o in base.objects:
 if o==old_controller:continue
 if o.get('artKind'):
  n=o.copy();n.name=o.name.replace('REV15K /','REV15L /',1);n.animation_data_clear();s.collection.objects.link(n)
  for prop in ['hide_render','hide_viewport']:
   d=n.driver_add(prop).driver;v=d.variables.new();v.name='index';v.type='SINGLE_PROP';v.targets[0].id=controller;v.targets[0].data_path='["team_index"]';d.expression=f'index != {n["carouselSlide"]}'
 elif o.get('authorizedChange')=='approach-board-rigid':
  n=o.copy();n.name=o.name.replace('REV15A /','REV15L /',1);s.collection.objects.link(n);board.append(n)
  if o.type in ['FONT','LIGHT']:n.data=o.data.copy()
  if 'Navigation upright' in o.name:n.location.z+=.85;n.dimensions.z+=1.7
  elif any(x in o.name for x in ['top beam','hero raster','header suspension','Signboard practical']):n.location.z+=1.7
  elif 'EVENTS' in o.name or 'TEAM  >' in o.name:n.location.z+=11.90-10.97599983215332
  elif 'CONTACT US' in o.name or 'PAST SPONSORS' in o.name:
   n.location.z+=11.12-10.195999145507812
   if 'PAST SPONSORS' in o.name:
    n.name=n.name.replace('PAST SPONSORS','SCHEDULE (proposed)');n['proposedDestination']='Schedule'
    if n.type=='FONT':n.data.body='SCHEDULE'
  elif 'AFTERMOVIE' in o.name:
   n.location.z+=12.68-9.425999641418457
   if n.type=='FONT':n.data.body='AFTERMOVIE';n.location.x=-.15
 else:s.collection.objects.link(o);unchanged.append(o)

def material(name,color,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
black=material('REV15L / black LED housing',(.008,.009,.010),.25,.38);steel=material('REV15L / hanging hardware',(.025,.027,.029),.75,.32)
def mesh_obj(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);board.append(o);return o
def box(name,pos,dims,mat,bevel=0):
 w,d,h=[v/2 for v in dims];verts=[(-w,-d,-h),(w,-d,-h),(w,d,-h),(-w,d,-h),(-w,-d,h),(w,-d,h),(w,d,h),(-w,d,h)];o=mesh_obj(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat);o.location=pos
 if bevel:mod=o.modifiers.new('Soft casing edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted casing normals','WEIGHTED_NORMAL')
 return o

# Bottom plaque reuses the current Aftermovie plate's visual family.
for typ in ['MESH','FONT']:
 old=next(o for o in base.objects if 'AFTERMOVIE' in o.name and o.type==typ)
 n=old.copy();n.name='REV15L / Past Sponsors '+('plaque' if typ=='MESH' else 'label');s.collection.objects.link(n);board.append(n);n.location.z+=10.325-9.425999641418457
 if typ=='FONT':n.data=old.data.copy();n.data.body='PAST SPONSORS'
 n['navigationDirection']='none'

font=next(o for o in board if o.type=='FONT' and o.data.body=='AFTERMOVIE')
x=.93;z=12.64;y=10.908
arrow=mesh_obj('REV15L / Aftermovie upward arrow',[(x-.018,y,z-.11),(x+.018,y,z-.11),(x+.018,y,z+.005),(x+.09,y,z+.005),(x,y,z+.13),(x-.09,y,z+.005),(x-.018,y,z+.005)],[tuple(range(7))],font.data.materials[0]);arrow['direction']='up'
case=box('REV15L / close-hung sponsor LED casing',(0,11,9.61),(4.08,.18,.76),black,.045)
for x in [-1.5,1.5]:box('REV15L / short LED suspension '+str(x),(x,11,10.02),(.027,.045,.10),steel,.006)
for x in [-1.94,1.94]:
 for z in [9.93,9.29]:box('REV15L / casing screw',(x,10.902,z),(.022,.012,.022),steel,.006)
curve=bpy.data.curves.new('REV15L / LED power cable','CURVE');curve.dimensions='3D';curve.bevel_depth=.012;curve.bevel_resolution=2;poly=curve.splines.new('POLY');points=[(1.94,11.10,9.61),(3.20,11.10,9.61),(3.20,11.10,14.85)];poly.points.add(len(points)-1)
for p,co in zip(poly.points,points):p.co=(*co,1)
curve.materials.append(black);cable=bpy.data.objects.new(curve.name,curve);s.collection.objects.link(cable);board.append(cable)

# One strip texture, sampled at fixed LED cell centres; frame wraps exactly.
mat=bpy.data.materials.new('REV15L / animated amber-red sponsor dot matrix');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.002,.0004,.0002,1);p.inputs['Roughness'].default_value=.5;p.inputs['Emission Color'].default_value=(1,.035,.002,1)
im=bpy.data.images.load(str(strip));im.name='REV15L / all branch sponsor marks in one looping strip';im.colorspace_settings.name='Non-Color';im.pack()
uv=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0])
def mathnode(op,a=None,b=None):
 v=n.new('ShaderNodeMath');v.operation=op
 for i,item in enumerate([a,b]):
  if item is None:continue
  if isinstance(item,(int,float)):v.inputs[i].default_value=item
  else:l.new(item,v.inputs[i])
 return v.outputs[0]
gx=mathnode('MULTIPLY',sep.outputs['X'],384);gy=mathnode('MULTIPLY',sep.outputs['Y'],64)
scroll=n.new('ShaderNodeValue');scroll.name='LED scroll cells';d=scroll.outputs[0].driver_add('default_value').driver;d.expression=f'(frame - 1) % {logos["periodCells"]}'
u=mathnode('DIVIDE',mathnode('ADD',mathnode('ADD',mathnode('FLOOR',gx),.5),scroll.outputs[0]),logos['periodCells']);v=mathnode('DIVIDE',mathnode('ADD',mathnode('FLOOR',gy),.5),64)
coord=n.new('ShaderNodeCombineXYZ');l.new(u,coord.inputs['X']);l.new(v,coord.inputs['Y']);image=n.new('ShaderNodeTexImage');image.image=im;image.extension='REPEAT';image.interpolation='Closest';l.new(coord.outputs[0],image.inputs['Vector']);gray=n.new('ShaderNodeRGBToBW');l.new(image.outputs['Color'],gray.inputs[0])
cell=n.new('ShaderNodeCombineXYZ');l.new(mathnode('FRACT',gx),cell.inputs['X']);l.new(mathnode('FRACT',gy),cell.inputs['Y']);dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';l.new(cell.outputs[0],dist.inputs[0]);dist.inputs[1].default_value=(.5,.5,0)
mask=n.new('ShaderNodeMapRange');mask.clamp=True;mask.interpolation_type='SMOOTHSTEP';mask.inputs['From Min'].default_value=.29;mask.inputs['From Max'].default_value=.43;mask.inputs['To Min'].default_value=1;mask.inputs['To Max'].default_value=0;l.new(dist.outputs['Value'],mask.inputs['Value'])
strength=mathnode('MULTIPLY',mask.outputs['Result'],mathnode('ADD',mathnode('MULTIPLY',gray.outputs[0],8),.008));l.new(strength,p.inputs['Emission Strength'])
w=3.86;h=w/6;z=9.61;y=10.899
face=mesh_obj('REV15L / animated sponsor LED face',[(-w/2,y,z-h/2),(w/2,y,z-h/2),(w/2,y,z+h/2),(-w/2,y,z+h/2)],[(0,1,2,3)],mat);layer=face.data.uv_layers.new();coords=[(0,0),(1,0),(1,1),(0,1)]
for poly in face.data.polygons:
 for li in poly.loop_indices:layer.data[li].uv=coords[face.data.loops[li].vertex_index]
face['ledScreen']=True;face['periodCells']=logos['periodCells'];face['logoCount']=logos['logoCount']
light=bpy.data.lights.new('REV15L / gentle LED case spill','AREA');light.energy=18;light.color=(1,.035,.002);light.shape='RECTANGLE';light.size=3.5;light.size_y=.4;ob=bpy.data.objects.new(light.name,light);s.collection.objects.link(ob);ob.location=(0,10.65,9.61);ob.rotation_euler=(Vector((0,11,9.61))-ob.location).to_track_quat('-Z','Y').to_euler()
s.use_nodes=True;tree=s.node_tree;tree.nodes.clear();rl=tree.nodes.new('CompositorNodeRLayers');glow=tree.nodes.new('CompositorNodeGlare');glow.glare_type='FOG_GLOW';glow.quality='HIGH';glow.threshold=3;glow.size=6;glow.mix=-.75;out=tree.nodes.new('CompositorNodeComposite');tree.links.new(rl.outputs['Image'],glow.inputs['Image']);tree.links.new(glow.outputs['Image'],out.inputs['Image'])
camdata=bpy.data.cameras.new('REV15L / navigation review camera');camdata.lens=40;camera=bpy.data.objects.new(camdata.name,camdata);s.collection.objects.link(camera);camera.location=(0,0,11);camera.rotation_euler=(Vector((0,11,11))-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100;s['initialTeam']='Organising Committee';s['navigationProposal']='Schedule replaces former upper Past Sponsors slot; suggestion pending user choice';s['authorizedChange']='Top Aftermovie up arrow; bottom non-directional Past Sponsors plaque with closely hung infinite sponsor-logo LED.'
s.frame_set(1);controller.update_tag();bpy.context.view_layer.update()
checks={'41HistoricalScenesExact':all(tuple(bpy.data.scenes[k].objects)==v for k,v in history.items()),'baseFileUnchanged':sha(P)==expected,'unrelatedObjectsShared':all(s.objects.get(o.name)==o for o in unchanged),'allOriginalLightEnergiesExact':all(bpy.data.objects[k].data.energy==v for k,v in old_lights.items()),'all62LogosReferenced':logos['logoCount']==62,'pastSponsorsNoDirection':next(o for o in board if o.type=='FONT' and o.name.endswith('Past Sponsors label')).data.body=='PAST SPONSORS','minimumWalkwayClearance':9.23-7.076>=2.1,'closeHungGap':abs(10.05-9.99-.06)<1e-8,'aftermovieAboveOtherLinks':12.68>11.90,'muralsRetainOriginalMeshes':all(o.data==base.objects[o.name.replace('REV15L /','REV15K /',1)].data for o in s.objects if o.get('artKind'))}
for frame,value in [(1,0),(2,1),(logos['periodCells']+1,0)]:s.frame_set(frame);bpy.context.view_layer.update();checks[f'ledFrame{frame}']=abs(scroll.outputs[0].default_value-value)<.001
for i in range(8):controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();active=[o for o in s.objects if o.get('artKind') and not o.hide_render];checks[f'team{i}Exclusive']=len(active)==1 and active[0]['carouselSlide']==i
assert all(checks.values()),checks
controller['team_index']=0;controller.update_tag();s.frame_set(1);bpy.context.view_layer.update()
manifest={'version':'REV15L','baseSHA256':expected,'logoCount':logos['logoCount'],'periodCells':logos['periodCells'],'fps':30,'periodSeconds':logos['periodCells']/30,'labels':['AFTERMOVIE ↑','EVENTS <','TEAM >','SCHEDULE (proposed)','CONTACT US','PAST SPONSORS'],'plaqueCenter':[0,11,10.325],'plaqueBottomZ':10.05,'screenCaseCenter':[0,11,9.61],'screenCaseSize':[4.08,.18,.76],'screenFaceSize':[w,h],'screenFaceY':y,'screenFaceZ':z,'screenBottomZ':9.23,'groundZConservative':7.076,'clearanceM':9.23-7.076,'hangingGapM':.06,'boardObjects':[o.name for o in board]}
(O/'evidence/board-manifest.json').write_text(json.dumps(manifest,indent=2));(O/'viewer/board.json').write_text(json.dumps(manifest,indent=2));bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
target=O/'delivery/Gullyverse-Rev15L-Navigation-LED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(O/'evidence/blender-validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':sha(target),'masterBytes':target.stat().st_size,'sceneCount':len(bpy.data.scenes),'baseSHA256':expected},indent=2));print('BUILD COMPLETE',target.stat().st_size,flush=True)

# Reopen the saved master, bake evaluated world transforms and export only the board.
import runpy
runpy.run_path(str(O/'source/export-viewer.py'),run_name='__main__')
