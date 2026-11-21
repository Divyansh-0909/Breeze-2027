"""Derive the courtyard footprint and obstacle data from locked Rev15Z."""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[2]
master, output = map(Path, sys.argv[sys.argv.index("--") + 1:])
base = json.loads((root / "components/gullyverse-runtime/cypher-walk-space.json").read_text())
with master.open("rb") as f:
    assert hashlib.file_digest(f, "sha256").hexdigest() == base["sourceSHA256"]
bpy.ops.wm.open_mainfile(filepath=str(master))
scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()
deck = scene.objects[base["strips"][-1]["source"]]
inverse = deck.matrix_world.inverted()
down = inverse.to_3x3() @ Vector((0, 0, -1))
tree = BVHTree.FromObject(deck, bpy.context.evaluated_depsgraph_get())


def lies_on_roof(x, y):
    result, _, _, _ = tree.ray_cast(inverse @ Vector((x, y, 10)), down)
    # The road has recessed potholes. The slab underside is 0.36 m below grade.
    return result is not None and (deck.matrix_world @ result).z > 6.95


def half_width(y):
    def edge(sign):
        low, high = 0, 17
        for _ in range(24):
            mid = (low + high) / 2
            if lies_on_roof(sign * mid, y):
                low = mid
            else:
                high = mid
        return low
    # Round inward so a supported point stays on the original slab.
    return int(1000 * min(edge(-1), edge(1))) / 1000


strips = [
    {"start": 14, "end": 16, "halfWidth": 5.5, "endHalfWidth": 5.5},
    {"start": 16, "end": 22, "halfWidth": half_width(16), "endHalfWidth": half_width(22)},
    {"start": 22, "end": 47.6, "halfWidth": half_width(22), "endHalfWidth": half_width(47.6)},
]
def width_at(strip, y):
    t = (y - strip["start"]) / (strip["end"] - strip["start"])
    return strip["halfWidth"] + t * (strip["endHalfWidth"] - strip["halfWidth"])


patches = set()
cell = 0.15
samples = 0
for strip in strips:
    for i in range(1, 100):
        t = i / 100
        y = strip["start"] + t * (strip["end"] - strip["start"])
        width = width_at(strip, y)
        for fraction in (-0.96, -0.8, -0.4, 0, 0.4, 0.8, 0.96):
            x = fraction * width
            if not lies_on_roof(x, y):
                patches.add((round(x / cell), round(y / cell)))
            samples += 1
    # The slab contains a few local openings. Exclude their sampled cells
    # from collision while preserving the original mesh and ground grade.
    for row in range(round(strip["start"] / cell) + 1, round(strip["end"] / cell)):
        y = cell * row
        columns = int((width_at(strip, y) - 0.36) / cell)
        for column in range(-columns, columns + 1):
            if not lies_on_roof(cell * column, y):
                patches.add((column, row))
            samples += 1

people, solids = [], []
for obj in sorted(scene.objects, key=lambda o: o.name):
    crowd = obj.get("originalActorID") or ("Cypher character" in obj.name and obj.get("crowdStyle"))
    solid = obj.name.startswith(("REV15Z / Screen slim rear casing", "REV15Z / Parapet screen support"))
    if obj.hide_render or not (crowd or solid):
        continue
    bounds = [obj.matrix_world @ Vector(point) for point in obj.bound_box]
    lo = [min(p[i] for p in bounds) for i in range(3)]
    hi = [max(p[i] for p in bounds) for i in range(3)]
    if crowd:
        x, y = [(lo[i] + hi[i]) / 2 for i in range(2)]
        person_radius = max(0.16, min(0.26, 0.4 * min(hi[i] - lo[i] for i in range(2))))
        people.append([round(x, 4), round(y, 4), round(person_radius, 4)])
    else:
        solids.append({"source": obj.name, "bounds": [round(v, 5) for v in (*lo[:2], *hi[:2])]})
assert len(people) == 186 and len(solids) == 9
for column, row in sorted(patches):
    x, y = cell * column, cell * row
    solids.append({
        "source": deck.name,
        "bounds": [round(value, 3) for value in (x - cell, y - cell, x + cell, y + cell)],
    })
result = {
    "sourceSHA256": base["sourceSHA256"], "deck": deck.name, "strips": strips,
    "footprintSamples": samples, "surfaceOpeningCells": len(patches), "people": people, "solids": solids,
}
output.write_text(json.dumps(result, indent=2) + "\n")
print("PLAZA_FOOTPRINT_PASS", strips, samples, len(people), len(solids), len(patches))
