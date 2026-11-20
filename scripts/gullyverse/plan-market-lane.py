"""Select two market chunks and the exact complement of the existing ramp."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPTS = Path(__file__).resolve().parent
MODELS = SCRIPTS.parents[1] / "public/models/gullyverse"
RAMP = "REV15Z / Accessible ramp / 1 to 20 / asphalt replacement"
FLAT = "REV15Z / Lane flat / 6.8m clear / asphalt replacement"
VOLUME_NODES = {"PRINCIPLED_VOLUME", "VOLUME_ABSORPTION", "VOLUME_SCATTER"}


def solid(obj):
    if obj.hide_render or obj.type not in {"MESH", "FONT", "CURVE"}:
        return False
    return not any(
        material and material.use_nodes and any(node.type in VOLUME_NODES for node in material.node_tree.nodes)
        for material in obj.data.materials
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("zone", choices=("south", "north"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    base = json.loads((SCRIPTS / "export-plan.json").read_text())
    with args.source.open("rb") as f:
        assert hashlib.file_digest(f, "sha256").hexdigest() == base["source"]["sha256"]
    base["source"]["path"] = str(args.source.resolve())
    bpy.ops.wm.open_mainfile(filepath=str(args.source))
    scene = bpy.context.scene
    assert scene.name == base["source"]["scene"]
    scene.frame_set(1)
    bpy.context.view_layer.update()
    approach = json.loads((MODELS / "locked-rev15z-cypher-approach/manifest.json").read_text())
    gate = json.loads((MODELS / "locked-rev15z-cypher-gate/manifest.json").read_text())
    assert approach["source"]["sha256"] == gate["source"]["sha256"] == base["source"]["sha256"]
    existing = {row["sourceObject"]: row["sourceFaces"] for manifest in (approach, gate) for row in manifest["objects"]}
    lower, upper = (-31.6, -10) if args.zone == "south" else (-10, 6.1)
    road = FLAT if args.zone == "south" else RAMP
    objects = [road]
    for obj in sorted(scene.objects, key=lambda ob: ob.name):
        if obj.name in existing or obj.get("groundSurface") or not solid(obj):
            continue
        points = [obj.matrix_world @ Vector(vertex) for vertex in obj.bound_box]
        x = [p.x for p in points]
        y = [p.y for p in points]
        centre_y = (min(y) + max(y)) / 2
        if lower <= centre_y < upper and min(x) < 13 and max(x) > -13:
            objects.append(obj.name)
    whole = objects.copy()
    excluded = {}
    if road == RAMP:
        assert isinstance(existing[RAMP], list) and existing[RAMP]
        excluded[RAMP] = existing[RAMP]
        whole.remove(RAMP)
    chunk = "market-" + args.zone
    base.update(
        version="locked-rev15z-" + chunk,
        output="public/models/gullyverse/locked-rev15z-" + chunk,
        chunk=chunk,
        chunks=[{"id": chunk, "sourceYCentres": [lower, upper]}],
        selection={
            "sourceObjects": objects, "wholeObjects": whole, "excludedFaces": excluded,
            "evaluateWholeMeshes": True, "batchStaticProps": True,
        },
        quality={
            "uvName": "RuntimeIrradianceUV", "resolution": 1024, "samples": 96,
            "skipLegacyIrradiance": True, "isolateMaterialBake": True,
            "proceduralUVOnly": True, "rayBiasM": 0.001,
        },
    )
    base["bake"].update(resolution=2048, margin=4)
    args.output.write_text(json.dumps(base, indent=2) + "\n")
    print("MARKET_PLAN", chunk, len(objects), flush=True)


if __name__ == "__main__":
    main()
