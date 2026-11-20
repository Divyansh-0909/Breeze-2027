import bpy, json, hashlib, math, time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
P=R.parent/'house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend'
EXPECTED='2c78b57e97a5a97683f946d60ad265b22a1eb88ae12abed6220ec268ce473657'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==EXPECTED
for p in ['delivery','viewer','renders','review','evidence']: (R/p).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P));base=bpy.context.scene
history={x.name:[o.name for o in x.objects] for x in bpy.data.scenes}
def signature(o):
 d={'type':o.type,'matrix':[list(v) for v in o.matrix_world],'data':o.data.name if o.data else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []}
 if o.type=='MESH':d.update(verts=[list(v.co) for v in o.data.vertices],polys=[list(p.vertices) for p in o.data.polygons])
 return hashlib.sha256(json.dumps(d,separators=(',',':')).encode()).hexdigest()
original_signatures={o.name:signature(o) for o in base.objects}
s=base.copy();s.name='REV15P / Isolated Night Atmosphere Pilot';s['variant']='REV15P_PILOT';s['sourceSHA256']=EXPECTED;s['pilotOnly']=True
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s
copies={}
for o in base.objects:
 a=o.copy();a.name='REV15P / '+o.name
 if o.type in ['LIGHT','CAMERA']:a.data=o.data.copy()
 s.collection.objects.link(a);copies[o]=a
for o,a in copies.items():
 if o.parent in copies:a.parent=copies[o.parent]
 if a.animation_data:
  for f in a.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
controller=copies[base.objects['REV15O / Team Carousel Controller']];controller['team_index']=0
layer=s.view_layers.new('REV15P / Pilot independent objects')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
s.world=base.world.copy();s.world.name='REV15P / Low cool night ambient'
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Color'].default_value=(.07,.105,.17,1);n.inputs['Strength'].default_value=.09
changes=[]
for old,a in copies.items():
 if old.type!='LIGHT':continue
 watts=old.data.energy;name=old.name
 if 'Moon' in name:a.data.energy=620;a.data.color=(.42,.57,.8)
 elif 'Rooftop ambient' in name:a.data.energy=460;a.data.color=(.45,.58,.78)
 elif 'Warm open-shop spill' in name:
  idx=int(name.split('spill ')[1].split('.')[0]);a.data.energy={0:12,1:150,2:95,3:170,4:10}[idx];a.data.color=(1,.56,.22)
 elif 'Soft screen' in name:a.data.energy=340
 elif 'Signboard practical' in name:a.data.energy=85;a.data.color=(1,.73,.4)
 elif 'lane-end warm' in name:a.data.energy=80;a.data.color=(1,.55,.22)
 elif 'Poster wall' in name:a.data.energy=110
 a.data.use_shadow=old.data.use_shadow
 changes.append({'source':old.name,'pilot':a.name,'sourceWatts':watts,'pilotWatts':a.data.energy,'color':list(a.data.color),'positionUnchanged':list(a.location)==list(old.location)})
# Lighting emphasis only; the approved five optional interior support lights stay off.
assert all(a.data.energy==0 for o,a in copies.items() if o.type=='LIGHT' and o.name.startswith('Rev05B'))
for old,a in copies.items():
 if 'Bounded lane haze' in old.name:a.hide_render=True;a.hide_viewport=True

# A restrained wet/dry roughness variation, on existing floor materials only.
damp=[]
for old,a in copies.items():
 if old.type!='MESH' or not any(k in old.name for k in ['Lane flat','Accessible ramp','Flared ramp apron','Rooftop slab']):continue
 for k,slot in enumerate(a.material_slots):
  if not slot.material or not slot.material.use_nodes:continue
  m=slot.material.copy();m.name='REV15P / Damp patches / '+slot.material.name
  slot.link='OBJECT';slot.material=m;n=m.node_tree.nodes;links=m.node_tree.links
  bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
  if not bs:continue
  geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.52;noise.inputs['Detail'].default_value=3
  links.new(geo.outputs['Position'],noise.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.37;ramp.color_ramp.elements[0].color=(.31,.31,.31,1);ramp.color_ramp.elements[1].position=.57;ramp.color_ramp.elements[1].color=(.91,.91,.91,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],bs.inputs['Roughness']);damp.append({'object':a.name,'material':m.name,'roughnessRange':[.31,.91]})

s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=32;s.view_settings.exposure=.25
s.render.resolution_x=1440;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=s;rl.layer=layer.name
layer.use_pass_z=True
square=nt.nodes.new('CompositorNodeMath');square.operation='MULTIPLY';nt.links.new(rl.outputs['Depth'],square.inputs[0]);nt.links.new(rl.outputs['Depth'],square.inputs[1]);density=nt.nodes.new('CompositorNodeMath');density.operation='MULTIPLY';density.inputs[1].default_value=-(.024**2);nt.links.new(square.outputs[0],density.inputs[0]);ex=nt.nodes.new('CompositorNodeMath');ex.operation='EXPONENT';nt.links.new(density.outputs[0],ex.inputs[0]);inv=nt.nodes.new('CompositorNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(ex.outputs[0],inv.inputs[1]);mix=nt.nodes.new('CompositorNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.014,.020,.029,1);nt.links.new(inv.outputs[0],mix.inputs[0]);nt.links.new(rl.outputs['Image'],mix.inputs[1]);out=nt.nodes.new('CompositorNodeComposite');nt.links.new(mix.outputs[0],out.inputs[0])

poses=[('far',(0,-24,7.9),(0,12,10.7),24),('middle',(0,-3.5,8.65),(0,16,10.5),24),('near',(0,4.6,9.1),(0,11.1,11.5),27)]
cameras=[]
for key,pos,target,lens in poses:
 data=bpy.data.cameras.new('REV15P / '+key);data.lens=lens;data.sensor_width=36;data.clip_start=.08;data.clip_end=160
 cam=bpy.data.objects.new('REV15P / fixed '+key,data);s.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cameras.append({'key':key,'object':cam.name,'position':pos,'target':target,'lens':lens,'fovDegrees':math.degrees(data.angle_x),'aspect':1.6})
s.camera=s.objects['REV15P / fixed far'];s.frame_set(1);layer.update()
checks={'45SourceSceneMembershipsPreserved':all([o.name for o in bpy.data.scenes[n].objects]==v for n,v in history.items()),'all1601SourceObjectGeometryTransformsMaterialsUnchanged':all(signature(o)==original_signatures[o.name] for o in base.objects),'189CrowdPreserved':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189,'11HouseGeometryPreserved':all(a.data==o.data for o,a in copies.items() if o.type=='MESH'),'sourceHashUnchanged':sha(P)==EXPECTED,'optionalSupportLightsRemainOff':all(a.data.energy==0 for o,a in copies.items() if o.type=='LIGHT' and o.name.startswith('Rev05B')),'all8MuralSlidesRetained':len([o for o in s.objects if o.get('artKind')])==8,'sourceSceneCount45':len(history)==45}
assert all(checks.values()),checks
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'),compress=True)
(R/'viewer/cameras.json').write_text(json.dumps({'cameras':cameras,'fogDensity':.024,'fogLinearColor':[.014,.020,.029],'nativeExposure':.25},indent=2))
(R/'evidence/preservation.json').write_text(json.dumps({'status':'PASS','checks':checks,'sourceSHA256':EXPECTED,'sourceBytes':P.stat().st_size,'pilotSHA256':sha(Path(bpy.data.filepath)),'pilotBytes':Path(bpy.data.filepath).stat().st_size,'pilotScenes':len(bpy.data.scenes),'sourceSceneMemberships':history,'sourceObjectSignatures':original_signatures,'pilotSourceObjects':{o.name:a.name for o,a in copies.items()}},indent=2))
(R/'evidence/look-changes.json').write_text(json.dumps({'lights':changes,'damp':damp,'fog':'Depth composite: 1-exp(-0.024^2 * distance^2), including all emissive/sign pixels; no runtime volume','unchangedShopFrontGeometry':'13 of 18 shut; five authored open fronts retained, three principal lit pools','authoritativeSource':'Rev15O remains authoritative; this is a pilot'},indent=2))
print('PILOT SAVED',flush=True)
