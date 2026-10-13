"""Safe authoring smoke test: writes only to the specified scratch directory.

blender --background --python scripts/blender/validate_toolchain.py -- <scratch-dir>
Requires an installed Blender executable; has not been executed without one.
"""
import json
import sys
from pathlib import Path
import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) != 1:
    raise RuntimeError("Specify one scratch output directory; existing festival assets are never overwritten.")
out = Path(args[0]).resolve()
if out.name != "blender-smoke":
    raise RuntimeError("Scratch directory must be named blender-smoke.")
out.mkdir(parents=True, exist_ok=True)
if any(out.iterdir()):
    raise RuntimeError("Scratch directory must be empty to preserve existing source/evidence.")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
cube = bpy.context.object
cube.name = "Toolchain_OneMetreCube"
bpy.ops.wm.save_as_mainfile(filepath=str(out / "one-metre-cube.blend"))
bpy.ops.export_scene.gltf(filepath=str(out / "one-metre-cube.glb"), export_format="GLB", use_selection=True)
(out / "manifest.json").write_text(json.dumps({
    "blender": bpy.app.version_string, "units": "metres", "object": cube.name,
    "source": "one-metre-cube.blend", "runtime": "one-metre-cube.glb",
    "size": list(cube.dimensions), "exported": True,
}, indent=2), encoding="utf-8")
print("Smoke source and GLB exported:", out)
