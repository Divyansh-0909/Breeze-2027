"""Recover the documented C8 A2 material from authentic CC0 source maps.

This authors maps only. It does not generate, displace or replace cliff geometry.
The original mask source is missing: this explicit, deterministic reconstruction
uses its documented inclined weathering/source-height design, not an exact copy.
Run from the repository: python3 scripts/blender/recover_c8_scanned_material.py
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import shutil
import urllib.request

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets-source/gullyverse/recovered-c8-material"
TEXTURES = SOURCE / "textures"
FAMILIES = {"marble_rock_03": 1.3489028164, "rock_face_03": 0.8928655525}
ATLAS_METRES = 10.790622


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch_metadata(asset, kind):
    directory = SOURCE / "licensed-source" / asset
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("provider-" + kind + ".json")
    url = "https://api.polyhaven.com/" + ("info/" if kind == "info" else "files/") + asset
    if not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "Breeze-Gullyverse-Recovery/2"})
        with urllib.request.urlopen(request, timeout=55) as response:
            path.write_bytes(response.read())
    return json.loads(path.read_text())


def download(job):
    path, item, asset, slot = job
    if not path.exists():
        request = urllib.request.Request(item["url"], headers={"User-Agent": "Breeze-Gullyverse-Recovery/2"})
        temporary = path.with_suffix(path.suffix + ".download")
        with urllib.request.urlopen(request, timeout=55) as response, temporary.open("wb") as stream:
            shutil.copyfileobj(response, stream)
        temporary.rename(path)
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "md5").hexdigest()
    assert actual == item["md5"], (path.name, "provider checksum mismatch")
    assert path.stat().st_size == item["size"], (path.name, "provider size mismatch")
    return {"asset": asset, "slot": slot, "file": str(path.relative_to(ROOT)),
            "url": item["url"], "providerMD5": actual, "sha256": sha256(path),
            "bytes": path.stat().st_size, "resolution": "2k"}


def load(path, scalar=False):
    image = Image.open(path)
    if scalar:
        values = np.asarray(image, dtype=np.float32)
        if values.ndim == 3:
            values = values[..., 0]
        return values / (65535 if values.max() > 255 else 255)
    return np.asarray(image.convert("RGB"), dtype=np.float32) / 255


def srgb_to_linear(rgb):
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(rgb):
    return np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * np.maximum(rgb, 0) ** (1 / 2.4) - 0.055)


def tile(array, u, v, periods, offset=(0, 0)):
    # Positive orientation only: no reflected UVs or rotated tangent frames.
    x = ((u * periods + offset[0]) % 1) * array.shape[1] - 0.5
    y = ((v * periods + offset[1]) % 1) * array.shape[0] - 0.5
    if array.ndim == 2:
        return map_coordinates(array, [y, x], order=1, mode="grid-wrap")
    return np.stack([map_coordinates(array[..., c], [y, x], order=1, mode="grid-wrap")
                     for c in range(array.shape[2])], axis=-1)


def channels(n, sources):
    v, u = np.meshgrid((np.arange(n, dtype=np.float32) + 0.5) / n,
                       (np.arange(n, dtype=np.float32) + 0.5) / n, indexing="ij")
    first = {key: tile(value, u, v, 6) for key, value in sources["marble_rock_03"].items()}
    second = {key: tile(value, u, v, 4, (0.173, 0.317))
              for key, value in sources["rock_face_03"].items()}
    # Interrupted inclined weathered beds, following the same atlas coordinates
    # as the scan. The source height prefers exposed faces; no random colours,
    # polygon assignment or painted shadow/AO multiplication is used.
    phase = 2 * np.pi * (2 * v - u) + 0.18 * np.sin(2 * np.pi * u)
    bed = np.exp(-(np.sin(phase) / 0.32) ** 2)
    interruption = (0.5 + 0.5 * np.cos(2 * np.pi * u + 0.8)) ** 2
    exposed = np.clip((first["height"] - 0.32) / 0.48, 0, 1)
    mask = np.clip(0.06 + 0.28 * bed * interruption + 0.10 * exposed, 0, 0.44)
    blend = mask[..., None]
    linear = first["colour"] * (1 - blend) + second["colour"] * blend
    normal = first["normal"] * (1 - blend) + second["normal"] * blend
    normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-8)
    roughness = first["roughness"] * (1 - mask) + second["roughness"] * mask
    return linear_to_srgb(linear), normal * 0.5 + 0.5, roughness, mask


def save(path, values):
    image = Image.fromarray(np.uint8(np.clip(values, 0, 1) * 255 + 0.5))
    image.save(path, **({"quality": 95, "subsampling": 0} if path.suffix == ".jpg" else {}))


def main():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    jobs, information = [], {}
    for asset in FAMILIES:
        info, files = fetch_metadata(asset, "info"), fetch_metadata(asset, "files")
        information[asset] = info
        for slot in ["Diffuse", "nor_gl", "Rough", "Displacement"]:
            item = files[slot]["2k"]["jpg" if slot == "Diffuse" else "png"]
            jobs.append((SOURCE / "licensed-source" / asset / item["url"].split("/")[-1], item, asset, slot))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        downloads = list(pool.map(download, jobs))
    license_source = ROOT / "assets-source/gullyverse/quarry-foundation/licensed-source/polyhaven-license.html"
    shutil.copyfile(license_source, SOURCE / "licensed-source/polyhaven-license.html")
    sources = {}
    for asset, gain in FAMILIES.items():
        paths = {row["slot"]: ROOT / row["file"] for row in downloads if row["asset"] == asset}
        rgb = srgb_to_linear(load(paths["Diffuse"])) * gain
        normal = load(paths["nor_gl"]) * 2 - 1
        normal /= np.maximum(np.linalg.norm(normal, axis=-1, keepdims=True), 1e-8)
        sources[asset] = {"colour": rgb, "normal": normal,
                          "roughness": load(paths["Rough"], True),
                          "height": load(paths["Displacement"], True)}
    colour, _, _, mask = channels(2048, sources)
    save(TEXTURES / "scanned-multi-basecolor.jpg", colour)
    _, normal, roughness, _ = channels(1024, sources)
    save(TEXTURES / "scanned-multi-normal.png", normal)
    save(TEXTURES / "scanned-multi-orm.png", np.stack([np.ones_like(roughness), roughness,
                                                   np.zeros_like(roughness)], axis=-1))
    # Authoring-only mask, not an additional visitor texture.
    save(TEXTURES / "geological-weathering-mask.png", mask)
    provenance = {"provider": "Poly Haven", "license": "CC0 1.0 Universal",
                  "licenseURL": "https://polyhaven.com/license",
                  "legalCodeURL": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
                  "claim": "Authentic provider PBR surface maps; the quarry is not claimed to be a scan.",
                  "referencePhotoPixelsUsedAsTextures": False,
                  "assets": [{"id": asset, "authors": info["authors"],
                              "scanCoverageMetres": [v / 1000 for v in info["dimensions"]],
                              "dimensionsProviderUnit": "millimetres",
                              "sourcePage": "https://polyhaven.com/a/" + asset}
                             for asset, info in information.items()], "downloads": downloads}
    (SOURCE / "source-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    manifest = {"version": "recovery-phase2-c8-material", "historicalSelector": "scanned-material-multi",
                "approvedDefaultScale": 3, "atlasMetresAt1x": ATLAS_METRES,
                "atlasMetresAt3x": ATLAS_METRES * 3, "hostUVUnitMetres": 2,
                "baseUVRepeat": 2 / ATLAS_METRES, "approvedUVRepeat": 2 / ATLAS_METRES / 3,
                "sourcePeriodsPerAtlas": {"marble_rock_03": 6, "rock_face_03": 4},
                "linearAlbedoGains": FAMILIES, "normalStrength": 0.7,
                "metallic": 0, "ormChannels": {"R": "1, no duplicate baked AO", "G": "source roughness blend", "B": 0},
                "colourSpaces": {"basecolor": "sRGB", "normal": "linear OpenGL tangent-space", "orm": "linear"},
                "runtimeResolutions": {"basecolor": [2048, 2048], "normal": [1024, 1024], "orm": [1024, 1024]},
                "uniqueRuntimeImages": 3, "estimatedRGBA8MipBytes": 33554432,
                "maskReconstruction": "Explicit interrupted inclined weathered beds and source-height preference; original lost mask formula unavailable, not claimed pixel-identical",
                "secondaryMaskRange": [float(mask.min()), float(mask.max())],
                "albedoMeanSRGB255": (colour.mean((0, 1)) * 255).tolist(),
                "roughnessRange": [float(roughness.min()), float(roughness.max())],
                "geometryChanged": False, "geometryDerivedUV1": "C5.1 has no UV1 bake; no replacement bake invented or sampled as UV0",
                "textures": [{"file": p.name, "bytes": p.stat().st_size, "sha256": sha256(p),
                              "runtime": not p.name.startswith("geological-")}
                             for p in sorted(TEXTURES.iterdir()) if p.is_file()]}
    (SOURCE / "material-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"sources": len(downloads), "sourceBytes": sum(r["bytes"] for r in downloads),
                      "runtimeBytes": sum(r["bytes"] for r in manifest["textures"] if r["runtime"]),
                      "albedoMeanSRGB255": manifest["albedoMeanSRGB255"],
                      "approvedUVRepeat": manifest["approvedUVRepeat"]}, indent=2))


if __name__ == "__main__":
    main()
