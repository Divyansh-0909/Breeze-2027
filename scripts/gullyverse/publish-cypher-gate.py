"""Copy validated runtime payloads from the editable gate build."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

build = Path(sys.argv[1])
root = Path(__file__).resolve().parents[2]
model_root = root / "public/models/gullyverse"
baseline = model_root / "locked-rev15z-clean-v2"
output = model_root / "locked-rev15z-cypher-gate"
manifest = json.loads((build / "manifest.json").read_text())
assert manifest["chunk"] == "cypher-gate"
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
manifest["collision"] = {"adapter": "cypher-space.ts", "data": "cypher-walk-space.json"}
(output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Published {len(manifest['files'])} validated gate assets to {output}")
