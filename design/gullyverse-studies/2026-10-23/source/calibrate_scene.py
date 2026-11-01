import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parents[1]
# One continuous width-fit video image across the original three-panel proportions.
whole=(13.6+4*2+.4*2)*.65
for o in bpy.data.objects:
 if not o.name.startswith('Existing Aftermovie /'):continue
 w,h=o.scale.x,o.scale.y;x=o.location.x
 for loop in o.data.loops:
  uv=o.data.uv_layers.active.data[loop.index];co=o.data.vertices[loop.vertex_index].co;u,v=co.x+.5,co.y+.5;uv.uv=(.5+x/whole+(u-.5)*w/whole,.5+(v-.5)*h/whole*(16/9))
# Clear the side gallery routes; fixed crowd positions apply identically each replay.
for o in bpy.data.objects:
 for prefix in ['Festival extra ','Balanced extra ']:
  if not o.name.startswith(prefix):continue
  i=int(o.name[len(prefix):].split(' ')[0]);old=(-1 if i%2 else 1)*(11.8+(i%3)*.3)if prefix.startswith('Festival')else 12.1;new=(-1 if i%2 else 1)*(10.65+(i%2)*.12)if prefix.startswith('Festival')else 10.9
  if 'unshifted_x'not in o:o['unshifted_x']=o.location.x
  o.location.x=o['unshifted_x']+new-old
for scene in bpy.data.scenes:scene.cycles.use_denoising=False;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16
# Simple sloped guards protect the elevated transition without placing stairs on the path.
coll=bpy.data.collections['00_SHARED_SITE_ARCHITECTURE']
for x in [-8.1,8.1]:
 name='Sloped apron parapet '+str(x)
 if name in bpy.data.objects:continue
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,9.5,7.525));o=bpy.context.object;o.name=name;o.dimensions=(.25,9.1,1.1);o.rotation_euler.x=math.atan(.05)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(bpy.data.materials['Deck concrete'])
# Bring the existing landmark into the first hub composition while keeping the central route clear.
for o in bpy.data.collections['02_SHARED_NAVIGATION_LANDMARK'].objects:
 if 'unshifted_y'not in o:o['unshifted_y']=o.location.y
 o.location.y=o['unshifted_y']+5
for o in bpy.data.objects:
 if o.name.startswith('Signboard practical'):
  if 'unshifted_y'not in o:o['unshifted_y']=o.location.y
  o.location.y=o['unshifted_y']+5
cam=bpy.data.objects['04-hub'];cam.location=(-1.3,19.5,9.12);from mathutils import Vector
cam.rotation_euler=(Vector((4.4,32,10.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
for cname,sign in [('05-team',1),('06-events',-1)]:
 o=bpy.data.objects[cname];o.rotation_euler=(Vector((sign*14.8,29,9.5))-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=22
mapcam=bpy.data.objects['11-overhead'];mapcam.location=(0,9,91);mapcam.rotation_euler=(0,0,0);mapcam.data.ortho_scale=135
bpy.data.objects['TEAM destination heading'].rotation_euler.z=-math.pi/2
bpy.data.objects['EVENTS destination heading'].rotation_euler.z=math.pi/2
# A few occupied apartments; restrained human activity, not a neon city.
m=bpy.data.materials.get('Occupied apartment warm window')
if m is None:
 m=bpy.data.materials.new('Occupied apartment warm window');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.5,.29,.12,1);p.inputs['Emission Color'].default_value=(1,.63,.3,1);p.inputs['Emission Strength'].default_value=.45
for i,o in enumerate(sorted([o for o in bpy.data.objects if o.name.startswith('Neighbor window')],key=lambda o:o.name)):
 if i%5==0:o.data.materials.clear();o.data.materials.append(m)
# Rim light motivated by an open roof-side doorway, revealing the distant lane silhouettes.
for scene in bpy.data.scenes:
 coll=next(c for c in scene.collection.children if c.name.startswith('10_'))
 name=scene['variant']+' lane-end warm doorway spill'
 if name in bpy.data.objects:continue
 d=bpy.data.lights.new(name,'AREA');d.energy=150;d.color=(1,.72,.43);d.shape='DISK';d.size=2;o=bpy.data.objects.new(name,d);coll.objects.link(o);o.location=(3.8,10.7,9.6);o.rotation_euler=(Vector((1.9,8,8))-o.location).to_track_quat('-Z','Y').to_euler()
# Deliberate clustered spacing breaks the regimented crowd grid while protecting the central aisle.
rows=[[-.3,.2,-.1,.25,.2,-.3,.15,-.2],[.2,-.1,.3,-.2,.25,.1,-.2,.2],[-.1,.35,.1,.2,-.2,.3,-.15,.1]]
for o in bpy.data.objects:
 if not o.name.startswith('Audience '):continue
 label=o.name.split(' ')[1];r,c=map(int,label.split('_'));dx=rows[r%3][c]*.8;dy=rows[(r+1)%3][c]*1.5
 if 'crowd_grid_origin'not in o:o['crowd_grid_origin']=list(o.location)
 o.location.x=o['crowd_grid_origin'][0]+dx;o.location.y=o['crowd_grid_origin'][1]+dy
# Surface-facing convention: left storefronts face +X, right storefronts face -X.
for o in bpy.data.objects:
 if o.name.startswith('Hand-painted '):o.rotation_euler.z=math.pi/2 if o.location.x<0 else -math.pi/2
 if o.name=='Small festival lane poster':o.rotation_euler.z=-math.pi/2
 if o.name=='Street wayfinding paste-up':o.location.x=-4.36;o.rotation_euler.z=-math.pi/2
# Shared matrices are exported from the actual saved scene after dependency update.
s=next(s for s in bpy.data.scenes if s.name.startswith('C /'));bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
p=O/'source/camera-guide.json';d=json.loads(p.read_text())
for r in d['rig']:
 o=bpy.data.objects[r['id']];r['position']=list(o.location);r['lensMM']=o.data.lens;r['target']=[4.4,32,10.6]if r['id']=='04-hub'else [14.8,29,9.5]if r['id']=='05-team'else[-14.8,29,9.5]if r['id']=='06-events'else r['target'];r['cameraToWorld']=[list(row)for row in o.matrix_world];r['rotationEuler']=list(o.rotation_euler);r['orthoScale']=o.data.ortho_scale
 if r['id']=='11-overhead':r['target']=[0,9,0]
d['proposedNavigation']['signboardCenter']=[5.6,25,7.2]
d['screenMapping']='Existing video poster still, width-fit continuously across three panels with vertical center crop; not three stretched copies, not runtime playback.';p.write_text(json.dumps(d,indent=2))
# Editable ramp surfaces have real underside thickness without duplicate central faces.
for name in ['Accessible ramp / 1 to 20','Flared ramp apron']:
 o=bpy.data.objects[name]
 if not o.modifiers.get('Deck thickness'):
  m=o.modifiers.new('Deck thickness','SOLIDIFY');m.thickness=.24;m.offset=-1
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/Gullyverse-Lane-Rooftop-ABC.blend'),compress=True)
print('CALIBRATION_SAVED',flush=True)
