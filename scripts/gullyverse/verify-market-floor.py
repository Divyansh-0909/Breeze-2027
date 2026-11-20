"""Check the four published GLBs against the walking grade and ramp ownership."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

models = Path(__file__).resolve().parents[2] / "public/models/gullyverse"
output = Path(sys.argv[sys.argv.index("--") + 1])
chunks = ["market-south", "market-north", "cypher-approach", "cypher-gate"]
ramp = "REV15Z / Accessible ramp / 1 to 20 / asphalt replacement"
bpy.ops.wm.read_factory_settings(use_empty=True)
owners = {}
sources = set()
road_objects = []
lamps = {}
for chunk in chunks:
    folder = models / ("locked-rev15z-" + chunk)
    manifest = json.loads((folder / "manifest.json").read_text())
    for row in manifest["objects"]:
        names = {row["sourceObject"], *row.get("batchedSourceObjects", [])}
        assert not ((sources & names) - {ramp}), (chunk, sources & names)
        sources.update(names)
        if row["sourceObject"] == ramp:
            owners[chunk] = set(row["sourceFaces"])
    scene_names = set(bpy.context.scene.objects.keys())
    bpy.ops.import_scene.gltf(filepath=str(folder / "contact-frontage.png.glb"))
    for ob in bpy.context.scene.objects:
        if ob.name in scene_names:
            continue
        if ob.type == "MESH" and ob.get("groundSurface"):
            road_objects.append((chunk, ob))
        if ob.get("streetLampPart") == "lens":
            lamp = ob["streetLampId"]
            assert lamp not in lamps, lamp
            lamps[lamp] = str(ob["lampState"])
assert set(owners) == {"market-north", "cypher-approach"}
north = owners["market-north"]
approach = owners["cypher-approach"]
assert north and approach and not (north & approach)
assert north | approach == set(range(max(north | approach) + 1))
assert lamps == {"L01": "steady", "L02": "dead", "L03": "flicker", "L04": "steady", "L05": "dead", "L06": "flicker"}

bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
surfaces = [(chunk, ob, BVHTree.FromObject(ob, deps), ob.matrix_world.inverted()) for chunk, ob in road_objects]
tested = set()
max_error = 0
samples = 0
for i in range(817):
    y = -29.5 + 51 * i / 816
    expected = 6 + min(24, max(0, y + 10)) * 0.05
    for x in (-2.85, -1.5, -0.38, 0, 0.38, 1.5, 2.85):
        start = Vector((x, y, 12))
        hits = []
        for chunk, ob, geometry, inverse in surfaces:
            hit, _, _, _ = geometry.ray_cast(inverse @ start, inverse.to_3x3() @ Vector((0, 0, -1)))
            if hit is not None:
                hits.append((ob.matrix_world @ hit).z)
                tested.add(chunk)
        assert hits, (x, y)
        deviation = abs(max(hits) - expected)
        assert deviation < 0.37, (x, y, hits, expected)
        max_error = max(max_error, deviation)
        samples += 1
assert tested == set(chunks)
result = {
    "status": "PASS",
    "sourceObjects": len(sources),
    "chunks": sorted(tested),
    "raySamples": samples,
    "maxDeviationFromWalkingGradeM": max_error,
    "rampFaces": {chunk: len(faces) for chunk, faces in owners.items()},
    "lampStates": lamps,
}
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
