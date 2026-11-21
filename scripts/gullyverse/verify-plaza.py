"""Check the published deck seam, walkable surface and audience provenance."""
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
output = Path(sys.argv[sys.argv.index("--") + 1])
models = root / "public/models/gullyverse"
space = json.loads((root / "components/gullyverse-runtime/plaza-walk-space.json").read_text())
deck = space["deck"]
bpy.ops.wm.read_factory_settings(use_empty=True)
owners = {}
deck_meshes = []
for chunk in ("cypher-gate", "cypher-plaza"):
    folder = models / ("locked-rev15z-" + chunk)
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["source"]["sha256"] == space["sourceSHA256"], chunk
    row = next(row for row in manifest["objects"] if row["sourceObject"] == deck)
    owners[chunk] = set(row["sourceFaces"])
    previous = set(bpy.context.scene.objects.keys())
    bpy.ops.import_scene.gltf(filepath=str(folder / "contact-frontage.png.glb"))
    objects = [obj for obj in bpy.context.scene.objects if obj.name not in previous
               and obj.get("runtimeOriginalSource") == deck]
    assert len(objects) == 1, chunk
    deck_meshes.extend(objects)
gate, plaza = owners.values()
assert gate and plaza and not (gate & plaza)
assert gate | plaza == set(range(15895))

bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
surfaces = [(obj, BVHTree.FromObject(obj, deps), obj.matrix_world.inverted()) for obj in deck_meshes]
surface_holes = [row["bounds"] for row in space["solids"] if row["source"] == deck]
samples = 0
for strip in space["strips"]:
    rows = round((strip["end"] - strip["start"]) * 20)
    for row in range(rows + 1):
        t = row / rows
        y = strip["start"] + t * (strip["end"] - strip["start"])
        width = strip["halfWidth"] + t * (strip["endHalfWidth"] - strip["halfWidth"]) - 0.38
        for scale in (-1, -0.8, -0.4, -0.2, 0, 0.2, 0.4, 0.8, 1):
            x = scale * width
            if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in surface_holes):
                continue
            ray = Vector((x, y, 10))
            hits = []
            for obj, geometry, inverse in surfaces:
                hit, _, _, _ = geometry.ray_cast(inverse @ ray, inverse.to_3x3() @ Vector((0, 0, -1)))
                if hit is not None:
                    hits.append((obj.matrix_world @ hit).z)
            assert hits and max(hits) > 6.95, (x, y, hits)
            samples += 1

audience = models / "locked-rev15z-cypher-audience"
manifest = json.loads((audience / "manifest.json").read_text())
assert manifest["source"]["sha256"] == space["sourceSHA256"]
assert len(manifest["objects"]) == 180 and all(
    row["sourceMesh"].endswith("/ LOD0") and row["runtimeMesh"].endswith("/ LOD1")
    for row in manifest["objects"]
)
def glb_json(file):
    with file.open("rb") as f:
        assert f.read(4) == b"glTF"
        f.seek(12)
        size, _ = struct.unpack("<II", f.read(8))
        return json.loads(f.read(size))


payload = glb_json(audience / "contact-frontage.png.glb")
actors = [node["extras"]["originalActorID"] for node in payload["nodes"] if "originalActorID" in node.get("extras", {})]
assert len(set(actors)) == len(actors) == 180
optimized = glb_json(audience / "contact-frontage.optimized.glb")
primitives = {key: sum(len(mesh["primitives"]) for mesh in data["meshes"])
              for key, data in (("sourceNodes", payload), ("optimized", optimized))}
assert primitives["optimized"] < primitives["sourceNodes"] / 4
result = {
    "status": "PASS", "roofRaySamples": samples, "deckFaceOwnership": {key: len(value) for key, value in owners.items()},
    "footprintSamples": space["footprintSamples"], "surfaceOpeningCells": space["surfaceOpeningCells"],
    "authoredLOD1Audience": len(actors), "audiencePrimitives": primitives,
}
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
