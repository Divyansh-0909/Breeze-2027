import bpy,json,time
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R;bpy.ops.wm.open_mainfile(filepath='/workspace/Breeze-2027/reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend');s=bpy.data.scenes.new('REV15P2 TEMP / exact native roughness');s.render.engine='CYCLES';s.cycles.samples=1;bpy.context.window.scene=s
bpy.ops.import_scene.gltf(filepath=str(B/'viewer/pilot.glb'),merge_vertices=False)
atlas={r['node']:r for r in json.loads((R/'evidence/ground-atlas.json').read_text())['objects']};conversions={r['export']:r['source'] for r in json.loads((B/'evidence/export.json').read_text())['materialConversions']};image=bpy.data.images.new('REV15P2 / native damp roughness',width=1024,height=2048,alpha=False);image.colorspace_settings.name='Non-Color'
ground=[o for o in s.objects if o.name in atlas];assert len(ground)==4
for o in ground:
 row=atlas[o.name];lo,hi=np.array(row['bounds']);tile=row['tileBlenderUV'];uv=o.data.uv_layers.new(name='P2LightUV');o.data.uv_layers.active=uv
 for p in o.data.polygons:
  for li in p.loop_indices:
   co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(tile[0]+(co.x-lo[0])/(hi[0]-lo[0])*(tile[2]-tile[0]),tile[1]+(co.y-lo[1])/(hi[1]-lo[1])*(tile[3]-tile[1])) if p.normal.z>.5 else (.002,.002)
 for i,m in enumerate(list(o.data.materials)):
  source=bpy.data.materials[conversions[m.name]];a=source.copy();o.data.materials[i]=a;nodes=a.node_tree.nodes;links=a.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');em=nodes.new('ShaderNodeEmission');links.new(bs.inputs['Roughness'].links[0].from_socket,em.inputs['Color']) if bs.inputs['Roughness'].is_linked else setattr(em.inputs['Color'],'default_value',(bs.inputs['Roughness'].default_value,)*3+(1,));output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');links.new(em.outputs[0],output.inputs['Surface']);target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
for o in s.objects:o.select_set(o in ground)
bpy.context.view_layer.objects.active=ground[0];s.render.bake.use_clear=False;s.render.bake.margin=4;bpy.ops.object.bake(type='EMIT',uv_layer='P2LightUV');image.filepath_raw=str(R/'viewer/textures/ground-roughness.png');image.file_format='PNG';image.save();print('NATIVE_ROUGHNESS_BAKED',flush=True)
