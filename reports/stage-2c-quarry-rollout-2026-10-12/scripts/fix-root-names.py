import bpy
from pathlib import Path
p=Path.cwd()/'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend';bpy.ops.wm.open_mainfile(filepath=str(p))
for i in range(3):bpy.data.objects[f'Wall_LOD{i}.001'].name=f'Quarry_LOD{i}'
bpy.ops.wm.save_as_mainfile(filepath=str(p))
