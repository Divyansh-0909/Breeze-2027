"""Copy validated runtime payloads from an editable cypher chunk build."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image

build = Path(sys.argv[1])
root = Path(__file__).resolve().parents[2]
model_root = root / "public/models/gullyverse"
baseline = model_root / "locked-rev15z-clean-v2"
manifest = json.loads((build / "manifest.json").read_text())
chunk = manifest["chunk"]
assert chunk in {"cypher-gate", "cypher-approach", "market-south", "market-north"}
output = model_root / ("locked-rev15z-" + chunk)
subprocess.run([
    sys.executable, str(Path(__file__).with_name("validate-output.py")),
    str(build), str(baseline / "source-inventory.json"), str(build / "validation"), "--ground",
], check=True)

output.mkdir(parents=True, exist_ok=True)
runtime_rows = manifest["runtime"]["files"]
for row in runtime_rows:
    file = build / row["file"]
    assert file.stat().st_size == row["bytes"]
    with file.open("rb") as data:
        assert hashlib.file_digest(data, "sha256").hexdigest() == row["sha256"]
    shutil.copyfile(file, output / row["file"])
transcoders = []
for file in sorted((baseline / "transcoders").iterdir()):
    target = output / "transcoders" / file.name
    target.parent.mkdir(exist_ok=True)
    shutil.copyfile(file, target)
    transcoders.append({
        "file": f"transcoders/{file.name}",
        "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
        "bytes": file.stat().st_size,
    })
manifest["files"] = runtime_rows + transcoders
if chunk == "cypher-approach":
    # Rearrange, rather than resample, the packed Blender strip. A single
    # 2048-wide texture also works on devices with small texture limits.
    packed_strip = build / "sponsor-strip.png"
    with Image.open(packed_strip) as image:
        red, green, blue = image.convert("RGB").split()
    assert red.size == (10676, 64) and red.tobytes() == green.tobytes() == blue.tobytes()
    atlas = Image.new("L", (2048, 384))
    for x in range(0, red.width, atlas.width):
        segment = red.crop((x, 0, min(x + atlas.width, red.width), red.height))
        atlas.paste(segment, (0, x // atlas.width * red.height))
    atlas_name = "sponsor-led.png"
    atlas.save(output / atlas_name)
    with Image.open(output / atlas_name) as check:
        for x in range(0, red.width, atlas.width):
            width = min(atlas.width, red.width - x)
            y = x // atlas.width * red.height
            assert check.crop((0, y, width, y + red.height)).tobytes() == red.crop(
                (x, 0, x + width, red.height),
            ).tobytes()
    data = (output / atlas_name).read_bytes()
    manifest["files"].append({
        "file": atlas_name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
    })
    manifest["sponsorDisplay"] = {
        "sourceStripSHA256": hashlib.sha256(packed_strip.read_bytes()).hexdigest(),
        "logoCount": 62, "minimumGapCells": 72, "periodCells": 10676,
        "cellsPerSecond": 30, "pixelsPreserved": True, "atlas": atlas_name,
    }
manifest["collision"] = {"adapter": "cypher-space.ts", "data": "cypher-walk-space.json"}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Published {len(manifest['files'])} validated {chunk} assets to {output}")
