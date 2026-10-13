"""Losslessly reuse Stage 2A's material on the unchanged connected excavation.

python scripts/blender/extract_original_rock_material.py
No modeling, texture generation or existing file overwrite is performed.
"""
from pathlib import Path
import hashlib, json, struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb"
OUT = ROOT / "public/models/gullyverse/rock-look-restore"
OUT.mkdir(parents=True, exist_ok=True)

def read_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<III", data)
    assert magic == 0x46546C67 and version == 2 and length == len(data)
    count, kind = struct.unpack_from("<II", data, 12)
    assert kind == 0x4E4F534A
    document = json.loads(data[20:20+count])
    size, kind = struct.unpack_from("<II", data, 20+count)
    assert kind == 0x004E4942
    return document, data[28+count:28+count+size]

def write_glb(path, document, payload):
    document["buffers"] = [{"byteLength": len(payload)}]
    content = json.dumps(document, separators=(",", ":")).encode()
    content += b" " * (-len(content) % 4)
    payload = bytes(payload) + b"\0" * (-len(payload) % 4)
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 28+len(content)+len(payload))
                     + struct.pack("<II", len(content), 0x4E4F534A) + content
                     + struct.pack("<II", len(payload), 0x004E4942) + payload)

original, binary = read_glb(SOURCE)
assert len(original["materials"]) == 1
assert original["materials"][0]["name"] == "Quarry_Pilot_Original_Stone_PBR"
views, mapping, payload, images, inventory = [], {}, bytearray(), [], []
for index in sorted({image["bufferView"] for image in original["images"]}):
    view = original["bufferViews"][index]
    chunk = binary[view.get("byteOffset", 0):view.get("byteOffset", 0)+view["byteLength"]]
    payload.extend(b"\0" * (-len(payload) % 4))
    mapping[index] = len(views)
    views.append({"buffer": 0, "byteOffset": len(payload), "byteLength": len(chunk)})
    payload.extend(chunk)
for image in original["images"]:
    images.append({**image, "bufferView": mapping[image["bufferView"]]})
    view = original["bufferViews"][image["bufferView"]]
    chunk = binary[view.get("byteOffset", 0):view.get("byteOffset", 0)+view["byteLength"]]
    inventory.append({"name": image["name"], "bytes": len(chunk), "sha256": hashlib.sha256(chunk).hexdigest()})

# An inert holder provides GLTFLoader with a valid material consumer. It is
# never attached to the rendered scene; no original pilot mesh is imported.
accessors = []
for values, kind, count in [([0,0,0,.001,0,0,0,.001,0], "VEC3", 3),
                            ([0,0,1]*3, "VEC3", 3),
                            ([0,0,1,0,0,1], "VEC2", 3),
                            ([1,0,0,1]*3, "VEC4", 3)]:
    payload.extend(b"\0" * (-len(payload) % 4))
    chunk = struct.pack("<" + "f"*len(values), *values)
    accessors.append({"bufferView": len(views), "componentType": 5126, "count": count, "type": kind})
    views.append({"buffer": 0, "byteOffset": len(payload), "byteLength": len(chunk), "target": 34962})
    payload.extend(chunk)
accessors[0].update({"min": [0,0,0], "max": [.001,.001,0]})
doc = {"asset": original["asset"], "scene": 0, "scenes": [{"nodes": [0]}],
       "nodes": [{"name": "Original_Rock_Material_Holder_Not_Rendered", "mesh": 0}],
       "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2, "TANGENT": 3}, "material": 0}]}],
       "accessors": accessors, "bufferViews": views, "materials": original["materials"],
       "textures": original["textures"], "samplers": original.get("samplers", []), "images": images}
for key in ["extensionsUsed", "extensionsRequired"]:
    if key in original:
        doc[key] = original[key]
output = OUT / "rock-pilot-material.glb"
write_glb(output, doc, payload)

manifest = {"material": "Quarry_Pilot_Original_Stone_PBR",
            "runtime": "/models/gullyverse/rock-look-restore/rock-pilot-material.glb",
            "sourceGLB": str(SOURCE.relative_to(ROOT)),
            "sourceBlend": "assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend",
            "sourceAuthoring": ["scripts/blender/rock_pilot_materials.py", "scripts/blender/author_rock_pilot_2a.py"],
            "sourceSHA256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "runtimeSHA256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "runtimeBytes": output.stat().st_size, "images": inventory,
            "materialJSONUnchanged": True, "imagePayloadBytesUnchanged": True,
            "geometry": "Unchanged Stage2C2 connected excavation GLBs; only borrowed material assignment changes.",
            "UV": "Existing metre-scaled painted-atlas UVs are compatible: both pilots use U .02-.88 / V .03-.97.",
            "holderMeshRendered": False, "normalScale": original["materials"][0]["normalTexture"]["scale"],
            "photorealism": "Deferred; original approved darker Stage2A look reused without new authoring."}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
