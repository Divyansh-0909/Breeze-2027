#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"
source_path=${1:?Pass the full path to the frozen Rev15Z Blender master}
build_dir=${2:?Pass a separate writable build directory for editable output}
mkdir -p "$build_dir"
export GULLYVERSE_OUT
GULLYVERSE_OUT=$(cd "$build_dir" && pwd)
export GULLYVERSE_PLAN
GULLYVERSE_PLAN=$(mktemp "${TMPDIR:-/tmp}/breeze-gate-plan.XXXXXX.json")
trap 'rm -f "$GULLYVERSE_PLAN"' EXIT

python - "$source_path" "$GULLYVERSE_PLAN" <<'PY'
import json
import sys
from pathlib import Path

scripts = Path("scripts/gullyverse")
base = json.loads((scripts / "export-plan.json").read_text())
gate = json.loads((scripts / "cypher-gate-plan.json").read_text())
base.update(gate)
base["source"]["path"] = str(Path(sys.argv[1]).resolve(strict=True))
Path(sys.argv[2]).write_text(json.dumps(base))
PY

blender -b --python-exit-code 1 -t 4 --python scripts/gullyverse/export_locked.py -- --plan "$GULLYVERSE_PLAN" --out "$GULLYVERSE_OUT" --samples 8
for step in bake_lighting.py finish_lightmap.py reexport.py verify-uv.py; do
  blender -b --python-exit-code 1 -t 4 --python "scripts/gullyverse/$step"
done
node scripts/gullyverse/postprocess.mjs "$GULLYVERSE_OUT"
python scripts/gullyverse/publish-cypher-gate.py "$GULLYVERSE_OUT"
