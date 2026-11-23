#!/bin/bash
# Compresses the baked Rocketbox crowd GLBs (crowd-rocketbox.py) for the web:
# desktop: colour 1024 px ETC1S, normal 512 px UASTC; mobile: everything at 512 px, ETC1S colour;
# Meshopt geometry. Output: public/models/gullyverse/crowd-rocketbox/<avatar>[.mobile].glb
set -euo pipefail
source /opt/gv/build/env.sh
export PATH=$KTX_BIN:$PATH
T=$GULLYVERSE_TOOLS/node_modules/.bin/gltf-transform
RAW=${1:-/opt/gv/crowd/raw}
OUT=public/models/gullyverse/crowd-rocketbox
TMP=$(mktemp -d)
mkdir -p $OUT
for f in $RAW/*.glb; do
  a=$(basename $f .glb)
  $T dedup $f $TMP/$a.d.glb >/dev/null
  $T resize $TMP/$a.d.glb $TMP/$a.r.glb --width 1024 --height 1024 >/dev/null
  $T resize $TMP/$a.r.glb $TMP/$a.rn.glb --width 512 --height 512 --pattern "*normal*" >/dev/null
  $T uastc $TMP/$a.rn.glb $TMP/$a.n.glb --slots "normalTexture" --level 2 --zstd 18 >/dev/null
  $T etc1s $TMP/$a.n.glb $TMP/$a.c.glb --slots "baseColorTexture" --quality 192 >/dev/null
  $T meshopt $TMP/$a.c.glb $OUT/$a.glb --level medium >/dev/null
  $T resize $TMP/$a.d.glb $TMP/$a.m.glb --width 512 --height 512 >/dev/null
  $T etc1s $TMP/$a.m.glb $TMP/$a.mc.glb --quality 160 >/dev/null
  $T meshopt $TMP/$a.mc.glb $OUT/$a.mobile.glb --level medium >/dev/null
  echo "$a $(stat -c %s $OUT/$a.glb) $(stat -c %s $OUT/$a.mobile.glb)"
done
rm -rf $TMP
