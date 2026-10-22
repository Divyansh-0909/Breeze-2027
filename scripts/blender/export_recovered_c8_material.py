"""Blender material master + hidden material-holder GLB; no wall export.
blender -b -t 2 --python scripts/blender/export_recovered_c8_material.py
"""
from pathlib import Path
import hashlib
import json
import bpy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets-source/gullyverse/recovered-c8-material"
OUT = ROOT / "public/models/gullyverse/recovered-c8-material"
OUT.mkdir(parents=True, exist_ok=True)
spec = json.loads((SOURCE / "material-manifest.json").read_text())
baseline = ROOT / "public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb"
host_manifest = json.loads((baseline.parent / "manifest.json").read_text())
part = next(part for part in host_manifest["parts"] if part["id"] == "Wall_15")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1

material = bpy.data.materials.new("Recovered_C8_Scanned_Multi_PBR")
material.use_nodes = True
material.use_backface_culling = True
nodes, links = material.node_tree.nodes, material.node_tree.links
principled = nodes.get("Principled BSDF")
principled.inputs["Metallic"].default_value = 0
coordinates = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeMapping")
mapping.name = "C8_APPROVED_3X_SAMPLING"
mapping.label = "Approved 3x features = one third repeat; UV0 only"
links.new(coordinates.outputs["UV"], mapping.inputs["Vector"])
mapping.inputs["Scale"].default_value = (spec["baseUVRepeat"], spec["baseUVRepeat"], 1)


def image(suffix, colour):
    node = nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(str(SOURCE / "textures" / ("scanned-multi-" + suffix)))
    node.image.colorspace_settings.name = "sRGB" if colour else "Non-Color"
    node.image.pack()
    links.new(mapping.outputs["Vector"], node.inputs["Vector"])
    return node


colour = image("basecolor.jpg", True)
normal = image("normal.png", False)
orm = image("orm.png", False)
links.new(colour.outputs["Color"], principled.inputs["Base Color"])
normal_map = nodes.new("ShaderNodeNormalMap")
normal_map.inputs["Strength"].default_value = 0.7
links.new(normal.outputs["Color"], normal_map.inputs["Color"])
links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
separate = nodes.new("ShaderNodeSeparateColor")
links.new(orm.outputs["Color"], separate.inputs["Color"])
links.new(separate.outputs["Green"], principled.inputs["Roughness"])
links.new(separate.outputs["Blue"], principled.inputs["Metallic"])
group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
group.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
occlusion = nodes.new("ShaderNodeGroup")
occlusion.node_tree = group
links.new(separate.outputs["Red"], occlusion.inputs["Occlusion"])
material["license"] = "Poly Haven CC0; originals and source-provenance.json retained"
material["scope"] = "Material-only C8 recovery on unchanged C5.1 geometry; no C6.2 bake reconstructed"

mesh = bpy.data.meshes.new("Hidden_Material_Holder_Mesh")
mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
mesh.materials.append(material)
uv = mesh.uv_layers.new(name="UVMap")
for loop in mesh.loops:
    uv.data[loop.index].uv = [(0, 0), (1, 0), (0, 1)][loop.vertex_index]
holder = bpy.data.objects.new("C8_Material_Owner_Not_Rendered", mesh)
scene.collection.objects.link(holder)
holder.select_set(True)
bpy.context.view_layer.objects.active = holder
runtime = OUT / "scanned-materials.glb"
bpy.ops.export_scene.gltf(filepath=str(runtime), export_format="GLB", use_selection=True,
                          export_texcoords=True, export_normals=True, export_tangents=True,
                          export_materials="EXPORT", export_extras=True, export_yup=True,
                          export_animations=False)
holder.select_set(False)
holder.hide_render = True
holder.hide_set(True)

# Read/import only the surviving export for an editable material-inspection host.
# Runtime always loads the ORIGINAL geometry file, never this import round trip.
bpy.ops.import_scene.gltf(filepath=str(baseline))
for object in list(scene.objects):
    if object == holder:
        continue
    if object.name not in part["nodes"]:
        bpy.data.objects.remove(object, do_unlink=True)
    else:
        object.data.materials.clear()
        object.data.materials.append(material)
        object.hide_set(not object.name.endswith("LOD0"))
        object.hide_render = not object.name.endswith("LOD0")
        object["inspection_copy_only"] = True

# Match runtime's repeat-only change, including the glTF V-origin translation.
mapping.inputs["Scale"].default_value = (spec["approvedUVRepeat"], spec["approvedUVRepeat"], 1)
mapping.inputs["Location"].default_value.y = spec["baseUVRepeat"] - spec["approvedUVRepeat"]
text = bpy.data.texts.new("RECOVERED_C8_MATERIAL_CONTRACT")
text.write("Rebuild maps with recover_c8_scanned_material.py, then this export script.\n"
           "Approved scale 3 enlarges UV0 features by dividing cached 1x repeats by three.\n"
           "Three source-derived images, 2K colour / 1K OpenGL normal / 1K ORM, normal strength 0.7, metal=0, AO=1.\n"
           "Inspection host is C5.1 Wall_15, not lost C6.2. Runtime reuses the original C5.1 GLB byte-for-byte.\n"
           "No geological geometry generated; no UV1 bake fabricated. Original inclined mask algorithm missing, reconstruction explicit.\n")
master = SOURCE / "recovered-c8-material.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(master))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


manifest = {"version": "recovery-phase2-c8", "material": material.name,
            "runtime": runtime.name, "runtimeBytes": runtime.stat().st_size,
            "runtimeSHA256": sha(runtime), "geometryChanged": False,
            "hostGeometryURL": "/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb",
            "hostGeometrySHA256": sha(baseline), "selectedPart": part,
            "selectedNodes": part["nodes"], "selectedArcMetres": part["arc"][1] - part["arc"][0],
            "approvedDefaultScale": 3, "baseUVRepeat": spec["baseUVRepeat"],
            "approvedUVRepeat": spec["approvedUVRepeat"], "UV1Bake": "not present in surviving host; unchanged",
            "uniqueRuntimeImages": 3, "estimatedRGBA8MipBytes": spec["estimatedRGBA8MipBytes"],
            "master": str(master.relative_to(ROOT)), "masterSHA256": sha(master),
            "historicalCompatibility": "Documented C8 A2 material reconstructed on original C5.1 sector; neither lost C6.2 geometry nor lost mask is claimed identical",
            "privateOnly": True, "lightingChanged": False, "publicDefaultChanged": False}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("RECOVERED_C8", json.dumps(manifest))
