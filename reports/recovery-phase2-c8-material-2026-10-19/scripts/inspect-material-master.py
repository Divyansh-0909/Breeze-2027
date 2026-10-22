"""Read the new editable master without saving or modifying it."""
from pathlib import Path
import bpy
import json

ROOT = Path.cwd()
master = ROOT / "assets-source/gullyverse/recovered-c8-material/recovered-c8-material.blend"
bpy.ops.wm.open_mainfile(filepath=str(master))
material = bpy.data.materials["Recovered_C8_Scanned_Multi_PBR"]
mapping = material.node_tree.nodes["C8_APPROVED_3X_SAMPLING"]
images = [image for image in bpy.data.images if image.source == "FILE"]
assert len(images) == 3
assert all(image.packed_file for image in images)
assert all(tuple(image.size) in [(2048, 2048), (1024, 1024)] for image in images)
assert abs(mapping.inputs["Scale"].default_value.x - (2 / 10.790622 / 3)) < 1e-8
hosts = [object for object in bpy.data.objects if object.name.startswith("Foundation_Wall_15_LOD")]
assert len(hosts) == 3
assert all(object.data.uv_layers for object in hosts)
result = {"status": "PASS", "master": str(master.relative_to(ROOT)),
          "blenderVersion": bpy.app.version_string, "unitScale": bpy.context.scene.unit_settings.scale_length,
          "fileImages": [{"name": image.name, "resolution": list(image.size),
                          "packed": bool(image.packed_file), "colourSpace": image.colorspace_settings.name}
                         for image in images],
          "missingLinkedLibraries": [library.filepath for library in bpy.data.libraries
                                     if not Path(bpy.path.abspath(library.filepath)).is_file()],
          "inspectionHostLODs": [{"name": object.name, "vertices": len(object.data.vertices),
                                  "polygons": len(object.data.polygons)} for object in hosts],
          "mappingScale": list(mapping.inputs["Scale"].default_value),
          "masterSavedDuringInspection": False, "runtimeWallGeometryExported": False}
assert not result["missingLinkedLibraries"]
(ROOT / "reports/recovery-phase2-c8-material-2026-10-19/raw/blender-master-inspection.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
