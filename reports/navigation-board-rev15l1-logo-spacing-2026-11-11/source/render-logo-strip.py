import bpy,json,time,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];m=json.loads((O/'evidence/sponsors.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='REV15L1 / source-logo strip render'
world=bpy.data.worlds.new('Logo strip black');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1);s.world=world
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
for row in m['logos']:
 im=bpy.data.images.load(str(O.parent/'navigation-board-rev15l-led-sponsors-2026-11-11'/row['file']));im.colorspace_settings.name='sRGB';im.alpha_mode='STRAIGHT'
 mat=bpy.data.materials.new(row['name']);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');emit=n.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,1,1,1);l.new(emit.outputs[0],out.inputs['Surface']);t=n.new('ShaderNodeTexImage');t.image=im;t.extension='CLIP'
 if row['transparentBackground']:
  if row['whiteOnly']:l.new(t.outputs['Alpha'],emit.inputs['Strength'])
  else:
   sep=n.new('ShaderNodeSeparateColor');l.new(t.outputs['Color'],sep.inputs[0]);a=n.new('ShaderNodeMath');a.operation='MINIMUM';l.new(sep.outputs[0],a.inputs[0]);l.new(sep.outputs[1],a.inputs[1]);b=n.new('ShaderNodeMath');b.operation='MINIMUM';l.new(a.outputs[0],b.inputs[0]);l.new(sep.outputs[2],b.inputs[1]);invert=n.new('ShaderNodeMath');invert.operation='MULTIPLY_ADD';invert.inputs[1].default_value=-.85;invert.inputs[2].default_value=1.;l.new(b.outputs[0],invert.inputs[0]);mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(invert.outputs[0],mask.inputs[0]);l.new(t.outputs['Alpha'],mask.inputs[1]);l.new(mask.outputs[0],emit.inputs['Strength'])
 else:
  delta=n.new('ShaderNodeVectorMath');delta.operation='SUBTRACT';delta.inputs[1].default_value=tuple(linear(v) for v in row['backgroundRGB']);l.new(t.outputs['Color'],delta.inputs[0]);absolute=n.new('ShaderNodeVectorMath');absolute.operation='ABSOLUTE';l.new(delta.outputs[0],absolute.inputs[0]);sep=n.new('ShaderNodeSeparateXYZ');l.new(absolute.outputs[0],sep.inputs[0]);a=n.new('ShaderNodeMath');a.operation='MAXIMUM';l.new(sep.outputs[0],a.inputs[0]);l.new(sep.outputs[1],a.inputs[1]);b=n.new('ShaderNodeMath');b.operation='MAXIMUM';l.new(a.outputs[0],b.inputs[0]);l.new(sep.outputs[2],b.inputs[1]);norm=n.new('ShaderNodeMapRange');norm.clamp=True;norm.inputs['From Min'].default_value=.03;norm.inputs['From Max'].default_value=.35;l.new(b.outputs[0],norm.inputs['Value']);l.new(norm.outputs['Result'],emit.inputs['Strength'])
 w,h=row['logoCells'];x=row['startCell']+row['tileCells']/2;z=32
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata([(x-w/2,0,z-h/2),(x+w/2,0,z-h/2),(x+w/2,0,z+h/2),(x-w/2,0,z+h/2)],[],[(0,1,2,3)]);mesh.materials.append(mat);uv=mesh.uv_layers.new();u0,v0,u1,v1=row['uv'];coords=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
 for p in mesh.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[mesh.loops[li].vertex_index]
 ob=bpy.data.objects.new(row['name'],mesh);s.collection.objects.link(ob)
data=bpy.data.cameras.new('Logo strip camera');data.type='ORTHO';data.ortho_scale=m['periodCells'];data.clip_start=.1;data.clip_end=1000;camera=bpy.data.objects.new(data.name,data);s.collection.objects.link(camera);camera.location=(m['periodCells']/2,-100,32);camera.rotation_euler=(Vector((m['periodCells']/2,0,32))-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=8;s.render.resolution_x=m['periodCells'];s.render.resolution_y=64;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
file=O/'viewer/logo-strip.png';s.render.filepath=str(file);start=time.monotonic();bpy.ops.render.render(write_still=True)
(O/'evidence/logo-strip.json').write_text(json.dumps({'file':'viewer/'+file.name,'size':[m['periodCells'],64],'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size,'logos':m['logoCount'],'method':'Blender render of the exact original image/vector artwork through alpha/background-contrast shaders. Repository logo bytes are unchanged.','seconds':time.monotonic()-start},indent=2));print('LOGO STRIP COMPLETE',m['logoCount'],flush=True)
