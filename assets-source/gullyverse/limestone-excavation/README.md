# Stage 2C.2 continuous limestone excavation

This is a reversible review asset. Production/default URLs retain Stage 2C.
The Grey limestone isolated LOD0 pilot is the approved material reference.
Its image payloads and glTF material factors are preserved exactly.

## Editable sources

- `excavation-macro.blend`: whole quarry macro form and its runtime LODs.
- `excavation-detailed.blend`: macro reference plus the three refined areas,
  each sampled from one continuous geological field.
- `manifest.json`: footprint, metre-based anchors, rim range, named nodes,
  detail-area arcs, part boundaries, texture contract and triangle counts.

The `EDITABLE_CONTINUOUS_MASTERS` collection contains joined source surfaces.
Unhide `Excavation_detailed_Master` or `Excavation_macro_Master` for editing.
Runtime collections are hidden in the saved authoring file to prevent multiple
LODs being shown together. Material images are packed in the Blender sources.

The origin is the existing world origin, not the isolated pilot's bottom pivot.
Blender coordinates `(x, -worldZ, worldY)` are exported as glTF Y-up metres.
No world-registry camera, stage, stall, walking or travel coordinate is rewritten.

## Reproduce

From the project root with Blender 4.3.2 and Python/numpy:

Khronos validation uses `gltf-validator@2.0.0-dev.3.10`. Install it in an
isolated tools directory if unavailable and set `GLTF_VALIDATOR_MODULE` to
that module's path; no new decoder or production dependency is required.

```sh
blender --background --python scripts/blender/author_limestone_excavation.py
python scripts/blender/pack_limestone_excavation.py
node reports/stage-2c2-limestone-excavation-2026-10-13/scripts/validate-glb.mjs
blender --background --python reports/stage-2c2-limestone-excavation-2026-10-13/scripts/validate-excavation.py
```

Authoring reads the current `blockout.layout.json`, existing tunnel topology and
approved Grey limestone Blender material. It writes only the new excavation
source/export directories. Do not run unrelated Breeze stage-generation scripts.

## Surface and UV contract

The perimeter is one periodic excavation curve. Bedding and faults use global
arc length and height, never independent noise or identical sculpted panels.
The three detailed areas are navigation-side wall, curved corner and the wall
visible from the stage looking back. The upper rim and terrain use common
geometry at every LOD. Partition borders have identical positions.

The original pilot's painted region is U=.02..88 and V=.03..97. UVs reflect
within this region, avoiding its padded end-cap smear strips. The reflection
preserves the original local UV/metre derivative. No source image is repainted,
recoloured, blurred or replaced. Tangent handedness is exported for the UVs.

Runtime GLBs contain geometry and a placeholder material. One small material
holder GLB contains the exact approved maps; its tiny mesh is never rendered.
The preview binds this shared family to macro/detailed geometry. All three
visual LODs are cached and warmed; only one per partition is visible. No Draco,
Meshopt or KTX2 decoder is introduced. Collision proxies are separate low-shell
raycast references; the existing navigation polygons remain authoritative.

## Review

Enable the existing local review build flag
`NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`, then open
`/?arrival=hub&quarryReview=excavation`. The panel switches Stage 2C, macro and
detailed modes. Remove the query and reload to restore the production default.
Stage 2C.1 remains available at `?quarryReview=geology`.

No permanent substitution, commit, push or deployment is authorized here.
Physical GPU/mobile acceptance remains pending; SwiftShader only validates
function, geometry, ownership and comparable software-renderer diagnostics.
