"""Explicit non-overlapping ground atlas; no native file is saved."""
import bpy,json,time
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];B=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11';bpy.ops.wm.open_mainfile(filepath=str(B/'delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'));native=bpy.context.scene;s=bpy.data.scenes.new('REV15P2 TEMP / ground atlas');s.world=native.world.copy();s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=2;bpy.context.window.scene=s
for o in native.objects:
 if o.type=='LIGHT' and o.data.energy>0 and not o.hide_render:a=o.copy();a.data=o.data.copy();s.collection.objects.link(a)
bpy.ops.import_scene.gltf(filepath=str(B/'viewer/pilot.glb'),merge_vertices=False)
ground=[o for o in s.objects if o.type=='MESH' and any(m and m.get('groundLightmap') for m in o.data.materials)];assert len(ground)==4
image=bpy.data.images.new('REV15P2 / ground diffuse light',width=1024,height=2048,alpha=False);image.colorspace_settings.name='Non-Color';rows=[]
for i,o in enumerate(ground):
 coords=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);lo=coords.min(0);hi=coords.max(0);tile=[.015,.015+i*.25,.985,.235+i*.25];uv=o.data.uv_layers.new(name='P2LightUV');o.data.uv_layers.active=uv
 for p in o.data.polygons:
  normal=o.matrix_world.to_3x3()@p.normal
  for li in p.loop_indices:
   co=coords[o.data.loops[li].vertex_index]
   uv.data[li].uv=(tile[0]+(co[0]-lo[0])/(hi[0]-lo[0])*(tile[2]-tile[0]),tile[1]+(co[1]-lo[1])/(hi[1]-lo[1])*(tile[3]-tile[1])) if normal.z>.5 else (.002,.002)
 for m in o.data.materials:
  if not m:continue
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':n.inputs['Metallic'].default_value=0;n.inputs['Roughness'].default_value=1
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;m.node_tree.nodes.active=n
 rows.append({'node':o.name,'bounds':[lo.tolist(),hi.tolist()],'tileBlenderUV':tile})
for o in s.objects:o.select_set(o in ground)
bpy.context.view_layer.objects.active=ground[0];s.render.bake.target='IMAGE_TEXTURES';s.render.bake.use_clear=False;s.render.bake.margin=4;s.render.bake.use_pass_color=False;s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True
start=time.monotonic();bpy.ops.object.bake(type='DIFFUSE',uv_layer='P2LightUV');p=R/'viewer/textures/ground-lightmap.png';p.parent.mkdir(exist_ok=True);image.filepath_raw=str(p);image.file_format='PNG';image.save()
(R/'evidence/ground-atlas.json').write_text(json.dumps({'status':'PASS','size':[1024,2048],'samples':4,'seconds':time.monotonic()-start,'objects':rows,'sourceUV1Issue':'Two prior floor meshes had metre-scale UVs in TEXCOORD_1 rather than valid atlas coordinates. This pass creates explicit bounded, non-overlapping tiles.','sourceMasterModified':False},indent=2));print('GROUND_ATLAS_COMPLETE',len(rows),flush=True)
