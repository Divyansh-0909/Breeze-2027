#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"
export GULLYVERSE_PLAN
GULLYVERSE_PLAN=$(mktemp "${TMPDIR:-/tmp}/breeze-ground-plan.XXXXXX.json")
trap 'rm -f "$GULLYVERSE_PLAN"' EXIT
python - "$ROOT/scripts/gullyverse/contact-ground-plan.json" "$GULLYVERSE_PLAN" "${1:-}" <<'PY'
import json,sys
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text())
if sys.argv[3]:p['source']['path']=str(Path(sys.argv[3]).resolve())
Path(sys.argv[2]).write_text(json.dumps(p))
PY
export GULLYVERSE_OUT="${GULLYVERSE_OUT:-$ROOT/public/models/gullyverse/locked-rev15z-m2a-contact-ground}"
mkdir -p "$GULLYVERSE_OUT"
cp public/models/gullyverse/locked-rev15z-clean-v2/source-inventory.json "$GULLYVERSE_OUT/source-inventory.json"
blender -b --python-exit-code 1 --threads 4 --python scripts/gullyverse/export_locked.py -- --plan "$GULLYVERSE_PLAN" --out "$GULLYVERSE_OUT" --samples 8
for step in bake_lighting.py finish_lightmap.py reexport.py verify-uv.py; do
  blender -b --python-exit-code 1 --threads 4 --python "scripts/gullyverse/$step"
done
node scripts/gullyverse/postprocess.mjs "$GULLYVERSE_OUT"
python scripts/gullyverse/validate-output.py "$GULLYVERSE_OUT" "$GULLYVERSE_OUT/source-inventory.json" "$GULLYVERSE_OUT/validation" --ground
python scripts/gullyverse/finalize-ground.py "$GULLYVERSE_OUT"
