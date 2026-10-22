"""Validate actual GLB maps, sampling, source provenance and baseline hashes."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import struct
import numpy as np
from PIL import Image

ROOT = Path.cwd()
OUT = ROOT / "reports/recovery-phase2-c8-material-2026-10-19/raw"
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / "assets-source/gullyverse/recovered-c8-material"
manifest = json.loads((ROOT / "public/models/gullyverse/recovered-c8-material/manifest.json").read_text())
spec = json.loads((source / "material-manifest.json").read_text())
provenance = json.loads((source / "source-provenance.json").read_text())
path = ROOT / "public/models/gullyverse/recovered-c8-material/scanned-materials.glb"
data = path.read_bytes()
size = struct.unpack_from("<I", data, 12)[0]
gltf, binary = json.loads(data[20:20 + size]), data[28 + size:]
assert len(gltf["images"]) == 3 and len(gltf["materials"]) == 1 and len(gltf["meshes"]) == 1
assert gltf["accessors"][gltf["meshes"][0]["primitives"][0]["indices"]]["count"] == 3
assert "COLOR_0" not in gltf["meshes"][0]["primitives"][0]["attributes"]
material = gltf["materials"][0]
slots = [material["normalTexture"], material["occlusionTexture"],
         material["pbrMetallicRoughness"]["baseColorTexture"],
         material["pbrMetallicRoughness"]["metallicRoughnessTexture"]]
transforms = [slot["extensions"]["KHR_texture_transform"] for slot in slots]
assert all(transform == transforms[0] for transform in transforms)
assert all(abs(value - spec["baseUVRepeat"]) < 1e-8 for value in transforms[0]["scale"])
assert all(slot.get("texCoord", 0) == 0 for slot in slots)
assert abs(material["normalTexture"]["scale"] - 0.7) < 1e-7
assert not material.get("doubleSided", False)
images = []
for image in gltf["images"]:
    view = gltf["bufferViews"][image["bufferView"]]
    payload = binary[view.get("byteOffset", 0):view.get("byteOffset", 0) + view["byteLength"]]
    decoded = Image.open(BytesIO(payload)).convert("RGB")
    values = np.asarray(decoded)
    if image["name"].endswith("orm"):
        assert decoded.size == (1024, 1024)
        assert np.all(values[..., 0] == 255) and np.all(values[..., 2] == 0)
    if image["name"].endswith("normal"):
        assert decoded.size == (1024, 1024)
        normal = values.astype(float) / 255 * 2 - 1
        assert np.max(np.abs(np.linalg.norm(normal, axis=-1) - 1)) < 0.015
    if image["name"].endswith("basecolor"):
        assert decoded.size == (2048, 2048)
    images.append({"name": image["name"], "size": decoded.size,
                   "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
for row in provenance["downloads"]:
    payload = (ROOT / row["file"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == row["sha256"]
    assert hashlib.md5(payload).hexdigest() == row["providerMD5"]
    assert len(payload) == row["bytes"]
host = ROOT / manifest["hostGeometryURL"].lstrip("/").replace("models/", "public/models/", 1)
assert hashlib.sha256(host.read_bytes()).hexdigest() == manifest["hostGeometrySHA256"]
result = {"status": "PASS", "sourceMapsVerified": len(provenance["downloads"]),
          "hostGeometrySHA256": manifest["hostGeometrySHA256"], "hostGeometryChanged": False,
          "holderTriangles": 1, "holderRendered": False, "images": images,
          "UV0TransformsAligned": True, "originalRepeat": transforms[0]["scale"],
          "approved3xRepeat": [value / 3 for value in transforms[0]["scale"]],
          "geometryUV1": "Absent from C5.1; no bake invented or altered",
          "estimatedUniqueRGBA8MipBytes": 33554432,
          "runtimeBytes": len(data), "runtimeSHA256": hashlib.sha256(data).hexdigest(),
          "originalMaskAvailable": False, "historicalScreenshotZIPAvailable": False}
(OUT / "material-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
