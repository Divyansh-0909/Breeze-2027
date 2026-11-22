"""Export the packed Team artwork without modifying the sealed Blender file."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SOURCE_SHA = "89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041"
SCENE = "REV15Z / Wide Contact window and restored graffiti"
ORDER = (
    "Organising Committee", "Content", "Design", "Marketing",
    "Public Relations", "Sponsorship", "Videography", "Web Development",
)

def extract(output):
    import bpy

    scene = bpy.data.scenes[SCENE]
    murals = sorted((obj for obj in scene.objects if obj.get("artKind") == "mural-composition"),
                    key=lambda obj: obj["carouselSlide"])
    assert tuple(obj["team"] for obj in murals) == ORDER
    panels = []
    for index, obj in enumerate(murals):
        assert obj["carouselSlide"] == index and obj.hide_render == (index != 0)
        vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        assert len(vertices) == 4 and all(abs(v.x - vertices[0].x) < 1e-6 for v in vertices)
        uv = [tuple(loop.uv) for loop in obj.data.uv_layers.active.data]
        assert uv == [(0, 0), (1, 0), (1, 1), (0, 1)]
        image, = (node.image for material in obj.data.materials
                  for node in material.node_tree.nodes if node.type == "TEX_IMAGE")
        source = image.packed_file.data
        slug = obj["team"].lower().replace(" ", "-")
        min_y, max_y = min(v.y for v in vertices), max(v.y for v in vertices)
        min_z, max_z = min(v.z for v in vertices), max(v.z for v in vertices)
        (output / (slug + ".png")).write_bytes(source)
        panels.append({
            "team": obj["team"],
            "file": None if index == 0 else slug + ".webp",
            "sourceImageSHA256": hashlib.sha256(source).hexdigest(),
            "widthM": round(max_y - min_y, 6),
            "heightM": round(max_z - min_z, 6),
            "centre": [round(vertices[0].x, 6), round((min_z + max_z) / 2, 6), round(-(min_y + max_y) / 2, 6)],
            "people": [{"name": entry["name"], "role": entry["role"]} for entry in json.loads(obj["people"])],
        })
    for panel in panels:
        assert all(abs(a - b) < 1e-5 for a, b in zip(panel["centre"], panels[0]["centre"]))
        assert abs(panel["heightM"] - panels[0]["heightM"]) < 1e-5
    (output / "native.json").write_text(json.dumps(panels))

def export(master, output):
    from PIL import Image

    with master.open("rb") as source:
        assert hashlib.file_digest(source, "sha256").hexdigest() == SOURCE_SHA
    with tempfile.TemporaryDirectory(prefix="breeze-team-") as name:
        scratch = Path(name)
        subprocess.run(["blender", "-b", str(master), "-t", "2", "--python-exit-code", "4",
                        "--python", str(Path(__file__).resolve()), "--", name], check=True)
        panels = json.loads((scratch / "native.json").read_text())
        output.mkdir(parents=True, exist_ok=True)
        for panel in panels[1:]:
            target = output / panel["file"]
            source_path = scratch / (target.stem + ".png")
            with Image.open(source_path) as source:
                source = source.convert("RGBA")
                source.save(target, lossless=True, method=6, exact=True)
                with Image.open(target) as restored:
                    assert restored.convert("RGBA").tobytes() == source.tobytes()
                panel["resolution"] = list(source.size)
            panel["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        manifest = {"sourceSHA256": SOURCE_SHA, "scene": SCENE, "slides": panels}
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"Verified {len(panels)} authored states and {len(panels) - 1} pixel-identical runtime textures.")

if "--" in sys.argv:
    extract(Path(sys.argv[-1]))
elif __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python export-team-murals.py SEALED_MASTER.blend OUTPUT_DIRECTORY")
    export(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
