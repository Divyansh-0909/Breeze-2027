"""Assemble public/models/gullyverse/locked-rev15z-fidelity/fidelity.json.

Inputs come from the locked Rev15Z master (see docs/runtime/M2M-BLENDER-FIDELITY.md):
  artspecs.json  written by scripts/gullyverse/fidelity-artspec.py
  probes.json    written by scripts/gullyverse/fidelity-probes.py
Road material classes come from the published chunk manifests (their recorded source images).
"""
import argparse
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public/models/gullyverse/locked-rev15z-fidelity"
MUD_MEAN = [0.4667, 0.4627, 0.451]  # mud-mean-color.png is a flat 4 x 4 mean; sRGB-encoded value


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def target(material):
    if "painted rolled steel" in material:
        return "Shutter slat"
    tail = re.sub(r"^(?:.* / )?ART / [^/]+ / ", "", material)
    return re.sub(r"\.\d{3}$", "", tail)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artspecs", type=Path)
    parser.add_argument("probes", type=Path)
    args = parser.parse_args()
    road = {}
    for manifest in sorted(glob.glob(str(ROOT / "public/models/gullyverse/locked-rev15z-*/manifest.json"))):
        data = json.loads(Path(manifest).read_text())
        for material in data.get("materials", []) if isinstance(data.get("materials"), list) else []:
            images = {image["name"] for image in material.get("sourceImages", [])}
            if "aggregate-1p2m-color.jpg" in images:
                road[material["name"]] = "aggregate"
            elif "mud-mean-color.png" in images:
                road[material["name"]] = "mud"
    arts = []
    for spec in json.loads(args.artspecs.read_text()):
        spec["id"] = re.sub(r"[^a-z0-9]+", "-", spec["material"].lower()).strip("-")
        spec["target"] = target(spec["material"])
        arts.append(spec)
    probes = []
    for probe in json.loads(args.probes.read_text()):
        x, y, z = probe["blender"]
        probes.append({
            "id": probe["id"], "position": [x, z, -y], "intensity": 1.0,
            "file": f"probe-{probe['id']}.hdr", "mobileFile": f"probe-{probe['id']}.mobile.hdr",
        })
    textures = {name: {"file": f"{name}.ktx2", "mobileFile": f"{name}.mobile.ktx2"}
                for name in sorted({a["texture"] for a in arts})}
    textures["aggregate"] = {"file": "aggregate-color.ktx2", "mobileFile": "aggregate-color.mobile.ktx2"}
    manifest = {
        "version": "rev15z-fidelity-1",
        "source": json.loads((ROOT / "scripts/gullyverse/export-plan.json").read_text())["source"],
        "road": {"materials": road, "mud": [round(srgb_to_linear(c), 4) for c in MUD_MEAN]},
        "textures": textures, "arts": arts, "probes": probes,
        # World shader "REV15P / Low cool night ambient": a constant linear colour (Cycles, geometry hidden).
        "sky": {"color": [0.0063, 0.0094, 0.0153]},
    }
    (OUT / "fidelity.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("FIDELITY", len(road), "road materials,", len(arts), "artworks,", len(probes), "probes")


if __name__ == "__main__":
    main()
