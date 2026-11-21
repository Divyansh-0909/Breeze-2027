#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"
source_path=${1:?Pass the full path to the frozen Rev15Z Blender master}
build_root=${2:?Pass a separate writable directory for editable output}
zone=${3:?Choose south, north, plaza or audience}
case "$zone" in
  south|north) planner=plan-market-lane.py ;;
  plaza|audience) planner=plan-cypher-plaza.py ;;
  *) echo "Choose south, north, plaza or audience" >&2; exit 2 ;;
esac
mkdir -p "$build_root"
build_root=$(cd "$build_root" && pwd)
export GULLYVERSE_OUT="$build_root/$zone"
export GULLYVERSE_PLAN="$build_root/plan-$zone.json"
mkdir -p "$GULLYVERSE_OUT"

blender -b -t 2 --python-exit-code 1 --python "scripts/gullyverse/$planner" -- "$source_path" "$zone" "$GULLYVERSE_PLAN"
if [[ "$planner" == "plan-cypher-plaza.py" ]]; then
  export GULLYVERSE_SOURCE_INVENTORY="$build_root/cypher-source-inventory.json"
fi
blender -b -t 2 --python-exit-code 1 --python scripts/gullyverse/export_locked.py -- --plan "$GULLYVERSE_PLAN" --out "$GULLYVERSE_OUT" --samples 2
for step in bake_lighting.py finish_lightmap.py reexport.py verify-uv.py; do
  blender -b -t 2 --python-exit-code 1 --python "scripts/gullyverse/$step"
done
node scripts/gullyverse/postprocess.mjs "$GULLYVERSE_OUT"
python scripts/gullyverse/publish-cypher-gate.py "$GULLYVERSE_OUT"
