#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"
source_path=${1:?Pass the full path to the frozen Rev15Z Blender master}
build_root=${2:?Pass a separate writable directory for editable output}
zone=${3:?Choose south or north}
case "$zone" in
  south|north) ;;
  *) echo "Choose south or north" >&2; exit 2 ;;
esac
mkdir -p "$build_root"
build_root=$(cd "$build_root" && pwd)
export GULLYVERSE_OUT="$build_root/$zone"
export GULLYVERSE_PLAN="$build_root/plan-$zone.json"
mkdir -p "$GULLYVERSE_OUT"

blender -b -t 2 --python-exit-code 1 --python scripts/gullyverse/plan-market-lane.py -- "$source_path" "$zone" "$GULLYVERSE_PLAN"
blender -b -t 2 --python-exit-code 1 --python scripts/gullyverse/export_locked.py -- --plan "$GULLYVERSE_PLAN" --out "$GULLYVERSE_OUT" --samples 2
for step in bake_lighting.py finish_lightmap.py reexport.py verify-uv.py; do
  blender -b -t 2 --python-exit-code 1 --python "scripts/gullyverse/$step"
done
node scripts/gullyverse/postprocess.mjs "$GULLYVERSE_OUT"
python scripts/gullyverse/publish-cypher-gate.py "$GULLYVERSE_OUT"
