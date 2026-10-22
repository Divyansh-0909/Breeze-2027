"""Blender read-only check: blender -b -t 2 --python THIS -- MASTER OUTPUT_JSON."""
from pathlib import Path
import hashlib
import json
import sys
import bpy

arguments = sys.argv[sys.argv.index('--') + 1:]
master, output = map(lambda name: Path(name).resolve(), arguments)
before = hashlib.sha256(master.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(master))
material = bpy.data.materials['Recovered_C8_Scanned_Multi_PBR']
mapping = material.node_tree.nodes['C8_APPROVED_3X_SAMPLING']
assert abs(mapping.inputs['Scale'].default_value.x - 2 / 10.790622 / 3) < 1e-8
images = [image for image in bpy.data.images if image.source == 'FILE']
assert len(images) == 3 and all(image.packed_file for image in images)
assert not [library for library in bpy.data.libraries if not Path(bpy.path.abspath(library.filepath)).is_file()]
assert hashlib.sha256(master.read_bytes()).hexdigest() == before
result = {'status': 'PASS', 'master': str(master), 'bytes': master.stat().st_size,
          'sha256': before, 'blender': bpy.app.version_string,
          'packedImages': len(images), 'mappingScale': list(mapping.inputs['Scale'].default_value),
          'linkedResourcesMissing': 0, 'sourceFileSaved': False}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
