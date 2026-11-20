"""Extract the market-to-cypher walk space from the immutable Blender scene."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy


def rounded(value):
    return round(float(value), 5)


def world_vertices(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def components(obj, vertices):
    """Keep the separate wall wings and jambs separate in the collision data."""
    neighbors = [[] for _ in vertices]
    for edge in obj.data.edges:
        a, b = edge.vertices
        neighbors[a].append(b)
        neighbors[b].append(a)
    remaining = set(range(len(vertices)))
    while remaining:
        start = min(remaining)
        pending = [start]
        remaining.remove(start)
        group = []
        while pending:
            current = pending.pop()
            group.append(vertices[current])
            for adjacent in neighbors[current]:
                if adjacent in remaining:
                    remaining.remove(adjacent)
                    pending.append(adjacent)
        yield group


def footprint(vertices):
    return [rounded(f(v[axis] for v in vertices)) for f in (min, max) for axis in (0, 1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    lock = json.loads((Path(__file__).resolve().parents[2] / "docs/runtime/ART-LOCK.json").read_text())
    with args.source.open("rb") as file:
        source_hash = hashlib.file_digest(file, "sha256").hexdigest()
    assert source_hash == lock["source"]["sha256"], "Use the frozen Rev15Z master"
    bpy.ops.wm.open_mainfile(filepath=str(args.source))
    scene = bpy.context.scene
    assert scene.name == lock["source"]["scene"]
    scene.frame_set(1)
    bpy.context.view_layer.update()
    strips = []
    for obj in scene.objects:
        if obj.hide_render or not obj.get("groundSurface"):
            continue
        shell = bpy.data.objects[obj["navigationSourceObject"]]
        terrain = world_vertices(obj)
        source = world_vertices(shell)
        # Use the locked road's location and the original smooth shell's slope.
        # The pothole depressions remain visible without jerking the camera.
        start = min(v.y for v in terrain)
        upper = [p for p in shell.data.polygons if p.normal.z > 0.9]
        top = [source[i] for p in upper for i in p.vertices]
        end = start + max(v.y for v in top) - min(v.y for v in top)
        start_height = max(v.z for v in terrain) - (max(v.z for v in top) - min(v.z for v in top))
        end_height = max(v.z for v in terrain)
        half_width = min(max(v.x for v in top), -min(v.x for v in top))
        if "Rooftop slab" in obj.name:
            end = 22.0  # Forecourt only. Later chunks extend beyond this limit.
        if "Flared ramp apron" in obj.name:
            # The connector houses flank this stretch. Stay inside their street face.
            half_width = min(half_width, 3.5)
        strips.append({
            "source": obj.name, "shell": shell.name,
            "start": rounded(start), "end": rounded(end),
            "halfWidth": rounded(half_width),
            "startHeight": rounded(start_height), "endHeight": rounded(end_height),
        })
    strips.sort(key=lambda strip: strip["start"])
    assert len(strips) == 4
    for a, b in zip(strips, strips[1:]):
        assert a["end"] == b["start"] and a["endHeight"] == b["startHeight"], (a, b)

    solids = []
    for obj in sorted(scene.objects, key=lambda item: item.name):
        if obj.type != "MESH" or obj.hide_render:
            continue
        role = obj.get("entryGatePart", "")
        street_hardware = obj.get("streetLampPart") == "hardware"
        base = " / Navigation base" in obj.name or " / Navigation upright" in obj.name
        person = "Cypher character" in obj.name and min(v.y for v in world_vertices(obj)) < 23
        ground_obstacle = role.startswith(("Boundary walls", "Left and right masonry", "Single see through"))
        if not (ground_obstacle or street_hardware or base or person):
            continue
        vertices = world_vertices(obj)
        split = role.startswith(("Boundary walls", "Left and right masonry")) or street_hardware
        for group in components(obj, vertices) if split else [vertices]:
            box = footprint(group)
            if street_hardware:
                # Only the part around a pole's foot blocks the player. The
                # overhead lamp arm is a different connected component.
                y = (box[1] + box[3]) / 2
                strip = next(s for s in strips if s["start"] <= y <= s["end"])
                height = strip["startHeight"] + (strip["endHeight"] - strip["startHeight"]) * (
                    (y - strip["start"]) / (strip["end"] - strip["start"])
                )
                group = [v for v in group if v.z < height + 1.7]
                if not group or min(v.z for v in group) > height + 0.35:
                    continue
                box = footprint(group)
            if min(box[2] - box[0], box[3] - box[1]) > 0.005:
                solids.append({"source": obj.name, "bounds": box})
    result = {"sourceSHA256": source_hash, "strips": strips, "solids": solids}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"WALK_SPACE_EXPORTED {len(strips)} road strips, {len(solids)} solid footprints")


if __name__ == "__main__":
    main()
