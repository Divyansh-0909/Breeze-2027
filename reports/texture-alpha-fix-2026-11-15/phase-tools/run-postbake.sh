#!/bin/bash
set -euo pipefail
cd /dev/shm/Breeze-2027-runtime
export TMPDIR=/dev/shm/gullyverse-runtime-tmp
export GULLYVERSE_OUT=/dev/shm/Breeze-2027-runtime/public/models/gullyverse/locked-rev15z-clean-v2
blender -b --python-exit-code 1 -t 4 --python scripts/gullyverse/finish_lightmap.py > /dev/shm/texture-alpha-fix-2026-11-15/evidence/denoise-final.log 2>&1
blender -b --python-exit-code 1 -t 2 --python scripts/gullyverse/reexport.py > /dev/shm/texture-alpha-fix-2026-11-15/evidence/reexport.log 2>&1
blender -b --python-exit-code 1 -t 2 --python scripts/gullyverse/verify-uv.py > /dev/shm/texture-alpha-fix-2026-11-15/evidence/uv-verification.log 2>&1
blender -b --python-exit-code 1 -t 2 --python scripts/gullyverse/collision.py > /dev/shm/texture-alpha-fix-2026-11-15/evidence/collision.log 2>&1
blender -b --python-exit-code 1 -t 2 --python scripts/gullyverse/export_graffiti.py > /dev/shm/texture-alpha-fix-2026-11-15/evidence/graffiti-export.log 2>&1
node scripts/gullyverse/postprocess.mjs "$GULLYVERSE_OUT" > /dev/shm/texture-alpha-fix-2026-11-15/evidence/compression.log 2>&1
python - <<'PY'
from pathlib import Path
import shutil
w=Path('/dev/shm/Breeze-2027-runtime');o=w/'public/models/gullyverse/locked-rev15z-clean-v2';old=w/'public/models/gullyverse/locked-rev15z-v1'
for f in ['index.html','pilot.css']:shutil.copy2(w/'components/gullyverse-runtime'/f,o/f)
shutil.copytree(old/'transcoders',o/'transcoders',dirs_exist_ok=True)
for f in ['contact.json','source-inventory.json']:shutil.copy2(old/f,o/f)
PY
node -e "require('esbuild').buildSync({entryPoints:['components/gullyverse-runtime/PrivatePilot.tsx'],bundle:true,format:'esm',platform:'browser',outfile:'public/models/gullyverse/locked-rev15z-clean-v2/pilot.js',minify:true,define:{'process.env.NODE_ENV':'\"production\"'}})"
