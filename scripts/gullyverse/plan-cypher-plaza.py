"""Select the visible locked courtyard and its separate audience payload."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPTS = Path(__file__).resolve().parent
MODELS = SCRIPTS.parents[1] / "public/models/gullyverse"
PRIOR = ("cypher-gate", "cypher-approach", "market-south", "market-north")
DECK = "REV15Z / Rooftop slab / 32m x 40m / asphalt replacement"
FORM_MOCKUP = {"native form label", "native form illustration"}
VOLUME_NODES = {"PRINCIPLED_VOLUME", "VOLUME_ABSORPTION", "VOLUME_SCATTER"}


def solid(obj):
    return not obj.hide_render and obj.type in {"MESH", "FONT", "CURVE"} and not any(
        mat and mat.use_nodes and any(node.type in VOLUME_NODES for node in mat.node_tree.nodes)
        for mat in obj.data.materials
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("zone", choices=("plaza", "audience"))
    parser.add_argument("output", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    plan = json.loads((SCRIPTS / "export-plan.json").read_text())
    with args.source.open("rb") as f:
        assert hashlib.file_digest(f, "sha256").hexdigest() == plan["source"]["sha256"]
    plan["source"]["path"] = str(args.source.resolve())
    bpy.ops.wm.open_mainfile(filepath=str(args.source))
    scene = bpy.context.scene
    assert scene.name == plan["source"]["scene"]
    scene.frame_set(1)
    bpy.context.view_layer.update()

    existing = {}
    for zone in PRIOR:
        manifest = json.loads((MODELS / f"locked-rev15z-{zone}/manifest.json").read_text())
        assert manifest["source"]["sha256"] == plan["source"]["sha256"]
        for row in manifest["objects"]:
            existing[row["sourceObject"]] = row["sourceFaces"]
            existing.update(dict.fromkeys(row.get("batchedSourceObjects", []), "ALL"))

    objects = []
    mesh_overrides = {}
    for obj in sorted(scene.objects, key=lambda item: item.name):
        if obj.name in existing or obj.get("groundSurface") or not solid(obj):
            continue
        if obj.get("contactPart") in FORM_MOCKUP:
            continue
        audience = bool(obj.get("originalActorID"))
        if audience != (args.zone == "audience"):
            continue
        if audience:
            mesh = bpy.data.meshes.get(obj["LOD1"])
            assert mesh and len(mesh.polygons) < len(obj.data.polygons), obj.name
            mesh_overrides[obj.name] = mesh.name
        else:
            points = [obj.matrix_world @ Vector(point) for point in obj.bound_box]
            x = [p.x for p in points]
            y = [p.y for p in points]
            centre_y = (min(y) + max(y)) / 2
            if not (13.9 <= centre_y <= 67 and min(x) < 31 and max(x) > -31):
                continue
        objects.append(obj.name)
    whole = objects.copy()
    excluded = {}
    if args.zone == "plaza":
        assert isinstance(existing[DECK], list) and existing[DECK]
        objects.append(DECK)
        excluded[DECK] = existing[DECK]
    else:
        assert len(objects) == 180, len(objects)
    chunk = "cypher-" + args.zone
    plan.update(
        version="locked-rev15z-" + chunk,
        output="public/models/gullyverse/locked-rev15z-" + chunk,
        chunk=chunk,
        chunks=[{"id": chunk}],
        selection={
            "sourceObjects": objects, "wholeObjects": whole, "excludedFaces": excluded,
            "meshOverrides": mesh_overrides, "evaluateWholeMeshes": True,
            "batchStaticProps": args.zone == "plaza",
        },
        quality={
            "uvName": "RuntimeIrradianceUV", "resolution": 1024, "samples": 96,
            "skipLegacyIrradiance": True, "isolateMaterialBake": True,
            "proceduralUVOnly": True, "rayBiasM": 0.001,
        },
    )
    plan["bake"].update(resolution=2048, margin=4)
    args.output.write_text(json.dumps(plan, indent=2) + "\n")
    print("CYPHER_PLAN", chunk, len(objects), sum(len(bpy.data.meshes[m].polygons) for m in mesh_overrides.values()), flush=True)


if __name__ == "__main__":
    main()
