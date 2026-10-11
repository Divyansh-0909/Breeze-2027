import bpy,sys,json
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
assert not any(out.iterdir()),'Fresh smoke directory required'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.5));cube=bpy.context.object;cube.name='Toolchain_OneMetreCube'
mat=bpy.data.materials.new('Smoke_PBR');mat.use_nodes=True;node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.2,.45,.3,1);node.inputs['Roughness'].default_value=.8;cube.data.materials.append(mat)
assert cube.data.uv_layers.active is not None
bpy.ops.wm.save_as_mainfile(filepath=str(out/'one-metre-cube.blend'))
bpy.ops.export_scene.gltf(filepath=str(out/'one-metre-cube.glb'),export_format='GLB',use_selection=True)
(out/'manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'units':'metres','blenderZUp':True,'glTFYUp':True,'dimensions':list(cube.dimensions),'UVLayers':len(cube.data.uv_layers),'materials':[m.name for m in cube.data.materials],'scope':'Isolated non-final technical cube, never replaces production art.'},indent=2))
